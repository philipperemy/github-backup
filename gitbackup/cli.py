import concurrent
import os
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime

import click as click
from git import Repo
from github import Github
from tqdm import tqdm


@click.group()
def cli():
    pass


@cli.command('clone_all', short_help='Clone all the repositories.')
@click.argument('github_token', envvar='GITHUB_TOKEN', type=str)
@click.option('--output_dir', default=str(datetime.now()),
              type=click.Path(exists=False, file_okay=True, dir_okay=False, writable=True, readable=True,
                              resolve_path=True))
def clone_all(github_token, output_dir):
    g = Github(github_token)
    num_workers = 4

    # https://github.com/git-lfs/git-lfs/issues/2406
    # skip LFS.
    os.environ['GIT_LFS_SKIP_SMUDGE'] = '1'

    user_repos = [r for r in g.get_user().get_repos()]

    print(f'Found {len(user_repos)} repositories (including org and private).')

    # We can use a with statement to ensure threads are cleaned up promptly
    with tqdm(total=len(user_repos), desc='backing up...') as bar:
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            future_to_repo = {
                executor.submit(Repo.clone_from, repo.ssh_url, os.path.join(output_dir, repo.full_name)): repo
                for repo in user_repos}
            for future in concurrent.futures.as_completed(future_to_repo):
                repo = future_to_repo[future]
                try:
                    future.result()
                except Exception as exc:
                    print('%r generated an exception: %s' % (repo, exc))
                else:
                    bar.set_description(f'[{repo.ssh_url}] backed up.')
                finally:
                    bar.update(1)
