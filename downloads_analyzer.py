#!/usr/bin/env python3
"""
Project-S Downloads Folder Analyzer
===================================
Részletes elemzés és szervezés a Downloads mappának:
1. Fájltípusok kategorizálása
2. Duplikátumok azonosítása  
3. Szervezési struktúra javaslata
4. Cleanup action plan
5. Implementáció opció

Használat:
    python downloads_analyzer.py

A script intelligens kategorizálást, duplikátum keresést és szervezési javaslatokat nyújt.
"""

import os
import sys
import asyncio
import logging
import hashlib
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
import mimetypes

# Project-S integration
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from integrations.multi_model_ai_client import multi_model_ai_client
from core.event_bus import event_bus
from core.error_handler import ErrorHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/downloads_analyzer.log', mode='w', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

class DownloadsAnalyzer:
    """
    Intelligens Downloads mappa elemző és szervezési rendszer.
    """
    
    def __init__(self, downloads_path: str = r"C:\Users\Admin\Downloads"):
        """Initialize analyzer with Downloads path."""
        self.downloads_path = Path(downloads_path)
        self.error_handler = ErrorHandler()
        
        # Analysis results
        self.file_categories = defaultdict(list)
        self.duplicates = defaultdict(list)
        self.file_stats = {}
        self.organization_plan = {}
        self.cleanup_actions = []
        
        # File type categories
        self.categories = {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico'],
            'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages'],
            'spreadsheets': ['.xls', '.xlsx', '.csv', '.ods', '.numbers'],
            'presentations': ['.ppt', '.pptx', '.odp', '.key'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'],
            'executables': ['.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm', '.appimage'],
            'code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.php', '.rb', '.go'],
            'data': ['.json', '.xml', '.sql', '.db', '.sqlite', '.yaml', '.yml'],
            'fonts': ['.ttf', '.otf', '.woff', '.woff2', '.eot'],
            'ebooks': ['.epub', '.mobi', '.azw', '.azw3', '.fb2'],
            'temporary': ['.tmp', '.temp', '.bak', '.~', '.crdownload', '.part'],
            'other': []
        }
        
        os.makedirs('logs', exist_ok=True)
        logger.info(f"Downloads Analyzer initialized for: {self.downloads_path}")
    
    def categorize_file(self, file_path: Path) -> str:
        """Categorize file by extension."""
        extension = file_path.suffix.lower()
        
        for category, extensions in self.categories.items():
            if extension in extensions:
                return category
        
        return 'other'
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash for duplicate detection."""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.warning(f"Could not hash file {file_path}: {e}")
            return ""
    
    def analyze_files(self):
        """Analyze all files in Downloads folder."""
        print(f"\\n🔍 Analyzing Downloads folder: {self.downloads_path}")
        print("=" * 60)
        
        if not self.downloads_path.exists():
            print(f"❌ ERROR: Downloads path does not exist: {self.downloads_path}")
            return
        
        file_hashes = {}
        total_size = 0
        file_count = 0
        
        # Scan all files
        for file_path in self.downloads_path.rglob('*'):
            if file_path.is_file():
                try:
                    file_count += 1
                    file_size = file_path.stat().st_size
                    total_size += file_size
                    
                    # Categorize
                    category = self.categorize_file(file_path)
                    
                    # File info
                    file_info = {
                        'path': file_path,
                        'size': file_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime),
                        'extension': file_path.suffix.lower(),
                        'mime_type': mimetypes.guess_type(str(file_path))[0] or 'unknown'
                    }
                    
                    self.file_categories[category].append(file_info)
                    
                    # Duplicate detection
                    if file_size > 0:  # Skip empty files
                        file_hash = self.calculate_file_hash(file_path)
                        if file_hash:
                            if file_hash in file_hashes:
                                # Found duplicate
                                if file_hash not in self.duplicates:
                                    self.duplicates[file_hash] = [file_hashes[file_hash]]
                                self.duplicates[file_hash].append(file_info)
                            else:
                                file_hashes[file_hash] = file_info
                    
                except Exception as e:
                    logger.warning(f"Error analyzing file {file_path}: {e}")
        
        # Store stats
        self.file_stats = {
            'total_files': file_count,
            'total_size': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'categories_count': len([cat for cat in self.file_categories if self.file_categories[cat]])
        }
        
        print(f"✅ Analysis complete!")
        print(f"   📁 Total files: {file_count}")
        print(f"   💾 Total size: {total_size / (1024 * 1024):.1f} MB")
        print(f"   📂 Categories found: {self.file_stats['categories_count']}")
    
    def display_categorization(self):
        """Display file categorization results."""
        print(f"\\n📂 FILE CATEGORIZATION")
        print("=" * 60)
        
        for category, files in self.file_categories.items():
            if files:
                total_size = sum(f['size'] for f in files)
                print(f"\\n{category.upper()}: {len(files)} files ({total_size / (1024 * 1024):.1f} MB)")
                
                # Show largest files in category
                sorted_files = sorted(files, key=lambda x: x['size'], reverse=True)[:5]
                for file_info in sorted_files:
                    size_mb = file_info['size'] / (1024 * 1024)
                    print(f"  • {file_info['path'].name} ({size_mb:.1f} MB)")
    
    def display_duplicates(self):
        """Display duplicate files found."""
        print(f"\\n🔄 DUPLICATE FILES ANALYSIS")
        print("=" * 60)
        
        if not self.duplicates:
            print("✅ No duplicate files found!")
            return
        
        total_duplicate_size = 0
        duplicate_groups = 0
        
        for file_hash, files in self.duplicates.items():
            duplicate_groups += 1
            file_size = files[0]['size']
            wasted_space = file_size * (len(files) - 1)
            total_duplicate_size += wasted_space
            
            print(f"\\nDuplicate Group #{duplicate_groups} ({file_size / (1024 * 1024):.1f} MB each):")
            for file_info in files:
                age_days = (datetime.now() - file_info['modified']).days
                print(f"  • {file_info['path']} (modified {age_days} days ago)")
        
        print(f"\\n📊 DUPLICATE SUMMARY:")
        print(f"   🔄 Duplicate groups: {duplicate_groups}")
        print(f"   💾 Wasted space: {total_duplicate_size / (1024 * 1024):.1f} MB")
    
    async def generate_organization_plan(self):
        """Generate intelligent organization plan using AI."""
        print(f"\\n🤖 GENERATING ORGANIZATION PLAN WITH AI")
        print("=" * 60)
        
        # Prepare analysis data for AI
        analysis_summary = {
            'total_files': self.file_stats['total_files'],
            'total_size_mb': self.file_stats['total_size_mb'],
            'categories': {}
        }
        
        for category, files in self.file_categories.items():
            if files:
                analysis_summary['categories'][category] = {
                    'count': len(files),
                    'size_mb': sum(f['size'] for f in files) / (1024 * 1024),
                    'extensions': list(set(f['extension'] for f in files))
                }
        
        # AI prompt for organization suggestions
        ai_prompt = f'''
Elemezd ezt a Downloads mappa struktúrát és javasolj intelligens szervezési megoldást:

JELENLEGI ÁLLAPOT:
- Összes fájl: {analysis_summary['total_files']}
- Összes méret: {analysis_summary['total_size_mb']:.1f} MB
- Kategóriák: {list(analysis_summary['categories'].keys())}

RÉSZLETES KATEGÓRIA ELEMZÉS:
{json.dumps(analysis_summary['categories'], indent=2, ensure_ascii=False)}

FELADAT:
1. Javasolj logikus mappa struktúrát
2. Adj konkrét mappanéveket és elválasztási szabályokat
3. Javasold a duplikátumok kezelését
4. Azonosítsd a törölhető/archiválható fájlokat
5. Adj priority sorrendet a szervezési lépésekhez

FORMÁTUM:
- Konkrét mappa nevek
- Szabályok minden kategóriához
- Cleanup prioritások
- Megőrzési javaslatok
'''
        
        try:
            ai_response = await multi_model_ai_client.generate_response(
                prompt=ai_prompt,
                task_type="tervezés",
                temperature=0.7
            )
            
            print("🤖 AI Organization Recommendations:")
            print("-" * 40)
            print(ai_response)
            
            return ai_response
            
        except Exception as e:
            logger.error(f"AI organization plan generation failed: {e}")
            print(f"❌ AI plan generation failed: {e}")
            return self._generate_basic_plan()
    
    def _generate_basic_plan(self):
        """Generate basic organization plan without AI."""
        print("📋 BASIC ORGANIZATION PLAN:")
        print("-" * 40)
        
        plan = {
            'Media/': ['images', 'videos', 'audio'],
            'Documents/': ['documents', 'spreadsheets', 'presentations', 'ebooks'],
            'Software/': ['executables', 'archives'],
            'Development/': ['code', 'data'],
            'Fonts/': ['fonts'],
            'Temporary/': ['temporary'],
            'Misc/': ['other']
        }
        
        for folder, categories in plan.items():
            category_files = []
            for cat in categories:
                category_files.extend(self.file_categories.get(cat, []))
            
            if category_files:
                total_size = sum(f['size'] for f in category_files) / (1024 * 1024)
                print(f"• {folder} ({len(category_files)} files, {total_size:.1f} MB)")
        
        return plan
    
    def generate_cleanup_actions(self):
        """Generate specific cleanup actions."""
        print(f"\\n🧹 CLEANUP ACTION PLAN")
        print("=" * 60)
        
        actions = []
        
        # 1. Duplicate removal
        if self.duplicates:
            duplicate_space = 0
            for files in self.duplicates.values():
                duplicate_space += files[0]['size'] * (len(files) - 1)
            
            actions.append({
                'action': 'Remove duplicate files',
                'description': f'Delete {len(self.duplicates)} duplicate groups',
                'space_saved_mb': duplicate_space / (1024 * 1024),
                'priority': 'HIGH',
                'safe': True
            })
        
        # 2. Temporary files cleanup
        temp_files = self.file_categories.get('temporary', [])
        if temp_files:
            temp_size = sum(f['size'] for f in temp_files)
            actions.append({
                'action': 'Remove temporary files',
                'description': f'Delete {len(temp_files)} temporary files',
                'space_saved_mb': temp_size / (1024 * 1024),
                'priority': 'HIGH',
                'safe': True
            })
        
        # 3. Large file review
        all_files = []
        for files in self.file_categories.values():
            all_files.extend(files)
        
        large_files = [f for f in all_files if f['size'] > 100 * 1024 * 1024]  # >100MB
        if large_files:
            actions.append({
                'action': 'Review large files',
                'description': f'Review {len(large_files)} files >100MB',
                'space_saved_mb': 0,  # Manual review needed
                'priority': 'MEDIUM',
                'safe': False
            })
        
        # 4. Old files archival
        old_files = []
        cutoff_date = datetime.now() - timedelta(days=180)  # 6 months
        for files in self.file_categories.values():
            old_files.extend([f for f in files if f['modified'] < cutoff_date])
        
        if old_files:
            old_size = sum(f['size'] for f in old_files)
            actions.append({
                'action': 'Archive old files',
                'description': f'Archive {len(old_files)} files older than 6 months',
                'space_saved_mb': old_size / (1024 * 1024),
                'priority': 'LOW',
                'safe': False
            })
        
        self.cleanup_actions = actions
        
        # Display actions
        for i, action in enumerate(actions, 1):
            print(f"\\n{i}. {action['action']} [{action['priority']} PRIORITY]")
            print(f"   📝 {action['description']}")
            if action['space_saved_mb'] > 0:
                print(f"   💾 Space saved: {action['space_saved_mb']:.1f} MB")
            print(f"   🛡️  Safe: {'Yes' if action['safe'] else 'Requires review'}")
    
    async def implement_cleanup(self, confirm: bool = False):
        """Implement cleanup actions if approved."""
        if not confirm:
            print(f"\\n⚠️  IMPLEMENTATION PREVIEW")
            print("=" * 60)
            print("This would perform the following actions:")
            
            for action in self.cleanup_actions:
                if action['safe']:
                    print(f"✅ {action['action']}")
                else:
                    print(f"⚠️  {action['action']} (requires manual review)")
            
            return False
        
        print(f"\\n🚀 IMPLEMENTING CLEANUP ACTIONS")
        print("=" * 60)
        
        # Create backup folder
        backup_folder = self.downloads_path / "_ProjectS_Backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder.mkdir(parents=True, exist_ok=True)
        
        implemented = 0
        
        try:
            # 1. Handle duplicates
            for file_hash, files in self.duplicates.items():
                if len(files) > 1:
                    # Keep the newest file, backup others
                    newest = max(files, key=lambda x: x['modified'])
                    for file_info in files:
                        if file_info != newest:
                            backup_path = backup_folder / "duplicates" / file_info['path'].name
                            backup_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(file_info['path']), str(backup_path))
                            implemented += 1
                            print(f"📦 Moved duplicate: {file_info['path'].name}")
            
            # 2. Remove temporary files
            for file_info in self.file_categories.get('temporary', []):
                try:
                    file_info['path'].unlink()
                    implemented += 1
                    print(f"🗑️  Deleted temp file: {file_info['path'].name}")
                except Exception as e:
                    logger.warning(f"Could not delete {file_info['path']}: {e}")
            
            print(f"\\n✅ Implementation complete!")
            print(f"   📁 Actions performed: {implemented}")
            print(f"   📦 Backup created: {backup_folder}")
            
            return True
            
        except Exception as e:
            logger.error(f"Implementation error: {e}")
            print(f"❌ Implementation failed: {e}")
            return False

async def main():
    """Main function to run Downloads analysis."""
    print("\\n" + "=" * 60)
    print("🗂️  PROJECT-S DOWNLOADS FOLDER ANALYZER")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = DownloadsAnalyzer()
    
    # Step 1: Analyze files
    analyzer.analyze_files()
    
    # Step 2: Display categorization
    analyzer.display_categorization()
    
    # Step 3: Show duplicates
    analyzer.display_duplicates()
    
    # Step 4: Generate AI organization plan
    ai_plan = await analyzer.generate_organization_plan()
    
    # Step 5: Generate cleanup actions
    analyzer.generate_cleanup_actions()
    
    # Step 6: Ask for implementation
    print(f"\\n❓ IMPLEMENTATION OPTIONS")
    print("=" * 60)
    print("1. Preview only (safe)")
    print("2. Implement safe actions (duplicates + temp files)")
    print("3. Full implementation (with manual review steps)")
    print("4. Generate detailed report only")
    
    try:
        choice = input("\\nChoose action (1-4): ").strip()
        
        if choice == "1":
            await analyzer.implement_cleanup(confirm=False)
        elif choice == "2":
            print("\\n⚠️  Ready to implement SAFE actions only.")
            confirm = input("Type 'YES' to proceed: ").strip()
            if confirm == 'YES':
                await analyzer.implement_cleanup(confirm=True)
            else:
                print("❌ Implementation cancelled.")
        elif choice == "3":
            print("\\n⚠️  Full implementation includes manual review steps.")
            print("This option would create organization folders and move files.")
            print("📝 This feature is available for full implementation.")
        elif choice == "4":
            # Generate JSON report
            report_path = Path("downloads_analysis_report.json")
            report_data = {
                'analysis_date': datetime.now().isoformat(),
                'file_stats': analyzer.file_stats,
                'categories': {cat: len(files) for cat, files in analyzer.file_categories.items() if files},
                'duplicates_count': len(analyzer.duplicates),
                'cleanup_actions': analyzer.cleanup_actions,
                'ai_recommendations': ai_plan if isinstance(ai_plan, str) else str(ai_plan)
            }
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            print(f"\\n📄 Detailed report saved: {report_path}")
        else:
            print("❌ Invalid choice.")
    
    except KeyboardInterrupt:
        print("\\n\\n❌ Analysis cancelled by user.")
    except Exception as e:
        print(f"\\n❌ Error: {e}")
    
    print(f"\\n" + "=" * 60)
    print("🏁 DOWNLOADS ANALYSIS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
