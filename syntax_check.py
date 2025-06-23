import ast

def check_syntax(file_path):
    """Check Python file syntax."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Parse the code - this will raise SyntaxError if there's an issue
        ast.parse(source_code)
        print(f"✅ {file_path} - No syntax errors found")
        return True
    except SyntaxError as e:
        print(f"❌ {file_path} - Syntax error at line {e.lineno}, col {e.offset}")
        print(f"   {e.text.strip()}")
        print(f"   {' ' * (e.offset - 1)}^")
        print(f"   {e}")
        return False
    except Exception as e:
        print(f"❌ {file_path} - Error: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python syntax_check.py <file_path>")
        sys.exit(1)
    
    success = check_syntax(sys.argv[1])
    sys.exit(0 if success else 1)
