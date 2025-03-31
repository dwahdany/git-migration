# Git Repository Migration Tool

This script helps migrate Git repositories from one remote (e.g., GitLab) to new private GitHub repositories. The repositories must be cloned locally. It creates new private repositories on GitHub and updates the remote URLs of existing repositories.

## Prerequisites

- Python 3.x
- GitHub CLI (`gh`) installed and authenticated
- Git installed

## Usage

The script can be used in two ways:

1. Migrate a specific repository:
```bash
python update_remotes.py /path/to/repository
```

2. Migrate all repositories in a directory:
```bash
python update_remotes.py /path/to/directory/
```

## Features

- Creates new private repositories on GitHub with prefix "migration25-"
- Preserves all branches and history (doesn't preserve issues and other non-git content)
- Shows a preview of repositories to be migrated before proceeding
- Requires confirmation before making changes
- Handles nested git repositories correctly

## Example

```bash
# Migrate all repositories in a directory
python update_remotes.py /Users/username/git/repos/

# Migrate a specific repository
python update_remotes.py /Users/username/git/repos/my-project
```

## Safety Features

- Lists all repositories that will be affected before making changes
- Requires explicit confirmation before proceeding
- Shows current remote URLs and new repository names
- Skips non-git directories
- Handles errors gracefully
