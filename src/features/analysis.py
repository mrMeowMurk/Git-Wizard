from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict
import re
from datetime import datetime

class CodeAnalyzer:
    def __init__(self, repository):
        self.repository = repository

    def analyze_complexity(self, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Анализ сложности кода"""
        results = []
        files = [file_path] if file_path else self._get_code_files()

        for file in files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    # Подсчет строк кода
                    code_lines = len([l for l in lines if l.strip() and not l.strip().startswith(('#', '//', '/*', '*', '*/'))])
                    
                    # Подсчет функций
                    functions = 0
                    complexity = 0
                    
                    for line in lines:
                        # Подсчет функций
                        if any(line.strip().startswith(keyword) for keyword in ['def ', 'function ', 'public ', 'private ', 'protected ']):
                            functions += 1
                        
                        # Подсчет сложности
                        if any(keyword in line for keyword in ['if ', 'for ', 'while ', 'switch ', 'case ', 'catch ', '&&', '||']):
                            complexity += 1
                    
                    results.append({
                        'file': file,
                        'code_lines': code_lines,
                        'functions': functions,
                        'complexity': complexity
                    })
            except Exception as e:
                print(f"Ошибка при анализе файла {file}: {str(e)}")

        return results

    def find_duplicates(self, min_length: int = 5) -> List[Dict[str, Any]]:
        """Поиск дубликатов кода"""
        results = []
        files = self._get_code_files()
        code_fragments = defaultdict(list)
        
        for file in files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for i in range(len(lines) - min_length + 1):
                        fragment = '\n'.join(lines[i:i + min_length])
                        if fragment.strip():
                            code_fragments[fragment].append((file, i + 1))
            except Exception as e:
                print(f"Ошибка при чтении файла {file}: {str(e)}")

        for fragment, occurrences in code_fragments.items():
            if len(occurrences) > 1:
                results.append({
                    'fragment': fragment,
                    'occurrences': occurrences
                })

        return results

    def analyze_security(self, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Анализ безопасности кода"""
        results = []
        files = [file_path] if file_path else self._get_code_files()

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

        for file in files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for i, line in enumerate(lines, 1):
                        for issue_type, patterns in security_patterns.items():
                            for pattern in patterns:
                                if re.search(pattern, line):
                                    results.append({
                                        'file': file,
                                        'line': i,
                                        'issue_type': issue_type,
                                        'code': line.strip()
                                    })
            except Exception as e:
                print(f"Ошибка при анализе файла {file}: {str(e)}")

        return results

    def analyze_performance(self, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Анализ производительности кода"""
        results = []
        files = [file_path] if file_path else self._get_code_files()

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
                    
                    results.append({
                        'file': file,
                        'loops': loops,
                        'recursion': recursion,
                        'max_nesting': max_nesting
                    })
            except Exception as e:
                print(f"Ошибка при анализе файла {file}: {str(e)}")

        return results

    def _get_code_files(self) -> List[str]:
        """Получение списка файлов с кодом"""
        return [f for f in self.repository.get_files() if f.endswith(('.py', '.js', '.java', '.cpp', '.c', '.h'))] 