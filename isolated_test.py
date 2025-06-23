#!/usr/bin/env python3
"""
Isolated test for filename extraction - bypassing all CLI
"""

import re
import sys
from pathlib import Path

def extract_filename_from_query_test(query):
    """Standalone implementation of the filename extraction logic for testing."""
    if not query:
        return "project_s_output.txt"
    
    # Normalize query
    query = query.strip()
    
    # Pattern 1: Quoted filenames
    quoted_patterns = [
        r'"([^"]+\.[a-zA-Z0-9]+)"',  # "filename.ext"
        r"'([^']+\.[a-zA-Z0-9]+)'",  # 'filename.ext'
    ]
    
    for pattern in quoted_patterns:
        match = re.search(pattern, query)
        if match:
            filename = match.group(1)
            # Basic sanitization
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            return filename
    
    # Pattern 2: Files with common extensions
    extension_pattern = r'\b([a-zA-Z0-9_-]+\.[a-zA-Z0-9]+)\b'
    match = re.search(extension_pattern, query)
    if match:
        filename = match.group(1)
        # Basic sanitization
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        return filename
    
    # Pattern 3: Natural language patterns
    query_lower = query.lower()
    
    # Hungarian patterns
    hungarian_patterns = [
        (r'(?:írj|készíts|hozz létre|generálj).*?(?:egy|egyet)?\s*([a-zA-Z0-9_-]+)\s*(?:fájlt|file)', 'hu'),
        (r'([a-zA-Z0-9_-]+)\s*(?:fájlt|file).*?(?:írj|készíts|hozz létre|generálj)', 'hu'),
    ]
    
    # English patterns  
    english_patterns = [
        (r'(?:create|make|write|generate).*?(?:a|an)?\s*(?:file\s+(?:called|named)\s+)?([a-zA-Z0-9_-]+)', 'en'),
        (r'(?:file\s+(?:called|named)\s+)?([a-zA-Z0-9_-]+).*?(?:create|make|write|generate)', 'en'),
    ]
    
    all_patterns = hungarian_patterns + english_patterns
    
    for pattern, lang in all_patterns:
        match = re.search(pattern, query_lower)
        if match:
            base_name = match.group(1)
            
            # Determine extension based on content type or keywords
            if any(keyword in query_lower for keyword in ['html', 'web', 'webpage']):
                return f"{base_name}.html"
            elif any(keyword in query_lower for keyword in ['python', 'py', 'script']):
                return f"{base_name}.py"
            elif any(keyword in query_lower for keyword in ['json', 'config', 'configuration']):
                return f"{base_name}.json"
            elif any(keyword in query_lower for keyword in ['text', 'txt', 'note']):
                return f"{base_name}.txt"
            elif any(keyword in query_lower for keyword in ['css', 'style']):
                return f"{base_name}.css"
            elif any(keyword in query_lower for keyword in ['js', 'javascript']):
                return f"{base_name}.js"
            else:
                return f"{base_name}.txt"
    
    # Pattern 4: Content type mapping
    content_mappings = {
        'html': 'index.html',
        'python': 'main.py',
        'javascript': 'main.js',
        'css': 'styles.css',
        'json': 'config.json',
        'markdown': 'README.md',
        'text': 'document.txt'
    }
    
    for content_type, filename in content_mappings.items():
        if content_type in query_lower:
            return filename
    
    # Fallback
    return "project_s_output.txt"

def run_tests():
    """Run the filename extraction tests."""
    print("🔧 Testing filename extraction logic...")
    print("=" * 50)
    
    test_cases = [
        ("Create a file called hello.txt", "hello.txt"),
        ("Írj egy test.py fájlt", "test.py"),
        ("Make a 'config.json' file", "config.json"),
        ('Write "data.csv" file', "data.csv"),
        ("Create main.py python script", "main.py"),
        ("Generate HTML webpage", "index.html"),
        ("Make CSS styles", "styles.css"),
        ("Create JavaScript code", "main.js"),
        ("Write JSON configuration", "config.json"),
        ("General request without filename", "project_s_output.txt"),
        ("Hozz létre egy setup fájlt", "setup.txt"),
        ("Készíts readme dokumentumot", "readme.txt"),
    ]
    
    passed = 0
    failed = 0
    
    for i, (query, expected) in enumerate(test_cases):
        try:
            result = extract_filename_from_query_test(query)
            status = "✅ PASS" if result == expected else "❌ FAIL"
            print(f"Test {i+1:2d}: {status}")
            print(f"   Query: '{query}'")
            print(f"   Expected: '{expected}'")
            print(f"   Got:      '{result}'")
            print()
            
            if result == expected:
                passed += 1
            else:
                failed += 1
                
        except Exception as e:
            print(f"❌ ERROR in test {i+1}: {e}")
            failed += 1
            print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The filename extraction logic is working correctly.")
        return True
    else:
        print(f"⚠️  {failed} tests failed. The logic needs adjustments.")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
