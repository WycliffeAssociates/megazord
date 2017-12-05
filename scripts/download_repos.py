import os
import yaml
import requests
import zipfile
import re
import shutil


def get_resources(filename):
    with open(filename, 'r') as stream:
        return yaml.load(stream)

def get_language_dirname(resource):
    return 'repos/' + resource.get('language').get('code') + '_' + resource.get('resource').get('code')

# def make_dir(dirname):
#     if not os.path.exists(dirname):
#         os.mkdir(dirname);

def download_and_extract_repos(urls, dirname):
    for url in urls:
        filename = get_filename(url)
        destination = os.path.join(dirname, filename)
        download_project_zip(url + '/archive/master.zip', destination)
        extract_project_zip(destination, dirname)

def get_filename(repo):
    repo_url_parts = repo.split('/')
    repo_url_parts.reverse()
    filename = repo_url_parts[0] + '.zip'
    return filename

def download_project_zip(url, target_file):
    r = requests.get(url, stream=True)
    with open(target_file, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

def extract_project_zip(filename, target_dir):
    try:
        with zipfile.ZipFile(filename, 'r') as z:
            z.extractall(target_dir)
            os.remove(filename)
    except zipfile.BadZipfile as exception:
        print('%s cannot be extracted' % filename)

def strip_checking_level(target_dir):
    for folder_name in os.listdir(target_dir):
        if 'l1' in folder_name or 'l2' in folder_name or 'l3' in folder_name:
            new_folder_name = re.sub(r'_l[123]', '', folder_name)
            shutil.move(
                os.path.join(target_dir, folder_name),
                os.path.join(target_dir, new_folder_name)
            )


if __name__ == "__main__":
    resources = get_resources('data/repo_urls.yaml')

    for resource in resources:
        language_dirname = get_language_dirname(resource)
        if not os.path.exists(language_dirname):
            os.mkdir(language_dirname);
            download_and_extract_repos(resource.get('repos', []), language_dirname)
            strip_checking_level(language_dirname)

    print "\nDone."
