from zipfile import ZipFile
import os
import re
import requests
import sys


OPTIMUS_REPO_URL = 'https://github.com/MolecularCartography/Optimus/releases'
OPTIMUS_VERSION_PATTERN = '[0-9]+\.[0-9]+\.[0-9]+'

if not 'OPTIMUS_GH_RELEASE_AUTH' in os.environ:
    raise ValueError('GitHub access token for publishing releases must be written to "OPTIMUS_GH_RELEASE_AUTH" environment variable.')


def findfilebymask(filemask, file_descriptor):
    for file_name in os.listdir('./'):
        match_result = re.match(filemask, file_name)
        if match_result:
            return match_result
    ValueError('Release publishing failed: cannot find {} file.'.format(file_descriptor))


optimus_file_match = findfilebymask('Optimus_v({}).knwf'.format(OPTIMUS_VERSION_PATTERN), 'Optimus workflow')
cmdline_optimus_file_match = findfilebymask('Optimus_v({})_cmdline.knwf'.format(OPTIMUS_VERSION_PATTERN), 'Optimus command line workflow')
installer_folder_match = findfilebymask('installer', 'installation script')

optimus_gui_version = optimus_file_match.group(1)
optimus_cmd_version = cmdline_optimus_file_match.group(1)
if optimus_gui_version != optimus_cmd_version:
    raise ValueError('Release publishing failed: ' \
        'version numbers are different for GUI and command line versions of Optimus: {} vs {}.'.format(optimus_gui_version, optimus_cmd_version))

payload = {
    'tag_name': 'v{}'.format(optimus_gui_version),
    'target_commitish': 'master',
    'name': 'v{}'.format(optimus_gui_version),
    'body': '',
    'draft': False,
    'prerelease': False
}

publish_response = requests.post(OPTIMUS_REPO_URL, headers={'Authorization': 'token {}'.format(os.environ['OPTIMUS_GH_RELEASE_AUTH']), "Accept": "application/vnd.github.manifold-preview"}, data=payload)

release_asset_name = 'Optimus.v{}.zip'.format(optimus_gui_version)
release_asset = ZipFile(release_asset_name, 'w')
release_asset.write(optimus_file_name)
release_asset.write(cmdline_optimus_file_name)
for script_name in os.listdir('installer'):
    release_asset.write('installer\\{}'.format(script_name))
release_asset.close()

requests.post('{}/{}/assets?name={}'.format(OPTIMUS_REPO_URL, publish_response['id']), headers={'Authorization': 'token {}'.format(os.environ['OPTIMUS_GH_RELEASE_AUTH']), "Accept": "application/vnd.github.manifold-preview"})
