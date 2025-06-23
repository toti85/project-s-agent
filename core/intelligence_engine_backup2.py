"""
PROJECT-S Intelligence Engine - Enhanced Intent Detection with Confidence Scoring
================================================================================
This module provides advanced natural language understanding capabilities for the
Project-S Multi-Model system, building on the existing intelligent_command_parser.

Key Features:
1. Intent Confidence Scoring (0.0-1.0)
2. Fuzzy String Matching for partial commands
3. Pattern Strength Analysis
4. Confidence-based execution thresholds
5. Uncertainty handling and user confirmation requests

Integration Strategy:
- Extends existing intelligent_command_parser() without breaking changes
- Maintains backward compatibility with current command patterns
- Adds optional confidence scoring and enhanced matching
"""

import logging
import re
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from difflib import SequenceMatcher
from dataclasses import dataclass, field

# Import configuration system
try:
    from core.intelligence_config import get_intelligence_config, IntelligenceConfig
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

# PHASE 2: Import semantic engine
try:
    from core.semantic_engine import semantic_engine, SemanticMatch
    SEMANTIC_ENGINE_AVAILABLE = True
except ImportError:
    SEMANTIC_ENGINE_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class IntentMatch:
    """Represents a detected intent with confidence scoring and semantic analysis."""
    intent_type: str
    confidence: float
    operation: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    matched_patterns: List[str] = field(default_factory=list)
    extraction_details: Dict[str, Any] = field(default_factory=dict)
    alternative_interpretations: List[Dict[str, Any]] = field(default_factory=list)
    
    # PHASE 2: Semantic enhancements
    semantic_details: Dict[str, Any] = field(default_factory=dict)
    semantic_confidence: float = 0.0
    semantic_alternatives: List[Dict[str, Any]] = field(default_factory=list)
    language_detected: str = "unknown"

@dataclass
class ConfidenceThresholds:
    """Configuration for confidence-based decision making."""
    auto_execute: float = 0.85  # Execute immediately without confirmation
    confirm_execute: float = 0.60  # Ask for user confirmation
    suggest_alternatives: float = 0.40  # Show alternatives and ask user
    fallback_to_ai: float = 0.30  # Use AI processing for low confidence
    
    @classmethod
    def from_config(cls, config: 'IntelligenceConfig') -> 'ConfidenceThresholds':
        """Create thresholds from intelligence config."""
        return cls(
            auto_execute=config.auto_execute_threshold,
            confirm_execute=config.confirm_execute_threshold,            suggest_alternatives=config.suggest_alternatives_threshold,
            fallback_to_ai=config.fallback_to_ai_threshold
        )

class IntelligenceEngine:
    """
    Enhanced intelligence engine for natural language command understanding.
    Provides confidence scoring and advanced pattern matching capabilities.
    """
    
    def __init__(self):
        """Initialize the intelligence engine with pattern databases."""
        # Load configuration
        if CONFIG_AVAILABLE:
            self.config = get_intelligence_config()
            self.confidence_thresholds = ConfidenceThresholds.from_config(self.config)
            logger.info("Intelligence Engine initialized with configuration system")
        else:
            self.config = None
            self.confidence_thresholds = ConfidenceThresholds()
            logger.warning("Configuration system not available, using defaults")
        
        # PHASE 2: Initialize semantic engine integration
        self.semantic_available = SEMANTIC_ENGINE_AVAILABLE and (
            self.config.enable_semantic_matching if self.config else True
        )
        
        if self.semantic_available:
            logger.info("✅ Semantic engine integration enabled")
        else:
            logger.info("⚠️ Semantic engine integration disabled or unavailable")
        
        # Enhanced pattern databases with weights and variations
        self.intent_patterns = {
            "DIRECTORY_ORGANIZATION": {
                "primary_patterns": [
                    ("rendszerezd", 1.0), ("szervezd", 1.0), ("organize", 1.0), 
                    ("rendezd", 0.9), ("kategorizáld", 0.9), ("clean up", 0.8),
                    ("tidy", 0.7), ("arrange", 0.7)
                ],
                "context_words": [
                    ("mappát", 0.3), ("folder", 0.3), ("mappa", 0.3), 
                    ("directory", 0.3), ("files", 0.2), ("fájlok", 0.2)
                ],
                "negative_patterns": ["ne", "don't", "stop", "ne szervezd"]
            },
            
            "FILE_OPERATION": {
                "create_patterns": [
                    ("hozz létre", 1.0), ("create file", 1.0), ("létrehozz", 0.9),
                    ("készíts", 0.9), ("new file", 0.8), ("make", 0.7),
                    ("generate", 0.6), ("build", 0.5)
                ],
                "read_patterns": [
                    ("olvasd", 1.0), ("read file", 1.0), ("mutasd", 0.9),
                    ("tartalom", 0.8), ("show", 0.7), ("display", 0.7),
                    ("view", 0.6), ("cat", 0.8), ("type", 0.6)
                ],
                "list_patterns": [
                    ("listázd", 1.0), ("list", 1.0), ("ls", 0.9), ("dir", 0.9),
                    ("show files", 0.8), ("fájlok", 0.7), ("contents", 0.6)
                ],
                "context_words": [
                    ("fájlt", 0.3), ("file", 0.3), ("document", 0.2),
                    ("text", 0.2), (".txt", 0.4), (".py", 0.4), (".json", 0.4)
                ]
            },
            
            "SHELL_COMMAND": {
                "primary_patterns": [
                    ("futtat", 1.0), ("execute", 1.0), ("run", 1.0),
                    ("powershell", 0.9), ("cmd", 0.9), ("command", 0.8),
                    ("terminal", 0.7), ("shell", 0.7)
                ],
                "context_words": [
                    ("parancs", 0.2), ("script", 0.2), ("batch", 0.2)
                ]
            }
        }
        
        # File extension patterns for better filename detection
        self.file_extensions = {
            'text': ['.txt', '.md', '.rst', '.log'],
            'code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c'],
            'data': ['.json', '.xml', '.csv', '.yaml', '.yml'],
            'config': ['.ini', '.conf', '.cfg', '.toml'],
            'document': ['.doc', '.docx', '.pdf', '.rtf']
        }
        
        logger.info("Intelligence Engine initialized with enhanced pattern matching")
    
    def calculate_fuzzy_similarity(self, text1: str, text2: str) -> float:
        """Calculate fuzzy string similarity using SequenceMatcher."""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def extract_filename_with_confidence(self, user_input: str) -> Tuple[Optional[str], float]:
        """
        Extract filename from user input with confidence scoring.
        
        Returns:
            Tuple of (filename, confidence_score)
        """
        words = user_input.split()
        filename_candidates = []
        
        for word in words:
            confidence = 0.0
            
            # Check for file extensions
            if '.' in word and len(word) > 3:
                extension = '.' + word.split('.')[-1].lower()
                
                # High confidence for known extensions
                for ext_category, extensions in self.file_extensions.items():
                    if extension in extensions:
                        confidence = 0.9
                        break
                else:
                    # Medium confidence for unknown extensions
                    if len(extension) <= 5:  # Reasonable extension length
                        confidence = 0.6
                
                filename_candidates.append((word, confidence))
            
            # Check for quoted filenames
            elif word.startswith('"') and word.endswith('"'):
                filename_candidates.append((word.strip('"'), 0.8))
            elif word.startswith("'") and word.endswith("'"):
                filename_candidates.append((word.strip("'"), 0.8))
        
        # Return the candidate with highest confidence
        if filename_candidates:
            return max(filename_candidates, key=lambda x: x[1])
        
        return None, 0.0
    
    def calculate_pattern_confidence(self, user_input: str, patterns: List[Tuple[str, float]]) -> Tuple[float, List[str]]:
        """
        Calculate confidence based on pattern matching.
        
        Returns:
            Tuple of (confidence_score, matched_patterns)
        """
        user_input_lower = user_input.lower()
        max_confidence = 0.0
        matched_patterns = []
        
        for pattern, weight in patterns:
            # Exact match
            if pattern in user_input_lower:
                confidence = weight
                matched_patterns.append(f"exact:{pattern}")
            else:
                # Fuzzy matching for partial matches
                words = user_input_lower.split()
                for word in words:
                    similarity = self.calculate_fuzzy_similarity(word, pattern)
                    if similarity > 0.7:  # Threshold for fuzzy match
                        confidence = weight * similarity * 0.8  # Reduce confidence for fuzzy matches
                        matched_patterns.append(f"fuzzy:{pattern}({similarity:.2f})")
                        break
                else:
                    confidence = 0.0
            
            max_confidence = max(max_confidence, confidence)
        
        return max_confidence, matched_patterns
    
    def detect_directory_organization_intent(self, user_input: str) -> IntentMatch:
        """Detect directory organization intent with confidence scoring."""
        patterns = self.intent_patterns["DIRECTORY_ORGANIZATION"]
        
        # Check primary patterns
        primary_confidence, primary_matches = self.calculate_pattern_confidence(
            user_input, patterns["primary_patterns"]
        )
        
        # Check context words for additional confidence
        context_confidence, context_matches = self.calculate_pattern_confidence(
            user_input, patterns["context_words"]
        )
        
        # Check for negative patterns (reduce confidence)
        negative_confidence = 0.0
        for neg_pattern in patterns["negative_patterns"]:
            if neg_pattern in user_input.lower():
                negative_confidence = 0.5
                break
        
        # Calculate final confidence
        final_confidence = primary_confidence + (context_confidence * 0.3) - negative_confidence
        final_confidence = max(0.0, min(1.0, final_confidence))  # Clamp to [0, 1]
        
        # Extract target folder
        words = user_input.split()
        target_folder = None
        extraction_confidence = 0.0
        
        for i, word in enumerate(words):
            if word.lower() in ["mappát", "folder", "mappa", "directory"] and i > 0:
                target_folder = words[i-1]
                extraction_confidence = 0.8
                break
            elif word.lower() in ["rendszerezd", "szervezd", "organize", "rendezd"] and i < len(words) - 1:
                next_word = words[i+1]
                if next_word.lower() not in ["a", "az", "the"]:
                    target_folder = next_word
                    extraction_confidence = 0.6
                elif i < len(words) - 2:
                    target_folder = words[i+2]
                    extraction_confidence = 0.5
                break
        
        if not target_folder:
            target_folder = "."
            extraction_confidence = 0.3  # Default assumption
        
        return IntentMatch(
            intent_type="DIRECTORY_ORGANIZATION",
            confidence=final_confidence,
            operation="organize",
            parameters={"path": target_folder},
            matched_patterns=primary_matches + context_matches,
            extraction_details={
                "target_folder": target_folder,
                "extraction_confidence": extraction_confidence,
                "primary_confidence": primary_confidence,
                "context_confidence": context_confidence
            }
        )
    
    def detect_file_operation_intent(self, user_input: str) -> Optional[IntentMatch]:
        """Detect file operation intent with confidence scoring."""
        patterns = self.intent_patterns["FILE_OPERATION"]
        user_input_lower = user_input.lower()
        
        # Detect operation type
        operation_type = None
        operation_confidence = 0.0
        matched_patterns = []
        
        # Check create patterns
        create_conf, create_matches = self.calculate_pattern_confidence(
            user_input, patterns["create_patterns"]
        )
        if create_conf > operation_confidence:
            operation_type = "create"
            operation_confidence = create_conf
            matched_patterns = create_matches
        
        # Check read patterns
        read_conf, read_matches = self.calculate_pattern_confidence(
            user_input, patterns["read_patterns"]
        )
        if read_conf > operation_confidence:
            operation_type = "read"
            operation_confidence = read_conf
            matched_patterns = read_matches
        
        # Check list patterns
        list_conf, list_matches = self.calculate_pattern_confidence(
            user_input, patterns["list_patterns"]
        )
        if list_conf > operation_confidence:
            operation_type = "list"
            operation_confidence = list_conf
            matched_patterns = list_matches
        
        if operation_type is None:
            return None
        
        # Extract filename/path with confidence
        filename, filename_confidence = self.extract_filename_with_confidence(user_input)
        
        # Calculate context confidence
        context_confidence, context_matches = self.calculate_pattern_confidence(
            user_input, patterns["context_words"]
        )
        
        # Calculate final confidence
        final_confidence = operation_confidence + (context_confidence * 0.2) + (filename_confidence * 0.1)
        final_confidence = max(0.0, min(1.0, final_confidence))
        
        # Set default values based on operation
        if operation_type == "create" and not filename:
            filename = "project_s_test.txt"
            filename_confidence = 0.3
        elif operation_type == "list" and not filename:
            filename = "."
            filename_confidence = 0.8
        
        parameters = {"path": filename} if filename else {}
        
        # Add content for create operations
        if operation_type == "create" and filename:
            parameters["content"] = (
                f"# Fájl létrehozva a Project-S Multi-Model rendszer által\n"
                f"# Időpont: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"# Felhasználói parancs: {user_input}\n"
            )
        
        return IntentMatch(
            intent_type="FILE_OPERATION",
            confidence=final_confidence,
            operation=operation_type,
            parameters=parameters,
            matched_patterns=matched_patterns + context_matches,
            extraction_details={
                "filename": filename,
                "filename_confidence": filename_confidence,
                "operation_confidence": operation_confidence,
                "context_confidence": context_confidence
            }
        )
    
    def detect_shell_command_intent(self, user_input: str) -> Optional[IntentMatch]:
        """Detect shell command intent with confidence scoring."""
        patterns = self.intent_patterns["SHELL_COMMAND"]
        
        # Check primary patterns
        primary_confidence, primary_matches = self.calculate_pattern_confidence(
            user_input, patterns["primary_patterns"]
        )
        
        if primary_confidence < 0.3:
            return None
        
        # Extract command
        command = user_input
        extraction_confidence = 0.5
        
        user_input_lower = user_input.lower()
        if "powershell" in user_input_lower:
            command = user_input[user_input_lower.find("powershell") + 10:].strip()
            extraction_confidence = 0.8
        elif "cmd" in user_input_lower:
            command = user_input[user_input_lower.find("cmd") + 3:].strip()
            extraction_confidence = 0.8
        
        # Calculate context confidence
        context_confidence, context_matches = self.calculate_pattern_confidence(
            user_input, patterns["context_words"]
        )
        
        final_confidence = primary_confidence + (context_confidence * 0.2) + (extraction_confidence * 0.1)
        final_confidence = max(0.0, min(1.0, final_confidence))
        
        return IntentMatch(
            intent_type="SHELL_COMMAND",
            confidence=final_confidence,
            operation="execute",
            parameters={"command": command},
            matched_patterns=primary_matches + context_matches,
            extraction_details={
                "command": command,
                "extraction_confidence": extraction_confidence,                "primary_confidence": primary_confidence
            }
        )
    
    async def analyze_intent_with_confidence(self, user_input: str) -> IntentMatch:
        """
        Main method to analyze user intent with confidence scoring and semantic enhancement.
        Returns the highest confidence intent match with semantic analysis.
        """
        candidates = []
        
        # Test directory organization
        dir_intent = self.detect_directory_organization_intent(user_input)
        if dir_intent.confidence > 0.1:
            candidates.append(dir_intent)
        
        # Test file operations
        file_intent = self.detect_file_operation_intent(user_input)
        if file_intent and file_intent.confidence > 0.1:
            candidates.append(file_intent)
        
        # Test shell commands
        shell_intent = self.detect_shell_command_intent(user_input)
        if shell_intent and shell_intent.confidence > 0.1:
            candidates.append(shell_intent)
        
        # Select best candidate from pattern matching
        if candidates:
            best_match = max(candidates, key=lambda x: x.confidence)
            
            # PHASE 2: Enhance with semantic analysis
            if self.semantic_available:
                try:
                    enhanced_confidence, semantic_details = await semantic_engine.enhance_intent_with_semantics(
                        user_input, best_match.confidence, best_match.intent_type, best_match.operation
                    )
                    
                    # Update confidence and add semantic information
                    best_match.confidence = enhanced_confidence
                    best_match.semantic_details = semantic_details
                    best_match.semantic_confidence = semantic_details.get('top_match', {}).get('similarity', 0.0)
                    best_match.language_detected = semantic_details.get('language_detected', 'unknown')
                    
                    # Get semantic alternatives if configured
                    if self.config and self.config.max_semantic_alternatives > 0:
                        semantic_alternatives = await semantic_engine.suggest_semantic_alternatives(user_input)
                        best_match.semantic_alternatives = semantic_alternatives[:self.config.max_semantic_alternatives]
                    
                    # Update context in semantic engine
                    semantic_engine.update_context(user_input, {
                        'intent_type': best_match.intent_type,
                        'operation': best_match.operation,
                        'confidence': best_match.confidence
                    })
                    
                    # Log semantic analysis if configured
                    if self.config and self.config.log_semantic_matches:
                        logger.debug(f"Semantic analysis: {semantic_details}")
                        
                except Exception as e:
                    logger.error(f"Error in semantic enhancement: {e}")
                    # Continue with pattern-based match if semantic fails
            
            # Add alternative interpretations from pattern matching
            alternatives = [c for c in candidates if c != best_match and c.confidence > 0.3]
            best_match.alternative_interpretations = [
                {
                    "intent_type": alt.intent_type,
                    "operation": alt.operation,
                    "confidence": alt.confidence,
                    "parameters": alt.parameters
                }
                for alt in alternatives
            ]
            
            return best_match
        
        # Fallback to AI query with semantic enhancement
        fallback_match = IntentMatch(
            intent_type="AI_QUERY",
            confidence=0.2,  # Low confidence indicates fallback
            operation="query",
            parameters={"query": user_input},
            matched_patterns=[],
            extraction_details={"fallback_reason": "No specific intent patterns matched"}
        )
        
        # PHASE 2: Try semantic matching for fallback cases
        if self.semantic_available:
            try:
                semantic_alternatives = await semantic_engine.suggest_semantic_alternatives(user_input)
                if semantic_alternatives:
                    # Use the best semantic match if it's good enough
                    best_semantic = semantic_alternatives[0]
                    if best_semantic['semantic_score'] >= 0.7:  # High semantic confidence
                        fallback_match.intent_type = best_semantic['intent_type']
                        fallback_match.operation = best_semantic['operation']
                        fallback_match.confidence = best_semantic['confidence']
                        fallback_match.semantic_confidence = best_semantic['semantic_score']
                        fallback_match.language_detected = best_semantic['language_detected']
                        fallback_match.semantic_details = {
                            "semantic_fallback": True,
                            "semantic_score": best_semantic['semantic_score'],
                            "example_command": best_semantic['example_command']
                        }
                        
                        # Add suggested parameters if available
                        if 'suggested_parameters' in best_semantic:
                            fallback_match.parameters.update(best_semantic['suggested_parameters'])
                    
                    fallback_match.semantic_alternatives = semantic_alternatives
                    
            except Exception as e:
                logger.error(f"Error in semantic fallback: {e}")
        
        return fallback_match
    
    def should_request_confirmation(self, intent_match: IntentMatch) -> bool:
        """Determine if user confirmation is needed based on confidence."""
        return (self.confidence_thresholds.confirm_execute <= 
                intent_match.confidence < 
                self.confidence_thresholds.auto_execute)
    
    def should_suggest_alternatives(self, intent_match: IntentMatch) -> bool:
        """Determine if alternatives should be suggested."""
        return (self.confidence_thresholds.suggest_alternatives <= 
                intent_match.confidence < 
                self.confidence_thresholds.confirm_execute)
    
    def should_fallback_to_ai(self, intent_match: IntentMatch) -> bool:
        """Determine if should fallback to AI processing."""
        return intent_match.confidence < self.confidence_thresholds.fallback_to_ai
    
    def format_confidence_report(self, intent_match: IntentMatch) -> str:
        """Format a human-readable confidence report."""
        confidence_level = "Unknown"
        if intent_match.confidence >= self.confidence_thresholds.auto_execute:
            confidence_level = "Very High"
        elif intent_match.confidence >= self.confidence_thresholds.confirm_execute:
            confidence_level = "High"
        elif intent_match.confidence >= self.confidence_thresholds.suggest_alternatives:
            confidence_level = "Medium"
        elif intent_match.confidence >= self.confidence_thresholds.fallback_to_ai:
            confidence_level = "Low"
        else:
            confidence_level = "Very Low"
        
        report = [
            f"🎯 Intent Analysis Report",
            f"   Intent: {intent_match.intent_type}",
            f"   Operation: {intent_match.operation}",
            f"   Confidence: {intent_match.confidence:.2f} ({confidence_level})",
            f"   Matched Patterns: {', '.join(intent_match.matched_patterns) if intent_match.matched_patterns else 'None'}"
        ]
        
        if intent_match.alternative_interpretations:
            report.append(f"   Alternatives: {len(intent_match.alternative_interpretations)} found")
        
        return "\n".join(report)

# Global instance for easy access
intelligence_engine = IntelligenceEngine()
