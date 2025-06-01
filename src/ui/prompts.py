from typing import List, Optional, Dict, Any
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter, NestedCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.prompt import Prompt, Confirm
from ui.console import ConsoleUI

class Prompts:
    def __init__(self, history_file: str, style: Style, ui: ConsoleUI):
        self.session = PromptSession(history=FileHistory(history_file))
        self.style = style
        self.ui = ui
        self.commands = self._create_commands_dict()

    def _create_commands_dict(self) -> Dict[str, Any]:
        """Создание словаря команд для автодополнения"""
        return {
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

    def get_completer(self) -> NestedCompleter:
        """Получение комплитера для команд"""
        return NestedCompleter.from_nested_dict(self.commands)

    def prompt(self, message: str = "gitwizard> ", auto_complete: bool = True) -> str:
        """Запрос ввода команды"""
        return self.session.prompt(
            message,
            completer=self.get_completer() if auto_complete else None,
            style=self.style
        ).strip()

    def confirm(self, message: str) -> bool:
        """Запрос подтверждения"""
        return Confirm.ask(message, console=self.ui.console)

    def select_from_list(self, items: List[str], message: str) -> Optional[str]:
        """Выбор элемента из списка"""
        if not items:
            return None

        for i, item in enumerate(items, 1):
            self.ui.print_info(f"{i}. {item}")

        while True:
            choice = Prompt.ask(message, default="q", console=self.ui.console)
            
            if choice.lower() == 'q':
                return None
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(items):
                    return items[index]
                else:
                    self.ui.print_error("Неверный номер")
            except ValueError:
                self.ui.print_error("Введите число или 'q'")

    def select_branch(self, branches: List[str]) -> Optional[str]:
        """Выбор ветки"""
        return self.select_from_list(branches, "Выберите номер ветки (или 'q' для отмены)")

    def select_commit(self, commits: List[str]) -> Optional[str]:
        """Выбор коммита"""
        return self.select_from_list(commits, "Выберите номер коммита (или 'q' для отмены)")

    def select_file(self, files: List[str]) -> Optional[str]:
        """Выбор файла"""
        return self.select_from_list(files, "Выберите номер файла (или 'q' для отмены)")

    def select_theme(self, themes: List[str]) -> Optional[str]:
        """Выбор темы"""
        return self.select_from_list(themes, "Выберите номер темы (или 'q' для отмены)")

    def select_ide(self, ides: List[str]) -> Optional[str]:
        """Выбор IDE"""
        return self.select_from_list(ides, "Выберите номер IDE (или 'q' для отмены)") 