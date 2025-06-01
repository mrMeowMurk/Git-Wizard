from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import List, Dict, Any
from core.theme import Theme

class ConsoleUI:
    def __init__(self, theme: Theme):
        self.console = Console()
        self.theme = theme

    def print_panel(self, text: str, title: str = None, style_type: str = "accent") -> None:
        """Вывод текста в панели с учетом темы"""
        style = self.theme.get_color(style_type)
        self.console.print(Panel(text, title=title, border_style=style))

    def print_table(self, title: str, columns: List[str], rows: List[List[str]], styles: Dict[str, str] = None) -> None:
        """Вывод таблицы с учетом темы"""
        table = Table(title=title, show_header=True, header_style=f"bold {self.theme.get_color('accent')}")
        
        for col in columns:
            col_style = styles.get(col, self.theme.get_color('cyan')) if styles else self.theme.get_color('cyan')
            table.add_column(col, style=col_style)
        
        for row in rows:
            styled_row = [Text(str(item), style=self.theme.get_color('foreground')) for item in row]
            table.add_row(*[str(item) for item in styled_row])
        
        self.console.print(table)

    def print_syntax(self, code: str, language: str = "python", theme_name: str = "monokai") -> None:
        """Вывод кода с подсветкой синтаксиса"""
        syntax = Syntax(code, language, theme=theme_name)
        self.console.print(syntax)

    def print_progress(self, description: str) -> Progress:
        """Создание индикатора прогресса"""
        return Progress(
            SpinnerColumn(),
            TextColumn(f"[{self.theme.get_color('accent')}][progress.description]{{task.description}}[/{self.theme.get_color('accent')}]"),
            console=self.console
        )

    def print_error(self, message: str) -> None:
        """Вывод сообщения об ошибке"""
        self.console.print(f"[{self.theme.get_color('error')}]Ошибка: {message}[/]")

    def print_warning(self, message: str) -> None:
        """Вывод предупреждения"""
        self.console.print(f"[{self.theme.get_color('warning')}]Предупреждение: {message}[/]")

    def print_success(self, message: str) -> None:
        """Вывод сообщения об успехе"""
        self.console.print(f"[{self.theme.get_color('success')}]{message}[/]")

    def print_info(self, message: str) -> None:
        """Вывод информационного сообщения"""
        self.console.print(f"[{self.theme.get_color('accent')}]{message}[/]")

    def print_diff(self, old_text: str, new_text: str) -> None:
        """Вывод различий в тексте с учетом темы"""
        from difflib import SequenceMatcher
        
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Старая версия", style=self.theme.get_color('error'), width=50)
        table.add_column("Новая версия", style=self.theme.get_color('success'), width=50)
        
        old_lines = old_text.split('\n')
        new_lines = new_text.split('\n')
        
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
        
        self.console.print(table) 