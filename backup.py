import concurrent
import os
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime

from git import Repo
from github import Github
# First create a Github instance:
# or using an access token
from tqdm import tqdm

g = Github(os.environ['GITHUB_TOKEN'])

# https://github.com/git-lfs/git-lfs/issues/2406
# skip LFS.
os.environ['GIT_LFS_SKIP_SMUDGE'] = '1'

user_repos = [r for r in g.get_user().get_repos()]

print(f'Found {len(user_repos)} repositories (including org and private).')

output_dir = f'backup_{datetime.now()}'

# We can use a with statement to ensure threads are cleaned up promptly
with tqdm(total=len(user_repos), desc='backing up...') as bar:
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_repo = {executor.submit(Repo.clone_from, repo.ssh_url, os.path.join(output_dir, repo.full_name)): repo
                          for repo in user_repos}
        for future in concurrent.futures.as_completed(future_to_repo):
            repo = future_to_repo[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (repo, exc))
            else:
                bar.set_description(f'[{repo.ssh_url}] backed up.')
            finally:
                bar.update(1)
