Write-Host "`n`nWelcome to installation of Optimus version 0.1.2016.01.13!`n"
Write-Host "To make sure the installation proceeds properly, please wait till this window closes. The installer will download about 2.3 GB of data so it can take some time depending on the speed of your internet connection.`n"
Write-Host "If you want to cancel the installation, close this window.`n"

Write-Host "Installation log:`n`n"

Write-Host "Creating temporary directory..."
$tmpDir = -join($env:TEMP, "\OptimusInstaller")
Remove-Item $tmpDir -Recurse -ErrorAction SilentlyContinue
New-Item -ItemType directory -Path $tmpDir | Out-Null

$client = new-object System.Net.WebClient

Write-Host "Downloading Python..."
$anacondaInstallerPath = -join($tmpDir, "\AnacondaInstaller.exe")
$client.DownloadFile("http://repo.continuum.io/archive/Anaconda2-4.2.0-Windows-x86_64.exe", $anacondaInstallerPath)

$anacondaInstallationDir = -join($env:LOCALAPPDATA, "\OptimusAnaconda")
Write-Host $(-join("Installing Python to `"", $anacondaInstallationDir, "`"..."))
$anacondaInstall = -join("& '", $anacondaInstallerPath, "' /S /D=", $anacondaInstallationDir, " | Out-Null")
iex $anacondaInstall

Write-Host "Installing additional packages..."

$pipUpgrade = -join("& '", $anacondaInstallationDir, "\python' -m pip install --upgrade pip")
iex $(-join($pipUpgrade, " | Out-Null"))

$installWithPip = -join("& '", $anacondaInstallationDir, "\Scripts\pip' install protobuf==2.6.1 pyopenms==2.0.1 pyMSpec==0.1", " | Out-Null")
iex $installWithPip

Write-Host "Downloading KNIME installer..."
$knimeInstallerPath = -join($tmpDir, "\KnimeInstaller.exe")
$client.DownloadFile("https://download.knime.org/analytics-platform/win/KNIME%20Full%203.3.1%20Installer%20(64bit).exe", $knimeInstallerPath)

Write-Host "Launching KNIME installer..."
iex $(-join("& '", $knimeInstallerPath, "' | Out-Null"))


Write-Host "Cleaning up temporary files...`n"
Remove-Item -Recurse -Force $tmpDir | Out-Null
