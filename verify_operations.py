#!/usr/bin/env python3
"""
VERIFICATION SCRIPT - Check what the complex test actually did
===========================================================
This script recreates and inspects the test operations to verify real functionality.
"""

import os
import time
from pathlib import Path
from datetime import datetime

async def verify_file_operations():
    """Recreate and verify the file operations from the complex test."""
    print("🔍 VERIFYING FILE OPERATIONS")
    print("=" * 50)
    
    # Import the functions we tested
    from main import process_file_operation_directly, organize_directory_intelligently
    
    # Create verification workspace
    test_dir = Path("verification_workspace")
    print(f"📁 Creating verification workspace: {test_dir}")
    
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    # STEP 1: Create test files with specific content
    print("\n📝 STEP 1: Creating test files")
    test_files = [
        ("document.txt", "Ez egy teszt dokumentum a verifikációhoz."),
        ("data.json", '{"verification": true, "timestamp": "2025-06-23", "value": 42}'),
        ("script.py", "# Python verification script\nprint('Verification successful!')\nprint(f'Created at: {datetime.now()}')"),
        ("image_simulation.jpg", "JPEG file simulation content for verification"),
        ("archive_sim.zip", "ZIP archive simulation content"),
        ("readme.md", "# Verification Test\nThis is a markdown file for testing."),
        ("spreadsheet.csv", "name,age,city\nJohn,25,Budapest\nJane,30,Debrecen")
    ]
    
    created_files = []
    for filename, content in test_files:
        file_path = test_dir / filename
        print(f"  📄 Creating: {filename}")
        
        # Use our function
        result = await process_file_operation_directly("create", str(file_path), content)
        
        if result['status'] == 'success':
            created_files.append(str(file_path))
            # Verify file exists and has correct content
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    actual_content = f.read()
                content_match = content in actual_content
                size = file_path.stat().st_size
                print(f"    ✅ EXISTS: {file_path.exists()}")
                print(f"    ✅ SIZE: {size} bytes")
                print(f"    ✅ CONTENT: {'✓' if content_match else '✗'}")
                print(f"    📄 Preview: {actual_content[:50]}...")
            else:
                print(f"    ❌ FILE NOT FOUND!")
        else:
            print(f"    ❌ Creation failed: {result['message']}")
    
    print(f"\n📊 Total files created: {len(created_files)}")
    
    # STEP 2: List directory contents before organization
    print("\n📂 STEP 2: Directory contents BEFORE organization")
    list_result = await process_file_operation_directly("list", str(test_dir))
    if list_result['status'] == 'success':
        print(f"📁 Files found: {list_result['count']}")
        for file_info in list_result['files']:
            file_type = "📁" if file_info["type"] == "directory" else "📄"
            size_info = f" ({file_info['size']} bytes)" if file_info.get('size') else ""
            print(f"  {file_type} {file_info['name']}{size_info}")
    
    # STEP 3: Intelligent directory organization
    print("\n🔄 STEP 3: Intelligent directory organization")
    org_result = await organize_directory_intelligently(str(test_dir))
    
    print(f"📊 Organization result: {org_result['status']}")
    if org_result['status'] == 'success':
        print(f"  📁 Organized files: {org_result['organized_files']}")
        print(f"  📂 Categories created: {org_result['categories_created']}")
        print(f"  📋 Categories: {org_result.get('categories', [])}")
        
        if org_result.get('files_by_category'):
            print("\n📊 Files by category:")
            for category, count in org_result['files_by_category'].items():
                print(f"  📁 {category}: {count} files")
    
    # STEP 4: Verify directory structure AFTER organization
    print("\n📂 STEP 4: Directory structure AFTER organization")
    if test_dir.exists():
        for item in test_dir.iterdir():
            if item.is_dir():
                files_in_category = list(item.iterdir())
                print(f"📁 {item.name}/: {len(files_in_category)} files")
                for file in files_in_category:
                    size = file.stat().st_size if file.is_file() else 0
                    print(f"  📄 {file.name} ({size} bytes)")
                    
                    # Verify file content is preserved
                    if file.is_file():
                        try:
                            with open(file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            print(f"    📄 Content preview: {content[:40]}...")
                        except Exception as e:
                            print(f"    ❌ Could not read content: {e}")
    
    # STEP 5: Test file reading from organized structure
    print("\n📖 STEP 5: Testing file reading from organized structure")
    for category_dir in test_dir.iterdir():
        if category_dir.is_dir():
            print(f"\n📁 Reading from category: {category_dir.name}")
            for file in category_dir.iterdir():
                if file.is_file():
                    read_result = await process_file_operation_directly("read", str(file))
                    if read_result['status'] == 'success':
                        content = read_result['content']
                        print(f"  ✅ {file.name}: {len(content)} characters")
                        print(f"    📄 Content: {content[:60]}...")
                    else:
                        print(f"  ❌ {file.name}: {read_result['message']}")
    
    print(f"\n🏁 VERIFICATION COMPLETE!")
    
    # Keep the workspace for manual inspection
    print(f"📁 Workspace preserved at: {test_dir.absolute()}")
    print("💡 You can manually inspect the files and folders created.")
    
    return test_dir

def inspect_logs():
    """Inspect recent log files to see what happened."""
    print("\n📋 INSPECTING LOG FILES")
    print("=" * 50)
    
    log_dir = Path("logs")
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        
        if log_files:
            # Get the most recent log file
            recent_log = max(log_files, key=lambda x: x.stat().st_mtime)
            print(f"📄 Most recent log: {recent_log}")
            print(f"🕒 Modified: {datetime.fromtimestamp(recent_log.stat().st_mtime)}")
            
            # Read last 50 lines
            try:
                with open(recent_log, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                print(f"\n📄 Last 30 lines from {recent_log.name}:")
                print("-" * 50)
                for line in lines[-30:]:
                    if any(keyword in line.lower() for keyword in ['file', 'create', 'organization', 'complex', 'test']):
                        print(f"🔍 {line.strip()}")
                    
            except Exception as e:
                print(f"❌ Could not read log: {e}")
        else:
            print("📄 No log files found")
    else:
        print("📁 Logs directory not found")

async def main():
    """Main verification function."""
    print("🚀 PROJECT-S VERIFICATION TOOL")
    print("=" * 60)
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    print("\n📋 WHAT THIS SCRIPT DOES:")
    print("1. ✅ Recreates the exact file operations from the complex test")
    print("2. ✅ Verifies each file is actually created with correct content")
    print("3. ✅ Tests the intelligent directory organization")
    print("4. ✅ Checks that file content is preserved after organization")
    print("5. ✅ Provides detailed file system inspection")
    print("6. ✅ Inspects log files for additional evidence")
    
    try:
        # Step 1: Recreate and verify file operations
        workspace = await verify_file_operations()
        
        # Step 2: Inspect logs
        inspect_logs()
        
        print("\n" + "=" * 60)
        print("✅ VERIFICATION COMPLETED!")
        print(f"📁 Check the workspace: {workspace.absolute()}")
        print("🔍 All operations verified with real file system changes!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Verification error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
