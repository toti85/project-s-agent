"""
PROJECT-S Enhanced Intelligence Demonstration
============================================
This script demonstrates the new Intent Confidence Scoring system
and enhanced natural language understanding capabilities.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging to see debug information
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(name)s - %(message)s'
)

async def test_enhanced_intelligence():
    """Test the enhanced intelligence capabilities with various command examples."""
    
    try:
        from core.intelligence_engine import intelligence_engine
        from main_multi_model import intelligent_command_parser
        
        print("🎯 PROJECT-S Enhanced Intelligence Demonstration")
        print("=" * 60)
        
        # Test cases with varying confidence levels
        test_cases = [
            # High confidence cases
            "hozz létre test.txt fájlt",
            "create file example.py",
            "listázd a fájlokat",
            "szervezd a downloads mappát",
            "futtat powershell Get-ChildItem",
            
            # Medium confidence cases (fuzzy matching)
            "létre hoz valami.txt",  # Reversed word order
            "organizze the folder",  # Typo
            "show me files",  # Partial match
            "run command ls",  # Mixed languages
            
            # Low confidence cases
            "something random",
            "mi a helyzet?",
            "create something",  # Ambiguous
            "organize",  # Missing parameters
            
            # Partial filename cases
            "create file test",  # No extension
            "read myfile.txt",  # Clear filename
            "list directory documents",  # Clear target
        ]
        
        for i, test_input in enumerate(test_cases, 1):
            print(f"\n🔍 Test Case {i}: '{test_input}'")
            print("-" * 50)
            
            # Test the enhanced parser
            try:
                result = await intelligent_command_parser(test_input)
                
                print(f"Intent Type: {result.get('type', 'Unknown')}")
                print(f"Operation: {result.get('operation', 'N/A')}")
                print(f"Confidence: {result.get('confidence', 0):.2f} ({result.get('confidence_level', 'Unknown')})")
                
                if result.get('matched_patterns'):
                    print(f"Matched Patterns: {', '.join(result['matched_patterns'])}")
                
                # Show parameters
                params = {k: v for k, v in result.items() 
                         if k not in ['type', 'operation', 'confidence', 'confidence_level', 
                                      'matched_patterns', 'extraction_details', 'alternatives']}
                if params:
                    print(f"Parameters: {params}")
                
                # Show special flags
                flags = []
                if result.get('requires_confirmation'):
                    flags.append("⚠️ Requires Confirmation")
                if result.get('suggest_alternatives'):
                    flags.append("💡 Has Alternatives")
                if result.get('fallback_to_ai'):
                    flags.append("🤖 AI Fallback")
                
                if flags:
                    print(f"Flags: {', '.join(flags)}")
                
                # Show alternatives
                if result.get('alternatives'):
                    print(f"Alternatives ({len(result['alternatives'])}):")
                    for alt in result['alternatives']:
                        print(f"  - {alt['intent_type']}: {alt['operation']} ({alt['confidence']:.2f})")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n" + "=" * 60)
        print("🎯 Interactive Intelligence Testing")
        print("Enter commands to test the enhanced intelligence engine.")
        print("Type 'quit' to exit.")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\nProject-S Intelligence> ").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not user_input:
                    continue
                
                print("\n🔍 Analysis:")
                result = await intelligent_command_parser(user_input)
                
                # Generate detailed report
                confidence_report = intelligence_engine.format_confidence_report(
                    await intelligence_engine.analyze_intent_with_confidence(user_input)
                )
                print(confidence_report)
                
                # Show recommended action
                if result.get('requires_confirmation'):
                    print("\n🤔 Recommendation: Request user confirmation before execution")
                elif result.get('suggest_alternatives'):
                    print("\n💡 Recommendation: Show alternatives to user")
                elif result.get('fallback_to_ai'):
                    print("\n🤖 Recommendation: Use AI processing for this query")
                else:
                    print("\n✅ Recommendation: Execute with high confidence")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
    except ImportError as e:
        print(f"❌ Could not import intelligence engine: {e}")
        print("Make sure the intelligence_engine.py file is in the core/ directory")

async def test_semantic_enhancement():
        """Test semantic similarity enhancements."""
        if not hasattr(intelligence_engine, 'semantic_available') or not intelligence_engine.semantic_available:
            self.log_test_result("Semantic Enhancement", True, "Skipped - Semantic engine not available")
            return
        
        test_cases = [
            # Test semantic boost
            ("hozz létre egy dokumentumot", "FILE_OPERATION", "create", 0.6),
            ("készíts egy fájlt", "FILE_OPERATION", "create", 0.6),
            ("mutasd meg a tartalmat", "FILE_OPERATION", "read", 0.6),
            ("organize the directory", "DIRECTORY_ORGANIZATION", "organize", 0.6),
        ]
        
        for user_input, expected_intent, expected_operation, min_confidence in test_cases:
            try:
                intent_match = await intelligence_engine.analyze_intent_with_confidence(user_input)
                
                # Check if semantic details are populated
                has_semantic = bool(intent_match.semantic_details.get('semantic_available', False))
                semantic_confidence = intent_match.semantic_confidence
                
                passed = (intent_match.intent_type == expected_intent and 
                         intent_match.operation == expected_operation and
                         intent_match.confidence >= min_confidence)
                
                details = f"'{user_input}' -> {intent_match.intent_type}.{intent_match.operation} " \
                         f"(conf: {intent_match.confidence:.3f}, semantic: {has_semantic}, " \
                         f"sem_conf: {semantic_confidence:.3f})"
                
                self.log_test_result(f"Semantic Enhancement: {user_input}", passed, details)
                
            except Exception as e:
                self.log_test_result(f"Semantic Enhancement: {user_input}", False, f"Error: {e}")
    
    async def test_cross_language_support():
        """Test cross-language semantic matching."""
        if not hasattr(intelligence_engine, 'semantic_available') or not intelligence_engine.semantic_available:
            self.log_test_result("Cross-Language Support", True, "Skipped - Semantic engine not available")
            return
        
        cross_language_cases = [
            # Mixed language inputs
            ("create egy fájlt", "FILE_OPERATION", "create"),
            ("hozz létre file", "FILE_OPERATION", "create"),
            ("mutasd a content", "FILE_OPERATION", "read"),
            ("organize a mappát", "DIRECTORY_ORGANIZATION", "organize"),
        ]
        
        for user_input, expected_intent, expected_operation in cross_language_cases:
            try:
                intent_match = await intelligence_engine.analyze_intent_with_confidence(user_input)
                
                passed = (intent_match.intent_type == expected_intent and 
                         intent_match.operation == expected_operation)
                
                language_detected = intent_match.language_detected
                
                details = f"'{user_input}' -> {intent_match.intent_type}.{intent_match.operation} " \
                         f"(lang: {language_detected}, conf: {intent_match.confidence:.3f})"
                
                self.log_test_result(f"Cross-Language: {user_input}", passed, details)
                
            except Exception as e:
                self.log_test_result(f"Cross-Language: {user_input}", False, f"Error: {e}")
    
    async def test_semantic_alternatives():
        """Test semantic alternative suggestions."""
        if not hasattr(intelligence_engine, 'semantic_available') or not intelligence_engine.semantic_available:
            self.log_test_result("Semantic Alternatives", True, "Skipped - Semantic engine not available")
            return
        
        ambiguous_inputs = [
            "mutasd",  # Could be read or list
            "készíts",  # Could be create file or other
            "rendezd",  # Could be organize or sort
        ]
        
        for user_input in ambiguous_inputs:
            try:
                intent_match = await intelligence_engine.analyze_intent_with_confidence(user_input)
                
                has_alternatives = len(intent_match.semantic_alternatives) > 0
                semantic_detail_count = len(intent_match.semantic_details) > 0
                
                passed = has_alternatives or semantic_detail_count
                
                details = f"'{user_input}' -> {len(intent_match.semantic_alternatives)} semantic alternatives, " \
                         f"{len(intent_match.alternative_interpretations)} pattern alternatives"
                
                self.log_test_result(f"Semantic Alternatives: {user_input}", passed, details)
                
            except Exception as e:
                self.log_test_result(f"Semantic Alternatives: {user_input}", False, f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_intelligence())
