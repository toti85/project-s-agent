"""
PROJECT-S Semantic Similarity Engine - Phase 2 Enhancement
=========================================================
This module provides advanced semantic understanding capabilities using sentence transformers
and embedding-based similarity matching, extending the Phase 1 confidence scoring system.

Key Features:
1. Sentence transformer integration for semantic command understanding
2. Command embedding database with cosine similarity matching
3. Contextual ambiguity resolution using conversation history
4. Multi-language semantic mapping (Hungarian-English)
5. Command synonym expansion and intent clustering
6. Performance optimization with caching and efficient search

Integration Strategy:
- Extends existing intelligence_engine.py without breaking changes
- Adds semantic similarity scores to confidence calculations
- Maintains backward compatibility with Phase 1 implementation
- Provides graceful fallback for offline operation
"""

import logging
import asyncio
import numpy as np
import json
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
import pickle
import hashlib

# Sentence transformers integration with fallback
try:
    from sentence_transformers import SentenceTransformer
    import torch
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Scipy for cosine similarity with fallback
try:
    from scipy.spatial.distance import cosine
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class SemanticMatch:
    """Represents a semantic similarity match with detailed analysis."""
    command: str
    similarity_score: float
    intent_type: str
    operation: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    embedding_vector: Optional[np.ndarray] = None
    matched_examples: List[str] = field(default_factory=list)
    semantic_confidence: float = 0.0
    language_detected: str = "unknown"

@dataclass
class SemanticContext:
    """Context information for semantic understanding."""
    conversation_history: List[str] = field(default_factory=list)
    recent_commands: List[str] = field(default_factory=list)
    current_workspace: Dict[str, Any] = field(default_factory=dict)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    session_embeddings: List[np.ndarray] = field(default_factory=list)

class SemanticCommandDatabase:
    """Database of semantic command examples with embeddings for similarity matching."""
    
    def __init__(self):
        """Initialize the semantic command database."""
        self.command_examples = {
            "FILE_OPERATION": {
                "create": [
                    # Hungarian examples
                    "hozz létre egy fájlt", "készíts új dokumentumot", "generálj fájlt",
                    "létrehozz egy szöveges fájlt", "csinálj egy új file-t", "írj ki egy fájlt",
                    "építs fel egy dokumentumot", "állítsd össze a fájlt",
                    
                    # English examples
                    "create a new file", "make a document", "generate a file",
                    "build a new text file", "produce a document", "write out a file",
                    "construct a new file", "establish a document", "form a new file",
                    "craft a text document", "develop a file", "compose a document"
                ],
                "read": [
                    # Hungarian examples
                    "olvasd fel a fájlt", "mutasd meg a tartalmat", "jelenítsd meg a fájlt",
                    "nézd meg mit tartalmaz", "tekintsd át a dokumentumot", "lapozz a fájlban",
                    "böngészd a tartalmat", "vizsgáld meg a fájlt",
                    
                    # English examples
                    "read the file content", "show me what's in the file", "display the document",
                    "view the file contents", "examine the document", "browse the file",
                    "look at the file", "check the document", "review the content",
                    "inspect the file", "scan the document", "peek into the file"
                ],
                "list": [
                    # Hungarian examples
                    "listázd ki a fájlokat", "sorold fel a dokumentumokat", "mutasd a mappát",
                    "nézd meg mi van itt", "adj egy áttekintést", "számold meg a fájlokat",
                    "tekintsd át a könyvtárat", "böngészd a mappát",
                    
                    # English examples
                    "list all files", "show directory contents", "display folder items",
                    "enumerate the files", "browse the directory", "show what's here",
                    "give me an overview", "catalog the files", "index the directory",
                    "scan the folder", "inventory the files", "survey the directory"
                ]
            },
            "DIRECTORY_ORGANIZATION": {
                "organize": [
                    # Hungarian examples
                    "rendszerezd a mappát", "szervezd át a fájlokat", "rakd rendbe a könyvtárat",
                    "kategorizáld a dokumentumokat", "tisztítsd meg a mappát", "rendezd el a fájlokat",
                    "strukturáld át a könyvtárat", "optimalizáld a mappát",
                    
                    # English examples
                    "organize the directory", "sort the files", "clean up the folder",
                    "arrange the documents", "structure the directory", "tidy the files",
                    "categorize the folder", "streamline the directory", "reorganize files",
                    "optimize folder structure", "systematize the directory", "rationalize files"
                ]
            },
            "SHELL_COMMAND": {
                "execute": [
                    # Hungarian examples
                    "futtasd le a parancsot", "hajts végre egy szkriptet", "indítsd el a programot",
                    "aktiválj egy folyamatot", "triggerelj egy műveletet", "végrehajtás",
                    
                    # English examples
                    "run the command", "execute the script", "launch the program",
                    "start the process", "trigger the operation", "invoke the command",
                    "fire up the script", "activate the process", "initiate execution",
                    "kick off the command", "spawn the process", "call the script"
                ]
            }
        }
        
        # Embedding cache for performance
        self.embedding_cache = {}
        self.embeddings_computed = False
        
    def get_all_examples(self) -> List[Tuple[str, str, str]]:
        """Get all command examples with their intent and operation."""
        examples = []
        for intent_type, operations in self.command_examples.items():
            for operation, commands in operations.items():
                for command in commands:
                    examples.append((command, intent_type, operation))
        return examples

class SemanticEngine:
    """Advanced semantic similarity engine for natural language command understanding."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the semantic engine with sentence transformer model."""
        self.model_name = model_name
        self.model = None
        self.command_db = SemanticCommandDatabase()
        self.context = SemanticContext()
        
        # Performance optimization
        self.embedding_cache = {}
        self.similarity_cache = {}
        self.cache_max_size = 1000
        
        # Configuration
        self.semantic_threshold = 0.6
        self.context_boost_factor = 0.15
        self.multi_language_boost = 0.1
        
        # Initialize model
        self._initialize_model()
        
        logger.info(f"Semantic Engine initialized with model: {model_name}")
    
    def _initialize_model(self) -> bool:
        """Initialize the sentence transformer model with error handling."""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.warning("Sentence transformers not available - semantic matching disabled")
            return False
        
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"✅ Sentence transformer model '{self.model_name}' loaded successfully")
            
            # Precompute embeddings for command database
            self._precompute_command_embeddings()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load sentence transformer model: {e}")
            self.model = None
            return False
    
    def _precompute_command_embeddings(self) -> None:
        """Precompute embeddings for all command examples for faster similarity search."""
        if not self.model:
            return
        
        try:
            logger.info("Computing embeddings for command database...")
            examples = self.command_db.get_all_examples()
            
            commands = [example[0] for example in examples]
            embeddings = self.model.encode(commands, convert_to_tensor=True)
            
            # Store embeddings with metadata
            for i, (command, intent_type, operation) in enumerate(examples):
                embedding_key = self._get_cache_key(command)
                self.command_db.embedding_cache[embedding_key] = {
                    'embedding': embeddings[i].cpu().numpy(),
                    'intent_type': intent_type,
                    'operation': operation,
                    'command': command
                }
            
            self.command_db.embeddings_computed = True
            logger.info(f"✅ Computed embeddings for {len(examples)} command examples")
            
        except Exception as e:
            logger.error(f"❌ Failed to precompute embeddings: {e}")
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(text.lower().encode()).hexdigest()
    
    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding for text with caching."""
        if not self.model:
            return None
        
        cache_key = self._get_cache_key(text)
        
        # Check cache first
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        try:
            # Compute embedding
            embedding = self.model.encode([text], convert_to_tensor=True)[0].cpu().numpy()
            
            # Cache with size limit
            if len(self.embedding_cache) < self.cache_max_size:
                self.embedding_cache[cache_key] = embedding
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to compute embedding for '{text}': {e}")
            return None
    
    def _calculate_cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings."""
        if SCIPY_AVAILABLE:
            try:
                return 1.0 - cosine(embedding1, embedding2)
            except:
                pass
        
        # Fallback to numpy implementation
        try:
            dot_product = np.dot(embedding1, embedding2)
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            logger.error(f"Failed to calculate cosine similarity: {e}")
            return 0.0
    
    def detect_language(self, text: str) -> str:
        """Simple language detection based on character patterns."""
        text_lower = text.lower()
        
        # Hungarian indicators
        hungarian_chars = set('áéíóöőúüű')
        hungarian_words = {'hozz', 'létre', 'készíts', 'mutasd', 'olvasd', 'listázd', 'szervezd', 'rendszerezd'}
        
        # Check for Hungarian characters
        if any(char in hungarian_chars for char in text_lower):
            return 'hu'
        
        # Check for Hungarian words
        words = set(text_lower.split())
        if words & hungarian_words:
            return 'hu'
        
        # English indicators
        english_words = {'create', 'make', 'show', 'list', 'organize', 'read', 'file', 'folder'}
        if words & english_words:
            return 'en'
        
        return 'unknown'
    
    async def find_semantic_matches(self, user_input: str, top_k: int = 5) -> List[SemanticMatch]:
        """Find semantically similar commands from the database."""
        if not self.model or not self.command_db.embeddings_computed:
            logger.debug("Semantic matching not available - using offline fallback")
            return self.offline_semantic_match(user_input, top_k)
        
        try:
            # Get embedding for user input
            user_embedding = self._get_embedding(user_input)
            if user_embedding is None:
                return []
            
            # Detect language for potential boost
            detected_lang = self.detect_language(user_input)
            
            matches = []
            
            # Compare with all cached embeddings
            for cache_key, cached_data in self.command_db.embedding_cache.items():
                try:
                    similarity = self._calculate_cosine_similarity(
                        user_embedding, 
                        cached_data['embedding']
                    )
                    
                    # Apply language boost for cross-language matches
                    if detected_lang != 'unknown':
                        example_lang = self.detect_language(cached_data['command'])
                        if detected_lang != example_lang and example_lang != 'unknown':
                            similarity += self.multi_language_boost
                    
                    # Apply context boost if available
                    if self._is_contextually_relevant(cached_data['command']):
                        similarity += self.context_boost_factor
                    
                    # Only include matches above threshold
                    if similarity >= self.semantic_threshold:
                        match = SemanticMatch(
                            command=cached_data['command'],
                            similarity_score=similarity,
                            intent_type=cached_data['intent_type'],
                            operation=cached_data['operation'],
                            embedding_vector=cached_data['embedding'],
                            semantic_confidence=min(similarity, 1.0),
                            language_detected=detected_lang
                        )
                        matches.append(match)
                        
                except Exception as e:
                    logger.debug(f"Error processing cached embedding: {e}")
                    continue
            
            # Sort by similarity score and return top_k
            matches.sort(key=lambda x: x.similarity_score, reverse=True)
            return matches[:top_k]
            
        except Exception as e:
            logger.error(f"Error in semantic matching: {e}")
            return []
    
    def _is_contextually_relevant(self, command: str) -> bool:
        """Check if a command is contextually relevant based on conversation history."""
        if not self.context.recent_commands:
            return False
        
        # Simple keyword-based relevance check
        command_words = set(command.lower().split())
        
        for recent_command in self.context.recent_commands[-3:]:
            recent_words = set(recent_command.lower().split())
            
            # If there's significant word overlap, consider it relevant
            overlap = len(command_words & recent_words)
            if overlap >= 2:
                return True
        
        return False
    
    def update_context(self, user_input: str, result: Dict[str, Any]) -> None:
        """Update semantic context with new user interaction."""
        # Add to conversation history
        self.context.conversation_history.append(user_input)
        
        # Maintain recent commands (last 10)
        self.context.recent_commands.append(user_input)
        if len(self.context.recent_commands) > 10:
            self.context.recent_commands.pop(0)
        
        # Store embeddings for context analysis
        if self.model:
            embedding = self._get_embedding(user_input)
            if embedding is not None:
                self.context.session_embeddings.append(embedding)
                if len(self.context.session_embeddings) > 20:
                    self.context.session_embeddings.pop(0)
    
    async def enhance_intent_with_semantics(self, user_input: str, base_confidence: float, 
                                          intent_type: str, operation: str) -> Tuple[float, Dict[str, Any]]:
        """Enhance existing intent detection with semantic similarity analysis."""
        try:
            # Find semantic matches
            semantic_matches = await self.find_semantic_matches(user_input, top_k=3)
            
            if not semantic_matches:
                return base_confidence, {"semantic_available": False}
            
            # Find matches that agree with the base detection
            agreeing_matches = [
                match for match in semantic_matches 
                if match.intent_type == intent_type and match.operation == operation
            ]
            
            # Calculate semantic boost
            semantic_boost = 0.0
            if agreeing_matches:
                max_similarity = max(match.similarity_score for match in agreeing_matches)
                semantic_boost = max_similarity * 0.2  # Up to 20% boost
            
            # Check for conflicting semantic evidence
            conflicting_matches = [
                match for match in semantic_matches 
                if match.intent_type != intent_type or match.operation != operation
            ]
            
            semantic_conflict = 0.0
            if conflicting_matches and agreeing_matches:
                max_conflict = max(match.similarity_score for match in conflicting_matches)
                max_agreement = max(match.similarity_score for match in agreeing_matches)
                
                if max_conflict > max_agreement:
                    semantic_conflict = (max_conflict - max_agreement) * 0.1
            
            # Calculate enhanced confidence
            enhanced_confidence = base_confidence + semantic_boost - semantic_conflict
            enhanced_confidence = max(0.0, min(1.0, enhanced_confidence))
            
            # Prepare semantic details
            semantic_details = {
                "semantic_available": True,
                "semantic_matches": len(semantic_matches),
                "agreeing_matches": len(agreeing_matches),
                "conflicting_matches": len(conflicting_matches),
                "semantic_boost": semantic_boost,
                "semantic_conflict": semantic_conflict,
                "top_match": {
                    "command": semantic_matches[0].command,
                    "similarity": semantic_matches[0].similarity_score,
                    "intent": semantic_matches[0].intent_type,
                    "operation": semantic_matches[0].operation
                } if semantic_matches else None,
                "language_detected": semantic_matches[0].language_detected if semantic_matches else "unknown"
            }
            
            return enhanced_confidence, semantic_details
            
        except Exception as e:
            logger.error(f"Error enhancing intent with semantics: {e}")
            return base_confidence, {"semantic_available": False, "error": str(e)}
    
    async def suggest_semantic_alternatives(self, user_input: str) -> List[Dict[str, Any]]:
        """Suggest alternative interpretations based on semantic similarity."""
        try:
            semantic_matches = await self.find_semantic_matches(user_input, top_k=10)
            
            if not semantic_matches:
                return []
            
            # Group matches by (intent_type, operation) and take the best from each group
            alternatives = {}
            for match in semantic_matches:
                key = (match.intent_type, match.operation)
                if key not in alternatives or match.similarity_score > alternatives[key]['semantic_score']:
                    alternatives[key] = {
                        'intent_type': match.intent_type,
                        'operation': match.operation,
                        'semantic_score': match.similarity_score,
                        'example_command': match.command,
                        'confidence': min(match.similarity_score * 0.9, 0.95),
                        'language_detected': match.language_detected
                    }
            
            # Convert to list and sort by semantic score
            result = list(alternatives.values())
            result.sort(key=lambda x: x['semantic_score'], reverse=True)
            
            return result[:5]
            
        except Exception as e:
            logger.error(f"Error generating semantic alternatives: {e}")
            return []
    
    def offline_semantic_match(self, user_input: str, top_k: int = 5) -> List[SemanticMatch]:
        """Provide semantic matching without transformer models using pattern-based fallback."""
        fallback_patterns = {
            'hungarian_patterns': {
                'hozz létre': {'intent': 'FILE_OPERATION', 'operation': 'create', 'confidence': 0.8},
                'készíts': {'intent': 'FILE_OPERATION', 'operation': 'create', 'confidence': 0.8},
                'mutasd': {'intent': 'FILE_OPERATION', 'operation': 'read', 'confidence': 0.8},
                'olvasd': {'intent': 'FILE_OPERATION', 'operation': 'read', 'confidence': 0.8},
                'listázd': {'intent': 'FILE_OPERATION', 'operation': 'list', 'confidence': 0.8},
                'rendszerezd': {'intent': 'DIRECTORY_ORGANIZATION', 'operation': 'organize', 'confidence': 0.8},
                'szervezd': {'intent': 'DIRECTORY_ORGANIZATION', 'operation': 'organize', 'confidence': 0.8},
                'futtasd': {'intent': 'SHELL_COMMAND', 'operation': 'execute', 'confidence': 0.8}
            },
            'english_patterns': {
                'create': {'intent': 'FILE_OPERATION', 'operation': 'create', 'confidence': 0.8},
                'make': {'intent': 'FILE_OPERATION', 'operation': 'create', 'confidence': 0.7},
                'show': {'intent': 'FILE_OPERATION', 'operation': 'read', 'confidence': 0.8},
                'read': {'intent': 'FILE_OPERATION', 'operation': 'read', 'confidence': 0.8},
                'list': {'intent': 'FILE_OPERATION', 'operation': 'list', 'confidence': 0.8},
                'organize': {'intent': 'DIRECTORY_ORGANIZATION', 'operation': 'organize', 'confidence': 0.8},
                'sort': {'intent': 'DIRECTORY_ORGANIZATION', 'operation': 'organize', 'confidence': 0.7},
                'run': {'intent': 'SHELL_COMMAND', 'operation': 'execute', 'confidence': 0.8},
                'execute': {'intent': 'SHELL_COMMAND', 'operation': 'execute', 'confidence': 0.8}
            }
        }
        
        matches = []
        user_input_lower = user_input.lower()
        
        # Check Hungarian patterns
        for pattern, match_data in fallback_patterns['hungarian_patterns'].items():
            if pattern in user_input_lower:
                matches.append(SemanticMatch(
                    command=pattern,
                    similarity_score=match_data['confidence'],
                    intent_type=match_data['intent'],
                    operation=match_data['operation'],
                    semantic_confidence=match_data['confidence'],
                    language_detected='hu'
                ))
        
        # Check English patterns
        for pattern, match_data in fallback_patterns['english_patterns'].items():
            if pattern in user_input_lower:
                matches.append(SemanticMatch(
                    command=pattern,
                    similarity_score=match_data['confidence'],
                    intent_type=match_data['intent'],
                    operation=match_data['operation'],
                    semantic_confidence=match_data['confidence'],
                    language_detected='en'
                ))
        
        # Sort by confidence and remove duplicates
        unique_matches = {}
        for match in matches:
            key = f"{match.intent_type}.{match.operation}"
            if key not in unique_matches or match.similarity_score > unique_matches[key].similarity_score:
                unique_matches[key] = match
        
        result = list(unique_matches.values())
        result.sort(key=lambda x: x.similarity_score, reverse=True)
        
        logger.debug(f"Offline semantic matching found {len(result)} matches for '{user_input}'")
        return result[:top_k]
    
    def get_semantic_statistics(self) -> Dict[str, Any]:
        """Get statistics about semantic engine performance and state."""
        return {
            "model_loaded": self.model is not None,
            "model_name": self.model_name,
            "embeddings_computed": self.command_db.embeddings_computed,
            "total_examples": len(self.command_db.get_all_examples()),
            "embedding_cache_size": len(self.embedding_cache),
            "similarity_cache_size": len(self.similarity_cache),
            "context_history_length": len(self.context.conversation_history),
            "recent_commands_count": len(self.context.recent_commands),
            "semantic_threshold": self.semantic_threshold,
            "libraries_available": {
                "sentence_transformers": SENTENCE_TRANSFORMERS_AVAILABLE,
                "scipy": SCIPY_AVAILABLE
            }
        }

# Global instance for easy access
semantic_engine = SemanticEngine()
