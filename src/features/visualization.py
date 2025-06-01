from typing import List, Dict, Any
from datetime import datetime
from rich.tree import Tree
from rich.table import Table
import os
from core.theme import Theme

class Visualizer:
    def __init__(self, repository, theme: Theme):
        self.repository = repository
        self.theme = theme

    def visualize_branches(self) -> Tree:
        """Визуализация веток в виде дерева"""
        tree = Tree(f"🌳 [bold {self.theme.get_color('accent')}]Ветки[/]")
        
        # Получаем все ветки
        branches = self.repository.get_branches()
        
        # Создаем основную ветку
        main_branch = self.repository.active_branch
        main_tree = tree.add(f"🌿 [bold {self.theme.get_color('warning')}]{main_branch}[/]")
        
        # Добавляем остальные ветки
        for branch in branches:
            if branch != main_branch:
                main_tree.add(f"🌱 [{self.theme.get_color('foreground')}]{branch}[/]")
        
        return tree

    def visualize_commit_graph(self) -> Table:
        """Визуализация графа коммитов"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Граф", style=self.theme.get_color('cyan'))
        table.add_column("Хеш", style=self.theme.get_color('green'), width=8)
        table.add_column("Автор", style=self.theme.get_color('yellow'))
        table.add_column("Дата", style=self.theme.get_color('magenta'))
        table.add_column("Сообщение", style=self.theme.get_color('foreground'))

        commits = self.repository.get_commits()
        branch_commits = {branch: self.repository.get_commits(branch)[0].hexsha for branch in self.repository.get_branches()}
        
        for commit in commits:
            # Определяем, является ли коммит частью какой-либо ветки
            branch_names = [name for name, hexsha in branch_commits.items() if hexsha == commit.hexsha]
            branch_marker = f"[bold {self.theme.get_color('success')}]{' '.join(branch_names)}[/{self.theme.get_color('success')}] " if branch_names else ""
            
            # Создаем визуальное представление графа
            graph_line = ""
            if commit.parents:
                graph_line += "│ " * (len(commit.parents) - 1)
                graph_line += "└─" if len(commit.parents) > 1 else "│"
            else:
                graph_line += "●"
            
            table.add_row(
                graph_line,
                commit.hexsha[:8],
                commit.author.name,
                datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M'),
                f"{branch_marker}{commit.message.split('\n')[0]}"
            )

        return table

    def visualize_history(self) -> List[List[str]]:
        """Визуализация истории коммитов"""
        commits = self.repository.get_commits()
        history_data = []
        for commit in commits[:10]:  # Показываем последние 10 коммитов
            history_data.append([
                commit.hexsha[:8],
                commit.author.name,
                datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M'),
                commit.message.split('\n')[0]
            ])
        return history_data

    def visualize_changes(self, commit_hash: str = None, file_path: str = None) -> List[List[str]]:
        """Визуализация изменений"""
        stats = self.repository.get_file_stats(commit_hash)
        changes_data = []
        for file, changes in stats.items():
            if not file_path or file == file_path:
                changes_data.append([
                    file,
                    str(changes['insertions']),
                    str(changes['deletions'])
                ])
        return changes_data

    def visualize_file_types(self) -> List[List[str]]:
        """Визуализация типов файлов"""
        files = self.repository.get_files()
        file_types = {}
        total_files = len(files)

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext:
                file_types[ext] = file_types.get(ext, 0) + 1
            else:
                file_types['без расширения'] = file_types.get('без расширения', 0) + 1

        file_type_data = []
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_files) * 100
            file_type_data.append([
                ext or 'без расширения',
                str(count),
                f"{percentage:.1f}%"
            ])
        return file_type_data

    def visualize_activity_stats(self) -> List[List[str]]:
        """Визуализация статистики активности"""
        commits = self.repository.get_commits()
        stats = {}
        
        for commit in commits:
            author = commit.author.name
            stats[author] = stats.get(author, 0) + 1

        activity_data = []
        for author, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            activity_data.append([author, str(count)])
        return activity_data

    def analyze_file_work_time(self, file_path: str = None) -> Any:
        return []

    def find_lost_commits(self) -> Any:
        return []

    def analyze_branch_conflicts(self, branch_name: str = None) -> Any:
        return []

    def search_in_files(self, query: str) -> Any:
        return []

    def search_commits(self, query: str) -> Any:
        return []

    def show_diff(self, commit_hash: str = None, file_path: str = None) -> str:
        """Показать различия между версиями файлов"""
        try:
            diffs = self.repository.get_diff(commit_hash, file_path)
            if not diffs:
                return ""

            diff_output = []
            for diff in diffs:
                if diff.a_path and diff.b_path:
                    diff_output.append(f"Файл: {diff.a_path}")
                    
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
                    from difflib import SequenceMatcher
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
                    
                    diff_output.append(str(table))
                    diff_output.append("")  # Пустая строка для разделения

            return "\n".join(diff_output)
        except Exception as e:
            return f"Ошибка при получении diff: {str(e)}" 