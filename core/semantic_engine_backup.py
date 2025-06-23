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
    """
    Database of semantic command examples with embeddings for similarity matching.
    """
    
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
                ],
                "create_samples": [
                    # Hungarian examples
                    "hozz létre minta fájlokat", "készíts teszt dokumentumokat", "generálj példa fájlokat",
                    "állíts össze demo anyagokat", "építs fel példa struktúrát",
                    
                    # English examples
                    "create sample files", "generate test documents", "make example files",
                    "build demo content", "produce sample data", "create test materials",
                    "generate example structure", "build prototype files"
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
            },
            "AI_QUERY": {
                "query": [
                    # Hungarian examples
                    "kérdezz rá", "tudakozódj", "kérj információt", "érdeklődj",
                    "nézz utána", "derítsd ki", "vizsgálj meg", "elemezz",
                    
                    # English examples
                    "ask about", "inquire", "question", "seek information",
                    "find out", "investigate", "explore", "analyze",
                    "research", "examine", "study", "look into"
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
    """
    Advanced semantic similarity engine for natural language command understanding.
    Extends Phase 1 confidence scoring with embedding-based semantic matching.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the semantic engine with sentence transformer model.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self.model = None
        self.command_db = SemanticCommandDatabase()
        self.context = SemanticContext()
        
        # Performance optimization
        self.embedding_cache = {}
        self.similarity_cache = {}
        self.cache_max_size = 1000
        
        # Configuration
        self.semantic_threshold = 0.6  # Minimum similarity for semantic match
        self.context_boost_factor = 0.15  # Boost for contextually relevant commands
        self.multi_language_boost = 0.1  # Boost for cross-language matches
          # Initialize model
        self._initialize_model()
        
        logger.info(f"Semantic Engine initialized with model: {model_name}")
    
    def _initialize_model(self) -> bool:
        """
        Initialize the sentence transformer model with error handling.
        
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.warning("Sentence transformers not available - semantic matching disabled")
            return False
        
        try:
            # Try to load cached embeddings first
            if self.load_embeddings_from_disk():
                logger.info(f"✅ Loaded cached embeddings for model '{self.model_name}'")
                
                # Still need to load the model for new queries
                self.model = SentenceTransformer(self.model_name)
                logger.info(f"✅ Sentence transformer model '{self.model_name}' loaded successfully")
                return True
              # Try to load the model
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"✅ Sentence transformer model '{self.model_name}' loaded successfully")
            
            # Precompute embeddings for command database
            self._precompute_command_embeddings()
            
            # Save embeddings to disk for future use
            self.save_embeddings_to_disk()
            
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
            
            # Optimize similarity search after computing embeddings
            self.optimize_similarity_search()
            
            logger.info(f"✅ Computed embeddings for {len(examples)} command examples")
            
        except Exception as e:
            logger.error(f"❌ Failed to precompute embeddings: {e}")
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(text.lower().encode()).hexdigest()
    
    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Get embedding for text with caching.
        
        Args:
            text: Input text to encode
            
        Returns:
            Embedding vector or None if model not available
        """
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
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if SCIPY_AVAILABLE:
            try:
                # Using scipy for optimized cosine similarity
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
        """
        Simple language detection based on character patterns.
        
        Args:
            text: Input text
            
        Returns:
            Detected language code ('hu', 'en', or 'unknown')
        """
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
        """
        Find semantically similar commands from the database.
        
        Args:
            user_input: User's input command
            top_k: Number of top matches to return
            
        Returns:
            List of semantic matches sorted by similarity score
        """
        if not self.model or not self.command_db.embeddings_computed:
            logger.debug("Semantic matching not available - using offline fallback")
            # Use offline fallback
            offline_matches = self.offline_semantic_match(user_input)
            return [
                SemanticMatch(
                    command=match['command'],
                    similarity_score=match['similarity_score'],
                    intent_type=match['intent_type'],
                    operation=match['operation'],
                    semantic_confidence=match['confidence'],
                    language_detected=match['language_detected']
                )
                for match in offline_matches[:top_k]
            ]
        
        try:
            # Expand user input with synonyms for better matching
            input_variations = self.expand_synonyms(user_input)
            all_matches = []
            
            # Process each variation
            for variation in input_variations[:3]:  # Limit to top 3 variations to avoid slowdown
                # Get embedding for variation
                user_embedding = self._get_embedding(variation)
                if user_embedding is None:
                    continue
                
                # Detect language for potential boost
                detected_lang = self.detect_language(variation)
                
                # Use fast similarity search if available
                if hasattr(self, 'normalized_embeddings'):
                    fast_results = self._fast_similarity_search(user_embedding, min(top_k * 2, 20))
                    
                    for idx, similarity in fast_results:
                        try:
                            metadata = self.embedding_metadata[idx]
                            
                            # Apply language boost for cross-language matches
                            if detected_lang != 'unknown':
                                example_lang = self.detect_language(metadata['command'])
                                if detected_lang != example_lang and example_lang != 'unknown':
                                    similarity += self.multi_language_boost
                            
                            # Apply context boost if available
                            if self._is_contextually_relevant(metadata['command']):
                                similarity += self.context_boost_factor
                            
                            # Only include matches above threshold
                            if similarity >= self.semantic_threshold:
                                match = SemanticMatch(
                                    command=metadata['command'],
                                    similarity_score=similarity,
                                    intent_type=metadata['intent_type'],
                                    operation=metadata['operation'],
                                    embedding_vector=self.embedding_matrix[idx],
                                    semantic_confidence=min(similarity, 1.0),
                                    language_detected=detected_lang
                                )
                                all_matches.append(match)
                                
                        except Exception as e:
                            logger.debug(f"Error processing fast search result: {e}")
                            continue
                else:
                    # Fallback to original method
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
                    
                    all_matches.extend(matches)
            
            # Remove duplicates and sort by similarity score
            unique_matches = {}
            for match in all_matches:
                key = f"{match.intent_type}.{match.operation}.{match.command}"
                if key not in unique_matches or match.similarity_score > unique_matches[key].similarity_score:
                    unique_matches[key] = match
            
            final_matches = list(unique_matches.values())
            final_matches.sort(key=lambda x: x.similarity_score, reverse=True)
            
            # Manage cache periodically
            if len(self.embedding_cache) > self.cache_max_size * 0.8:
                self.manage_embedding_cache()
            
            return final_matches[:top_k]
            
        except Exception as e:
            logger.error(f"Error in semantic matching: {e}")
            return []
    
    def _is_contextually_relevant(self, command: str) -> bool:
        """
        Check if a command is contextually relevant based on conversation history.
        
        Args:
            command: Command to check for relevance
            
        Returns:
            True if command is contextually relevant
        """
        if not self.context.recent_commands:
            return False
        
        # Simple keyword-based relevance check
        command_words = set(command.lower().split())
        
        for recent_command in self.context.recent_commands[-3:]:  # Check last 3 commands
            recent_words = set(recent_command.lower().split())
            
            # If there's significant word overlap, consider it relevant
            overlap = len(command_words & recent_words)
            if overlap >= 2:
                return True
        
        return False
    
    def update_context(self, user_input: str, result: Dict[str, Any]) -> None:
        """
        Update semantic context with new user interaction.
        
        Args:
            user_input: User's input command
            result: Command execution result
        """
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
        """
        Enhance existing intent detection with semantic similarity analysis.
        
        Args:
            user_input: User's input command
            base_confidence: Base confidence from pattern matching
            intent_type: Detected intent type
            operation: Detected operation
            
        Returns:
            Tuple of (enhanced_confidence, semantic_details)
        """
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
                # Use the highest similarity score from agreeing matches
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
                
                # Reduce confidence if conflict is stronger than agreement
                if max_conflict > max_agreement:
                    semantic_conflict = (max_conflict - max_agreement) * 0.1
            
            # Calculate enhanced confidence
            enhanced_confidence = base_confidence + semantic_boost - semantic_conflict
            enhanced_confidence = max(0.0, min(1.0, enhanced_confidence))  # Clamp to [0, 1]
            
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
        """
        Suggest alternative interpretations based on semantic similarity.
        
        Args:
            user_input: User's input command
            
        Returns:
            List of alternative interpretations with semantic scores
        """
        try:
            semantic_matches = await self.find_semantic_matches(user_input, top_k=15)
            
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
                        'confidence': min(match.similarity_score * 0.9, 0.95),  # Slightly reduce for alternatives
                        'language_detected': match.language_detected,
                        'suggested_parameters': self.suggest_default_parameters(
                            match.intent_type, match.operation, user_input
                        )
                    }
            
            # Convert to list and resolve ambiguity using context
            alternatives_list = list(alternatives.values())
            
            # Use context to resolve ambiguity if there are multiple high-confidence matches
            high_confidence_matches = [alt for alt in alternatives_list if alt['semantic_score'] > 0.75]
            if len(high_confidence_matches) > 1:
                # Convert to SemanticMatch objects for context resolution
                semantic_matches_for_resolution = []
                for alt in high_confidence_matches:
                    match = SemanticMatch(
                        command=alt['example_command'],
                        similarity_score=alt['semantic_score'],
                        intent_type=alt['intent_type'],
                        operation=alt['operation'],
                        language_detected=alt['language_detected']
                    )
                    semantic_matches_for_resolution.append(match)
                
                # Try to resolve ambiguity
                resolved_match = await self.resolve_ambiguity_with_context(
                    user_input, semantic_matches_for_resolution
                )
                
                if resolved_match:
                    # Boost the resolved match's confidence
                    for alt in alternatives_list:
                        if (alt['intent_type'] == resolved_match.intent_type and 
                            alt['operation'] == resolved_match.operation):
                            alt['confidence'] = min(alt['confidence'] + 0.1, 0.98)
                            alt['context_resolved'] = True
                            break
            
            # Sort by semantic score
            alternatives_list.sort(key=lambda x: x['semantic_score'], reverse=True)
            
            # Return top alternatives
            return alternatives_list[:7]
            
        except Exception as e:
            logger.error(f"Error generating semantic alternatives: {e}")
            return []
    
    def expand_synonyms(self, user_input: str) -> List[str]:
        """
        Expand user input with synonyms for better matching.
        
        Args:
            user_input: Original user input
            
        Returns:
            List of expanded variations including synonyms
        """
        variations = [user_input]
        
        # Hungarian-English synonym mappings
        synonym_mappings = {
            # Hungarian synonyms
            'hozz létre': ['készíts', 'generálj', 'állíts össze', 'építsd fel'],
            'készíts': ['hozz létre', 'csinálj', 'állíts össze'],
            'mutasd': ['jelenítsd meg', 'nézd meg', 'tekintsd át', 'olvasd fel'],
            'olvasd': ['mutasd', 'jelenítsd meg', 'nézd meg'],
            'listázd': ['sorold fel', 'mutasd', 'tekintsd át'],
            'rendszerezd': ['szervezd', 'rakd rendbe', 'kategorizáld'],
            'szervezd': ['rendszerezd', 'rendezd', 'tisztítsd meg'],
            'futtasd': ['hajts végre', 'indítsd el', 'aktiválj'],
            
            # English synonyms
            'create': ['make', 'generate', 'build', 'produce', 'construct'],
            'make': ['create', 'build', 'generate', 'produce'],
            'show': ['display', 'view', 'present', 'reveal'],
            'display': ['show', 'view', 'present', 'exhibit'],
            'list': ['show', 'display', 'enumerate', 'catalog'],
            'organize': ['sort', 'arrange', 'structure', 'categorize'],
            'sort': ['organize', 'arrange', 'order', 'tidy'],
            'run': ['execute', 'launch', 'start', 'invoke'],
            'execute': ['run', 'launch', 'invoke', 'trigger'],
            
            # Cross-language mappings
            'file': ['fájl', 'dokumentum'],
            'fájl': ['file', 'document'],
            'folder': ['mappa', 'könyvtár'],
            'mappa': ['folder', 'directory'],
            'command': ['parancs'],
            'parancs': ['command']
        }
        
        # Extract words from input
        words = user_input.lower().split()
        
        # Generate variations by replacing words with synonyms
        for word in words:
            if word in synonym_mappings:
                for synonym in synonym_mappings[word]:
                    # Replace the word with synonym
                    new_variation = user_input.lower().replace(word, synonym)
                    if new_variation not in variations:
                        variations.append(new_variation)
        
        # Generate cross-language variations
        for hungarian, english_list in [
            ('hozz létre', ['create', 'make']),
            ('mutasd', ['show', 'display']),
            ('listázd', ['list', 'show']),
            ('rendszerezd', ['organize', 'sort']),
            ('futtasd', ['run', 'execute'])
        ]:
            if hungarian in user_input.lower():
                for english in english_list:
                    variation = user_input.lower().replace(hungarian, english)
                    if variation not in variations:
                        variations.append(variation)
        
        logger.debug(f"Expanded '{user_input}' to {len(variations)} variations")
        return variations
    
    def cluster_intents(self, semantic_matches: List[SemanticMatch]) -> Dict[str, List[SemanticMatch]]:
        """
        Group semantic matches by intent clusters for better organization.
        
        Args:
            semantic_matches: List of semantic matches to cluster
            
        Returns:
            Dictionary mapping cluster names to lists of matches
        """
        clusters = {}
        
        # Define intent clusters
        intent_clusters = {
            'file_management': ['FILE_OPERATION'],
            'directory_operations': ['DIRECTORY_ORGANIZATION'],
            'system_commands': ['SHELL_COMMAND'],
            'information_queries': ['AI_QUERY'],
            'automation': ['SHELL_COMMAND', 'FILE_OPERATION']
        }
        
        # Group matches by clusters
        for match in semantic_matches:
            match_added = False
            
            for cluster_name, intent_types in intent_clusters.items():
                if match.intent_type in intent_types:
                    if cluster_name not in clusters:
                        clusters[cluster_name] = []
                    clusters[cluster_name].append(match)
                    match_added = True
            
            # Add to miscellaneous if not clustered
            if not match_added:
                if 'miscellaneous' not in clusters:
                    clusters['miscellaneous'] = []
                clusters['miscellaneous'].append(match)
        
        # Sort matches within each cluster by similarity
        for cluster_name in clusters:
            clusters[cluster_name].sort(key=lambda x: x.similarity_score, reverse=True)
        
        return clusters
    
    async def resolve_ambiguity_with_context(self, user_input: str, 
                                           competing_matches: List[SemanticMatch]) -> Optional[SemanticMatch]:
        """
        Resolve ambiguous commands using conversation context and user preferences.
        
        Args:
            user_input: Original user input
            competing_matches: List of matches with similar confidence scores
            
        Returns:
            Best match after context analysis, or None if still ambiguous
        """
        if not competing_matches:
            return None
        
        if len(competing_matches) == 1:
            return competing_matches[0]
        
        # Score matches based on context
        context_scores = []
        
        for match in competing_matches:
            context_score = 0.0
            
            # Check recent command history for similar operations
            for recent_cmd in self.context.recent_commands[-5:]:
                recent_embedding = self._get_embedding(recent_cmd)
                if recent_embedding is not None and match.embedding_vector is not None:
                    similarity = self._calculate_cosine_similarity(recent_embedding, match.embedding_vector)
                    context_score += similarity * 0.1  # Small boost for similar recent commands
            
            # Check for workspace context (if available)
            if self.context.current_workspace:
                workspace_type = self.context.current_workspace.get('type', '')
                
                # Boost file operations in code workspaces
                if workspace_type == 'code' and match.intent_type == 'FILE_OPERATION':
                    context_score += 0.05
                
                # Boost directory operations in organization contexts
                elif workspace_type == 'organization' and match.intent_type == 'DIRECTORY_ORGANIZATION':
                    context_score += 0.05
            
            # Check user preferences
            if self.context.user_preferences:
                preferred_language = self.context.user_preferences.get('language', 'mixed')
                
                if preferred_language == 'hungarian' and match.language_detected == 'hu':
                    context_score += 0.02
                elif preferred_language == 'english' and match.language_detected == 'en':
                    context_score += 0.02
            
            # Calculate final score
            final_score = match.similarity_score + context_score
            context_scores.append((match, final_score))
        
        # Sort by final score and check if there's a clear winner
        context_scores.sort(key=lambda x: x[1], reverse=True)
        
        best_match, best_score = context_scores[0]
        
        # Check if there's a significant difference (> 0.05) with the second best
        if len(context_scores) > 1:
            second_best_score = context_scores[1][1]
            if best_score - second_best_score > 0.05:
                logger.debug(f"Context resolved ambiguity: '{best_match.command}' (score: {best_score:.3f})")
                return best_match
        
        # If still ambiguous, return the original best match
        return best_match
    
    def suggest_default_parameters(self, intent_type: str, operation: str, 
                                 user_input: str) -> Dict[str, Any]:
        """
        Suggest default parameters for commands based on context and patterns.
        
        Args:
            intent_type: Detected intent type
            operation: Detected operation
            user_input: Original user input
            
        Returns:
            Dictionary of suggested parameters
        """
        suggestions = {}
        
        # File operation parameter suggestions
        if intent_type == 'FILE_OPERATION':
            if operation == 'create':
                # Suggest filename based on input or context
                if 'test' in user_input.lower():
                    suggestions['filename'] = 'test_file.txt'
                elif 'config' in user_input.lower():
                    suggestions['filename'] = 'config.json'
                elif 'readme' in user_input.lower():
                    suggestions['filename'] = 'README.md'
                else:
                    suggestions['filename'] = 'new_file.txt'
                
                # Suggest content based on file type
                if suggestions['filename'].endswith('.py'):
                    suggestions['content'] = '#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n\n'
                elif suggestions['filename'].endswith('.md'):
                    suggestions['content'] = '# New Document\n\nCreated by Project-S\n'
            
            elif operation == 'list':
                # Suggest directory based on context
                if 'current' in user_input.lower() or 'itt' in user_input.lower():
                    suggestions['path'] = '.'
                elif 'parent' in user_input.lower() or 'feljebb' in user_input.lower():
                    suggestions['path'] = '..'
                else:
                    suggestions['path'] = '.'
        
        # Directory organization parameter suggestions
        elif intent_type == 'DIRECTORY_ORGANIZATION':
            if operation == 'organize':
                suggestions['target_path'] = '.'
                suggestions['create_subdirs'] = True
                suggestions['backup_before'] = True
                
                # Suggest organization strategy based on input
                if 'type' in user_input.lower() or 'típus' in user_input.lower():
                    suggestions['strategy'] = 'by_type'
                elif 'date' in user_input.lower() or 'dátum' in user_input.lower():
                    suggestions['strategy'] = 'by_date'
                else:
                    suggestions['strategy'] = 'by_type'
        
        # Shell command parameter suggestions
        elif intent_type == 'SHELL_COMMAND':
            if operation == 'execute':
                # Suggest shell based on context
                if 'powershell' in user_input.lower():
                    suggestions['shell'] = 'powershell'
                elif 'cmd' in user_input.lower():
                    suggestions['shell'] = 'cmd'
                else:
                    suggestions['shell'] = 'powershell'  # Default on Windows
        
        logger.debug(f"Suggested parameters for {intent_type}.{operation}: {suggestions}")
        return suggestions
    
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
    
    def optimize_similarity_search(self) -> None:
        """
        Optimize similarity search by creating indexed embeddings for faster retrieval.
        """
        if not self.command_db.embeddings_computed:
            logger.warning("Cannot optimize search - embeddings not computed")
            return
        
        try:
            # Create embedding matrix for vectorized operations
            embeddings_list = []
            metadata_list = []
            
            for cache_key, cached_data in self.command_db.embedding_cache.items():
                embeddings_list.append(cached_data['embedding'])
                metadata_list.append({
                    'command': cached_data['command'],
                    'intent_type': cached_data['intent_type'],
                    'operation': cached_data['operation'],
                    'cache_key': cache_key
                })
            
            if embeddings_list:
                # Convert to numpy array for efficient operations
                self.embedding_matrix = np.array(embeddings_list)
                self.embedding_metadata = metadata_list
                
                # Normalize embeddings for faster cosine similarity computation
                norms = np.linalg.norm(self.embedding_matrix, axis=1, keepdims=True)
                self.normalized_embeddings = self.embedding_matrix / norms
                
                logger.info(f"✅ Optimized similarity search with {len(embeddings_list)} embeddings")
            
        except Exception as e:
            logger.error(f"Failed to optimize similarity search: {e}")
    
    def _fast_similarity_search(self, query_embedding: np.ndarray, top_k: int) -> List[Tuple[int, float]]:
        """
        Perform fast similarity search using vectorized operations.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of top results to return
            
        Returns:
            List of (index, similarity_score) tuples
        """
        if not hasattr(self, 'normalized_embeddings'):
            # Fallback to regular search
            return []
        
        try:
            # Normalize query embedding
            query_norm = np.linalg.norm(query_embedding)
            if query_norm == 0:
                return []
            
            normalized_query = query_embedding / query_norm
            
            # Compute cosine similarities using dot product (since embeddings are normalized)
            similarities = np.dot(self.normalized_embeddings, normalized_query)
            
            # Get top_k indices
            top_indices = np.argpartition(similarities, -top_k)[-top_k:]
            top_indices = top_indices[np.argsort(similarities[top_indices])[::-1]]
            
            return [(int(idx), float(similarities[idx])) for idx in top_indices]
            
        except Exception as e:
            logger.error(f"Fast similarity search failed: {e}")
            return []
    
    def manage_embedding_cache(self) -> None:
        """
        Manage embedding cache to prevent memory issues and improve performance.
        """
        # Clean up old cache entries if cache is too large
        if len(self.embedding_cache) > self.cache_max_size:
            # Keep only the most recently used embeddings
            # This is a simple LRU-like strategy
            
            # For now, just clear the oldest half
            cache_items = list(self.embedding_cache.items())
            cache_size = len(cache_items)
            keep_size = self.cache_max_size // 2
            
            # Keep the last half (more recently added)
            self.embedding_cache = dict(cache_items[-keep_size:])
            
            logger.info(f"Cleaned embedding cache: {cache_size} -> {len(self.embedding_cache)} entries")
        
        # Clean up similarity cache
        if len(self.similarity_cache) > self.cache_max_size:
            self.similarity_cache.clear()
            logger.info("Cleared similarity cache")
    
    def save_embeddings_to_disk(self, filepath: Optional[Path] = None) -> bool:
        """
        Save computed embeddings to disk for faster startup.
        
        Args:
            filepath: Optional path to save embeddings, defaults to config directory
            
        Returns:
            True if saved successfully, False otherwise
        """
        if not self.command_db.embeddings_computed:
            logger.warning("No embeddings to save")
            return False
        
        try:
            if filepath is None:
                cache_dir = Path("cache")
                cache_dir.mkdir(exist_ok=True)
                filepath = cache_dir / f"embeddings_{self.model_name.replace('/', '_')}.pkl"
            
            # Prepare data for saving
            save_data = {
                'model_name': self.model_name,
                'embedding_cache': self.command_db.embedding_cache,
                'timestamp': datetime.now().isoformat(),
                'version': '2.0'  # Phase 2 version
            }
            
            # Save using pickle for efficiency
            with open(filepath, 'wb') as f:
                pickle.dump(save_data, f)
            
            logger.info(f"✅ Saved embeddings to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save embeddings: {e}")
            return False
    
    def load_embeddings_from_disk(self, filepath: Optional[Path] = None) -> bool:
        """
        Load precomputed embeddings from disk.
        
        Args:
            filepath: Optional path to load embeddings from
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if filepath is None:
                cache_dir = Path("cache")
                filepath = cache_dir / f"embeddings_{self.model_name.replace('/', '_')}.pkl"
            
            if not filepath.exists():
                logger.debug(f"No cached embeddings found at {filepath}")
                return False
            
            # Load data
            with open(filepath, 'rb') as f:
                save_data = pickle.load(f)
            
            # Verify compatibility
            if save_data.get('model_name') != self.model_name:
                logger.warning(f"Model mismatch in cached embeddings: {save_data.get('model_name')} vs {self.model_name}")
                return False
            
            # Load embeddings
            self.command_db.embedding_cache = save_data['embedding_cache']
            self.command_db.embeddings_computed = True
            
            # Optimize search if embeddings loaded
            self.optimize_similarity_search()
            
            logger.info(f"✅ Loaded {len(self.command_db.embedding_cache)} embeddings from cache")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load embeddings from disk: {e}")
            return False
    
    def create_offline_fallback(self) -> Dict[str, Any]:
        """
        Create a lightweight offline fallback using pre-computed similarity mappings.
        
        Returns:
            Dictionary containing offline similarity mappings
        """
        fallback_mappings = {
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
            },
            'cross_language_mappings': {
                'file': 'fájl', 'fájl': 'file',
                'folder': 'mappa', 'mappa': 'folder',
                'command': 'parancs', 'parancs': 'command'
            }
        }
        
        return fallback_mappings
    
    def offline_semantic_match(self, user_input: str) -> List[Dict[str, Any]]:
        """
        Provide semantic matching without transformer models using pattern-based fallback.
        
        Args:
            user_input: User input to match
            
        Returns:
            List of matches using offline patterns
        """
        fallback = self.create_offline_fallback()
        matches = []
        
        user_input_lower = user_input.lower()
        
        # Check Hungarian patterns
        for pattern, match_data in fallback['hungarian_patterns'].items():
            if pattern in user_input_lower:
                matches.append({
                    'command': pattern,
                    'intent_type': match_data['intent'],
                    'operation': match_data['operation'],
                    'confidence': match_data['confidence'],
                    'similarity_score': match_data['confidence'],
                    'offline_match': True,
                    'language_detected': 'hu'
                })
        
        # Check English patterns
        for pattern, match_data in fallback['english_patterns'].items():
            if pattern in user_input_lower:
                matches.append({
                    'command': pattern,
                    'intent_type': match_data['intent'],
                    'operation': match_data['operation'],
                    'confidence': match_data['confidence'],
                    'similarity_score': match_data['confidence'],
                    'offline_match': True,
                    'language_detected': 'en'
                })
        
        # Sort by confidence and remove duplicates
        unique_matches = {}
        for match in matches:
            key = f"{match['intent_type']}.{match['operation']}"
            if key not in unique_matches or match['confidence'] > unique_matches[key]['confidence']:
                unique_matches[key] = match
        
        result = list(unique_matches.values())
        result.sort(key=lambda x: x['confidence'], reverse=True)
        
        logger.debug(f"Offline semantic matching found {len(result)} matches for '{user_input}'")
        return result[:5]  # Return top 5 matches
# Global instance for easy access
semantic_engine = SemanticEngine()
