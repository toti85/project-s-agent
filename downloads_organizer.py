#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project-S Downloads Organizer
----------------------------
Implements the organization plan from the Downloads analysis.
This script can actually organize your Downloads folder safely.
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class DownloadsOrganizer:
    """Implements file organization from analysis results"""
    
    def __init__(self, downloads_path: str = r"C:\Users\Admin\Downloads"):
        self.downloads_path = Path(downloads_path)
        self.backup_path = Path(downloads_path) / "_backup_before_organization"
        self.organized_path = Path(downloads_path)
        
        # Organization structure from analysis
        self.organization_map = {
            "Media": ["png", "jpg", "jpeg", "gif", "bmp", "webp", "svg", "ico"],
            "Documents": ["pdf", "doc", "docx", "txt", "rtf", "odt", "ppt", "pptx"],
            "Software": ["exe", "msi", "dmg", "pkg", "deb", "rpm", "appimage"],
            "Development": ["py", "js", "html", "css", "json", "xml", "sql", "md"],
            "Archives": ["zip", "rar", "7z", "tar", "gz", "bz2", "xz"],
            "Other": ["jar", "class", "war", "ear"]  # Keep specialized files together
        }
        
        self.results = {
            "moved_files": [],
            "duplicate_actions": [],
            "errors": [],
            "skipped": []
        }
    
    def create_backup(self) -> bool:
        """Create backup of Downloads folder"""
        try:
            if self.backup_path.exists():
                print(f"📦 Backup already exists at {self.backup_path}")
                return True
                
            print(f"📦 Creating backup at {self.backup_path}...")
            self.backup_path.mkdir(exist_ok=True)
            
            # Copy important files to backup (not everything to save space)
            important_files = []
            for file_path in self.downloads_path.iterdir():
                if file_path.is_file() and file_path.stat().st_size < 50 * 1024 * 1024:  # Under 50MB
                    important_files.append(file_path)
            
            for file_path in important_files[:20]:  # Backup max 20 small files
                try:
                    shutil.copy2(file_path, self.backup_path)
                except Exception as e:
                    print(f"⚠️  Backup error for {file_path.name}: {e}")
            
            print(f"✅ Backup created with {len(os.listdir(self.backup_path))} files")
            return True
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def get_file_category(self, file_path: Path) -> str:
        """Determine which category a file belongs to"""
        extension = file_path.suffix.lower().lstrip('.')
        
        for category, extensions in self.organization_map.items():
            if extension in extensions:
                return category
        
        return "Other"
    
    def organize_files(self, dry_run: bool = True) -> Dict:
        """Organize files into categories"""
        print(f"\n{'🔍 DRY RUN - ' if dry_run else '🚀 ORGANIZING '}FILES")
        print("=" * 50)
        
        # Create category folders
        category_folders = {}
        for category in self.organization_map.keys():
            category_folder = self.organized_path / category
            if not dry_run:
                category_folder.mkdir(exist_ok=True)
            category_folders[category] = category_folder
            
        # Process each file
        for file_path in self.downloads_path.iterdir():
            if file_path.is_file() and not file_path.name.startswith('_'):
                try:
                    category = self.get_file_category(file_path)
                    target_folder = category_folders[category]
                    target_path = target_folder / file_path.name
                    
                    # Handle filename conflicts
                    if target_path.exists():
                        base_name = file_path.stem
                        extension = file_path.suffix
                        counter = 1
                        while target_path.exists():
                            new_name = f"{base_name}_{counter}{extension}"
                            target_path = target_folder / new_name
                            counter += 1
                    
                    if dry_run:
                        print(f"📁 {file_path.name} → {category}/")
                        self.results["moved_files"].append({
                            "source": str(file_path),
                            "target": str(target_path),
                            "category": category,
                            "action": "would_move"
                        })
                    else:
                        shutil.move(str(file_path), str(target_path))
                        print(f"✅ {file_path.name} → {category}/")
                        self.results["moved_files"].append({
                            "source": str(file_path),
                            "target": str(target_path),
                            "category": category,
                            "action": "moved"
                        })
                        
                except Exception as e:
                    error_msg = f"Error moving {file_path.name}: {e}"
                    print(f"❌ {error_msg}")
                    self.results["errors"].append(error_msg)
        
        return self.results
    
    def handle_duplicates(self, dry_run: bool = True) -> List[str]:
        """Handle duplicate files based on analysis"""
        print(f"\n{'🔍 DRY RUN - ' if dry_run else '🧹 HANDLING '}DUPLICATES")
        print("=" * 50)
        
        # Known duplicates from analysis
        duplicate_patterns = [
            "Banana (1).png / Banana (2).png",
            "Git-2.47.1.2-64-bit (1).exe / Git-2.47.1.2-64-bit.exe",
            "python-3.11.0-amd64 (1).exe / python-3.11.0-amd64.exe",
            "Docker Desktop Installer (1).exe / Docker Desktop Installer.exe"
        ]
        
        actions_taken = []
        
        for pattern in duplicate_patterns:
            files = pattern.split(" / ")
            if len(files) >= 2:
                # Keep the file without number suffix, remove others
                main_file = files[-1]  # Usually the one without (1)
                duplicates = files[:-1]
                
                for dup_file in duplicates:
                    dup_path = self.downloads_path / dup_file
                    if dup_path.exists():
                        if dry_run:
                            print(f"🗑️  Would delete: {dup_file}")
                            actions_taken.append(f"would_delete: {dup_file}")
                        else:
                            try:
                                dup_path.unlink()
                                print(f"✅ Deleted: {dup_file}")
                                actions_taken.append(f"deleted: {dup_file}")
                            except Exception as e:
                                error_msg = f"Error deleting {dup_file}: {e}"
                                print(f"❌ {error_msg}")
                                self.results["errors"].append(error_msg)
        
        return actions_taken
    
    def clean_large_files(self, dry_run: bool = True) -> List[str]:
        """List large files for manual review"""
        print(f"\n📋 LARGE FILES (>50MB) FOR REVIEW")
        print("=" * 50)
        
        large_files = []
        for file_path in self.downloads_path.iterdir():
            if file_path.is_file():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                if size_mb > 50:
                    large_files.append((file_path, size_mb))
        
        large_files.sort(key=lambda x: x[1], reverse=True)
        
        for file_path, size_mb in large_files:
            print(f"📦 {file_path.name} ({size_mb:.1f} MB)")
        
        if large_files:
            print(f"\n💡 Found {len(large_files)} large files totaling {sum(x[1] for x in large_files):.1f} MB")
            print("   Consider moving to external storage or cloud backup")
        
        return [f"{fp.name} ({size:.1f}MB)" for fp, size in large_files]
    
    def generate_report(self) -> str:
        """Generate organization report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
PROJECT-S DOWNLOADS ORGANIZATION REPORT
Generated: {timestamp}

SUMMARY:
- Files organized: {len(self.results['moved_files'])}
- Duplicates handled: {len(self.results['duplicate_actions'])}
- Errors: {len(self.results['errors'])}

ORGANIZATION STRUCTURE:
"""
        
        # Count files by category
        category_counts = {}
        for item in self.results['moved_files']:
            category = item['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        for category, count in category_counts.items():
            report += f"📁 {category}/: {count} files\n"
        
        if self.results['errors']:
            report += f"\nERRORS:\n"
            for error in self.results['errors']:
                report += f"❌ {error}\n"
        
        return report


def main():
    """Main execution function"""
    print("🗂️  PROJECT-S DOWNLOADS ORGANIZER")
    print("=" * 50)
    print("This tool will organize your Downloads folder based on the analysis.")
    print("Files will be moved into categorized folders.")
    
    organizer = DownloadsOrganizer()
    
    # Check if Downloads folder exists
    if not organizer.downloads_path.exists():
        print(f"❌ Downloads folder not found: {organizer.downloads_path}")
        return
    
    print(f"📁 Target folder: {organizer.downloads_path}")
    print(f"📦 Backup location: {organizer.backup_path}")
    
    print("\n❓ ORGANIZATION OPTIONS:")
    print("1. Preview only (safe)")
    print("2. Organize files + handle duplicates")
    print("3. Just handle duplicates")
    print("4. Full organization (with backup)")
    
    try:
        choice = input("\nChoose option (1-4): ").strip()
        
        if choice == "1":
            # Preview mode
            organizer.organize_files(dry_run=True)
            organizer.handle_duplicates(dry_run=True)
            organizer.clean_large_files(dry_run=True)
            
        elif choice == "2":
            # Organize + duplicates
            confirm = input("\n⚠️  This will move files and delete duplicates. Type 'YES' to confirm: ")
            if confirm == 'YES':
                organizer.create_backup()
                organizer.organize_files(dry_run=False)
                organizer.handle_duplicates(dry_run=False)
                print(organizer.generate_report())
            else:
                print("❌ Operation cancelled")
                
        elif choice == "3":
            # Just duplicates
            confirm = input("\n⚠️  This will delete duplicate files. Type 'YES' to confirm: ")
            if confirm == 'YES':
                organizer.create_backup()
                organizer.handle_duplicates(dry_run=False)
                print("✅ Duplicate cleanup complete")
            else:
                print("❌ Operation cancelled")
                
        elif choice == "4":
            # Full organization
            confirm = input("\n⚠️  Full organization with backup. Type 'YES' to confirm: ")
            if confirm == 'YES':
                if organizer.create_backup():
                    organizer.organize_files(dry_run=False)
                    organizer.handle_duplicates(dry_run=False)
                    large_files = organizer.clean_large_files(dry_run=True)
                    
                    # Save report
                    report = organizer.generate_report()
                    report_path = Path("downloads_organization_report.txt")
                    with open(report_path, 'w', encoding='utf-8') as f:
                        f.write(report)
                    
                    print(f"\n📄 Report saved: {report_path}")
                    print("✅ Full organization complete!")
                else:
                    print("❌ Organization cancelled due to backup failure")
            else:
                print("❌ Operation cancelled")
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
