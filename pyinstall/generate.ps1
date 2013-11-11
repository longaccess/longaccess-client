function upload([string]$file, [string]$latest) {
        $ErrorActionPreference = 'SilentlyContinue'
	$bucket="download.longaccess.com"
	$region="us-east-1"
	
	$s3put=$env:VIRTUAL_ENV
	$s3put+="\Scripts/s3put"
        if (Test-Path $s3put) { 
                python $s3put -g "public-read" --bucket $bucket --region $region --prefix (pwd) "$file"
        } else {
                write-host "Unable to upload, s3put not found"
        }
	python -c @"
from boto.s3.connection import S3Connection
key = S3Connection().get_bucket(\"$bucket\").new_key(\"$latest\")
key.set_redirect(\"http://$bucket/$file\")
key.set_acl(\"public-read\")
"@
}
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

$rcc=$env:VIRTUAL_ENV
$rcc+="\lib\site-packages\PySide\pyside-rcc.exe"
& $rcc "..\lacli\views\decrypt.qrc" -o "..\lacli\views\qrc_decrypt.py"
pyinstaller lacli-win7.spec
$outfile="Longaccess-$ver-$arch.exe"
$latest="Longaccess-latest-$arch.exe"
makensis /X"OutFile $outfile" .\win.nsis
upload $outfile $latest
