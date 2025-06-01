from typing import Dict, Any
import os
import yaml

class CICDSetup:
    def __init__(self, repository):
        self.repository = repository

    def setup_github_actions(self) -> str:
        """Настройка GitHub Actions"""
        workflow = {
            'name': 'CI/CD Pipeline',
            'on': {
                'push': {
                    'branches': ['main', 'master']
                },
                'pull_request': {
                    'branches': ['main', 'master']
                }
            },
            'jobs': {
                'test': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {
                            'uses': 'actions/checkout@v2'
                        },
                        {
                            'name': 'Set up Python',
                            'uses': 'actions/setup-python@v2',
                            'with': {
                                'python-version': '3.9'
                            }
                        },
                        {
                            'name': 'Install dependencies',
                            'run': 'pip install -r requirements.txt'
                        },
                        {
                            'name': 'Run tests',
                            'run': 'python -m pytest tests/'
                        },
                        {
                            'name': 'Run linting',
                            'run': 'pip install flake8 && flake8 .'
                        }
                    ]
                },
                'build': {
                    'needs': 'test',
                    'runs-on': 'ubuntu-latest',
                    'if': "github.event_name == 'push'",
                    'steps': [
                        {
                            'uses': 'actions/checkout@v2'
                        },
                        {
                            'name': 'Set up Python',
                            'uses': 'actions/setup-python@v2',
                            'with': {
                                'python-version': '3.9'
                            }
                        },
                        {
                            'name': 'Install dependencies',
                            'run': 'pip install -r requirements.txt'
                        },
                        {
                            'name': 'Build package',
                            'run': 'python setup.py sdist bdist_wheel'
                        },
                        {
                            'name': 'Upload to PyPI',
                            'if': "startsWith(github.ref, 'refs/tags/')",
                            'run': 'pip install twine && twine upload dist/*'
                        }
                    ]
                }
            }
        }
        
        # Создаем директорию .github/workflows если её нет
        os.makedirs('.github/workflows', exist_ok=True)
        
        # Сохраняем конфигурацию
        workflow_path = '.github/workflows/ci-cd.yml'
        with open(workflow_path, 'w') as f:
            yaml.dump(workflow, f, default_flow_style=False)
        
        return f"GitHub Actions настроены. Конфигурация сохранена в {workflow_path}"

    def setup_gitlab_ci(self) -> str:
        """Настройка GitLab CI/CD"""
        pipeline = {
            'image': 'python:3.9',
            'stages': ['test', 'build', 'deploy'],
            'variables': {
                'PIP_CACHE_DIR': '$CI_PROJECT_DIR/.pip-cache'
            },
            'cache': {
                'paths': ['.pip-cache']
            },
            'test': {
                'stage': 'test',
                'script': [
                    'pip install -r requirements.txt',
                    'python -m pytest tests/',
                    'pip install flake8',
                    'flake8 .'
                ]
            },
            'build': {
                'stage': 'build',
                'script': [
                    'pip install -r requirements.txt',
                    'python setup.py sdist bdist_wheel'
                ],
                'artifacts': {
                    'paths': ['dist/']
                },
                'only': ['master', 'main']
            },
            'deploy': {
                'stage': 'deploy',
                'script': [
                    'pip install twine',
                    'twine upload dist/*'
                ],
                'only': ['tags']
            }
        }
        
        # Сохраняем конфигурацию
        config_path = '.gitlab-ci.yml'
        with open(config_path, 'w') as f:
            yaml.dump(pipeline, f, default_flow_style=False)
        
        return f"GitLab CI/CD настроен. Конфигурация сохранена в {config_path}"

    def setup_circle_ci(self) -> str:
        """Настройка CircleCI"""
        config = {
            'version': 2.1,
            'jobs': {
                'test': {
                    'docker': [{'image': 'python:3.9'}],
                    'steps': [
                        'checkout',
                        {
                            'name': 'Install dependencies',
                            'command': 'pip install -r requirements.txt'
                        },
                        {
                            'name': 'Run tests',
                            'command': 'python -m pytest tests/'
                        },
                        {
                            'name': 'Run linting',
                            'command': 'pip install flake8 && flake8 .'
                        }
                    ]
                },
                'build': {
                    'docker': [{'image': 'python:3.9'}],
                    'steps': [
                        'checkout',
                        {
                            'name': 'Install dependencies',
                            'command': 'pip install -r requirements.txt'
                        },
                        {
                            'name': 'Build package',
                            'command': 'python setup.py sdist bdist_wheel'
                        },
                        {
                            'name': 'Store artifacts',
                            'command': 'mkdir -p artifacts && cp dist/* artifacts/',
                            'store_artifacts': {
                                'path': 'artifacts'
                            }
                        }
                    ]
                }
            },
            'workflows': {
                'version': 2,
                'build-test-deploy': {
                    'jobs': [
                        'test',
                        {
                            'build': {
                                'requires': ['test'],
                                'filters': {
                                    'branches': {
                                        'only': ['main', 'master']
                                    }
                                }
                            }
                        }
                    ]
                }
            }
        }
        
        # Создаем директорию .circleci если её нет
        os.makedirs('.circleci', exist_ok=True)
        
        # Сохраняем конфигурацию
        config_path = '.circleci/config.yml'
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        return f"CircleCI настроен. Конфигурация сохранена в {config_path}"

    def setup_travis_ci(self) -> str:
        """Настройка Travis CI"""
        config = {
            'language': 'python',
            'python': ['3.9'],
            'install': ['pip install -r requirements.txt'],
            'script': [
                'python -m pytest tests/',
                'pip install flake8',
                'flake8 .'
            ],
            'deploy': {
                'provider': 'pypi',
                'user': '__token__',
                'password': {
                    'secure': 'YOUR_ENCRYPTED_PYPI_TOKEN'
                },
                'on': {
                    'tags': True
                }
            }
        }
        
        # Сохраняем конфигурацию
        config_path = '.travis.yml'
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        return f"Travis CI настроен. Конфигурация сохранена в {config_path}" 