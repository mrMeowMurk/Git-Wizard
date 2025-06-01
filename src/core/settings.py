import os
import json
from typing import Dict, Any

class Settings:
    def __init__(self):
        self.settings_file = os.path.join(os.path.expanduser("~"), ".gitwizard_settings.json")
        self.settings = self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        """Загрузка настроек пользователя"""
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
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    user_settings = json.load(f)
                    # Обновляем дефолтные настройки пользовательскими
                    default_settings.update(user_settings)
        except Exception as e:
            print(f"Не удалось загрузить настройки: {str(e)}")
        
        return default_settings

    def save_settings(self) -> bool:
        """Сохранение настроек пользователя"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка при сохранении настроек: {str(e)}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Получение значения настройки"""
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Установка значения настройки"""
        self.settings[key] = value

    def reset(self) -> None:
        """Сброс настроек к значениям по умолчанию"""
        self.settings = self.load_settings()

    def get_all(self) -> Dict[str, Any]:
        """Получение всех настроек"""
        return self.settings.copy() 