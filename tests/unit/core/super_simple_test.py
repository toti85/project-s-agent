import re

def test_extraction(query):
    if not query:
        return "project_s_output.txt"
    
    # Test quoted filenames
    quoted_match = re.search(r'"([^"]+\.[a-zA-Z0-9]+)"', query)
    if quoted_match:
        return quoted_match.group(1)
    
    # Test extensions
    ext_match = re.search(r'\b([a-zA-Z0-9_-]+\.[a-zA-Z0-9]+)\b', query)
    if ext_match:
        return ext_match.group(1)
    
    return "project_s_output.txt"

# Simple test
print("Starting simple test...")
tests = [
    ("Create hello.txt", "hello.txt"),
    ('Make "config.json"', "config.json"),
    ("General request", "project_s_output.txt")
]

for query, expected in tests:
    result = test_extraction(query)
    status = "PASS" if result == expected else "FAIL"
    print(f"{status}: '{query}' -> '{result}' (expected '{expected}')")

print("Test complete!")
