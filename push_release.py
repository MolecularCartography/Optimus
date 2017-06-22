from zipfile import ZipFile
from StringIO import StringIO
import json
import os
import re
import requests
import sys


if not 'OPTIMUS_GH_RELEASE_AUTH' in os.environ:
    raise ValueError('GitHub access token for publishing releases must be written to "OPTIMUS_GH_RELEASE_AUTH" environment variable.')


OPTIMUS_REPO_URL = 'https://api.github.com/repos/MolecularCartography/Optimus/releases'
OPTIMUS_VERSION_PATTERN = '[0-9]+\.[0-9]+\.[0-9]+'


def findfilebymask(filemask, file_descriptor):
    for file_name in os.listdir('./'):
        match_result = re.match(filemask, file_name)
        if match_result:
            return match_result
    ValueError('Release publishing failed: cannot find {} file.'.format(file_descriptor))


def checkgithubresponse(response, success_code, request_descriptor):
    if response.status_code != success_code:
        raise ValueError('Failed to {}. Reason: {}'.format(request_descriptor, response.text))


optimus_file_match = findfilebymask('Optimus_v({}).knwf'.format(OPTIMUS_VERSION_PATTERN), 'Optimus workflow')
cmdline_optimus_file_match = findfilebymask('Optimus_v({})_cmdline.knwf'.format(OPTIMUS_VERSION_PATTERN), 'Optimus command line workflow')
installer_folder_match = findfilebymask('installer', 'installation script')

optimus_gui_version = optimus_file_match.group(1)
optimus_cmd_version = cmdline_optimus_file_match.group(1)
if optimus_gui_version != optimus_cmd_version:
    raise ValueError('Release publishing failed: ' \
        'version numbers are different for GUI and command line versions of Optimus: {} vs {}.'.format(optimus_gui_version, optimus_cmd_version))

release_name = 'v{}'.format(optimus_gui_version)
payload = {
    'tag_name': release_name,
    'target_commitish': 'master',
    'name': release_name,
    'body': '',
    'draft': False,
    'prerelease': False
}
publish_headers = {
    'Authorization': 'token {}'.format(os.environ['OPTIMUS_GH_RELEASE_AUTH']),
    'Content-Type': 'application/json'
}

publish_response = requests.post(OPTIMUS_REPO_URL, headers=publish_headers, data=json.dumps(payload))
checkgithubresponse(publish_response, 201, 'publish release')

release_asset_name = 'Optimus.v{}.zip'.format(optimus_gui_version)
with ZipFile(release_asset_name, 'w') as release_asset:
    release_asset.write(optimus_file_match.group(0))
    release_asset.write(cmdline_optimus_file_match.group(0))
    for script_name in os.listdir('installer'):
        release_asset.write('installer\\{}'.format(script_name))

with open(release_asset_name, 'rb') as release_asset:
    asset_upload_url = json.loads(publish_response.content)['upload_url']
    if not '{' in asset_upload_url:
        raise ValueError('Release publishing failed: assets upload URL notation has changed.')
    else:
        asset_upload_url = asset_upload_url[:asset_upload_url.index('{')]
    upload_headers = {
        'Authorization': 'token {}'.format(os.environ['OPTIMUS_GH_RELEASE_AUTH']),
        'Content-Type': 'application/zip'
    }
    upload_asset_response = requests.post('{}?name={}'.format(asset_upload_url, release_asset_name), headers=upload_headers, data=release_asset.read())
    checkgithubresponse(upload_asset_response, 201, 'upload release assets')

os.remove(release_asset_name)

print('Optimus {} has been published successfully on GitHub.'.format(optimus_gui_version))
