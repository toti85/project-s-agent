"""
PROJECT-S Intelligence Configuration
===================================
Configuration settings for the enhanced intelligence system.
Allows tuning of confidence thresholds and pattern matching behavior.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class IntelligenceConfig:
    """Configuration settings for the intelligence engine."""
    
    # Confidence thresholds
    auto_execute_threshold: float = 0.85
    confirm_execute_threshold: float = 0.60
    suggest_alternatives_threshold: float = 0.40
    fallback_to_ai_threshold: float = 0.30
    
    # Fuzzy matching settings
    fuzzy_match_threshold: float = 0.7
    fuzzy_confidence_reduction: float = 0.8
    
    # Pattern matching weights
    primary_pattern_weight: float = 1.0
    context_pattern_weight: float = 0.3
    filename_extraction_weight: float = 0.1
    
    # PHASE 2: Semantic similarity settings
    enable_semantic_matching: bool = True
    semantic_similarity_threshold: float = 0.6
    semantic_boost_factor: float = 0.2
    context_boost_factor: float = 0.15
    multi_language_boost: float = 0.1
    semantic_cache_max_size: int = 1000
    
    # Sentence transformer model settings
    sentence_transformer_model: str = "all-MiniLM-L6-v2"
    enable_offline_fallback: bool = True
    precompute_embeddings: bool = True
    
    # Semantic alternatives configuration
    max_semantic_alternatives: int = 5
    alternative_confidence_reduction: float = 0.1
    cross_language_matching: bool = True
    
    # Debug and logging
    enable_debug_logging: bool = False
    log_confidence_reports: bool = True
    log_pattern_matches: bool = False
    log_semantic_matches: bool = False  # New for Phase 2
    
    # Language preferences
    prefer_hungarian: bool = True
    prefer_english: bool = True
    
    # Extended pattern matching
    enable_fuzzy_matching: bool = True
    enable_synonym_detection: bool = True  # Now available in Phase 2
    enable_context_awareness: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IntelligenceConfig':
        """Create configuration from dictionary."""
        return cls(**data)
    
    def save_to_file(self, filepath: Path) -> None:
        """Save configuration to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, filepath: Path) -> 'IntelligenceConfig':
        """Load configuration from JSON file."""
        if not filepath.exists():
            # Create default config if file doesn't exist
            config = cls()
            config.save_to_file(filepath)
            return config
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)

# Configuration profiles for different use cases
PROFILES = {
    "conservative": IntelligenceConfig(
        auto_execute_threshold=0.95,
        confirm_execute_threshold=0.80,
        suggest_alternatives_threshold=0.60,
        fallback_to_ai_threshold=0.40,
        enable_debug_logging=False,
        # Conservative semantic settings
        enable_semantic_matching=True,
        semantic_similarity_threshold=0.75,
        semantic_boost_factor=0.15,
        max_semantic_alternatives=3
    ),
    
    "balanced": IntelligenceConfig(
        auto_execute_threshold=0.85,
        confirm_execute_threshold=0.60,
        suggest_alternatives_threshold=0.40,
        fallback_to_ai_threshold=0.30,
        enable_debug_logging=False,
        # Balanced semantic settings (defaults)
        enable_semantic_matching=True,
        semantic_similarity_threshold=0.6,
        semantic_boost_factor=0.2,
        max_semantic_alternatives=5
    ),
    
    "aggressive": IntelligenceConfig(
        auto_execute_threshold=0.75,
        confirm_execute_threshold=0.50,
        suggest_alternatives_threshold=0.30,
        fallback_to_ai_threshold=0.20,
        enable_debug_logging=False,
        # Aggressive semantic settings
        enable_semantic_matching=True,
        semantic_similarity_threshold=0.5,
        semantic_boost_factor=0.25,
        max_semantic_alternatives=7,
        cross_language_matching=True
    ),
    
    "development": IntelligenceConfig(
        auto_execute_threshold=0.85,
        confirm_execute_threshold=0.60,
        suggest_alternatives_threshold=0.40,
        fallback_to_ai_threshold=0.30,
        enable_debug_logging=True,
        log_confidence_reports=True,
        log_pattern_matches=True,
        log_semantic_matches=True,  # Debug semantic matching
        # Development semantic settings
        enable_semantic_matching=True,
        semantic_similarity_threshold=0.6,
        semantic_boost_factor=0.2,
        max_semantic_alternatives=5
    ),
    
    "offline": IntelligenceConfig(
        auto_execute_threshold=0.85,
        confirm_execute_threshold=0.60,
        suggest_alternatives_threshold=0.40,
        fallback_to_ai_threshold=0.30,
        enable_debug_logging=False,
        # Offline mode - disable semantic features
        enable_semantic_matching=False,
        enable_offline_fallback=True,
        precompute_embeddings=False
    )
}

def get_intelligence_config(profile: str = "balanced") -> IntelligenceConfig:
    """Get intelligence configuration by profile name."""
    if profile in PROFILES:
        return PROFILES[profile]
    
    # Try to load from file
    config_path = Path("config/intelligence_config.json")
    if config_path.exists():
        return IntelligenceConfig.load_from_file(config_path)
    
    # Return default balanced profile
    return PROFILES["balanced"]

def save_current_config(config: IntelligenceConfig, name: Optional[str] = None) -> None:
    """Save current configuration to file."""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    if name:
        filepath = config_dir / f"intelligence_config_{name}.json"
    else:
        filepath = config_dir / "intelligence_config.json"
    
    config.save_to_file(filepath)

# Default configuration instance
default_config = get_intelligence_config("balanced")
