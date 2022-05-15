if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) { Start-Process pwsh.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs; exit }
while ($true) {
    $clip=Get-Clipboard
    $input_ = Read-Host "Type y to add $clip to path"
    if(($input_ -eq 'y') -or ($input_ -eq 'Y'))
    {
        [Environment]::SetEnvironmentVariable("Path", $env:Path + ";"+$clip, "Machine")
        Read-Host "Added . Press Enter to continue"
    }
    }

