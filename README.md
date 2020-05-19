## Github backup
Back up all your github repositories.

### Installation

Generate a *personal access token* to access the Github API here: https://github.com/settings/tokens.

Tick *repo Full control of private repositories* and click on Generate.

Create a environment variable called `GITHUB_TOKEN` whose value is your freshly created token.

`export GITHUB_TOKEN="MY_GITHUB_TOKEN"`

Then run this command to install `gitbackup`.

`pip install github-back-up`

### Usage
```
Usage: gitbackup [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  clone_all  Clone all the repositories.
  pull_all   Pull from all previously cloned repositories.
```

### Example

- Clone all your public/private repositories to a timestamp-ed directory: `gitbackup clone_all`.

- Clone all your public/private repositories to `here`: `gitbackup clone_all --clone_dir here`.

- Update a backup directory: `gitbackup pull_all here`.
