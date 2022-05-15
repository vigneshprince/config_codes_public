Start-Process cmd {/c rclone mount mystoshiv: H: --network-mode}
while(-Not (Test-Path -Path 'H:\'))
{
   Start-Sleep -s .5
}
Invoke-Item H:\