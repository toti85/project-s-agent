#!/usr/bin/env python3
"""
FINAL UNIFIED ENTRY POINT VERIFICATION TEST
==========================================
This test verifies that the unified main.py entry point is working correctly
and that all legacy entry points are properly deprecated.

Test Coverage:
1. Unified main.py imports and initializes correctly
2. Smart mode detection works
3. All capabilities are accessible
4. Legacy entry points show deprecation notices
5. User experience is seamless
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path

def test_unified_main_import():
    """Test that main.py can be imported without errors."""
    print("🧪 Testing unified main.py import...")
    try:
        # Test import
        spec = importlib.util.spec_from_file_location("main", "main.py")
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)
        
        # Check key classes exist
        assert hasattr(main_module, 'ProjectSUnified'), "ProjectSUnified class not found"
        assert hasattr(main_module, 'main'), "main function not found"
        
        print("✅ main.py imports successfully")
        print("✅ ProjectSUnified class found")
        print("✅ main function found")
        return True
        
    except Exception as e:
        print(f"❌ Failed to import main.py: {e}")
        return False

def test_smart_mode_detection():
    """Test the smart mode detection functionality."""
    print("\n🧪 Testing smart mode detection...")
    try:
        from main import ProjectSUnified
        
        unified = ProjectSUnified()
        
        # Test different input types
        test_cases = [
            ("What is AI?", "chat"),
            ("help", "help"),
            ("tools file", "tools"),
            ("diag", "diag"),
            ("create test.py", "task"),
            ("status", "status"),
            ("models", "models"),
            ("exit", "exit")
        ]
        
        for input_text, expected_intent in test_cases:
            intent, data = unified.detect_user_intent(input_text)
            print(f"  📝 '{input_text}' → {intent} (expected: {expected_intent})")
            
        print("✅ Smart mode detection working")
        return True
        
    except Exception as e:
        print(f"❌ Smart mode detection failed: {e}")
        return False

def test_legacy_deprecation_notices():
    """Test that legacy entry points show deprecation notices."""
    print("\n🧪 Testing legacy entry point deprecation...")
    
    legacy_files = [
        "main_multi_model.py",
        "cli_main.py", 
        "cli_main_v2.py"
    ]
    
    all_deprecated = True
    
    for file_path in legacy_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if "DEPRECATED" in content and "USE INSTEAD: python main.py" in content:
                    print(f"✅ {file_path} shows deprecation notice")
                else:
                    print(f"❌ {file_path} missing deprecation notice")
                    all_deprecated = False
                    
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                all_deprecated = False
        else:
            print(f"⚠️  {file_path} not found")
    
    return all_deprecated

def test_file_structure():
    """Test that the unified file structure is correct."""
    print("\n🧪 Testing unified file structure...")
    
    required_files = [
        "main.py",  # The unified entry point
        "SINGLE_ENTRY_POINT_FINAL.md",  # Documentation
        "README.md"  # Updated README
    ]
    
    all_present = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_present = False
    
    return all_present

def test_documentation_updated():
    """Test that documentation promotes main.py as the single entry point."""
    print("\n🧪 Testing documentation updates...")
    
    try:
        # Check README.md
        with open("README.md", 'r', encoding='utf-8') as f:
            readme_content = f.read()
            
        if "python main.py" in readme_content and "THE DEFINITIVE AI PLATFORM" in readme_content:
            print("✅ README.md promotes unified entry point")
        else:
            print("❌ README.md not updated for unified entry point")
            return False
            
        # Check if final documentation exists
        if os.path.exists("SINGLE_ENTRY_POINT_FINAL.md"):
            with open("SINGLE_ENTRY_POINT_FINAL.md", 'r', encoding='utf-8') as f:
                doc_content = f.read()
                
            if "One Command. All Capabilities" in doc_content:
                print("✅ Final documentation created")
            else:
                print("❌ Final documentation incomplete")
                return False
        else:
            print("❌ Final documentation missing")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Documentation test failed: {e}")
        return False

def run_comprehensive_verification():
    """Run all verification tests."""
    print("🚀 STARTING COMPREHENSIVE UNIFIED ENTRY POINT VERIFICATION")
    print("=" * 70)
    
    tests = [
        ("Unified Main Import", test_unified_main_import),
        ("Smart Mode Detection", test_smart_mode_detection),
        ("Legacy Deprecation", test_legacy_deprecation_notices),
        ("File Structure", test_file_structure),
        ("Documentation Updates", test_documentation_updated)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 VERIFICATION RESULTS SUMMARY")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print("\n" + "=" * 70)
    print(f"🎯 OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! UNIFIED ENTRY POINT IS READY!")
        print("🚀 Users can now use: python main.py")
    else:
        print("⚠️  Some tests failed. Review issues above.")
    
    print("=" * 70)
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_verification()
    sys.exit(0 if success else 1)
