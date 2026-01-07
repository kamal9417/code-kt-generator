import ast
from pathlib import Path
from typing import Dict, List

def analyze_python_file(file_path: Path) -> Dict:
    """Extract classes, functions, imports from Python file"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return None
    
    analysis = {
        'file_path': str(file_path),
        'file_name': file_path.name,
        'classes': [],
        'functions': [],
        'imports': [],
        'complexity': 0
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_info = {
                'name': node.name,
                'docstring': ast.get_docstring(node),
                'methods': [],
                'line_number': node.lineno
            }
            
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    class_info['methods'].append({
                        'name': item.name,
                        'docstring': ast.get_docstring(item),
                        'args': [arg.arg for arg in item.args.args]
                    })
            
            analysis['classes'].append(class_info)
        
        elif isinstance(node, ast.FunctionDef):
            # Only top-level functions
            if node.col_offset == 0:
                func_info = {
                    'name': node.name,
                    'docstring': ast.get_docstring(node),
                    'args': [arg.arg for arg in node.args.args],
                    'line_number': node.lineno,
                    'returns': ast.unparse(node.returns) if node.returns else None
                }
                analysis['functions'].append(func_info)
        
        elif isinstance(node, ast.Import):
            for alias in node.names:
                analysis['imports'].append(alias.name)
        
        elif isinstance(node, ast.ImportFrom):
            analysis['imports'].append(node.module)
    
    # Calculate basic complexity
    analysis['complexity'] = len(analysis['classes']) + len(analysis['functions'])
    
    return analysis