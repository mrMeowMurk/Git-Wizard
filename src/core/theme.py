from typing import Dict, Any
from prompt_toolkit.styles import Style

class Theme:
    def __init__(self):
        self.themes = {
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
        self.current_theme = 'dark'

    def get_theme(self, theme_name: str) -> Dict[str, str]:
        """Получение темы по имени"""
        return self.themes.get(theme_name, self.themes['dark'])

    def get_style(self, theme_name: str) -> Style:
        """Получение стиля для prompt_toolkit"""
        theme = self.get_theme(theme_name)
        return Style.from_dict({
            'prompt': f"{theme['accent']} bold",
            'background': theme['background'],
            'foreground': theme['foreground']
        })

    def get_available_themes(self) -> list:
        """Получение списка доступных тем"""
        return list(self.themes.keys())

    def set_theme(self, theme_name: str) -> bool:
        """Установка текущей темы"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False

    def get_current_theme(self) -> str:
        """Получение текущей темы"""
        return self.current_theme

    def get_color(self, color_type: str) -> str:
        """Получение цвета по типу для текущей темы"""
        theme = self.get_theme(self.current_theme)
        return theme.get(color_type, theme['foreground']) 