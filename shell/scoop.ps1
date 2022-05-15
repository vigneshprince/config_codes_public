if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) { Start-Process pwsh.exe -WorkingDirectory (Get-Location).path "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs; exit }
$install = (Get-Content -Path 'scoop.txt' | Where-Object {$_ -notmatch '#|;'}) | Join-String -Separator ' '
$cmd="scoop install $install"
$response = Read-Host "$cmd (y/n)?"
if ( ($response -eq "y") -or ($response -eq 'Y')) {
    Invoke-Expression $cmd
}
else {
    write-host "Not installed"
}
    
Pause