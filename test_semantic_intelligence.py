"""
PROJECT-S Enhanced Intelligence System - Semantic Test Suite
==========================================================
Comprehensive test suite for Phase 2 semantic similarity features.
Tests semantic matching, synonym expansion, context awareness, and performance.
"""

import asyncio
import time
import logging
from pathlib import Path
import sys

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

# Import the enhanced intelligence system
try:
    from core.intelligence_engine import intelligence_engine, IntentMatch
    from core.semantic_engine import semantic_engine, SemanticMatch
    from core.intelligence_config import get_intelligence_config
    ENHANCED_AVAILABLE = True
except ImportError as e:
    print(f"❌ Enhanced intelligence system not available: {e}")
    ENHANCED_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class SemanticTestSuite:
    """Test suite for semantic intelligence features."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.test_results = []
        self.semantic_available = ENHANCED_AVAILABLE
        
    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'details': details
        })
        print(f"{status} {test_name}: {details}")
    
    async def test_semantic_matching_basic(self):
        """Test basic semantic matching functionality."""
        test_cases = [
            # Hungarian inputs
            ("hozz létre egy fájlt", "FILE_OPERATION", "create"),
            ("mutasd meg a tartalmat", "FILE_OPERATION", "read"),
            ("listázd ki a fájlokat", "FILE_OPERATION", "list"),
            ("rendszerezd a mappát", "DIRECTORY_ORGANIZATION", "organize"),
            ("futtasd le a parancsot", "SHELL_COMMAND", "execute"),
            
            # English inputs
            ("create a new file", "FILE_OPERATION", "create"),
            ("show the content", "FILE_OPERATION", "read"),
            ("list all files", "FILE_OPERATION", "list"),
            ("organize the folder", "DIRECTORY_ORGANIZATION", "organize"),
            ("run the command", "SHELL_COMMAND", "execute"),
            
            # Cross-language variations
            ("make a fájl", "FILE_OPERATION", "create"),
            ("show the tartalom", "FILE_OPERATION", "read"),
        ]
        
        for user_input, expected_intent, expected_operation in test_cases:
            try:
                matches = await semantic_engine.find_semantic_matches(user_input, top_k=3)
                
                if matches:
                    best_match = matches[0]
                    passed = (best_match.intent_type == expected_intent and 
                             best_match.operation == expected_operation and
                             best_match.similarity_score >= 0.6)
                    
                    details = f"'{user_input}' -> {best_match.intent_type}.{best_match.operation} (score: {best_match.similarity_score:.3f})"
                else:
                    passed = False
                    details = f"'{user_input}' -> No matches found"
                
                self.log_test_result(f"Semantic Match: {user_input}", passed, details)
                
            except Exception as e:
                self.log_test_result(f"Semantic Match: {user_input}", False, f"Error: {e}")
    
    async def test_synonym_expansion(self):
        """Test synonym expansion functionality."""
        test_cases = [
            ("hozz létre", ["készíts", "generálj", "állíts össze"]),
            ("create", ["make", "generate", "build"]),
            ("mutasd", ["jelenítsd meg", "nézd meg", "tekintsd át"]),
            ("show", ["display", "view", "present"]),
        ]
        
        for original, expected_synonyms in test_cases:
            variations = semantic_engine.expand_synonyms(original)
            
            # Check if expected synonyms are in variations
            found_synonyms = []
            for synonym in expected_synonyms:
                for variation in variations:
                    if synonym in variation:
                        found_synonyms.append(synonym)
                        break
            
            passed = len(found_synonyms) >= 2  # At least 2 synonyms should be found
            details = f"'{original}' expanded to {len(variations)} variations, found synonyms: {found_synonyms}"
            
            self.log_test_result(f"Synonym Expansion: {original}", passed, details)
    
    async def test_context_awareness(self):
        """Test context-aware command interpretation."""
        # Set up context
        semantic_engine.context.recent_commands = [
            "hozz létre egy fájlt",
            "mutasd meg a tartalmat",
            "listázd ki a fájlokat"
        ]
        semantic_engine.context.current_workspace = {'type': 'code'}
        
        test_cases = [
            ("készíts még egyet", "FILE_OPERATION", "create"),  # Should infer file creation from context
            ("szervezd meg", "DIRECTORY_ORGANIZATION", "organize"),  # Should get boost for organization in code workspace
        ]
        
        for user_input, expected_intent, expected_operation in test_cases:
            try:
                # Test with intelligence engine to include context processing
                intent_match = await intelligence_engine.analyze_intent_with_confidence(user_input)
                
                passed = (intent_match.intent_type == expected_intent and 
                         intent_match.operation == expected_operation)
                
                details = f"'{user_input}' -> {intent_match.intent_type}.{intent_match.operation} (confidence: {intent_match.confidence:.3f})"
                
                self.log_test_result(f"Context Awareness: {user_input}", passed, details)
                
            except Exception as e:
                self.log_test_result(f"Context Awareness: {user_input}", False, f"Error: {e}")
    
    async def test_ambiguity_resolution(self):
        """Test ambiguity resolution with competing matches."""
        ambiguous_inputs = [
            "mutasd",  # Could be read file or list files
            "rendezd",  # Could be organize or sort
            "futtasd",  # Could be run or execute
        ]
        
        for user_input in ambiguous_inputs:
            try:
                alternatives = await semantic_engine.suggest_semantic_alternatives(user_input)
                
                # Should provide multiple alternatives
                passed = len(alternatives) >= 2
                
                # Check if context resolution is attempted
                context_resolved = any(alt.get('context_resolved', False) for alt in alternatives)
                
                details = f"'{user_input}' -> {len(alternatives)} alternatives, context resolved: {context_resolved}"
                
                self.log_test_result(f"Ambiguity Resolution: {user_input}", passed, details)
                
            except Exception as e:
                self.log_test_result(f"Ambiguity Resolution: {user_input}", False, f"Error: {e}")
    
    async def test_multilingual_support(self):
        """Test multi-language semantic matching."""
        cross_language_cases = [
            # Hungarian input should match English examples
            ("hozz létre file", "FILE_OPERATION", "create"),
            ("create fájl", "FILE_OPERATION", "create"),
            ("mutasd content", "FILE_OPERATION", "read"),
            ("show tartalom", "FILE_OPERATION", "read"),
        ]
        
        for user_input, expected_intent, expected_operation in cross_language_cases:
            try:
                matches = await semantic_engine.find_semantic_matches(user_input, top_k=3)
                
                if matches:
                    best_match = matches[0]
                    passed = (best_match.intent_type == expected_intent and 
                             best_match.operation == expected_operation)
                    
                    details = f"'{user_input}' -> {best_match.intent_type}.{best_match.operation} (lang: {best_match.language_detected})"
                else:
                    passed = False
                    details = f"'{user_input}' -> No matches found"
                
                self.log_test_result(f"Multilingual: {user_input}", passed, details)
                
            except Exception as e:
                self.log_test_result(f"Multilingual: {user_input}", False, f"Error: {e}")
    
    async def test_performance_optimization(self):
        """Test performance optimizations."""
        # Test embedding caching
        start_time = time.time()
        
        # First run - should compute embeddings
        matches1 = await semantic_engine.find_semantic_matches("create a file", top_k=5)
        first_run_time = time.time() - start_time
        
        start_time = time.time()
        
        # Second run - should use cached embeddings
        matches2 = await semantic_engine.find_semantic_matches("create a file", top_k=5)
        second_run_time = time.time() - start_time
        
        # Second run should be faster due to caching
        caching_effective = second_run_time < first_run_time or second_run_time < 0.1
        
        # Test fast similarity search
        fast_search_available = hasattr(semantic_engine, 'normalized_embeddings')
        
        details = f"First: {first_run_time:.3f}s, Second: {second_run_time:.3f}s, Fast search: {fast_search_available}"
        
        self.log_test_result("Performance Optimization", caching_effective, details)
    
    async def test_offline_fallback(self):
        """Test offline fallback functionality."""
        # Test offline pattern matching
        offline_matches = semantic_engine.offline_semantic_match("create a file")
        
        passed = len(offline_matches) > 0 and offline_matches[0]['intent_type'] == 'FILE_OPERATION'
        
        details = f"Offline matches: {len(offline_matches)}, best: {offline_matches[0] if offline_matches else 'None'}"
        
        self.log_test_result("Offline Fallback", passed, details)
    
    async def test_parameter_suggestion(self):
        """Test parameter suggestion functionality."""
        test_cases = [
            ("FILE_OPERATION", "create", "create a test file", "filename", "test"),
            ("FILE_OPERATION", "create", "create config", "filename", "config"),
            ("DIRECTORY_ORGANIZATION", "organize", "organize by type", "strategy", "by_type"),
        ]
        
        for intent_type, operation, user_input, param_key, expected_value in test_cases:
            suggestions = semantic_engine.suggest_default_parameters(intent_type, operation, user_input)
            
            passed = param_key in suggestions and expected_value in str(suggestions[param_key]).lower()
            
            details = f"{intent_type}.{operation} -> {suggestions}"
            
            self.log_test_result(f"Parameter Suggestion: {user_input}", passed, details)
    
    async def test_intent_clustering(self):
        """Test intent clustering functionality."""
        # Create some test matches
        test_matches = [
            SemanticMatch("create file", 0.9, "FILE_OPERATION", "create"),
            SemanticMatch("read file", 0.8, "FILE_OPERATION", "read"),
            SemanticMatch("organize folder", 0.85, "DIRECTORY_ORGANIZATION", "organize"),
            SemanticMatch("run command", 0.7, "SHELL_COMMAND", "execute"),
        ]
        
        clusters = semantic_engine.cluster_intents(test_matches)
        
        # Should have at least 3 clusters
        passed = len(clusters) >= 3
        
        # Check if file operations are properly clustered
        file_cluster_exists = 'file_management' in clusters and len(clusters['file_management']) >= 2
        
        details = f"Clusters: {list(clusters.keys())}, file cluster has {len(clusters.get('file_management', []))} items"
        
        self.log_test_result("Intent Clustering", passed and file_cluster_exists, details)
    
    def print_test_summary(self):
        """Print test summary."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        
        print(f"\n{'='*60}")
        print(f"SEMANTIC TEST SUITE SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests / total_tests * 100):.1f}%")
        
        if total_tests - passed_tests > 0:
            print(f"\nFailed Tests:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  ❌ {result['test']}: {result['details']}")
        
        print(f"{'='*60}")

async def run_semantic_tests():
    """Run the complete semantic test suite."""
    if not ENHANCED_AVAILABLE:
        print("❌ Enhanced intelligence system not available. Please ensure all modules are properly installed.")
        return False
    
    print("🧪 Starting PROJECT-S Semantic Intelligence Test Suite...")
    print(f"📊 Semantic Engine Model Loaded: {semantic_engine.model is not None}")
    print(f"📊 Intelligence Engine Semantic Integration: {intelligence_engine.semantic_available}")
    
    test_suite = SemanticTestSuite()
    
    # Run all test categories
    test_categories = [
        ("Basic Semantic Matching", test_suite.test_semantic_matching_basic),
        ("Synonym Expansion", test_suite.test_synonym_expansion),
        ("Context Awareness", test_suite.test_context_awareness),
        ("Ambiguity Resolution", test_suite.test_ambiguity_resolution),
        ("Multilingual Support", test_suite.test_multilingual_support),
        ("Performance Optimization", test_suite.test_performance_optimization),
        ("Offline Fallback", test_suite.test_offline_fallback),
        ("Parameter Suggestion", test_suite.test_parameter_suggestion),
        ("Intent Clustering", test_suite.test_intent_clustering),
    ]
    
    for category_name, test_function in test_categories:
        print(f"\n🔍 Testing {category_name}...")
        try:
            await test_function()
        except Exception as e:
            print(f"❌ Error in {category_name}: {e}")
            test_suite.log_test_result(f"{category_name} (Category)", False, f"Category error: {e}")
    
    # Print summary
    test_suite.print_test_summary()
    
    # Return overall success
    total_tests = len(test_suite.test_results)
    passed_tests = sum(1 for result in test_suite.test_results if result['passed'])
    return passed_tests == total_tests

if __name__ == "__main__":
    # Run the test suite
    success = asyncio.run(run_semantic_tests())
    
    if success:
        print("\n🎉 All semantic tests passed!")
        exit(0)
    else:
        print("\n⚠️ Some semantic tests failed. Check the output above for details.")
        exit(1)
