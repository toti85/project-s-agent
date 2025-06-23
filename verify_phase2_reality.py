"""
Verification Test - Confirm Phase 2 Implementation is Real
==========================================================
This test validates that the reported Phase 2 results are genuine by:
1. Checking actual file contents and imports
2. Testing specific semantic engine functionality 
3. Verifying sentence transformer model is actually loaded
4. Confirming integration points exist in main system
"""

import asyncio
import sys
import os
from pathlib import Path
import importlib.util

async def verify_phase2_implementation():
    """Comprehensive verification that Phase 2 is real and functional."""
    print("🔍 VERIFICATION: PROJECT-S Phase 2 Implementation Reality Check")
    print("=" * 70)
    
    verification_results = []
    
    # Test 1: Verify sentence-transformers library is actually installed
    print("\n1. Testing sentence-transformers library...")
    try:
        import sentence_transformers
        from sentence_transformers import SentenceTransformer
        print(f"✅ sentence-transformers version: {sentence_transformers.__version__}")
        
        # Actually load a model to prove it works
        model = SentenceTransformer('all-MiniLM-L6-v2')
        test_embedding = model.encode(["test sentence"])
        print(f"✅ Model loaded successfully, embedding shape: {test_embedding.shape}")
        verification_results.append("Sentence transformers: REAL")
    except Exception as e:
        print(f"❌ sentence-transformers issue: {e}")
        verification_results.append("Sentence transformers: FAILED")
    
    # Test 2: Verify semantic engine file exists and has real functionality
    print("\n2. Testing semantic engine file structure...")
    semantic_file = Path("core/semantic_engine.py")
    if semantic_file.exists():
        content = semantic_file.read_text(encoding='utf-8')
        
        # Check for key classes and methods
        key_components = [
            "class SemanticEngine",
            "def find_semantic_matches",
            "def _calculate_cosine_similarity", 
            "SENTENCE_TRANSFORMERS_AVAILABLE",
            "command_examples"
        ]
        
        found_components = []
        for component in key_components:
            if component in content:
                found_components.append(component)
                print(f"✅ Found: {component}")
            else:
                print(f"❌ Missing: {component}")
        
        verification_results.append(f"Semantic engine: {len(found_components)}/{len(key_components)} components")
    else:
        print("❌ core/semantic_engine.py not found")
        verification_results.append("Semantic engine: FILE MISSING")
    
    # Test 3: Test actual semantic matching with real embeddings
    print("\n3. Testing real semantic matching functionality...")
    try:
        from core.semantic_engine import semantic_engine
        
        # Test actual semantic matching
        matches = await semantic_engine.find_semantic_matches("create file", top_k=3)
        
        if matches:
            print(f"✅ Found {len(matches)} semantic matches")
            for i, match in enumerate(matches[:2]):
                print(f"   {i+1}. '{match.command}' (score: {match.similarity_score:.3f})")
            verification_results.append(f"Semantic matching: REAL ({len(matches)} matches)")
        else:
            print("❌ No semantic matches found")
            verification_results.append("Semantic matching: NO RESULTS")
            
    except Exception as e:
        print(f"❌ Semantic matching error: {e}")
        verification_results.append("Semantic matching: ERROR")
    
    # Test 4: Verify intelligence engine integration
    print("\n4. Testing intelligence engine integration...")
    try:
        from core.intelligence_engine import intelligence_engine
        
        # Test confidence analysis
        intent_match = await intelligence_engine.analyze_intent_with_confidence("hozz létre teszt.txt")
        
        print(f"✅ Intent analysis working:")
        print(f"   Intent: {intent_match.intent_type}")
        print(f"   Confidence: {intent_match.confidence:.3f}")
        print(f"   Has semantic details: {bool(intent_match.semantic_details)}")
        
        verification_results.append("Intelligence engine: REAL")
    except Exception as e:
        print(f"❌ Intelligence engine error: {e}")
        verification_results.append("Intelligence engine: ERROR")
    
    # Test 5: Verify main system integration points
    print("\n5. Testing main system integration...")
    try:
        # Check if main_multi_model has the integration
        spec = importlib.util.spec_from_file_location("main_multi_model", "main_multi_model.py")
        main_module = importlib.util.module_from_spec(spec)
        
        # Read the source to check integration
        main_content = Path("main_multi_model.py").read_text(encoding='utf-8')
        
        integration_points = [
            "from core.intelligence_engine import intelligence_engine",
            "analyze_intent_with_confidence",
            "confidence_level",
            "requires_confirmation",
            "semantic_details"
        ]
        
        found_integration = []
        for point in integration_points:
            if point in main_content:
                found_integration.append(point)
                print(f"✅ Found integration: {point}")
            else:
                print(f"❌ Missing integration: {point}")
        
        verification_results.append(f"Main integration: {len(found_integration)}/{len(integration_points)} points")
        
    except Exception as e:
        print(f"❌ Main system integration error: {e}")
        verification_results.append("Main integration: ERROR")
    
    # Test 6: Test actual embedding computation
    print("\n6. Testing real embedding computation...")
    try:
        from core.semantic_engine import semantic_engine
        
        # Test if embeddings are actually computed
        embedding = semantic_engine._get_embedding("test command")
        
        if embedding is not None:
            print(f"✅ Embedding computed, shape: {embedding.shape}")
            print(f"   Sample values: {embedding[:3]}")
            verification_results.append("Embedding computation: REAL")
        else:
            print("❌ No embedding computed")
            verification_results.append("Embedding computation: FAILED")
            
    except Exception as e:
        print(f"❌ Embedding computation error: {e}")
        verification_results.append("Embedding computation: ERROR")
    
    # Test 7: Test cosine similarity calculation
    print("\n7. Testing cosine similarity calculation...")
    try:
        from core.semantic_engine import semantic_engine
        import numpy as np
        
        # Test actual similarity calculation
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([0.0, 1.0, 0.0])
        vec3 = np.array([1.0, 0.0, 0.0])
        
        sim1 = semantic_engine._calculate_cosine_similarity(vec1, vec2)  # Should be ~0
        sim2 = semantic_engine._calculate_cosine_similarity(vec1, vec3)  # Should be ~1
        
        print(f"✅ Cosine similarity working:")
        print(f"   Orthogonal vectors: {sim1:.3f} (expected ~0)")
        print(f"   Identical vectors: {sim2:.3f} (expected ~1)")
        
        if abs(sim1) < 0.1 and abs(sim2 - 1.0) < 0.1:
            verification_results.append("Cosine similarity: CORRECT")
        else:
            verification_results.append("Cosine similarity: INCORRECT")
            
    except Exception as e:
        print(f"❌ Cosine similarity error: {e}")
        verification_results.append("Cosine similarity: ERROR")
    
    # Summary
    print(f"\n{'=' * 70}")
    print("🎯 VERIFICATION SUMMARY")
    print("=" * 70)
    
    real_count = 0
    total_count = len(verification_results)
    
    for result in verification_results:
        if "REAL" in result or "CORRECT" in result or "components" in result:
            real_count += 1
        print(f"📊 {result}")
    
    print(f"\n🏆 REALITY SCORE: {real_count}/{total_count} tests confirmed REAL")
    
    if real_count >= total_count * 0.8:  # 80% threshold
        print("✅ VERDICT: Phase 2 implementation is GENUINE and FUNCTIONAL")
        return True
    else:
        print("❌ VERDICT: Phase 2 implementation has issues or may be exaggerated")
        return False

if __name__ == "__main__":
    is_real = asyncio.run(verify_phase2_implementation())
    
    if is_real:
        print("\n🚀 Phase 2 is confirmed REAL and ready for production!")
    else:
        print("\n⚠️ Phase 2 implementation needs verification and fixes.")
