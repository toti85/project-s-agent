"""
Simple test script to verify Phase 2 Semantic Similarity Engine implementation.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

async def test_phase2_implementation():
    """Test Phase 2 semantic features."""
    print("🚀 PROJECT-S Phase 2 Semantic Similarity Engine Test")
    print("=" * 60)
    
    try:
        # Import the enhanced intelligence system
        from core.intelligence_engine import intelligence_engine
        from core.semantic_engine import semantic_engine
        
        print("✅ Successfully imported intelligence and semantic engines")
        
        # Test cases for comprehensive evaluation
        test_cases = [
            # Hungarian commands
            ("hozz létre egy új fájlt", "FILE_OPERATION", "create"),
            ("mutasd meg a tartalom", "FILE_OPERATION", "read"),
            ("listázd ki a fájlokat", "FILE_OPERATION", "list"),
            ("rendszerezd a mappát", "DIRECTORY_ORGANIZATION", "organize"),
            ("futtasd le a parancsot", "SHELL_COMMAND", "execute"),
            
            # English commands
            ("create a new document", "FILE_OPERATION", "create"),
            ("show the content", "FILE_OPERATION", "read"),
            ("list all files", "FILE_OPERATION", "list"),
            ("organize the folder", "DIRECTORY_ORGANIZATION", "organize"),
            ("run the command", "SHELL_COMMAND", "execute"),
            
            # Cross-language/mixed commands
            ("create egy fájlt", "FILE_OPERATION", "create"),
            ("mutasd the content", "FILE_OPERATION", "read"),
            ("organize a mappát", "DIRECTORY_ORGANIZATION", "organize"),
            
            # Synonym variations
            ("make a file", "FILE_OPERATION", "create"),
            ("display content", "FILE_OPERATION", "read"),
            ("sort the directory", "DIRECTORY_ORGANIZATION", "organize"),
        ]
        
        print(f"\n🧪 Testing {len(test_cases)} command variations...")
        print("-" * 60)
        
        passed_tests = 0
        total_tests = len(test_cases)
        
        for i, (command, expected_intent, expected_operation) in enumerate(test_cases, 1):
            try:
                # Analyze the command
                result = await intelligence_engine.analyze_intent_with_confidence(command)
                
                # Check results
                intent_correct = result.intent_type == expected_intent
                operation_correct = result.operation == expected_operation
                has_semantic_data = bool(result.semantic_details)
                confidence_good = result.confidence >= 0.5
                
                test_passed = intent_correct and operation_correct and confidence_good
                
                if test_passed:
                    passed_tests += 1
                    status = "✅ PASS"
                else:
                    status = "❌ FAIL"
                
                print(f"{status} Test {i:2d}: '{command}'")
                print(f"         → {result.intent_type}.{result.operation}")
                print(f"         → Confidence: {result.confidence:.3f}")
                print(f"         → Semantic: {result.semantic_confidence:.3f}")
                print(f"         → Language: {result.language_detected}")
                
                if has_semantic_data and result.semantic_details.get('semantic_available'):
                    semantic_matches = result.semantic_details.get('semantic_matches', 0)
                    print(f"         → Semantic matches: {semantic_matches}")
                
                print()
                
            except Exception as e:
                print(f"❌ FAIL Test {i:2d}: '{command}' - Error: {e}")
                print()
        
        # Summary
        success_rate = (passed_tests / total_tests) * 100
        print("=" * 60)
        print("📊 PHASE 2 TEST RESULTS")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Test semantic engine statistics
        print("\n🔍 SEMANTIC ENGINE STATISTICS")
        print("-" * 30)
        stats = semantic_engine.get_semantic_statistics()
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        # Overall assessment
        if success_rate >= 90:
            print("\n🎉 EXCELLENT: Phase 2 implementation is working excellently!")
        elif success_rate >= 75:
            print("\n✅ GOOD: Phase 2 implementation is working well!")
        elif success_rate >= 50:
            print("\n⚠️ FAIR: Phase 2 implementation needs some improvements.")
        else:
            print("\n❌ POOR: Phase 2 implementation needs significant fixes.")
        
        return success_rate >= 75
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Please ensure all required modules are installed.")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_phase2_implementation())
    exit(0 if success else 1)
