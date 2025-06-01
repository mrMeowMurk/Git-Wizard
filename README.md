# GitWizard

Умный помощник для работы с Git, предоставляющий расширенные возможности анализа и управления репозиторием.

## Возможности

- 🔍 Анализ кода
  - Анализ сложности кода
  - Поиск дубликатов
  - Анализ безопасности
  - Анализ производительности

- 📊 Визуализация
  - Граф коммитов
  - История изменений
  - Статистика по типам файлов
  - Активность авторов

- 📚 Документация
  - Генерация документации в Markdown и HTML
  - Экспорт статистики в JSON и YAML
  - Автоматическое обновление

- 🔄 CI/CD
  - Настройка GitHub Actions
  - Настройка GitLab CI/CD
  - Настройка CircleCI
  - Настройка Travis CI

- 🎨 Пользовательский интерфейс
  - Настраиваемые цветовые темы
  - Интерактивные подсказки
  - Сохранение настроек
  - Интеграция с популярными IDE

## Установка

```bash
# Клонирование репозитория
git clone https://github.com/yourusername/gitwizard.git
cd gitwizard

# Установка зависимостей
pip install -r requirements.txt

# Установка пакета
pip install -e .
```

## Использование

```bash
# Запуск программы
gitwizard

# Доступные команды
gitwizard> help
```

### Примеры команд

```bash
# Анализ кода
gitwizard> complexity src/main.py
gitwizard> duplicates 10
gitwizard> security
gitwizard> performance

# Визуализация
gitwizard> graph
gitwizard> history
gitwizard> changes HEAD
gitwizard> filetypes

# Документация
gitwizard> docs md
gitwizard> docs html
gitwizard> export json
gitwizard> export yaml

# CI/CD
gitwizard> ci-cd github
gitwizard> ci-cd gitlab
gitwizard> ci-cd circle
gitwizard> ci-cd travis

# Настройки
gitwizard> theme dark
gitwizard> settings show
gitwizard> ide vscode
```

## Структура проекта

```
gitwizard/
├── src/
│   ├── core/
│   │   ├── repository.py
│   │   ├── settings.py
│   │   └── theme.py
│   ├── features/
│   │   ├── analysis.py
│   │   ├── visualization.py
│   │   ├── documentation.py
│   │   └── ci_cd.py
│   ├── ui/
│   │   ├── console.py
│   │   └── prompts.py
│   └── main.py
├── tests/
│   └── ...
├── requirements.txt
├── setup.py
└── README.md
```

## Разработка

### Зависимости

- Python >= 3.9
- GitPython
- Rich
- Prompt Toolkit
- PyYAML
- Colorama

### Запуск тестов

```bash
pytest tests/
```

### Сборка пакета

```bash
python setup.py sdist bdist_wheel
```

## Лицензия

MIT License

## Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте изменения в репозиторий (`git push origin feature/amazing-feature`)
5. Создайте Pull Request 