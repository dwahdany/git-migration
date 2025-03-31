#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path

def is_git_repo(path):
    """Check if a directory is a git repository."""
    return (path / '.git').exists()

def get_current_remote(path):
    """Get the current remote URL of a git repository."""
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            cwd=path,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def create_github_repo(name, description=""):
    """Create a new private repository on GitHub using gh CLI."""
    try:
        # Add prefix to repository name
        prefixed_name = f"migration25-{name}"
        
        # Create a new private repository
        result = subprocess.run(
            ['gh', 'repo', 'create', prefixed_name, '--private', '--description', description],
            capture_output=True,
            text=True,
            check=True
        )
        # Extract the repository URL from the output
        repo_url = result.stdout.strip()
        print(f"✓ Created new repository: {repo_url}")
        return repo_url
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create repository {prefixed_name}: {e}")
        return None

def update_remote(path, new_remote_url):
    """Update the remote URL of a git repository and push the code."""
    try:
        # Update remote URL
        subprocess.run(
            ['git', 'remote', 'set-url', 'origin', new_remote_url],
            cwd=path,
            check=True
        )
        print(f"✓ Updated remote for {path}")

        # Push all branches to the new remote
        subprocess.run(
            ['git', 'push', '--all', 'origin'],
            cwd=path,
            check=True
        )
        print(f"✓ Pushed all branches to new remote")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to update/push to remote for {path}: {e}")
        return False

def repo_exists(name):
    """Check if a repository exists on GitHub."""
    try:
        # Try to get the repository info
        subprocess.run(
            ['gh', 'repo', 'view', name],
            capture_output=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def process_repository(directory):
    """Process a single repository directory."""
    print(f"\nProcessing {directory}...")
    
    if not is_git_repo(directory):
        print(f"✗ {directory} is not a git repository")
        return False

    current_remote = get_current_remote(directory)
    if current_remote:
        print(f"Current remote: {current_remote}")
        
        # Check if repository already exists
        new_name = f"migration25-{directory.name}"
        if repo_exists(new_name):
            print(f"✓ Repository {new_name} already exists, skipping...")
            return True
        
        # Create new repository on GitHub
        new_repo_url = create_github_repo(directory.name)
        if new_repo_url:
            return update_remote(directory, new_repo_url)
        else:
            print(f"✗ Skipping remote update due to repository creation failure")
    else:
        print(f"✗ No remote found for {directory}")
    return False

def find_repositories(target):
    """Find all repositories that match the target (directory or prefix)."""
    target_path = Path(target)
    
    # If target ends with a slash or is a directory, treat it as a prefix
    if str(target).endswith('/') or (target_path.exists() and target_path.is_dir()):
        # Get the base directory to search in
        search_dir = target_path if target_path.exists() else target_path.parent
        
        # Find all git repositories in the directory and its subdirectories
        repos = []
        for root, dirs, _ in os.walk(search_dir):
            # Skip .git directories
            if '.git' in dirs:
                repo_path = Path(root)
                if is_git_repo(repo_path):
                    repos.append(repo_path)
                # Skip subdirectories of git repos
                dirs[:] = [d for d in dirs if d != '.git']
        return repos
    else:
        # If it's a specific repository path
        if target_path.exists() and is_git_repo(target_path):
            return [target_path]
        return []

def list_repositories(repos):
    """List all repositories and their current remotes."""
    print("\nFound repositories:")
    print("-" * 80)
    for repo in repos:
        if is_git_repo(repo):
            remote = get_current_remote(repo)
            new_name = f"migration25-{repo.name}"
            exists = repo_exists(new_name)
            print(f"Repository: {repo.name}")
            print(f"Path: {repo}")
            print(f"Current remote: {remote if remote else 'No remote'}")
            print(f"New name will be: {new_name}")
            print(f"Status: {'Already exists on GitHub' if exists else 'Will be created'}")
            print("-" * 80)
        else:
            print(f"Repository: {repo.name}")
            print(f"Path: {repo}")
            print("Status: Not a git repository")
            print("-" * 80)

def main():
    if len(sys.argv) != 2:
        print("Usage: python update_remotes.py <directory_or_prefix>")
        print("Example: python update_remotes.py /path/to/repo")
        print("Example: python update_remotes.py my-project")
        sys.exit(1)

    target = Path(sys.argv[1])
    repositories = find_repositories(target)
    
    if not repositories:
        print(f"No repositories found matching '{target}'")
        sys.exit(1)

    # List all repositories first
    list_repositories(repositories)
    
    # Ask for confirmation
    response = input("\nDo you want to proceed with the migration? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled.")
        sys.exit(0)

    # Process each repository
    for directory in repositories:
        process_repository(directory)

if __name__ == "__main__":
    main() 