#!/usr/bin/env python3
"""
Simple Downloads Analyzer Test
"""

import os
from pathlib import Path

print("=== SIMPLE DOWNLOADS ANALYZER TEST ===")

downloads_path = Path(r"C:\Users\Admin\Downloads")
print(f"Downloads path: {downloads_path}")
print(f"Path exists: {downloads_path.exists()}")

if downloads_path.exists():
    files = list(downloads_path.iterdir())
    print(f"Total items in Downloads: {len(files)}")
    
    file_count = sum(1 for f in files if f.is_file())
    folder_count = sum(1 for f in files if f.is_dir())
    
    print(f"Files: {file_count}")
    print(f"Folders: {folder_count}")
    
    # Show first 10 items
    print("\nFirst 10 items:")
    for i, item in enumerate(files[:10]):
        print(f"  {i+1}. {item.name} ({'file' if item.is_file() else 'folder'})")
    
    print("\nBasic analysis completed!")
else:
    print("Downloads folder not found!")
