#Add-OdbcDsn -Name "PostgresForPS" -DriverName "PostgreSQL Unicode(x64)" -SetPropertyValue @("Server=localhost","Database=appendage","Port=7245","Username=postgres","Password=pcs4ppl123#") -DsnType "User"

$conn = New-Object -comobject ADODB.Connection
$connStr = "Remote Provider={PostgreSQL};Data Source=192.168.1.3;location=appendage;Port=7245"
$conn.Open($connStr,"postgres","pcs4ppl123#")

$recordset = $conn.Execute("SELECT * 
                            FROM staff;")

while ($recordset.EOF -ne $True)
{
    foreach ($field in $recordset.Fields)
    {
        '{0,30} = {1,-30}' -f # this line sets up a nice pretty field format, but you don't really need it
        $field.name, $field.value
    }
   ''  # this line adds a line between records
$recordset.MoveNext()
}

$dInfo = @{}
$info = wmic diskdrive get serialNumber
$dInfo.add("diskdrive_serialNumber",$info[2])
$info = wmic diskdrive get model
$dInfo.add("diskdrive_model",$info[2])
$info = wmic diskdrive get size
$dInfo.add("diskdrive_size",$info[2])
$info = wmic bios get serialNumber
$dInfo.add("bios_serialNumber",$info[2])
$info = wmic bios get manufacturer
$dInfo.add("bios_manufacturer",$info[2])
$info = wmic cpu get description
$dInfo.add("cpu_description",$info[2])

$snQuery = "SELECT sanitized
                FROM harddrives
                WHERE devicehdsn = "
$snQuery = $snQuery + "TRIM(LOWer('" + $dInfo["diskdrive_serialNumber"] +"'))"

$recordset=$conn.Execute($snQuery)
IF ($recordset.Fields[0].value -eq $null) {Write-Host "HD " + + "not in DB"}
ELSE {
    "HD is NOT logged as sanitized!!" 
    pause
    }
$sanitized = $null
while ($recordset.EOF -ne $True)
{
    foreach ($field in $recordset.Fields)
    {
        $sanitized = $field.value
        Write-Host $field.value
        Write-Host 'here'

    }
   ''  # this line adds a line between records
$recordset.MoveNext()
}
IF ($sanitized -eq 1) {Write-Host "HD is sanitized"}
ELSE {
    "HD is NOT logged as sanitized!!" 
    pause
    }


$conn.Close();
