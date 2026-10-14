param([Parameter(Mandatory=$true)][int]$Port,[Parameter(Mandatory=$true)][string]$Database,[Parameter(Mandatory=$true)][string]$AdomdAssembly)
$ErrorActionPreference='Stop'
[Reflection.Assembly]::LoadFrom($AdomdAssembly) | Out-Null
$taskReference=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'validation/python-reference.json') -Raw | ConvertFrom-Json
$taskConnection=[Microsoft.AnalysisServices.AdomdClient.AdomdConnection]::new(('Data Source=localhost:'+$Port+';Initial Catalog='+$Database));$taskChecks=@()
try {
 $taskConnection.Open()
 foreach($taskCase in $taskReference.cases) {
  $taskDax='ROW("STR",[STR Net],"LTR",[LTR Net],"Gap",[Annual Difference],"Nights",[Break-even Nights],"ADR",[Break-even ADR],"LTRRent",[Break-even LTR Rent])';$taskFilters=@()
  foreach($taskProperty in $taskCase.selections.PSObject.Properties) { $taskNumber=[Convert]::ToString($taskProperty.Value,[Globalization.CultureInfo]::InvariantCulture);$taskFilters+=('TREATAS({'+$taskNumber+'},P'+$taskProperty.Name+'[Value])') }
  if($taskFilters.Count) { $taskDax='CALCULATETABLE('+ $taskDax+','+($taskFilters -join ',')+')' }
  $taskCommand=$taskConnection.CreateCommand();$taskCommand.CommandText='EVALUATE '+$taskDax;$taskReader=$taskCommand.ExecuteReader()
  if(-not $taskReader.Read()) { throw ('No DAX row for '+$taskCase.name) }
  $taskActual=[ordered]@{}
  for($taskIndex=0;$taskIndex -lt $taskReader.FieldCount;$taskIndex++) {
   $taskName=$taskReader.GetName($taskIndex).Trim('[',']');$taskValue=$taskReader.GetValue($taskIndex);$taskActual[$taskName]=if($taskValue -is [DBNull]) { $null } else { $taskValue };$taskExpected=$taskCase.expected.$taskName
   if($null -eq $taskExpected) { if($null -ne $taskActual[$taskName]) { throw ('Expected blank: '+$taskCase.name+'/'+$taskName) } }
   elseif([Math]::Abs([double]$taskActual[$taskName]-[double]$taskExpected) -gt 0.000001) { throw ('DAX/Python mismatch: '+$taskCase.name+'/'+$taskName) }
  }
  $taskReader.Close();$taskChecks+=@{case=$taskCase.name;status='pass';actual=$taskActual}
 }
} finally { $taskConnection.Close() }
$taskResult=@{engine='Actual Power BI Desktop Analysis Services engine';case_count=$taskChecks.Count;numerical_checks=$taskChecks.Count*6;tolerance=0.000001;cases=$taskChecks;note='DAX filter contexts validate parameter calculations; native slicer/navigation interaction and visual QA are recorded separately.'}
$taskResult | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'validation/desktop-dax-validation.json') -Encoding utf8
Write-Output ('PASS: '+$taskChecks.Count+' actual DAX cases / '+($taskChecks.Count*6)+' numeric or blank checks.')
