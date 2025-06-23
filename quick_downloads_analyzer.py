#!/usr/bin/env python3
"""
Project-S Downloads Analyzer - Quick Version
"""

import os
from pathlib import Path
from collections import defaultdict
import hashlib
from datetime import datetime

def analyze_downloads():
    downloads_path = Path(r"C:\Users\Admin\Downloads")
    print("🗂️  PROJECT-S DOWNLOADS FOLDER ANALYSIS")
    print("=" * 50)
    
    if not downloads_path.exists():
        print("❌ Downloads folder not found!")
        return
    
    print(f"📁 Analyzing: {downloads_path}")
    
    # File categories
    categories = {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico'],
        'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
        'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
        'spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
        'presentations': ['.ppt', '.pptx', '.odp'],
        'archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'executables': ['.exe', '.msi', '.dmg', '.pkg', '.deb'],
        'code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.php'],
        'temporary': ['.tmp', '.temp', '.bak', '.crdownload', '.part'],
    }
    
    file_categories = defaultdict(list)
    total_size = 0
    file_count = 0
    file_sizes = {}  # For duplicate detection
    
    # Analyze files
    for item in downloads_path.iterdir():
        if item.is_file():
            try:
                file_count += 1
                size = item.stat().st_size
                total_size += size
                ext = item.suffix.lower()
                modified = datetime.fromtimestamp(item.stat().st_mtime)
                
                file_info = {
                    'name': item.name,
                    'size': size,
                    'ext': ext,
                    'modified': modified,
                    'path': str(item)
                }
                
                # Categorize
                categorized = False
                for category, extensions in categories.items():
                    if ext in extensions:
                        file_categories[category].append(file_info)
                        categorized = True
                        break
                
                if not categorized:
                    file_categories['other'].append(file_info)
                
                # Track for duplicates (by size)
                if size in file_sizes:
                    file_sizes[size].append(file_info)
                else:
                    file_sizes[size] = [file_info]
                    
            except Exception as e:
                print(f"⚠️  Error analyzing {item.name}: {e}")
    
    # Results
    print(f"✅ Analysis complete!")
    print(f"📊 Total files: {file_count}")
    print(f"💾 Total size: {total_size / (1024*1024):.1f} MB")
    print()
    
    print("📂 CATEGORIZATION RESULTS:")
    print("-" * 40)
    
    for category, files in file_categories.items():
        if files:
            cat_size = sum(f['size'] for f in files)
            print(f"{category.upper()}: {len(files)} files ({cat_size / (1024*1024):.1f} MB)")
            
            # Show top 3 largest files
            sorted_files = sorted(files, key=lambda x: x['size'], reverse=True)[:3]
            for f in sorted_files:
                size_mb = f['size'] / (1024*1024)
                print(f"  • {f['name']} ({size_mb:.1f} MB)")
            print()
    
    # Duplicate detection by size
    print("🔄 POTENTIAL DUPLICATES (same size):")
    print("-" * 40)
    
    duplicates_found = 0
    for size, files in file_sizes.items():
        if len(files) > 1 and size > 0:  # Multiple files with same size
            duplicates_found += 1
            size_mb = size / (1024*1024)
            print(f"Group {duplicates_found} ({size_mb:.1f} MB each):")
            for f in files:
                print(f"  • {f['name']}")
            print()
    
    if duplicates_found == 0:
        print("✅ No obvious duplicates found (by file size)")
    
    # Organization suggestions
    print("🏗️  ORGANIZATION SUGGESTIONS:")
    print("-" * 40)
    
    suggestions = {
        "Media/": ['images', 'videos', 'audio'],
        "Documents/": ['documents', 'spreadsheets', 'presentations'],
        "Software/": ['executables', 'archives'],
        "Development/": ['code'],
        "Cleanup/": ['temporary']
    }
    
    for folder, cats in suggestions.items():
        total_files = sum(len(file_categories[cat]) for cat in cats)
        total_size_mb = sum(sum(f['size'] for f in file_categories[cat]) for cat in cats) / (1024*1024)
        if total_files > 0:
            print(f"📁 {folder} → {total_files} files ({total_size_mb:.1f} MB)")
    
    # Cleanup recommendations
    print("\n🧹 CLEANUP RECOMMENDATIONS:")
    print("-" * 40)
    
    temp_files = file_categories.get('temporary', [])
    if temp_files:
        temp_size = sum(f['size'] for f in temp_files) / (1024*1024)
        print(f"🗑️  Remove {len(temp_files)} temporary files ({temp_size:.1f} MB)")
    
    # Large files (>50MB)
    large_files = []
    for files in file_categories.values():
        large_files.extend([f for f in files if f['size'] > 50 * 1024 * 1024])
    
    if large_files:
        large_size = sum(f['size'] for f in large_files) / (1024*1024)
        print(f"📋 Review {len(large_files)} large files (>50MB, total {large_size:.1f} MB)")
    
    # Old files (>6 months)
    from datetime import timedelta
    cutoff = datetime.now() - timedelta(days=180)
    old_files = []
    for files in file_categories.values():
        old_files.extend([f for f in files if f['modified'] < cutoff])
    
    if old_files:
        old_size = sum(f['size'] for f in old_files) / (1024*1024)
        print(f"📦 Archive {len(old_files)} old files (>6 months, {old_size:.1f} MB)")
    
    print("\n" + "=" * 50)
    print("🎯 SUMMARY:")
    print(f"• Found {file_count} files in {len([c for c in file_categories if file_categories[c]])} categories")
    print(f"• Total size: {total_size / (1024*1024):.1f} MB")
    print(f"• Potential duplicates: {duplicates_found} groups")
    print(f"• Cleanup opportunities identified")
    print("=" * 50)

if __name__ == "__main__":
    analyze_downloads()
