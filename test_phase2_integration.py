"""
PROJECT-S Phase 2 Integration Test
=====================================
Test the enhanced intelligence engine in a real PROJECT-S environment.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

# Import the enhanced intelligence system
try:
    from core.intelligence_engine import intelligence_engine
    from main_multi_model import intelligent_command_parser
    ENHANCED_AVAILABLE = True
except ImportError as e:
    print(f"❌ Enhanced intelligence system not available: {e}")
    ENHANCED_AVAILABLE = False

async def test_real_commands():
    """Test real commands with the enhanced intelligence system."""
    if not ENHANCED_AVAILABLE:
        print("❌ Cannot run integration test - enhanced system not available")
        return
    
    print("🚀 PROJECT-S Phase 2 Semantic Intelligence Integration Test")
    print("=" * 60)
    print("Testing real commands with confidence scoring and semantic enhancement...\n")
    
    # Test commands as requested
    test_commands = [
        "hozz létre teszt.txt fájlt",
        "create document.txt", 
        "létrehz typo.txt",  # This has a typo to test fuzzy matching
        "rendszerezd a mappát",
        "organize the folder",
        "mutasd meg a fájlt",
        "show file content",
        "listázd ki a dokumentumokat"
    ]
    
    for i, command in enumerate(test_commands, 1):
        print(f"🔍 Test {i}: '{command}'")
        print("-" * 40)
        
        try:
            # Use the intelligent command parser (enhanced version)
            result = await intelligent_command_parser(command)
            
            # Extract key information
            intent_type = result.get('type', 'Unknown')
            operation = result.get('operation', 'unknown')
            confidence = result.get('confidence', 0.0)
            confidence_level = result.get('confidence_level', 'Unknown')
            
            # Show main results
            print(f"🎯 Intent: {intent_type}")
            print(f"🔧 Operation: {operation}")
            print(f"📊 Confidence: {confidence:.1%} ({confidence_level})")
            
            # Show semantic information if available
            if 'semantic_details' in result and result['semantic_details']:
                semantic_info = result['semantic_details']
                if semantic_info.get('semantic_available', False):
                    print(f"🧠 Semantic Available: Yes")
                    if 'top_match' in semantic_info and semantic_info['top_match']:
                        top_match = semantic_info['top_match']
                        print(f"🔍 Top Semantic Match: '{top_match.get('command', 'N/A')}' (similarity: {top_match.get('similarity', 0.0):.3f})")
                    print(f"🌐 Language Detected: {semantic_info.get('language_detected', 'unknown')}")
                    print(f"⚡ Semantic Boost: {semantic_info.get('semantic_boost', 0.0):.3f}")
                else:
                    print(f"🧠 Semantic Available: No")
            
            # Show parameters
            if 'parameters' in result and result['parameters']:
                print(f"⚙️ Parameters: {result['parameters']}")
            
            # Show confidence-based recommendation
            if result.get('requires_confirmation'):
                print("🤔 Recommendation: Request user confirmation")
            elif result.get('suggest_alternatives'):
                print("💡 Recommendation: Show alternatives to user")
            elif result.get('fallback_to_ai'):
                print("🤖 Recommendation: Use AI processing")
            else:
                print("✅ Recommendation: Execute with high confidence")
            
            print()
            
        except Exception as e:
            print(f"❌ Error processing command: {e}")
            print()
    
    print("=" * 60)
    print("✅ Integration test completed!")
    
    # Show semantic engine statistics
    try:
        if hasattr(intelligence_engine, 'semantic_available') and intelligence_engine.semantic_available:
            print("\n📊 Semantic Engine Status: Available")
        else:
            print("\n📊 Semantic Engine Status: Not Available")
    except:
        pass

if __name__ == "__main__":
    asyncio.run(test_real_commands())
