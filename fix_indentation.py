#!/usr/bin/env python3
"""
Quick fix for indentation errors in core files
"""

import re
import os

def fix_indentation_in_file(file_path):
    """Fix common indentation errors in Python files"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix double indented methods/functions
    content = re.sub(r'\n(\s+)(\s+)(def |async def |class )', r'\n\1\3', content)
    
    # Fix wrong indentations after class definitions
    lines = content.split('\n')
    fixed_lines = []
    for i, line in enumerate(lines):
        if line.strip().endswith(':') and ('class ' in line or 'def ' in line):
            # Next non-empty line should be properly indented
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if next_line.strip() and not next_line.startswith('    '):
                    # If not properly indented, fix it
                    lines[i + 1] = '    ' + next_line.lstrip()
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed indentation in {file_path}")

# Fix the problematic files
files_to_fix = [
    'core/cognitive_core_langgraph.py',
    'core/cognitive_core.py',
]

for file_path in files_to_fix:
    if os.path.exists(file_path):
        fix_indentation_in_file(file_path)
    else:
        print(f"File not found: {file_path}")

print("Indentation fixes completed!")
