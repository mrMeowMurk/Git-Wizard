#!/usr/bin/env python3
import os
import sys
from datetime import datetime
from typing import List, Optional, Dict
from collections import defaultdict

import click
from git import Repo, GitCommandError, Commit, Diff
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
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
            "merge", "pull", "push", "search", "stats", "graph",
            "history", "changes", "filesearch", "filetypes", "diff"
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

    def visualize_history(self):
        """Визуализация истории коммитов в виде графа"""
        commits = list(self.repo.iter_commits())
        if not commits:
            console.print("[yellow]История коммитов пуста[/yellow]")
            return

        table = Table(title="История коммитов", show_header=True, header_style="bold magenta")
        table.add_column("Хеш", style="cyan", width=8)
        table.add_column("Автор", style="green")
        table.add_column("Дата", style="yellow")
        table.add_column("Сообщение", style="white")

        for commit in commits[:10]:  # Показываем последние 10 коммитов
            table.add_row(
                commit.hexsha[:8],
                commit.author.name,
                datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M'),
                commit.message.split('\n')[0]
            )

        console.print(table)

    def analyze_changes(self, commit_hash: Optional[str] = None):
        """Анализ изменений в файлах"""
        if commit_hash:
            try:
                commit = self.repo.commit(commit_hash)
            except ValueError:
                console.print(f"[red]Ошибка: Коммит {commit_hash} не найден[/red]")
                return
        else:
            commit = self.repo.head.commit

        stats = commit.stats.total
        files_changed = commit.stats.files

        console.print(Panel(f"[bold green]Статистика изменений[/bold green]"))
        console.print(f"Добавлено строк: [green]{stats['insertions']}[/green]")
        console.print(f"Удалено строк: [red]{stats['deletions']}[/red]")
        console.print(f"Изменено файлов: [yellow]{stats['files']}[/yellow]")

        table = Table(title="Измененные файлы", show_header=True, header_style="bold magenta")
        table.add_column("Файл", style="cyan")
        table.add_column("Добавлено", style="green")
        table.add_column("Удалено", style="red")

        for file, changes in files_changed.items():
            table.add_row(
                file,
                str(changes['insertions']),
                str(changes['deletions'])
            )

        console.print(table)

    def search_in_files(self, query: str):
        """Поиск по содержимому файлов"""
        results = []
        for root, _, files in os.walk(self.repo_path):
            if '.git' in root:
                continue
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if query.lower() in content.lower():
                            results.append(file_path)
                except Exception:
                    continue

        if not results:
            console.print(f"[yellow]Ничего не найдено по запросу: {query}[/yellow]")
            return

        table = Table(title=f"Результаты поиска: {query}")
        table.add_column("Файл", style="cyan")
        
        for file in results:
            table.add_row(file)

        console.print(table)

    def analyze_file_types(self):
        """Анализ типов файлов в репозитории"""
        file_types = defaultdict(int)
        total_files = 0

        for root, _, files in os.walk(self.repo_path):
            if '.git' in root:
                continue
            for file in files:
                total_files += 1
                ext = os.path.splitext(file)[1].lower()
                if ext:
                    file_types[ext] += 1
                else:
                    file_types['без расширения'] += 1

        table = Table(title="Статистика по типам файлов")
        table.add_column("Тип файла", style="cyan")
        table.add_column("Количество", style="magenta")
        table.add_column("Процент", style="green")

        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_files) * 100
            table.add_row(
                ext or 'без расширения',
                str(count),
                f"{percentage:.1f}%"
            )

        console.print(table)

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

    def show_diff(self, commit_hash: Optional[str] = None, file_path: Optional[str] = None):
        """Показать изменения в файлах"""
        try:
            if commit_hash:
                commit = self.repo.commit(commit_hash)
            else:
                # Если хеш не указан, показываем изменения в рабочей директории
                if self.repo.is_dirty():
                    console.print("[yellow]Есть несохраненные изменения в рабочей директории[/yellow]")
                    return
                commit = self.repo.head.commit

            if file_path:
                # Показываем изменения для конкретного файла
                try:
                    diff = commit.diff(commit.parents[0] if commit.parents else None, paths=[file_path])
                    if not diff:
                        console.print(f"[yellow]Файл {file_path} не был изменен в этом коммите[/yellow]")
                        return
                except ValueError:
                    console.print(f"[red]Ошибка: Файл {file_path} не найден[/red]")
                    return
            else:
                # Показываем изменения для всех файлов
                diff = commit.diff(commit.parents[0] if commit.parents else None)

            if not diff:
                console.print("[yellow]Нет изменений для отображения[/yellow]")
                return

            console.print(Panel(f"[bold green]Изменения в коммите {commit.hexsha[:8]}[/bold green]"))
            console.print(f"Автор: {commit.author.name}")
            console.print(f"Дата: {datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M')}")
            console.print(f"Сообщение: {commit.message.split('\n')[0]}\n")

            for diff_item in diff:
                if diff_item.a_path:
                    console.print(Panel(f"[bold cyan]Файл: {diff_item.a_path}[/bold cyan]"))
                    
                    # Показываем статистику изменений
                    try:
                        # Получаем статистику из diff_item
                        diff_text = diff_item.diff.decode('utf-8') if isinstance(diff_item.diff, bytes) else str(diff_item.diff)
                        insertions = sum(1 for line in diff_text.split('\n') if line.startswith('+') and not line.startswith('+++'))
                        deletions = sum(1 for line in diff_text.split('\n') if line.startswith('-') and not line.startswith('---'))
                        
                        console.print(f"Добавлено строк: [green]{insertions}[/green]")
                        console.print(f"Удалено строк: [red]{deletions}[/red]")
                    except Exception as e:
                        console.print(f"[yellow]Не удалось подсчитать статистику изменений: {str(e)}[/yellow]")
                    
                    # Показываем diff с подсветкой синтаксиса
                    try:
                        diff_text = diff_item.diff.decode('utf-8') if isinstance(diff_item.diff, bytes) else str(diff_item.diff)
                        syntax = Syntax(diff_text, "diff", theme="monokai")
                        console.print(syntax)
                    except Exception as e:
                        console.print(f"[red]Ошибка при отображении diff: {str(e)}[/red]")
                    
                    console.print()  # Пустая строка для разделения

        except Exception as e:
            console.print(f"[red]Ошибка при показе изменений: {str(e)}[/red]")

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
                elif command == "history":
                    self.visualize_history()
                elif command.startswith("changes"):
                    parts = command.split()
                    commit_hash = parts[1] if len(parts) > 1 else None
                    self.analyze_changes(commit_hash)
                elif command.startswith("diff"):
                    parts = command.split()
                    if len(parts) == 1:
                        self.show_diff()
                    elif len(parts) == 2:
                        self.show_diff(commit_hash=parts[1])
                    elif len(parts) == 3:
                        self.show_diff(commit_hash=parts[1], file_path=parts[2])
                elif command.startswith("filesearch "):
                    query = command[11:]
                    self.search_in_files(query)
                elif command == "filetypes":
                    self.analyze_file_types()
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
  graph      - Визуализация веток
  history    - История коммитов
  changes    - Анализ изменений (опционально: хеш коммита)
  diff       - Показать изменения (опционально: хеш коммита и путь к файлу)
  filesearch - Поиск по содержимому файлов
  filetypes  - Статистика по типам файлов
  search     - Поиск коммитов
  stats      - Статистика активности
  help       - Показать эту справку
  exit       - Выйти из программы
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