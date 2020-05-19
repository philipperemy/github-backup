import concurrent
import os
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from glob import glob
from pathlib import Path

import click as click
from git import Repo, Git
from github import Github
from tqdm import tqdm


@click.group()
def cli():
    pass


@cli.command('pull_all', short_help='Pull from all previously cloned repositories.')
@click.argument('clone_dir', required=True,
                type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True))
def pull_all(clone_dir):
    cloned_repos = glob(clone_dir + '/*/*', recursive=True)
    print(f'Found {len(cloned_repos)} cloned repositories in {clone_dir}.')
    with tqdm(cloned_repos, desc='pulling...') as bar:
        for cloned_repo in bar:
            Git(cloned_repo).pull()
            bar.set_description(f'[{Path(cloned_repo).name}] updated')


@cli.command('clone_all', short_help='Clone all the repositories.')
@click.option('--github_token', required=True, envvar='GITHUB_TOKEN', type=str)
@click.option('--clone_dir', default=str(datetime.now()),
              type=click.Path(exists=False, file_okay=False, dir_okay=True, writable=True, readable=True,
                              resolve_path=True))
def clone_all(github_token, clone_dir):
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
                executor.submit(Repo.clone_from, repo.ssh_url, os.path.join(clone_dir, repo.full_name)): repo
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


if __name__ == '__main__':
    cli()
