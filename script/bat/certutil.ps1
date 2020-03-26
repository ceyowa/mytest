
# 在Win10环境下Q-Dir增加命令:
#certutil/MD5=%SystemRoot%\system32\WindowsPowerShell\v1.0\powershell.exe=-file F:\Code\mytest\script\bat\certutil.ps1 -al md5 -f %sel_files%
#certutil/SHA1=%SystemRoot%\system32\WindowsPowerShell\v1.0\powershell.exe=-file F:\Code\mytest\script\bat\certutil.ps1 -al sha1 -f %sel_files%
#certutil/SHA256=%SystemRoot%\system32\WindowsPowerShell\v1.0\powershell.exe=-file F:\Code\mytest\script\bat\certutil.ps1 -al sha256 -f %sel_files%
#certutil/All=%SystemRoot%\system32\WindowsPowerShell\v1.0\powershell.exe=-file F:\Code\mytest\script\bat\certutil.ps1 -al all -f %sel_files%
#
#

[CmdletBinding()]
param (
    [System.String]
    $al="MD5",

    [System.String]
    $f
)

Write-Output "Algorithm=$al"
Write-Output "FilePath=$f"

$hashResult = @()
if ($al -eq "all") {
    $allType = "SHA1", "SHA256", "SHA384", "SHA512", "MACTripleDES", "MD5", "RIPEMD160";
    foreach ($item in $allType) {
        $hashResult += Get-FileHash -Algorithm $item $f 
    }
    # $hashResult
}
else {
    $hashResult += Get-FileHash -Algorithm $al $f
}
$formatResult = $hashResult | Format-Table -Property Algorithm, Hash
$formatResult

# 确认是否需要保存结果
$confirmSaveToFile = Read-Host "Do you want to save the result to file Y/N?[N]"
if ($confirmSaveToFile -eq "Y"){
    $currentDay = Get-Date -Format "%yyy-%M-%d_%H_%m_%s"
    $fileName = "hashCode_$CurrentDay.txt"
    $parentPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
    if (Test-Path -Path $parentPath -Include $fileName){
        $confirmOverwrite = Read-Host "Do you want to overwrite it Y/N?[N]"
        if (not ($confirmOverWrite -eq "Y")){
            return
        }
    }
    
    $outFile = "$ParentPath\$fileName"
    "FilePath=$f" | Out-File -FilePath $outFile 
    $formatResult | Out-File -FilePath $outFile -Append 
    "Save success, result file is $outFile"
    Pause
}

