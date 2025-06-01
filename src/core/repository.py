from typing import List, Optional, Dict
from datetime import datetime
from git import Repo, GitCommandError, Commit, Diff

class GitRepository:
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        try:
            self.repo = Repo(self.repo_path)
        except GitCommandError:
            raise ValueError(f"Директория {repo_path} не является Git репозиторием")

    @property
    def active_branch(self):
        return self.repo.active_branch

    @property
    def is_dirty(self) -> bool:
        return self.repo.is_dirty()

    @property
    def working_dir(self) -> str:
        """Возвращает рабочий каталог репозитория"""
        return self.repo.working_dir

    def get_untracked_files(self) -> List[str]:
        return self.repo.untracked_files

    def get_modified_files(self) -> List[str]:
        return [item.a_path for item in self.repo.index.diff(None)]

    def get_last_commit(self) -> Commit:
        return self.repo.head.commit

    def get_branches(self) -> List[str]:
        return [branch.name for branch in self.repo.heads]

    def get_commits(self, branch: Optional[str] = None) -> List[Commit]:
        if branch:
            return list(self.repo.iter_commits(branch))
        return list(self.repo.iter_commits())

    def get_diff(self, commit_hash: Optional[str] = None, file_path: Optional[str] = None) -> List[Diff]:
        if commit_hash:
            commit = self.repo.commit(commit_hash)
        else:
            commit = self.repo.head.commit

        if file_path:
            return commit.diff(commit.parents[0] if commit.parents else None, paths=[file_path])
        return commit.diff(commit.parents[0] if commit.parents else None)

    def get_file_content(self, commit_hash: str, file_path: str) -> str:
        return self.repo.git.show(f"{commit_hash}:{file_path}")

    def get_stats(self, commit_hash: Optional[str] = None) -> Dict:
        if commit_hash:
            commit = self.repo.commit(commit_hash)
        else:
            commit = self.repo.head.commit
        return commit.stats.total

    def get_file_stats(self, commit_hash: Optional[str] = None) -> Dict:
        if commit_hash:
            commit = self.repo.commit(commit_hash)
        else:
            commit = self.repo.head.commit
        return commit.stats.files

    def get_files(self) -> List[str]:
        """Получает список всех файлов в репозитории"""
        return self.repo.git.ls_files().splitlines() 