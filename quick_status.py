import os

print("=== PROJECT-S STATUS CHECK ===")
print(f"Directory: {os.getcwd()}")

# Check key files
files_to_check = [
    "main_multi_model.py",
    "WORKING_MINIMAL_VERSION.py", 
    "stable_website_analyzer.py",
    "fix_unicode_encoding.py"
]

print("\nCore files status:")
for filename in files_to_check:
    exists = os.path.exists(filename)
    status = "EXISTS" if exists else "MISSING"
    print(f"  {filename}: {status}")

print("\nTesting imports:")
try:
    import fix_unicode_encoding
    print("  fix_unicode_encoding: OK")
except Exception as e:
    print(f"  fix_unicode_encoding: ERROR - {e}")

try:
    import WORKING_MINIMAL_VERSION
    print("  WORKING_MINIMAL_VERSION: OK")
except Exception as e:
    print(f"  WORKING_MINIMAL_VERSION: ERROR - {e}")

print("\n=== STATUS CHECK COMPLETE ===")
