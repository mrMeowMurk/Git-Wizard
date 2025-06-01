#!/usr/bin/env python3
import os
import sys
from datetime import datetime
from typing import List, Optional

import click
from git import Repo, GitCommandError
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style

console = Console()

class GitWizard:
    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)
        try:
            self.repo = Repo(self.repo_path)
        except GitCommandError:
            console.print(f"[red]Ошибка: Директория {repo_path} не является Git репозиторием[/red]")
            sys.exit(1)
        
        self.session = PromptSession()
        self.commands = [
            "status", "branch", "log", "commit", "checkout",
            "merge", "pull", "push", "search", "stats", "graph"
        ]
        self.completer = WordCompleter(self.commands)
        self.style = Style.from_dict({
            'prompt': 'ansicyan bold',
        })

    def visualize_branches(self):
        """Визуализация веток в виде ASCII-графа"""
        tree = Tree("🌳 [bold green]Ветки[/bold green]")
        
        # Получаем все ветки
        branches = self.repo.heads
        
        # Создаем основную ветку
        main_branch = self.repo.active_branch
        main_tree = tree.add(f"🌿 [bold yellow]{main_branch.name}[/bold yellow]")
        
        # Добавляем остальные ветки
        for branch in branches:
            if branch.name != main_branch.name:
                main_tree.add(f"🌱 {branch.name}")
        
        console.print(tree)

    def search_commits(self, query: str):
        """Поиск коммитов по сообщению или содержимому"""
        table = Table(title=f"Результаты поиска: {query}")
        table.add_column("Хеш", style="cyan")
        table.add_column("Автор", style="magenta")
        table.add_column("Дата", style="green")
        table.add_column("Сообщение", style="white")

        for commit in self.repo.iter_commits():
            if query.lower() in commit.message.lower():
                table.add_row(
                    commit.hexsha[:8],
                    commit.author.name,
                    datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M'),
                    commit.message.split('\n')[0]
                )

        console.print(table)

    def show_activity_stats(self):
        """Показать статистику активности по авторам"""
        stats = {}
        
        for commit in self.repo.iter_commits():
            author = commit.author.name
            if author not in stats:
                stats[author] = 0
            stats[author] += 1

        table = Table(title="Статистика активности")
        table.add_column("Автор", style="cyan")
        table.add_column("Количество коммитов", style="magenta")

        for author, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            table.add_row(author, str(count))

        console.print(table)

    def run(self):
        """Запуск интерактивного режима"""
        console.print("[bold green]Добро пожаловать в GitWizard![/bold green]")
        console.print("Введите 'help' для списка команд или 'exit' для выхода")

        while True:
            try:
                command = self.session.prompt(
                    "gitwizard> ",
                    completer=self.completer,
                    style=self.style
                ).strip()

                if command == "exit":
                    break
                elif command == "help":
                    self.show_help()
                elif command == "graph":
                    self.visualize_branches()
                elif command.startswith("search "):
                    query = command[7:]
                    self.search_commits(query)
                elif command == "stats":
                    self.show_activity_stats()
                else:
                    console.print(f"[yellow]Неизвестная команда: {command}[/yellow]")

            except KeyboardInterrupt:
                continue
            except EOFError:
                break

    def show_help(self):
        """Показать справку по командам"""
        help_text = """
[bold cyan]Доступные команды:[/bold cyan]
  graph    - Визуализация веток
  search   - Поиск коммитов
  stats    - Статистика активности
  help     - Показать эту справку
  exit     - Выйти из программы
        """
        console.print(help_text)

@click.command()
@click.argument('repo_path', default='.')
def main(repo_path: str):
    """GitWizard - Улучшенный интерфейс для работы с Git"""
    wizard = GitWizard(repo_path)
    wizard.run()

if __name__ == '__main__':
    main() 