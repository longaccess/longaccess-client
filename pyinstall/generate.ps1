$os=(Get-WmiObject Win32_OperatingSystem)
if ($os.version -ge "6.1" -and $os.version -le "6.3") {
   $arch="Windows7-"
} else {
   Write-Host "Windows version not supported"
   return
}
$arch+=$os.OSArchitecture
$ver=(lacli --version | cut -c 7-)


pip uninstall -y lacli
pip install --egg ..

Remove-Item -Recurse -Force build
Remove-Item -Recurse -Force dist

pyinstaller lacli-win7.spec
