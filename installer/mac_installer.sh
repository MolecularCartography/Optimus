echo
echo
echo Welcome to installation of Optimus version 0.1.2016.11.03!
echo
echo The installer will download about 1.5 GB of data so it will take some time depending on the speed of your internet connection.
echo
echo Installation log:
echo
echo

echo Creating temporary directory...
tmpDir=/tmp/OptimusInstaller
rm -rf $tmpDir
mkdir -p $tmpDir

echo Installing necessary Python packages...
pip install -q numpy==1.11.2 six==1.10.0 pandas==0.19.0 protobuf==2.6.1 pyopenms==2.0 pyMSpec==0.1

echo Downloading KNIME installer...
knimeVersion=3.2.1
(cd $tmpDir; curl -O "https://download.knime.org/analytics-platform/macosx/knime-full_"$knimeVersion".app.macosx.cocoa.x86_64.dmg")
knimeInstallerPath=$tmpDir"/knime-full_"$knimeVersion".app.macosx.cocoa.x86_64.dmg"

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
