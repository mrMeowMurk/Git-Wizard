#!/usr/bin/env python3
import os
import sys
from datetime import datetime
from typing import List, Optional, Dict
from collections import defaultdict
import json
import random

import click
from git import Repo, GitCommandError, Commit, Diff
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter, NestedCompleter
from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory

console = Console()

class GitWizard:
    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                progress.add_task(description="Инициализация GitWizard...", total=None)
                self.repo = Repo(self.repo_path)
        except GitCommandError:
            console.print(f"[red]Ошибка: Директория {repo_path} не является Git репозиторием[/red]")
            sys.exit(1)
        
        # Загружаем настройки
        self.settings = self.load_settings()
        
        # Создаем историю команд
        history_file = os.path.join(os.path.expanduser("~"), ".gitwizard_history")
        self.session = PromptSession(history=FileHistory(history_file))
        
        # Создаем вложенный комплитер для команд
        self.commands = {
            "graph": None,
            "history": None,
            "commit-graph": None,
            "worktime": {
                "": None,
            },
            "lost-commits": None,
            "conflicts": {
                "": None,
            },
            "changes": {
                "": None,
            },
            "diff": {
                "": None,
            },
            "filesearch": {
                "": None,
            },
            "filetypes": None,
            "search": {
                "": None,
            },
            "stats": None,
            "security": {
                "": None,
            },
            "docs": {
                "md": None,
                "html": None,
            },
            "performance": {
                "": None,
            },
            "ci-cd": {
                "github": None,
                "gitlab": None,
            },
            "theme": {
                "light": None,
                "dark": None,
                "monokai": None,
                "solarized": None,
            },
            "settings": {
                "show": None,
                "save": None,
                "reset": None,
            },
            "help": None,
            "exit": None,
        }
        
        self.completer = NestedCompleter.from_nested_dict(self.commands)
        self.style = Style.from_dict({
            'prompt': 'ansicyan bold',
        })

    def load_settings(self) -> Dict:
        """Загрузка настроек пользователя"""
        settings_file = os.path.join(os.path.expanduser("~"), ".gitwizard_settings.json")
        default_settings = {
            'theme': 'dark',
            'show_welcome': True,
            'show_tips': True,
            'max_history': 1000,
            'auto_complete': True,
            'color_output': True,
            'default_branch': 'main',
            'editor': os.environ.get('EDITOR', 'vim'),
            'ide_integration': {
                'vscode': False,
                'pycharm': False,
                'sublime': False
            }
        }
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    user_settings = json.load(f)
                    # Обновляем дефолтные настройки пользовательскими
                    default_settings.update(user_settings)
        except Exception as e:
            console.print(f"[yellow]Не удалось загрузить настройки: {str(e)}[/yellow]")
        
        return default_settings

    def save_settings(self):
        """Сохранение настроек пользователя"""
        settings_file = os.path.join(os.path.expanduser("~"), ".gitwizard_settings.json")
        try:
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            console.print("[green]Настройки успешно сохранены[/green]")
        except Exception as e:
            console.print(f"[red]Ошибка при сохранении настроек: {str(e)}[/red]")

    def show_settings(self):
        """Показать текущие настройки"""
        table = Table(title="Текущие настройки GitWizard")
        table.add_column("Параметр", style="cyan")
        table.add_column("Значение", style="green")
        
        for key, value in self.settings.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    table.add_row(f"{key}.{subkey}", str(subvalue))
            else:
                table.add_row(key, str(value))
        
        console.print(table)

    def set_theme(self, theme: str):
        """Установка цветовой темы"""
        themes = {
            'light': {
                'background': 'white',
                'foreground': 'black',
                'accent': 'blue',
                'success': 'green',
                'warning': 'yellow',
                'error': 'red'
            },
            'dark': {
                'background': 'black',
                'foreground': 'white',
                'accent': 'cyan',
                'success': 'green',
                'warning': 'yellow',
                'error': 'red'
            },
            'monokai': {
                'background': '#272822',
                'foreground': '#f8f8f2',
                'accent': '#a6e22e',
                'success': '#66d9ef',
                'warning': '#fd971f',
                'error': '#f92672'
            },
            'solarized': {
                'background': '#002b36',
                'foreground': '#93a1a1',
                'accent': '#268bd2',
                'success': '#859900',
                'warning': '#b58900',
                'error': '#dc322f'
            }
        }
        
        if theme in themes:
            self.settings['theme'] = theme
            self.style = Style.from_dict({
                'prompt': f"{themes[theme]['accent']} bold",
                'background': themes[theme]['background'],
                'foreground': themes[theme]['foreground']
            })
            console.print(f"[green]Тема {theme} успешно применена[/green]")
            self.save_settings()
        else:
            console.print(f"[red]Тема {theme} не найдена[/red]")

    def show_tips(self):
        """Показать полезные советы"""
        tips = [
            "Используйте Tab для автодополнения команд",
            "Нажмите Ctrl+C для отмены текущей операции",
            "Используйте 'help' для получения справки по командам",
            "История команд сохраняется между сессиями",
            "Для выбора веток и коммитов используйте интерактивный режим",
            "Используйте 'theme' для изменения цветовой схемы",
            "Настройки сохраняются в ~/.gitwizard_settings.json",
            "Используйте 'settings' для управления настройками",
            "Для анализа кода используйте команды 'security' и 'performance'",
            "Генерируйте документацию с помощью команды 'docs'"
        ]
        
        if self.settings['show_tips']:
            tip = random.choice(tips)
            console.print(Panel(f"[bold cyan]Совет:[/bold cyan] {tip}", border_style="cyan"))

    def integrate_with_ide(self, ide: str):
        """Интеграция с IDE"""
        try:
            if ide == 'vscode':
                # Создаем конфигурацию для VS Code
                vscode_dir = os.path.join(self.repo_path, '.vscode')
                os.makedirs(vscode_dir, exist_ok=True)
                
                settings = {
                    "git.enableSmartCommit": True,
                    "git.confirmSync": False,
                    "git.autofetch": True,
                    "gitwizard.enabled": True,
                    "gitwizard.commands": {
                        "analyze": "gitwizard security",
                        "document": "gitwizard docs",
                        "performance": "gitwizard performance"
                    }
                }
                
                with open(os.path.join(vscode_dir, 'settings.json'), 'w') as f:
                    json.dump(settings, f, indent=2)
                
                console.print("[green]Интеграция с VS Code настроена[/green]")
                
            elif ide == 'pycharm':
                # Создаем конфигурацию для PyCharm
                idea_dir = os.path.join(self.repo_path, '.idea')
                os.makedirs(idea_dir, exist_ok=True)
                
                # Создаем файл конфигурации для внешних инструментов
                tools_xml = """<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ExternalToolsSettings">
    <option name="tools">
      <list>
        <ExternalTool>
          <option name="name" value="GitWizard Security" />
          <option name="program" value="gitwizard" />
          <option name="parameters" value="security" />
        </ExternalTool>
        <ExternalTool>
          <option name="name" value="GitWizard Docs" />
          <option name="program" value="gitwizard" />
          <option name="parameters" value="docs" />
        </ExternalTool>
      </list>
    </option>
  </component>
</project>"""
                
                with open(os.path.join(idea_dir, 'external_tools.xml'), 'w') as f:
                    f.write(tools_xml)
                
                console.print("[green]Интеграция с PyCharm настроена[/green]")
                
            elif ide == 'sublime':
                # Создаем конфигурацию для Sublime Text
                sublime_dir = os.path.join(self.repo_path, '.sublime')
                os.makedirs(sublime_dir, exist_ok=True)
                
                keymap = """[
    {
        "keys": ["ctrl+shift+g", "ctrl+s"],
        "command": "gitwizard_security"
    },
    {
        "keys": ["ctrl+shift+g", "ctrl+d"],
        "command": "gitwizard_docs"
    }
]"""
                
                with open(os.path.join(sublime_dir, 'Default.sublime-keymap'), 'w') as f:
                    f.write(keymap)
                
                console.print("[green]Интеграция с Sublime Text настроена[/green]")
            
            else:
                raise ValueError(f"Неподдерживаемая IDE: {ide}")
            
            # Обновляем настройки
            self.settings['ide_integration'][ide] = True
            self.save_settings()
            
        except Exception as e:
            console.print(f"[red]Ошибка при интеграции с IDE: {str(e)}[/red]")

    def show_status(self):
        """Показать текущий статус репозитория"""
        try:
            # Получаем информацию о текущей ветке
            current_branch = self.repo.active_branch
            console.print(Panel(f"[bold green]Текущая ветка: {current_branch.name}[/bold green]"))
            
            # Проверяем статус рабочей директории
            if self.repo.is_dirty():
                console.print("[yellow]Есть несохраненные изменения:[/yellow]")
                
                # Показываем измененные файлы
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Статус", style="cyan")
                table.add_column("Файл", style="green")
                
                for item in self.repo.index.diff(None):
                    table.add_row("Изменен", item.a_path)
                
                for item in self.repo.untracked_files:
                    table.add_row("Новый", item)
                
                console.print(table)
            else:
                console.print("[green]Рабочая директория чиста[/green]")
            
            # Показываем последний коммит
            last_commit = self.repo.head.commit
            console.print(Panel(
                f"[bold]Последний коммит:[/bold]\n"
                f"Хеш: [cyan]{last_commit.hexsha[:8]}[/cyan]\n"
                f"Автор: [green]{last_commit.author.name}[/green]\n"
                f"Дата: [yellow]{datetime.fromtimestamp(last_commit.committed_date).strftime('%Y-%m-%d %H:%M')}[/yellow]\n"
                f"Сообщение: [white]{last_commit.message.split('\n')[0]}[/white]"
            ))
            
        except Exception as e:
            console.print(f"[red]Ошибка при получении статуса: {str(e)}[/red]")

    def interactive_branch_select(self) -> Optional[str]:
        """Интерактивный выбор ветки"""
        try:
            branches = list(self.repo.heads)
            if not branches:
                console.print("[yellow]Нет доступных веток[/yellow]")
                return None
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("№", style="cyan")
            table.add_column("Ветка", style="green")
            table.add_column("Последний коммит", style="yellow")
            
            for i, branch in enumerate(branches, 1):
                last_commit = branch.commit
                table.add_row(
                    str(i),
                    branch.name,
                    f"{last_commit.message.split('\n')[0]} ({last_commit.hexsha[:8]})"
                )
            
            console.print(table)
            
            while True:
                choice = Prompt.ask(
                    "Выберите номер ветки (или 'q' для отмены)",
                    default="q"
                )
                
                if choice.lower() == 'q':
                    return None
                
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(branches):
                        return branches[index].name
                    else:
                        console.print("[red]Неверный номер ветки[/red]")
                except ValueError:
                    console.print("[red]Введите число или 'q'[/red]")
            
        except Exception as e:
            console.print(f"[red]Ошибка при выборе ветки: {str(e)}[/red]")
            return None

    def interactive_commit_select(self) -> Optional[str]:
        """Интерактивный выбор коммита"""
        try:
            commits = list(self.repo.iter_commits())
            if not commits:
                console.print("[yellow]Нет доступных коммитов[/yellow]")
                return None
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("№", style="cyan")
            table.add_column("Хеш", style="green", width=8)
            table.add_column("Автор", style="yellow")
            table.add_column("Дата", style="magenta")
            table.add_column("Сообщение", style="white")
            
            for i, commit in enumerate(commits[:10], 1):  # Показываем последние 10 коммитов
                table.add_row(
                    str(i),
                    commit.hexsha[:8],
                    commit.author.name,
                    datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M'),
                    commit.message.split('\n')[0]
                )
            
            console.print(table)
            
            while True:
                choice = Prompt.ask(
                    "Выберите номер коммита (или 'q' для отмены)",
                    default="q"
                )
                
                if choice.lower() == 'q':
                    return None
                
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(commits):
                        return commits[index].hexsha
                    else:
                        console.print("[red]Неверный номер коммита[/red]")
                except ValueError:
                    console.print("[red]Введите число или 'q'[/red]")
            
        except Exception as e:
            console.print(f"[red]Ошибка при выборе коммита: {str(e)}[/red]")
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

    def analyze_changes(self, commit_hash: Optional[str] = None, file_path: Optional[str] = None):
        """Анализ изменений в файлах"""
        try:
            if commit_hash:
                try:
                    commit = self.repo.commit(commit_hash)
                except Exception:
                    # Если не удалось найти коммит, возможно это имя файла
                    file_path = commit_hash
                    commit = self.repo.head.commit
            else:
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
                if not file_path or file == file_path:
                    table.add_row(
                        file,
                        str(changes['insertions']),
                        str(changes['deletions'])
                    )

            console.print(table)

        except Exception as e:
            console.print(f"[red]Ошибка при анализе изменений: {str(e)}[/red]")

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
                        # Получаем статистику из коммита
                        stats = commit.stats.files.get(diff_item.a_path, {})
                        insertions = stats.get('insertions', 0)
                        deletions = stats.get('deletions', 0)
                        
                        console.print(f"Добавлено строк: [green]{insertions}[/green]")
                        console.print(f"Удалено строк: [red]{deletions}[/red]")
                    except Exception as e:
                        console.print(f"[yellow]Не удалось подсчитать статистику изменений: {str(e)}[/yellow]")
                    
                    # Показываем изменения в двух колонках
                    try:
                        # Получаем diff в виде строк
                        diff_text = self.repo.git.show(
                            f"{commit.hexsha}:{diff_item.a_path}",
                            '--unified=0'  # Убираем контекстные строки
                        )
                        
                        if not diff_text:
                            continue

                        # Создаем таблицу для отображения изменений
                        table = Table(show_header=False, box=None, padding=(0, 1))
                        table.add_column("Старая версия", style="red", width=50)
                        table.add_column("Новая версия", style="green", width=50)
                        
                        # Получаем содержимое файла до изменений
                        try:
                            old_text = self.repo.git.show(
                                f"{commit.parents[0].hexsha}:{diff_item.a_path}" if commit.parents else "",
                                '--unified=0'
                            )
                        except:
                            old_text = ""

                        # Разбиваем на строки
                        old_lines = old_text.split('\n') if old_text else []
                        new_lines = diff_text.split('\n') if diff_text else []

                        # Находим различия
                        from difflib import SequenceMatcher
                        matcher = SequenceMatcher(None, old_lines, new_lines)
                        
                        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                            if tag == 'equal':
                                # Неизмененные строки
                                for i in range(i1, i2):
                                    table.add_row(old_lines[i], new_lines[j1 + (i - i1)])
                            elif tag == 'delete':
                                # Удаленные строки
                                for i in range(i1, i2):
                                    table.add_row(old_lines[i], "")
                            elif tag == 'insert':
                                # Добавленные строки
                                for j in range(j1, j2):
                                    table.add_row("", new_lines[j])
                            elif tag == 'replace':
                                # Замененные строки
                                for i, j in zip(range(i1, i2), range(j1, j2)):
                                    table.add_row(old_lines[i], new_lines[j])
                        
                        console.print(table)
                        
                    except Exception as e:
                        console.print(f"[red]Ошибка при отображении изменений: {str(e)}[/red]")
                        # Показываем обычный diff как запасной вариант
                        try:
                            diff_text = self.repo.git.diff(
                                commit.parents[0].hexsha if commit.parents else '--root',
                                commit.hexsha,
                                '--',
                                diff_item.a_path
                            )
                            syntax = Syntax(diff_text, "diff", theme="monokai")
                            console.print(syntax)
                        except:
                            pass
                    
                    console.print()  # Пустая строка для разделения

        except Exception as e:
            console.print(f"[red]Ошибка при показе изменений: {str(e)}[/red]")

    def visualize_commit_graph(self):
        """Визуализация графа коммитов с ветками"""
        try:
            # Получаем все ветки
            branches = self.repo.heads
            # Получаем все коммиты
            commits = list(self.repo.iter_commits(all=True))
            
            # Создаем граф
            graph = Table(show_header=False, box=None, padding=(0, 1))
            graph.add_column("Граф", style="cyan")
            graph.add_column("Хеш", style="green", width=8)
            graph.add_column("Автор", style="yellow")
            graph.add_column("Дата", style="magenta")
            graph.add_column("Сообщение", style="white")

            # Словарь для отслеживания веток
            branch_commits = {branch.name: branch.commit.hexsha for branch in branches}
            
            for commit in commits:
                # Определяем, является ли коммит частью какой-либо ветки
                branch_names = [name for name, hexsha in branch_commits.items() if hexsha == commit.hexsha]
                branch_marker = f"[bold green]{' '.join(branch_names)}[/bold green] " if branch_names else ""
                
                # Создаем визуальное представление графа
                graph_line = ""
                if commit.parents:
                    graph_line += "│ " * (len(commit.parents) - 1)
                    graph_line += "└─" if len(commit.parents) > 1 else "│"
                else:
                    graph_line += "●"
                
                graph.add_row(
                    graph_line,
                    commit.hexsha[:8],
                    commit.author.name,
                    datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M'),
                    f"{branch_marker}{commit.message.split('\n')[0]}"
                )

            console.print(Panel("[bold green]Граф коммитов[/bold green]"))
            console.print(graph)

        except Exception as e:
            console.print(f"[red]Ошибка при визуализации графа: {str(e)}[/red]")

    def analyze_file_work_time(self, file_path: Optional[str] = None):
        """Анализ времени работы над файлами"""
        try:
            if file_path:
                # Анализ конкретного файла
                commits = list(self.repo.iter_commits(paths=[file_path]))
            else:
                # Анализ всех файлов
                commits = list(self.repo.iter_commits())

            # Словарь для хранения времени работы
            file_times = defaultdict(lambda: {"first_commit": None, "last_commit": None, "total_time": 0})
            
            for commit in commits:
                for diff in commit.diff(commit.parents[0] if commit.parents else None):
                    if diff.a_path:
                        file_times[diff.a_path]["last_commit"] = commit.committed_date
                        if file_times[diff.a_path]["first_commit"] is None:
                            file_times[diff.a_path]["first_commit"] = commit.committed_date

            # Создаем таблицу
            table = Table(title="Время работы над файлами")
            table.add_column("Файл", style="cyan")
            table.add_column("Первый коммит", style="green")
            table.add_column("Последний коммит", style="yellow")
            table.add_column("Всего дней", style="magenta")

            for file, times in file_times.items():
                if times["first_commit"] and times["last_commit"]:
                    first_date = datetime.fromtimestamp(times["first_commit"])
                    last_date = datetime.fromtimestamp(times["last_commit"])
                    days = (last_date - first_date).days
                    
                    table.add_row(
                        file,
                        first_date.strftime('%Y-%m-%d'),
                        last_date.strftime('%Y-%m-%d'),
                        str(days)
                    )

            console.print(table)

        except Exception as e:
            console.print(f"[red]Ошибка при анализе времени работы: {str(e)}[/red]")

    def find_lost_commits(self):
        """Поиск 'потерянных' коммитов (не связанных с текущими ветками)"""
        try:
            # Получаем все коммиты
            all_commits = set(self.repo.iter_commits(all=True))
            # Получаем коммиты из текущих веток
            branch_commits = set()
            for branch in self.repo.heads:
                branch_commits.update(self.repo.iter_commits(branch))
            
            # Находим потерянные коммиты
            lost_commits = all_commits - branch_commits
            
            if not lost_commits:
                console.print("[green]Потерянных коммитов не найдено[/green]")
                return

            table = Table(title="Потерянные коммиты")
            table.add_column("Хеш", style="cyan", width=8)
            table.add_column("Автор", style="green")
            table.add_column("Дата", style="yellow")
            table.add_column("Сообщение", style="white")

            for commit in lost_commits:
                table.add_row(
                    commit.hexsha[:8],
                    commit.author.name,
                    datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M'),
                    commit.message.split('\n')[0]
                )

            console.print(table)

        except Exception as e:
            console.print(f"[red]Ошибка при поиске потерянных коммитов: {str(e)}[/red]")

    def analyze_branch_conflicts(self, branch_name: Optional[str] = None):
        """Анализ потенциальных конфликтов в ветках"""
        try:
            if branch_name:
                branches = [self.repo.heads[branch_name]]
            else:
                branches = self.repo.heads

            table = Table(title="Анализ конфликтов в ветках")
            table.add_column("Ветка", style="cyan")
            table.add_column("Общие файлы", style="green")
            table.add_column("Потенциальные конфликты", style="red")

            current_branch = self.repo.active_branch
            
            for branch in branches:
                if branch.name == current_branch.name:
                    continue

                # Получаем изменения в обеих ветках
                current_diff = set(diff.a_path for diff in current_branch.commit.diff())
                branch_diff = set(diff.a_path for diff in branch.commit.diff())
                
                # Находим общие файлы
                common_files = current_diff & branch_diff
                
                # Проверяем каждый общий файл на конфликты
                conflicts = []
                for file in common_files:
                    try:
                        # Пытаемся выполнить merge в памяти
                        merge_base = self.repo.merge_base(current_branch, branch)
                        if merge_base:
                            current_content = self.repo.git.show(f"{current_branch.name}:{file}")
                            branch_content = self.repo.git.show(f"{branch.name}:{file}")
                            
                            if current_content != branch_content:
                                conflicts.append(file)
                    except:
                        conflicts.append(file)

                table.add_row(
                    branch.name,
                    str(len(common_files)),
                    str(len(conflicts))
                )

            console.print(table)

        except Exception as e:
            console.print(f"[red]Ошибка при анализе конфликтов: {str(e)}[/red]")

    def analyze_code_complexity(self, file_path: Optional[str] = None):
        """Анализ сложности кода"""
        try:
            if file_path:
                files = [file_path]
            else:
                files = [f for f in self.repo.git.ls_files().split('\n') if f.endswith(('.py', '.js', '.java', '.cpp', '.c', '.h'))]

            table = Table(title="Анализ сложности кода")
            table.add_column("Файл", style="cyan")
            table.add_column("Строк кода", style="green")
            table.add_column("Функций", style="yellow")
            table.add_column("Сложность", style="magenta")

            for file in files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        # Подсчет строк кода (исключая пустые строки и комментарии)
                        code_lines = len([l for l in lines if l.strip() and not l.strip().startswith(('#', '//', '/*', '*', '*/'))])
                        
                        # Подсчет функций
                        functions = 0
                        complexity = 0
                        
                        for line in lines:
                            # Подсчет функций
                            if any(line.strip().startswith(keyword) for keyword in ['def ', 'function ', 'public ', 'private ', 'protected ']):
                                functions += 1
                            
                            # Подсчет сложности (по ключевым словам)
                            if any(keyword in line for keyword in ['if ', 'for ', 'while ', 'switch ', 'case ', 'catch ', '&&', '||']):
                                complexity += 1
                        
                        table.add_row(
                            file,
                            str(code_lines),
                            str(functions),
                            str(complexity)
                        )
                except Exception as e:
                    console.print(f"[red]Ошибка при анализе файла {file}: {str(e)}[/red]")

            console.print(table)

        except Exception as e:
            console.print(f"[red]Ошибка при анализе сложности кода: {str(e)}[/red]")

    def find_code_duplicates(self, min_length: int = 5):
        """Поиск дубликатов кода"""
        try:
            files = [f for f in self.repo.git.ls_files().split('\n') if f.endswith(('.py', '.js', '.java', '.cpp', '.c', '.h'))]
            
            # Словарь для хранения фрагментов кода
            code_fragments = defaultdict(list)
            
            for file in files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        # Ищем повторяющиеся последовательности строк
                        for i in range(len(lines) - min_length + 1):
                            fragment = '\n'.join(lines[i:i + min_length])
                            if fragment.strip():
                                code_fragments[fragment].append((file, i + 1))
                except Exception as e:
                    console.print(f"[red]Ошибка при чтении файла {file}: {str(e)}[/red]")

            # Выводим найденные дубликаты
            found_duplicates = False
            for fragment, occurrences in code_fragments.items():
                if len(occurrences) > 1:
                    found_duplicates = True
                    console.print(Panel(f"[bold yellow]Найден дубликат кода:[/bold yellow]"))
                    console.print(Syntax(fragment, "python", theme="monokai"))
                    console.print("[bold]Встречается в:[/bold]")
                    for file, line in occurrences:
                        console.print(f"[cyan]{file}:{line}[/cyan]")
                    console.print()

            if not found_duplicates:
                console.print("[green]Дубликатов кода не найдено[/green]")

        except Exception as e:
            console.print(f"[red]Ошибка при поиске дубликатов: {str(e)}[/red]")

    def analyze_dependencies(self):
        """Анализ зависимостей проекта"""
        try:
            # Анализ Python зависимостей
            if os.path.exists('requirements.txt'):
                console.print(Panel("[bold green]Python зависимости:[/bold green]"))
                with open('requirements.txt', 'r') as f:
                    requirements = f.read()
                    console.print(Syntax(requirements, "text", theme="monokai"))

            # Анализ Node.js зависимостей
            if os.path.exists('package.json'):
                console.print(Panel("[bold green]Node.js зависимости:[/bold green]"))
                with open('package.json', 'r') as f:
                    package_json = f.read()
                    console.print(Syntax(package_json, "json", theme="monokai"))

            # Анализ импортов в Python файлах
            python_files = [f for f in self.repo.git.ls_files().split('\n') if f.endswith('.py')]
            imports = defaultdict(set)
            
            for file in python_files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        for line in lines:
                            if line.startswith(('import ', 'from ')):
                                imports[file].add(line.strip())
                except Exception as e:
                    console.print(f"[red]Ошибка при чтении файла {file}: {str(e)}[/red]")

            if imports:
                console.print(Panel("[bold green]Импорты в Python файлах:[/bold green]"))
                for file, file_imports in imports.items():
                    console.print(f"[cyan]{file}:[/cyan]")
                    for imp in sorted(file_imports):
                        console.print(f"  {imp}")

        except Exception as e:
            console.print(f"[red]Ошибка при анализе зависимостей: {str(e)}[/red]")

    def export_stats(self, format: str = 'json'):
        """Экспорт статистики в различных форматах"""
        try:
            stats = {
                'repository': {
                    'name': os.path.basename(self.repo_path),
                    'branches': [b.name for b in self.repo.heads],
                    'active_branch': self.repo.active_branch.name,
                    'last_commit': {
                        'hash': self.repo.head.commit.hexsha,
                        'author': self.repo.head.commit.author.name,
                        'date': datetime.fromtimestamp(self.repo.head.commit.committed_date).isoformat(),
                        'message': self.repo.head.commit.message
                    }
                },
                'files': {
                    'total': len(self.repo.git.ls_files().split('\n')),
                    'by_extension': defaultdict(int)
                },
                'commits': {
                    'total': len(list(self.repo.iter_commits())),
                    'by_author': defaultdict(int)
                }
            }

            # Собираем статистику по файлам
            for file in self.repo.git.ls_files().split('\n'):
                ext = os.path.splitext(file)[1]
                stats['files']['by_extension'][ext] += 1

            # Собираем статистику по коммитам
            for commit in self.repo.iter_commits():
                stats['commits']['by_author'][commit.author.name] += 1

            # Экспортируем в выбранном формате
            if format == 'json':
                output = json.dumps(stats, indent=2)
                filename = 'gitwizard_stats.json'
            elif format == 'yaml':
                import yaml
                output = yaml.dump(stats)
                filename = 'gitwizard_stats.yaml'
            else:
                raise ValueError(f"Неподдерживаемый формат: {format}")

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(output)

            console.print(f"[green]Статистика экспортирована в файл {filename}[/green]")

        except Exception as e:
            console.print(f"[red]Ошибка при экспорте статистики: {str(e)}[/red]")

    def analyze_security(self, file_path: Optional[str] = None):
        """Анализ безопасности кода"""
        try:
            if file_path:
                files = [file_path]
            else:
                files = [f for f in self.repo.git.ls_files().split('\n') if f.endswith(('.py', '.js', '.java', '.cpp', '.c', '.h'))]

            # Паттерны для поиска потенциальных уязвимостей
            security_patterns = {
                'SQL Injection': [
                    r'SELECT.*FROM.*WHERE.*=.*[\'"]\s*\+\s*[\'"]',
                    r'INSERT.*INTO.*VALUES.*[\'"]\s*\+\s*[\'"]',
                    r'UPDATE.*SET.*=.*[\'"]\s*\+\s*[\'"]',
                    r'DELETE.*FROM.*WHERE.*=.*[\'"]\s*\+\s*[\'"]'
                ],
                'Command Injection': [
                    r'os\.system\(',
                    r'subprocess\.call\(',
                    r'exec\(',
                    r'eval\('
                ],
                'Path Traversal': [
                    r'\.\./',
                    r'\.\.\\',
                    r'%2e%2e%2f',
                    r'%252e%252e%252f'
                ],
                'Hardcoded Credentials': [
                    r'password\s*=\s*[\'"][^\'"]+[\'"]',
                    r'api_key\s*=\s*[\'"][^\'"]+[\'"]',
                    r'secret\s*=\s*[\'"][^\'"]+[\'"]'
                ]
            }

            import re
            from collections import defaultdict

            issues = defaultdict(list)
            
            for file in files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        for i, line in enumerate(lines, 1):
                            for issue_type, patterns in security_patterns.items():
                                for pattern in patterns:
                                    if re.search(pattern, line):
                                        issues[issue_type].append((file, i, line.strip()))
                except Exception as e:
                    console.print(f"[red]Ошибка при анализе файла {file}: {str(e)}[/red]")

            if issues:
                console.print(Panel("[bold red]Найдены потенциальные проблемы безопасности:[/bold red]"))
                
                for issue_type, occurrences in issues.items():
                    console.print(f"\n[bold yellow]{issue_type}:[/bold yellow]")
                    table = Table(show_header=True, header_style="bold magenta")
                    table.add_column("Файл", style="cyan")
                    table.add_column("Строка", style="green")
                    table.add_column("Код", style="white")
                    
                    for file, line_num, code in occurrences:
                        table.add_row(file, str(line_num), code)
                    
                    console.print(table)
            else:
                console.print("[green]Потенциальных проблем безопасности не найдено[/green]")

        except Exception as e:
            console.print(f"[red]Ошибка при анализе безопасности: {str(e)}[/red]")

    def generate_documentation(self, format: str = 'md'):
        """Генерация документации проекта"""
        try:
            # Собираем информацию о проекте
            project_info = {
                'name': os.path.basename(self.repo_path),
                'description': self.get_project_description(),
                'authors': self.get_project_authors(),
                'files': self.get_project_files(),
                'dependencies': self.get_project_dependencies()
            }

            if format == 'md':
                self.generate_markdown_docs(project_info)
            elif format == 'html':
                self.generate_html_docs(project_info)
            else:
                raise ValueError(f"Неподдерживаемый формат: {format}")

        except Exception as e:
            console.print(f"[red]Ошибка при генерации документации: {str(e)}[/red]")

    def get_project_description(self) -> str:
        """Получение описания проекта"""
        try:
            # Пробуем найти README.md
            if os.path.exists('README.md'):
                with open('README.md', 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Ищем первое описание
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip() and not line.startswith('#'):
                            return line.strip()
            return "Описание проекта отсутствует"
        except:
            return "Не удалось получить описание проекта"

    def get_project_authors(self) -> List[str]:
        """Получение списка авторов проекта"""
        authors = set()
        for commit in self.repo.iter_commits():
            authors.add(commit.author.name)
        return sorted(list(authors))

    def get_project_files(self) -> Dict[str, List[str]]:
        """Получение структуры файлов проекта"""
        files = defaultdict(list)
        for file in self.repo.git.ls_files().split('\n'):
            ext = os.path.splitext(file)[1]
            files[ext].append(file)
        return dict(files)

    def get_project_dependencies(self) -> Dict[str, List[str]]:
        """Получение зависимостей проекта"""
        deps = {}
        
        # Python зависимости
        if os.path.exists('requirements.txt'):
            with open('requirements.txt', 'r') as f:
                deps['python'] = [line.strip() for line in f if line.strip()]
        
        # Node.js зависимости
        if os.path.exists('package.json'):
            import json
            with open('package.json', 'r') as f:
                package = json.load(f)
                deps['nodejs'] = []
                if 'dependencies' in package:
                    deps['nodejs'].extend(package['dependencies'].keys())
                if 'devDependencies' in package:
                    deps['nodejs'].extend(package['devDependencies'].keys())
        
        return deps

    def generate_markdown_docs(self, project_info: Dict):
        """Генерация документации в формате Markdown"""
        try:
            with open('DOCUMENTATION.md', 'w', encoding='utf-8') as f:
                f.write(f"# {project_info['name']}\n\n")
                f.write(f"{project_info['description']}\n\n")
                
                # Авторы
                f.write("## Авторы\n\n")
                for author in project_info['authors']:
                    f.write(f"- {author}\n")
                f.write("\n")
                
                # Структура проекта
                f.write("## Структура проекта\n\n")
                for ext, files in project_info['files'].items():
                    f.write(f"### {ext or 'Без расширения'}\n\n")
                    for file in files:
                        f.write(f"- {file}\n")
                    f.write("\n")
                
                # Зависимости
                f.write("## Зависимости\n\n")
                for lang, deps in project_info['dependencies'].items():
                    f.write(f"### {lang.upper()}\n\n")
                    for dep in deps:
                        f.write(f"- {dep}\n")
                    f.write("\n")
            
            console.print("[green]Документация сгенерирована в файле DOCUMENTATION.md[/green]")
            
        except Exception as e:
            console.print(f"[red]Ошибка при генерации Markdown документации: {str(e)}[/red]")

    def generate_html_docs(self, project_info: Dict):
        """Генерация документации в формате HTML"""
        try:
            html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{project_info['name']} - Документация</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1, h2, h3 {{ color: #333; }}
        .section {{ margin: 20px 0; }}
        .file-list, .author-list, .dep-list {{ list-style-type: none; padding: 0; }}
        .file-list li, .author-list li, .dep-list li {{ margin: 5px 0; }}
    </style>
</head>
<body>
    <h1>{project_info['name']}</h1>
    <p>{project_info['description']}</p>
    
    <div class="section">
        <h2>Авторы</h2>
        <ul class="author-list">
"""
            
            for author in project_info['authors']:
                html += f"            <li>{author}</li>\n"
            
            html += """        </ul>
    </div>
    
    <div class="section">
        <h2>Структура проекта</h2>
"""
            
            for ext, files in project_info['files'].items():
                html += f"""        <h3>{ext or 'Без расширения'}</h3>
        <ul class="file-list">
"""
                for file in files:
                    html += f"            <li>{file}</li>\n"
                html += "        </ul>\n"
            
            html += """    </div>
    
    <div class="section">
        <h2>Зависимости</h2>
"""
            
            for lang, deps in project_info['dependencies'].items():
                html += f"""        <h3>{lang.upper()}</h3>
        <ul class="dep-list">
"""
                for dep in deps:
                    html += f"            <li>{dep}</li>\n"
                html += "        </ul>\n"
            
            html += """    </div>
</body>
</html>"""
            
            with open('documentation.html', 'w', encoding='utf-8') as f:
                f.write(html)
            
            console.print("[green]Документация сгенерирована в файле documentation.html[/green]")
            
        except Exception as e:
            console.print(f"[red]Ошибка при генерации HTML документации: {str(e)}[/red]")

    def analyze_performance(self, file_path: Optional[str] = None):
        """Анализ производительности кода"""
        try:
            if file_path:
                files = [file_path]
            else:
                files = [f for f in self.repo.git.ls_files().split('\n') if f.endswith('.py')]

            table = Table(title="Анализ производительности")
            table.add_column("Файл", style="cyan")
            table.add_column("Циклы", style="yellow")
            table.add_column("Рекурсия", style="magenta")
            table.add_column("Вложенность", style="green")

            for file in files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        # Подсчет циклов
                        loops = 0
                        for line in lines:
                            if any(line.strip().startswith(keyword) for keyword in ['for ', 'while ']):
                                loops += 1
                        
                        # Подсчет рекурсивных вызовов
                        recursion = 0
                        for line in lines:
                            if 'def ' in line:
                                func_name = line.split('def ')[1].split('(')[0].strip()
                                if func_name in content:
                                    recursion += 1
                        
                        # Подсчет максимальной вложенности
                        max_nesting = 0
                        current_nesting = 0
                        for line in lines:
                            if line.strip().startswith(('if ', 'for ', 'while ', 'def ', 'class ')):
                                current_nesting += 1
                                max_nesting = max(max_nesting, current_nesting)
                            elif line.strip() and not line.strip().startswith(('else:', 'elif ')):
                                current_nesting = 0
                        
                        table.add_row(
                            file,
                            str(loops),
                            str(recursion),
                            str(max_nesting)
                        )
                except Exception as e:
                    console.print(f"[red]Ошибка при анализе файла {file}: {str(e)}[/red]")

            console.print(table)

        except Exception as e:
            console.print(f"[red]Ошибка при анализе производительности: {str(e)}[/red]")

    def setup_ci_cd(self, platform: str = 'github'):
        """Настройка CI/CD для проекта"""
        try:
            if platform == 'github':
                # Создаем директорию .github/workflows если её нет
                os.makedirs('.github/workflows', exist_ok=True)
                
                # Создаем базовый workflow файл
                workflow = """name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    - name: Run tests
      run: |
        python -m unittest discover tests
    - name: Run linting
      run: |
        pip install flake8
        flake8 .
"""
                
                with open('.github/workflows/main.yml', 'w') as f:
                    f.write(workflow)
                
                console.print("[green]GitHub Actions workflow создан в .github/workflows/main.yml[/green]")
                
            elif platform == 'gitlab':
                # Создаем .gitlab-ci.yml
                gitlab_ci = """image: python:3.x

stages:
  - test
  - lint
  - deploy

test:
  stage: test
  script:
    - pip install -r requirements.txt
    - python -m unittest discover tests

lint:
  stage: lint
  script:
    - pip install flake8
    - flake8 .

deploy:
  stage: deploy
  script:
    - echo "Deploy to production"
  only:
    - main
"""
                
                with open('.gitlab-ci.yml', 'w') as f:
                    f.write(gitlab_ci)
                
                console.print("[green]GitLab CI/CD конфигурация создана в .gitlab-ci.yml[/green]")
            
            else:
                raise ValueError(f"Неподдерживаемая платформа: {platform}")

        except Exception as e:
            console.print(f"[red]Ошибка при настройке CI/CD: {str(e)}[/red]")

    def run(self):
        """Запуск интерактивного режима"""
        if self.settings['show_welcome']:
            console.print(Panel.fit(
                "[bold green]Добро пожаловать в GitWizard![/bold green]\n"
                "[cyan]Улучшенный интерфейс для работы с Git[/cyan]",
                border_style="green"
            ))
        
        # Показываем статус при запуске
        self.show_status()
        
        if self.settings['show_tips']:
            self.show_tips()
        
        console.print("\n[bold cyan]Доступные команды:[/bold cyan]")
        console.print("Введите 'help' для подробной справки или 'exit' для выхода")

        while True:
            try:
                command = self.session.prompt(
                    "gitwizard> ",
                    completer=self.completer if self.settings['auto_complete'] else None,
                    style=self.style
                ).strip()

                if command == "exit":
                    if Confirm.ask("Вы уверены, что хотите выйти?"):
                        break
                elif command == "help":
                    self.show_help()
                elif command == "status":
                    self.show_status()
                elif command == "graph":
                    self.visualize_branches()
                elif command == "history":
                    self.visualize_history()
                elif command == "commit-graph":
                    self.visualize_commit_graph()
                elif command.startswith("worktime"):
                    parts = command.split()
                    if len(parts) == 1:
                        self.analyze_file_work_time()
                    elif len(parts) == 2:
                        self.analyze_file_work_time(parts[1])
                elif command == "lost-commits":
                    self.find_lost_commits()
                elif command.startswith("conflicts"):
                    parts = command.split()
                    if len(parts) == 1:
                        branch = self.interactive_branch_select()
                        if branch:
                            self.analyze_branch_conflicts(branch)
                    elif len(parts) == 2:
                        self.analyze_branch_conflicts(parts[1])
                elif command.startswith("changes"):
                    parts = command.split()
                    if len(parts) == 1:
                        commit = self.interactive_commit_select()
                        if commit:
                            self.analyze_changes(commit_hash=commit)
                    elif len(parts) == 2:
                        self.analyze_changes(commit_hash=parts[1])
                    elif len(parts) == 3:
                        self.analyze_changes(commit_hash=parts[1], file_path=parts[2])
                elif command.startswith("diff"):
                    parts = command.split()
                    if len(parts) == 1:
                        commit = self.interactive_commit_select()
                        if commit:
                            self.show_diff(commit_hash=commit)
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
                elif command.startswith("complexity"):
                    parts = command.split()
                    if len(parts) == 1:
                        self.analyze_code_complexity()
                    elif len(parts) == 2:
                        self.analyze_code_complexity(parts[1])
                elif command.startswith("duplicates"):
                    parts = command.split()
                    min_length = int(parts[1]) if len(parts) > 1 else 5
                    self.find_code_duplicates(min_length)
                elif command == "dependencies":
                    self.analyze_dependencies()
                elif command.startswith("export"):
                    parts = command.split()
                    format = parts[1] if len(parts) > 1 else 'json'
                    self.export_stats(format)
                elif command.startswith("security"):
                    parts = command.split()
                    if len(parts) == 1:
                        self.analyze_security()
                    elif len(parts) == 2:
                        self.analyze_security(parts[1])
                elif command.startswith("docs"):
                    parts = command.split()
                    format = parts[1] if len(parts) > 1 else 'md'
                    self.generate_documentation(format)
                elif command.startswith("performance"):
                    parts = command.split()
                    if len(parts) == 1:
                        self.analyze_performance()
                    elif len(parts) == 2:
                        self.analyze_performance(parts[1])
                elif command.startswith("ci-cd"):
                    parts = command.split()
                    platform = parts[1] if len(parts) > 1 else 'github'
                    self.setup_ci_cd(platform)
                elif command.startswith("theme"):
                    parts = command.split()
                    if len(parts) == 2:
                        self.set_theme(parts[1])
                    else:
                        console.print("[yellow]Использование: theme <название_темы>[/yellow]")
                        console.print("Доступные темы: light, dark, monokai, solarized")
                elif command.startswith("settings"):
                    parts = command.split()
                    if len(parts) == 1:
                        self.show_settings()
                    elif len(parts) == 2:
                        if parts[1] == "save":
                            self.save_settings()
                        elif parts[1] == "reset":
                            self.settings = self.load_settings()
                            console.print("[green]Настройки сброшены к значениям по умолчанию[/green]")
                        else:
                            console.print("[yellow]Использование: settings [show|save|reset][/yellow]")
                elif command.startswith("ide"):
                    parts = command.split()
                    if len(parts) == 2:
                        self.integrate_with_ide(parts[1])
                    else:
                        console.print("[yellow]Использование: ide <название_ide>[/yellow]")
                        console.print("Поддерживаемые IDE: vscode, pycharm, sublime")
                else:
                    console.print(f"[yellow]Неизвестная команда: {command}[/yellow]")
                    console.print("Введите 'help' для списка доступных команд")

            except KeyboardInterrupt:
                continue
            except EOFError:
                break

    def show_help(self):
        """Показать справку по командам"""
        help_text = """
[bold cyan]Доступные команды:[/bold cyan]
  status       - Показать текущий статус репозитория
  graph        - Визуализация веток
  history      - История коммитов
  commit-graph - Визуализация графа коммитов с ветками
  worktime     - Анализ времени работы над файлами
  lost-commits - Поиск потерянных коммитов
  conflicts    - Анализ конфликтов в ветках
  changes      - Анализ изменений (опционально: хеш коммита и путь к файлу)
  diff         - Показать изменения (опционально: хеш коммита и путь к файлу)
  filesearch   - Поиск по содержимому файлов
  filetypes    - Статистика по типам файлов
  search       - Поиск коммитов
  stats        - Статистика активности
  complexity   - Анализ сложности кода
  duplicates   - Поиск дубликатов кода
  dependencies - Анализ зависимостей проекта
  export       - Экспорт статистики (json/yaml)
  security     - Анализ безопасности кода
  docs         - Генерация документации (md/html)
  performance  - Анализ производительности
  ci-cd        - Настройка CI/CD (github/gitlab)
  theme        - Изменение цветовой темы (light/dark/monokai/solarized)
  settings     - Управление настройками (show/save/reset)
  ide          - Интеграция с IDE (vscode/pycharm/sublime)
  help         - Показать эту справку
  exit         - Выйти из программы

[bold yellow]Подсказки:[/bold yellow]
  - Используйте Tab для автодополнения команд
  - История команд сохраняется между сессиями
  - Для выбора веток и коммитов используйте интерактивный режим
  - Нажмите Ctrl+C для отмены текущей операции
  - Настройки сохраняются в ~/.gitwizard_settings.json
  - Используйте 'theme' для изменения цветовой схемы
  - Интегрируйте GitWizard с вашей IDE для удобства
        """
        console.print(Panel(help_text, title="[bold green]Справка GitWizard[/bold green]"))

@click.command()
@click.argument('repo_path', default='.')
def main(repo_path: str):
    """GitWizard - Улучшенный интерфейс для работы с Git"""
    wizard = GitWizard(repo_path)
    wizard.run()

if __name__ == '__main__':
    main() 