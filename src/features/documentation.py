from typing import Dict, Any, List
import os
import json
import yaml
from datetime import datetime

class DocumentationGenerator:
    def __init__(self, repository):
        self.repository = repository

    def generate_markdown(self) -> str:
        """Генерация документации в формате Markdown"""
        content = []
        
        # Заголовок
        content.append("# Документация проекта\n")
        
        # Информация о репозитории
        content.append("## Информация о репозитории\n")
        content.append(f"- **Название**: {os.path.basename(self.repository.working_dir)}")
        content.append(f"- **Последнее обновление**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        
        # Статистика
        content.append("## Статистика\n")
        commits = self.repository.get_commits()
        files = self.repository.get_files()
        content.append(f"- **Количество коммитов**: {len(commits)}")
        content.append(f"- **Количество файлов**: {len(files)}")
        content.append(f"- **Активная ветка**: {self.repository.active_branch}\n")
        
        # Авторы
        content.append("## Авторы\n")
        authors = {}
        for commit in commits:
            author = commit.author.name
            authors[author] = authors.get(author, 0) + 1
        
        for author, count in sorted(authors.items(), key=lambda x: x[1], reverse=True):
            content.append(f"- {author} ({count} коммитов)")
        content.append("")
        
        # Структура проекта
        content.append("## Структура проекта\n")
        content.append("```")
        for file in sorted(files):
            content.append(file)
        content.append("```\n")
        
        # Последние изменения
        content.append("## Последние изменения\n")
        for commit in commits[:5]:
            content.append(f"### {commit.message.split('\n')[0]}")
            content.append(f"- **Автор**: {commit.author.name}")
            content.append(f"- **Дата**: {datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M')}")
            content.append(f"- **Хеш**: {commit.hexsha[:8]}\n")
        
        return "\n".join(content)

    def generate_html(self) -> str:
        """Генерация документации в формате HTML"""
        content = []
        
        # HTML шаблон
        content.append("""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Документация проекта</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }
        h1, h2, h3 { color: #333; }
        .container { max-width: 1200px; margin: 0 auto; }
        .section { margin-bottom: 30px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
        .stat-card { background: #f5f5f5; padding: 15px; border-radius: 5px; }
        .commit { border-left: 3px solid #007bff; padding-left: 15px; margin-bottom: 20px; }
        pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">""")
        
        # Заголовок
        content.append("""        <h1>Документация проекта</h1>
        <div class="section">
            <h2>Информация о репозитории</h2>
            <div class="stats">""")
        
        content.append(f"""                <div class="stat-card">
                    <h3>Название</h3>
                    <p>{os.path.basename(self.repository.working_dir)}</p>
                </div>
                <div class="stat-card">
                    <h3>Последнее обновление</h3>
                    <p>{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                </div>""")
        
        # Статистика
        commits = self.repository.get_commits()
        files = self.repository.get_files()
        content.append(f"""                <div class="stat-card">
                    <h3>Количество коммитов</h3>
                    <p>{len(commits)}</p>
                </div>
                <div class="stat-card">
                    <h3>Количество файлов</h3>
                    <p>{len(files)}</p>
                </div>
                <div class="stat-card">
                    <h3>Активная ветка</h3>
                    <p>{self.repository.active_branch}</p>
                </div>
            </div>
        </div>""")
        
        # Авторы
        content.append("""        <div class="section">
            <h2>Авторы</h2>
            <div class="stats">""")
        
        authors = {}
        for commit in commits:
            author = commit.author.name
            authors[author] = authors.get(author, 0) + 1
        
        for author, count in sorted(authors.items(), key=lambda x: x[1], reverse=True):
            content.append(f"""                <div class="stat-card">
                    <h3>{author}</h3>
                    <p>{count} коммитов</p>
                </div>""")
        
        content.append("""            </div>
        </div>""")
        
        # Структура проекта
        content.append("""        <div class="section">
            <h2>Структура проекта</h2>
            <pre>""")
        
        for file in sorted(files):
            content.append(file)
        
        content.append("""            </pre>
        </div>""")
        
        # Последние изменения
        content.append("""        <div class="section">
            <h2>Последние изменения</h2>""")
        
        for commit in commits[:5]:
            content.append(f"""            <div class="commit">
                <h3>{commit.message.split('\n')[0]}</h3>
                <p><strong>Автор:</strong> {commit.author.name}</p>
                <p><strong>Дата:</strong> {datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M')}</p>
                <p><strong>Хеш:</strong> {commit.hexsha[:8]}</p>
            </div>""")
        
        content.append("""        </div>
    </div>
</body>
</html>""")
        
        return "\n".join(content)

    def export_stats(self, format: str = 'json') -> str:
        """Экспорт статистики в JSON или YAML"""
        stats = {
            'repository': {
                'name': os.path.basename(self.repository.working_dir),
                'active_branch': self.repository.active_branch,
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M')
            },
            'commits': {
                'total': len(self.repository.get_commits()),
                'authors': {}
            },
            'files': {
                'total': len(self.repository.get_files()),
                'types': {}
            }
        }
        
        # Статистика по авторам
        for commit in self.repository.get_commits():
            author = commit.author.name
            stats['commits']['authors'][author] = stats['commits']['authors'].get(author, 0) + 1
        
        # Статистика по типам файлов
        for file in self.repository.get_files():
            ext = os.path.splitext(file)[1].lower()
            if ext:
                stats['files']['types'][ext] = stats['files']['types'].get(ext, 0) + 1
            else:
                stats['files']['types']['без расширения'] = stats['files']['types'].get('без расширения', 0) + 1
        
        if format.lower() == 'yaml':
            return yaml.dump(stats, allow_unicode=True)
        else:
            return json.dumps(stats, ensure_ascii=False, indent=2) 