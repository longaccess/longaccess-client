
$os=(Get-WmiObject Win32_OperatingSystem)
if ($os.version -ge "6.1" -and $os.version -le "6.3") {
   $arch="Windows7-"
} else {
   Write-Host "Windows version not supported"
   return
}
$arch+=$os.OSArchitecture

Remove-Item -Recurse -Force build
Remove-Item -Recurse -Force dist
$rcc=$env:VIRTUAL_ENV
$rcc+="\lib\site-packages\PySide\pyside-rcc.exe"
& $rcc "..\lacli\views\decrypt.qrc" -o "qrc_decrypt.py"
pyinstaller lacli-win7.spec
makensis .\win.nsis

