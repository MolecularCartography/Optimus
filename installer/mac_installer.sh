echo
echo
echo Welcome to installation of Optimus version 0.1.2017.01.15!
echo
echo The installer will download about 2.4 GB of data so it will take some time depending on the speed of your internet connection.
echo
echo If you want to cancel the installation, press Ctrl+C.
echo
echo Installation log:
echo
echo

echo Creating temporary directory...
tmpDir=/tmp/OptimusInstaller
rm -rf $tmpDir
mkdir -p $tmpDir
echo

echo Downloading Python installer...
minicondaInstallScriptName=miniconda.sh
(cd $tmpDir; curl "https://repo.continuum.io/miniconda/Miniconda2-latest-MacOSX-x86_64.sh" > $minicondaInstallScriptName)
echo

echo Installing Python...
echo
minicondaInstallerPath=$tmpDir/$minicondaInstallScriptName
pythonInstallationDir=$HOME/OptimusMiniconda
rm -rf $pythonInstallationDir
bash $minicondaInstallerPath -b -p $pythonInstallationDir
echo

pythonExeDir=$pythonInstallationDir/bin
export PATH=$pythonExeDir:$PATH
echo "export PATH="$pythonExeDir:$PATH"" > ~/.bash_profile

echo Installing additional Python packages...
$pythonExeDir/pip install -q numpy==1.11.2 six==1.10.0 pandas==0.19.0 protobuf==2.6.1 pyopenms==2.0 pyMSpec==0.1
echo

echo Downloading KNIME installer...
knimeVersion=3.3.1
knimeImageName=knime.dmg
(cd $tmpDir; curl "https://download.knime.org/analytics-platform/macosx/knime-full_"$knimeVersion".app.macosx.cocoa.x86_64.dmg" > $knimeImageName)
knimeInstallerPath=$tmpDir/$knimeImageName

echo
echo Installing KNIME...
hdiutil mount $knimeInstallerPath > /dev/null
cp -R "/Volumes/KNIME $knimeVersion/KNIME $knimeVersion.app" /Applications
hdiutil unmount "/Volumes/KNIME $knimeVersion" > /dev/null

echo Cleaning up temporary files...
echo
rm -rf $tmpDir

echo Installation has finished successfully. You can run KNIME from \"Applications\".
echo

