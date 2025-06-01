import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from difflib import SequenceMatcher
from core.repository import GitRepository
from core.settings import Settings
from core.theme import Theme
from ui.console import ConsoleUI
from ui.prompts import Prompts
from features.analysis import CodeAnalyzer
from features.visualization import Visualizer
from features.documentation import DocumentationGenerator
from features.ci_cd import CICDSetup

class GitWizard:
    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)
        self.settings = Settings()
        self.theme = Theme()
        self.ui = ConsoleUI(self.theme)
        
        try:
            with self.ui.print_progress(description="Инициализация GitWizard...") as progress:
                self.repo = GitRepository(self.repo_path)
        except ValueError as e:
            self.ui.print_error(f"Ошибка инициализации: {str(e)}")
            sys.exit(1)
        
        history_file = os.path.join(os.path.expanduser("~"), ".gitwizard_history")
        current_style = self.theme.get_style(self.theme.get_current_theme())
        self.prompts = Prompts(history_file=history_file, style=current_style, ui=self.ui)
        
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
                "circle": None,
                "travis": None,
            },
            "theme": {
                theme for theme in self.theme.get_available_themes()
            },
            "settings": {
                "show": None,
                "save": None,
                "reset": None,
            },
            "ide": {
                "vscode": None,
                "pycharm": None,
                "sublime": None,
            },
            "help": None,
            "exit": None,
        }
        self.prompts.completer = self.prompts.get_completer()

        self.analyzer = CodeAnalyzer(self.repo)
        self.visualizer = Visualizer(self.repo, self.theme)
        self.docs = DocumentationGenerator(self.repo)
        self.ci_cd = CICDSetup(self.repo)

    def show_welcome(self):
        """Показывает приветственное сообщение"""
        welcome_text = """
        [bold green]GitWizard[/bold green] - ваш умный помощник для работы с Git
        
        Используйте команды для анализа и управления репозиторием.
        Введите 'help' для получения списка доступных команд.
        """
        self.ui.print_panel(welcome_text, title="Добро пожаловать!")

    def show_help(self):
        """Показывает справку по командам"""
        commands_info = [
            ("Анализ кода", "complexity [файл]", "Анализ сложности кода"),
            ("Анализ кода", "duplicates [мин_длина]", "Поиск дубликатов кода"),
            ("Анализ кода", "security [файл]", "Анализ безопасности кода"),
            ("Анализ кода", "performance [файл]", "Анализ производительности"),
            ("Визуализация", "graph", "Визуализация графа коммитов"),
            ("Визуализация", "history", "История коммитов"),
            ("Визуализация", "changes [коммит]", "Изменения в коммите"),
            ("Визуализация", "filetypes", "Статистика по типам файлов"),
            ("Документация", "docs [md/html]", "Генерация документации"),
            ("Документация", "export [json/yaml]", "Экспорт статистики"),
            ("CI/CD", "ci-cd [github/gitlab/circle/travis]", "Настройка CI/CD"),
            ("Настройки", "theme [тема]", "Изменение цветовой темы"),
            ("Настройки", "settings [show/save/reset]", "Управление настройками"),
            ("Настройки", "ide [vscode/pycharm/sublime]", "Интеграция с IDE"),
            ("Общие", "help", "Показать эту справку"),
            ("Общие", "exit", "Выход из программы")
        ]

        table_rows = [[cat, cmd, desc] for cat, cmd, desc in commands_info]
        self.ui.print_table("Доступные команды", ["Категория", "Команда", "Описание"], table_rows)

    def show_tips(self):
        """Показать полезные советы"""
        tips = [
            "Используйте 'help' для получения списка всех доступных команд",
            "Команда 'graph' покажет визуальное представление веток",
            "Используйте 'history' для просмотра истории коммитов",
            "Команда 'stats' покажет статистику активности",
            "Используйте 'search' для поиска по коммитам и файлам"
        ]
        
        self.ui.print_panel("\n".join(tips), title="Полезные советы", style_type='info')

    def run(self):
        """Запускает основной цикл программы"""
        if self.settings.get('show_welcome', True):
            self.show_welcome()
        
        self.show_status()

        if self.settings.get('show_tips', True):
             self.show_tips()
        
        self.ui.print_info("\nДоступные команды:")
        self.ui.print_info("Введите 'help' для подробной справки или 'exit' для выхода")

        while True:
            try:
                command = self.prompts.prompt("gitwizard> ", auto_complete=self.settings.get('auto_complete', True)).strip()
                
                if not command:
                    continue
                
                if command == "exit":
                    if self.prompts.confirm("Вы уверены, что хотите выйти?"):
                        break
                    else:
                        continue
                
                if command == "help":
                    self.show_help()
                    continue

                parts = command.split(maxsplit=1)
                cmd = parts[0].lower()
                args_str = parts[1] if len(parts) > 1 else ""
                args = args_str.split()

                if cmd == "status":
                    self.show_status()
                
                elif cmd == "graph":
                    self.visualize_branches()
                
                elif cmd == "history":
                    self.visualize_history()
                
                elif cmd == "commit-graph":
                    self.visualize_commit_graph()
                
                elif cmd == "worktime":
                    file_path = args[0] if args else None
                    self.analyze_file_work_time(file_path)

                elif cmd == "lost-commits":
                    self.find_lost_commits()

                elif cmd == "conflicts":
                    branch_name = args[0] if args else self.prompts.select_branch(self.repo.get_branches())
                    if branch_name:
                         self.analyze_branch_conflicts(branch_name)

                elif cmd == "changes":
                    commit_hash = args[0] if args else self.prompts.select_commit([c.hexsha for c in self.repo.get_commits()])
                    if commit_hash:
                        file_path = args[1] if len(args) > 1 else None
                        self.analyze_changes(commit_hash=commit_hash, file_path=file_path)

                elif cmd == "diff":
                    commit_hash = args[0] if args else self.prompts.select_commit([c.hexsha for c in self.repo.get_commits()])
                    if commit_hash:
                        file_path = args[1] if len(args) > 1 else None
                        self.show_diff(commit_hash=commit_hash, file_path=file_path)

                elif cmd == "filesearch":
                     query = args_str
                     if query:
                         self.search_in_files(query)
                     else:
                          self.ui.print_warning("Укажите строку для поиска")

                elif cmd == "filetypes":
                    self.analyze_file_types()

                elif cmd == "search":
                    query = args_str
                    if query:
                        self.search_commits(query)
                    else:
                        self.ui.print_warning("Укажите строку для поиска")

                elif cmd == "stats":
                    self.show_activity_stats()
                
                elif cmd == "complexity":
                    file = args[0] if args else None
                    self.analyze_code_complexity(file)
                
                elif cmd == "duplicates":
                    # Проверяем, является ли аргумент числом для min_length
                    if args and args[0].isdigit():
                        min_length = int(args[0])
                        self.find_code_duplicates(min_length)
                    elif not args:
                        # Нет аргументов, используем значение по умолчанию
                        self.find_code_duplicates()
                    else:
                        # Аргумент не является числом, выводим сообщение об ошибке
                        self.ui.print_error(f"Неверный аргумент для 'duplicates': {args[0]}. Ожидается число.")
                        self.ui.print_info("Использование: duplicates [мин_длина]")
                
                elif cmd == "security":
                    file = args[0] if args else None
                    self.analyze_security(file)
                
                elif cmd == "performance":
                    file = args[0] if args else None
                    self.analyze_performance(file)
                
                elif cmd == "docs":
                    format = args[0] if args else "md"
                    if format not in ['md', 'html']:
                         self.ui.print_error(f"Неподдерживаемый формат: {format}. Доступные: md, html")
                    else:
                         self.generate_documentation(format)
                
                elif cmd == "export":
                    format = args[0] if args else "json"
                    if format not in ['json', 'yaml']:
                         self.ui.print_error(f"Неподдерживаемый формат: {format}. Доступные: json, yaml")
                    else:
                        self.export_stats(format)
                
                elif cmd == "ci-cd":
                    platform = args[0] if args else "github"
                    supported_platforms = ['github', 'gitlab', 'circle', 'travis']
                    if platform not in supported_platforms:
                        self.ui.print_error(f"Неизвестная платформа: {platform}. Поддерживаемые: {', '.join(supported_platforms)}")
                    else:
                         self.setup_ci_cd(platform)
                
                elif cmd == "theme":
                    theme_name = args[0] if args else None
                    if not theme_name:
                        self.ui.print_warning("Укажите название темы. Доступные: light, dark, monokai, solarized")
                    else:
                        if self.theme.set_theme(theme_name):
                            self.prompts.session.style = self.theme.get_style(theme_name)
                            self.ui.print_success(f"Тема изменена на {theme_name}")
                        else:
                            self.ui.print_error(f"Неизвестная тема: {theme_name}")
                
                elif cmd == "settings":
                    action = args[0] if args else "show"
                    if action == "show":
                         all_settings = self.settings.get_all()
                         settings_data = [[key, str(value)] for key, value in all_settings.items()]
                         self.ui.print_table("Настройки", ["Настройка", "Значение"], settings_data)
                    elif action == "save":
                         if self.settings.save_settings():
                             self.ui.print_success("Настройки сохранены")
                         else:
                              self.ui.print_error("Не удалось сохранить настройки")
                    elif action == "reset":
                        self.settings.reset()
                        self.ui.print_success("Настройки сброшены к значениям по умолчанию")
                    else:
                         self.ui.print_error(f"Неизвестное действие: {action}. Доступные действия: show, save, reset")
                
                elif cmd == "ide":
                    ide_name = args[0] if args else self.prompts.select_ide(['vscode', 'pycharm', 'sublime'])
                    supported_ides = ["vscode", "pycharm", "sublime"]
                    if ide_name:
                        if ide_name in supported_ides:
                            try:
                                current_ide_settings = self.settings.get('ide_integration', {})
                                for key in current_ide_settings:
                                    current_ide_settings[key] = False
                                current_ide_settings[ide_name] = True

                                self.settings.set('ide_integration', current_ide_settings)
                                self.settings.save_settings()
                                self.ui.print_success(f"Интеграция с {ide_name} настроена")
                            except Exception as e:
                                self.ui.print_error(f"Ошибка при настройке интеграции с IDE: {str(e)}")
                        else:
                            self.ui.print_error(f"Неподдерживаемая IDE: {ide_name}. Поддерживаемые: {', '.join(supported_ides)}")
                    else:
                         self.ui.print_warning("Укажите название IDE")

                else:
                    self.ui.print_error(f"Неизвестная команда: {cmd}")
                    self.ui.print_info("Введите 'help' для получения списка команд")

            except KeyboardInterrupt:
                self.ui.print_info("Отменено пользователем.")
            except EOFError:
                break
            except Exception as e:
                self.ui.print_error(f"Произошла ошибка: {str(e)}")

        self.ui.print_info("До свидания!")

    def show_status(self):
        """Показать текущий статус репозитория"""
        try:
            current_branch = self.repo.active_branch
            self.ui.print_panel(f"[bold green]Текущая ветка: {current_branch}[/bold green]", title="Статус", style_type='info')
            
            if self.repo.is_dirty:
                self.ui.print_warning("Есть несохраненные изменения:")
                
                table_data = []
                modified_files = self.repo.get_modified_files()
                untracked_files = self.repo.get_untracked_files()

                for item in modified_files:
                    table_data.append(["Изменен", item])
                
                for item in untracked_files:
                    table_data.append(["Новый", item])
                
                self.ui.print_table("", ["Статус", "Файл"], table_data)
            else:
                self.ui.print_success("Рабочая директория чиста")
            
            last_commit = self.repo.get_last_commit()
            commit_info = (f"[bold]Последний коммит:[/bold]\n"
                           f"Хеш: [{self.theme.get_color('cyan')}]{last_commit.hexsha[:8]}[/]\n"
                           f"Автор: [{self.theme.get_color('green')}]{last_commit.author.name}[/]\n"
                           f"Дата: [{self.theme.get_color('warning')}]{datetime.fromtimestamp(last_commit.committed_date).strftime('%Y-%m-%d %H:%M')}[/]\n"
                           f"Сообщение: [{self.theme.get_color('foreground')}]{last_commit.message.split('\n')[0]}[/]")
            self.ui.print_panel(commit_info, style_type='info')
            
        except Exception as e:
            self.ui.print_error(f"Ошибка при получении статуса: {str(e)}")

    def visualize_branches(self):
        """Визуализация веток в виде дерева"""
        try:
            tree = self.visualizer.visualize_branches()
            self.ui.console.print(tree)
        except Exception as e:
            self.ui.print_error(f"Ошибка при визуализации веток: {str(e)}")

    def visualize_history(self):
        """Визуализация истории коммитов"""
        try:
            history_data = self.visualizer.visualize_history()
            header = ["Хеш", "Автор", "Дата", "Сообщение"]
            self.ui.print_table("История коммитов", header, history_data)
        except Exception as e:
            self.ui.print_error(f"Ошибка при визуализации истории: {str(e)}")

    def visualize_commit_graph(self):
        """Визуализация графа коммитов"""
        try:
            graph_table = self.visualizer.visualize_commit_graph()
            self.ui.console.print(graph_table)
        except Exception as e:
            self.ui.print_error(f"Ошибка при визуализации графа: {str(e)}")

    def analyze_file_work_time(self, file_path: Optional[str] = None):
        """Анализ времени работы над файлами"""
        try:
            self.ui.print_warning("Функционал анализа времени работы пока не адаптирован к новой структуре.")
        except Exception as e:
             self.ui.print_error(f"Ошибка при анализе времени работы: {str(e)}")

    def find_lost_commits(self):
        """Поиск 'потерянных' коммитов"""
        try:
            self.ui.print_warning("Функционал поиска потерянных коммитов пока не адаптирован к новой структуре.")
        except Exception as e:
             self.ui.print_error(f"Ошибка при поиске потерянных коммитов: {str(e)}")

    def analyze_branch_conflicts(self, branch_name: Optional[str] = None):
        """Анализ потенциальных конфликтов в ветках"""
        try:
            self.ui.print_warning("Функционал анализа конфликтов пока не адаптирован к новой структуре.")
        except Exception as e:
             self.ui.print_error(f"Ошибка при анализе конфликтов: {str(e)}")

    def analyze_changes(self, commit_hash: Optional[str] = None, file_path: Optional[str] = None):
        """Анализ изменений в файлах"""
        try:
            changes_data = self.visualizer.visualize_changes(commit_hash, file_path)
            header = ["Файл", "Добавлено", "Удалено"]
            self.ui.print_table("Изменения", header, changes_data)
        except Exception as e:
              self.ui.print_error(f"Ошибка при анализе изменений: {str(e)}")

    def search_in_files(self, query: str):
        """Поиск по содержимому файлов"""
        try:
            results = self.visualizer.search_in_files(query)
            if results:
                self.ui.print_table(f"Результаты поиска: {query}", ["Файл"], results)
            else:
                self.ui.print_info(f"Ничего не найдено по запросу: {query}")
        except Exception as e:
             self.ui.print_error(f"Ошибка при поиске в файлах: {str(e)}")

    def analyze_file_types(self):
        """Анализ типов файлов в репозитории"""
        try:
            file_type_stats = self.visualizer.visualize_file_types()
            header = ["Тип файла", "Количество", "Процент"]
            self.ui.print_table("Статистика по типам файлов", header, file_type_stats)
        except Exception as e:
              self.ui.print_error(f"Ошибка при анализе типов файлов: {str(e)}")

    def search_commits(self, query: str):
        """Поиск коммитов по сообщению или содержимому"""
        try:
            self.ui.print_warning("Функционал поиска коммитов пока не адаптирован к новой структуре.")
        except Exception as e:
             self.ui.print_error(f"Ошибка при поиске коммитов: {str(e)}")

    def show_activity_stats(self):
        """Показать статистику активности по авторам"""
        try:
            activity_stats = self.visualizer.visualize_activity_stats()
            header = ["Автор", "Количество коммитов"]
            self.ui.print_table("Статистика активности", header, activity_stats)
        except Exception as e:
             self.ui.print_error(f"Ошибка при показе статистики активности: {str(e)}")

    def show_diff(self, commit_hash: Optional[str] = None, file_path: Optional[str] = None):
        """Показать различия между версиями файлов"""
        try:
            # Получаем raw diffs напрямую из репозитория
            diffs = self.repo.get_diff(commit_hash, file_path)

            if not diffs:
                self.ui.print_info("Изменений не найдено.")
                return

            self.ui.print_panel("Изменения (Diff)")

            # Адаптируем логику форматирования из visualization.py
            from difflib import SequenceMatcher # Импорт здесь, чтобы не зависеть от visualization.py
            from rich.table import Table # Импорт Rich Table здесь
            import os # Импорт os здесь

            for diff in diffs:
                if diff.a_path and diff.b_path:
                    self.ui.print_info(f"Файл: {diff.a_path}")

                    # Получаем содержимое старой и новой версии
                    old_content = diff.a_blob.data_stream.read().decode('utf-8', errors='replace') if diff.a_blob else ""
                    new_content = diff.b_blob.data_stream.read().decode('utf-8', errors='replace') if diff.b_blob else ""

                    # Разбиваем на строки
                    old_lines = old_content.splitlines()
                    new_lines = new_content.splitlines()

                    # Создаем таблицу для отображения различий
                    table = Table(show_header=False, box=None, padding=(0, 1))
                    table.add_column("Старая версия", style=self.theme.get_color('error'), width=50)
                    table.add_column("Новая версия", style=self.theme.get_color('success'), width=50)

                    # Используем SequenceMatcher для определения различий
                    matcher = SequenceMatcher(None, old_lines, new_lines)

                    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                        if tag == 'equal':
                            for i in range(i1, i2):
                                table.add_row(old_lines[i], new_lines[j1 + (i - i1)])
                        elif tag == 'delete':
                            for i in range(i1, i2):
                                table.add_row(old_lines[i], "")
                        elif tag == 'insert':
                            for j in range(j1, j2):
                                table.add_row("", new_lines[j])
                        elif tag == 'replace':
                            for i, j in zip(range(i1, i2), range(j1, j2)):
                                table.add_row(old_lines[i], new_lines[j])

                    # Печатаем таблицу напрямую
                    self.ui.console.print(table)
                    self.ui.console.print("") # Пустая строка для разделения между файлами

        except Exception as e:
             self.ui.print_error(f"Ошибка при показе изменений: {str(e)}")

    def analyze_code_complexity(self, file_path: Optional[str] = None):
        """Анализ сложности кода"""
        try:
            results = self.analyzer.analyze_complexity(file_path)
            if results:
                table_rows = [[r['file'], str(r['code_lines']), str(r['functions']), str(r['complexity'])] for r in results]
                self.ui.print_table("Анализ сложности кода", ["Файл", "Строк кода", "Функций", "Сложность"], table_rows)
            else:
                self.ui.print_info("Файлы для анализа сложности не найдены или произошла ошибка.")
        except Exception as e:
             self.ui.print_error(f"Ошибка при анализе сложности кода: {str(e)}")

    def find_code_duplicates(self, min_length: int = 5):
        """Поиск дубликатов кода"""
        try:
            results = self.analyzer.find_duplicates(min_length)
            if results:
                self.ui.print_panel("Найдены дубликаты кода:", style_type='warning')
                for item in results:
                    self.ui.print_panel(item['fragment'], title="Дубликат", style_type='warning')
                    self.ui.print_info("Встречается в:")
                    occurrences_data = [[file, str(line)] for file, line in item['occurrences']]
                    self.ui.print_table("", ["Файл", "Строка"], occurrences_data, styles={'Файл': self.theme.get_color('cyan'), 'Строка': self.theme.get_color('green')})
            else:
                self.ui.print_success("Дубликатов кода не найдено")
        except Exception as e:
             self.ui.print_error(f"Ошибка при поиске дубликатов: {str(e)}")

    def analyze_dependencies(self):
        """Анализ зависимостей проекта"""
        try:
            self.ui.print_warning("Функционал анализа зависимостей пока не адаптирован к новой структуре.")
        except Exception as e:
             self.ui.print_error(f"Ошибка при анализе зависимостей: {str(e)}")

    def export_stats(self, format: str = 'json'):
        """Экспорт статистики"""
        try:
            self.ui.print_warning("Функционал экспорта статистики пока не адаптирован к новой структуре.")
        except Exception as e:
             self.ui.print_error(f"Ошибка при экспорте статистики: {str(e)}")

    def analyze_security(self, file_path: Optional[str] = None):
        """Анализ безопасности кода"""
        try:
            results = self.analyzer.analyze_security(file_path)
            if results:
                self.ui.print_panel("Найдены потенциальные проблемы безопасности:", style_type='error')
                
                issues_by_type = defaultdict(list)
                for issue in results:
                    issues_by_type[issue['issue_type']].append(issue)
                
                for issue_type, occurrences in issues_by_type.items():
                    self.ui.print_warning(f"\n{issue_type}:")
                    table_rows = [[item['file'], str(item['line']), item['code']] for item in occurrences]
                    self.ui.print_table("", ["Файл", "Строка", "Код"], table_rows, styles={'Файл': self.theme.get_color('cyan'), 'Строка': self.theme.get_color('green'), 'Код': self.theme.get_color('foreground')})
            else:
                self.ui.print_success("Потенциальных проблем безопасности не найдено")
        except Exception as e:
             self.ui.print_error(f"Ошибка при анализе безопасности: {str(e)}")

    def generate_documentation(self, format: str = 'md'):
        """Генерация документации проекта"""
        try:
             self.ui.print_warning("Функционал генерации документации пока не адаптирован к новой структуре.")
        except Exception as e:
             self.ui.print_error(f"Ошибка при генерации документации: {str(e)}")

    def analyze_performance(self, file_path: Optional[str] = None):
        """Анализ производительности кода"""
        try:
            results = self.analyzer.analyze_performance(file_path)
            if results:
                table_rows = [[r['file'], str(r['loops']), str(r['recursion']), str(r['max_nesting'])] for r in results]
                self.ui.print_table("Анализ производительности", ["Файл", "Циклы", "Рекурсия", "Вложенность"], table_rows, styles={'Файл': self.theme.get_color('cyan'), 'Циклы': self.theme.get_color('warning'), 'Рекурсия': self.theme.get_color('magenta'), 'Вложенность': self.theme.get_color('success')})
            else:
                 self.ui.print_info("Файлы для анализа производительности не найдены или произошла ошибка.")
        except Exception as e:
             self.ui.print_error(f"Ошибка при анализе производительности: {str(e)}")

    def setup_ci_cd(self, platform: str = 'github'):
        """Настройка CI/CD для проекта"""
        try:
            self.ui.print_warning("Функционал настройки CI/CD пока не адаптирован к новой структуре.")
        except Exception as e:
             self.ui.print_error(f"Ошибка при настройке CI/CD: {str(e)}")

    def get_project_description(self) -> str:
        """Получение описания проекта"""
        return "Описание проекта отсутствует"

    def get_project_authors(self) -> List[str]:
         """Получение списка авторов проекта"""
         return []

    def get_project_files(self) -> Dict[str, List[str]]:
         """Получение структуры файлов проекта"""
         return {}

    def get_project_dependencies(self) -> Dict[str, List[str]]:
         """Получение зависимостей проекта"""
         return {}

def main():
    wizard = GitWizard()
    wizard.run()

if __name__ == "__main__":
    main() 