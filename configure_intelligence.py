"""
PROJECT-S Intelligence Configuration Interface
=============================================
Simple interface for configuring the enhanced intelligence system.
"""

import json
from pathlib import Path
from core.intelligence_config import IntelligenceConfig, PROFILES, get_intelligence_config

def display_current_config():
    """Display the current intelligence configuration."""
    config = get_intelligence_config()
    
    print("🎯 PROJECT-S Intelligence Configuration")
    print("=" * 50)
    print(f"Auto Execute Threshold:      {config.auto_execute_threshold:.2f}")
    print(f"Confirm Execute Threshold:   {config.confirm_execute_threshold:.2f}")
    print(f"Suggest Alternatives:        {config.suggest_alternatives_threshold:.2f}")
    print(f"Fallback to AI:              {config.fallback_to_ai_threshold:.2f}")
    print()
    print(f"Fuzzy Match Threshold:       {config.fuzzy_match_threshold:.2f}")
    print(f"Fuzzy Confidence Reduction:  {config.fuzzy_confidence_reduction:.2f}")
    print()
    print(f"Debug Logging:               {config.enable_debug_logging}")
    print(f"Log Confidence Reports:      {config.log_confidence_reports}")
    print(f"Enable Fuzzy Matching:       {config.enable_fuzzy_matching}")

def configure_intelligence_system():
    """Interactive configuration of the intelligence system."""
    
    print("🎯 PROJECT-S Intelligence System Configuration")
    print("=" * 55)
    
    # Show available profiles
    print("\nAvailable Profiles:")
    for name, profile in PROFILES.items():
        print(f"  {name}: Auto={profile.auto_execute_threshold:.2f}, Confirm={profile.confirm_execute_threshold:.2f}")
    
    # Profile selection
    while True:
        profile_choice = input(f"\nSelect profile ({'/'.join(PROFILES.keys())}) or 'custom': ").strip().lower()
        
        if profile_choice in PROFILES:
            config = PROFILES[profile_choice]
            print(f"✅ Selected {profile_choice} profile")
            break
        elif profile_choice == 'custom':
            config = create_custom_config()
            break
        else:
            print("❌ Invalid profile. Please try again.")
    
    # Display selected configuration
    print("\n📋 Selected Configuration:")
    print("-" * 30)
    print(f"Auto Execute:         {config.auto_execute_threshold:.2f}")
    print(f"Confirm Execute:      {config.confirm_execute_threshold:.2f}")
    print(f"Suggest Alternatives: {config.suggest_alternatives_threshold:.2f}")
    print(f"Fallback to AI:       {config.fallback_to_ai_threshold:.2f}")
    
    # Save configuration
    save_choice = input("\nSave this configuration? (y/n): ").strip().lower()
    if save_choice in ['y', 'yes']:
        # Create config directory
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)
        
        # Save configuration
        config_file = config_dir / "intelligence_config.json"
        config.save_to_file(config_file)
        print(f"✅ Configuration saved to {config_file}")
    else:
        print("⏸️ Configuration not saved")

def create_custom_config():
    """Create a custom configuration interactively."""
    print("\n🛠️ Custom Configuration")
    print("-" * 25)
    
    config = IntelligenceConfig()
    
    # Confidence thresholds
    print("\nConfidence Thresholds (0.0-1.0):")
    
    try:
        auto_exec = float(input(f"Auto Execute Threshold [{config.auto_execute_threshold}]: ") or config.auto_execute_threshold)
        confirm_exec = float(input(f"Confirm Execute Threshold [{config.confirm_execute_threshold}]: ") or config.confirm_execute_threshold)
        suggest_alt = float(input(f"Suggest Alternatives Threshold [{config.suggest_alternatives_threshold}]: ") or config.suggest_alternatives_threshold)
        fallback_ai = float(input(f"Fallback to AI Threshold [{config.fallback_to_ai_threshold}]: ") or config.fallback_to_ai_threshold)
        
        # Validate thresholds
        if not (0.0 <= auto_exec <= 1.0 and 0.0 <= confirm_exec <= 1.0 and 
                0.0 <= suggest_alt <= 1.0 and 0.0 <= fallback_ai <= 1.0):
            raise ValueError("Thresholds must be between 0.0 and 1.0")
        
        if not (auto_exec >= confirm_exec >= suggest_alt >= fallback_ai):
            raise ValueError("Thresholds must be in descending order")
        
        config.auto_execute_threshold = auto_exec
        config.confirm_execute_threshold = confirm_exec
        config.suggest_alternatives_threshold = suggest_alt
        config.fallback_to_ai_threshold = fallback_ai
        
    except ValueError as e:
        print(f"❌ Invalid input: {e}")
        print("Using default values")
    
    # Debug settings
    debug_choice = input(f"\nEnable debug logging? (y/n) [{config.enable_debug_logging}]: ").strip().lower()
    if debug_choice in ['y', 'yes']:
        config.enable_debug_logging = True
    elif debug_choice in ['n', 'no']:
        config.enable_debug_logging = False
    
    return config

def test_configuration():
    """Test the current configuration with sample commands."""
    from core.intelligence_engine import intelligence_engine
    
    print("\n🧪 Testing Current Configuration")
    print("=" * 40)
    
    test_commands = [
        ("hozz létre test.txt", "High confidence file creation"),
        ("create something", "Ambiguous command"),
        ("organizze folder", "Typo in command"),
        ("list files", "Clear list command"),
        ("random text", "Random input")
    ]
    
    for command, description in test_commands:
        print(f"\n📝 Test: {command} ({description})")
        try:
            import asyncio
            intent_match = asyncio.run(intelligence_engine.analyze_intent_with_confidence(command))
            
            confidence_level = "Unknown"
            if intent_match.confidence >= 0.85:
                confidence_level = "Very High ✅"
            elif intent_match.confidence >= 0.60:
                confidence_level = "High ⚠️"
            elif intent_match.confidence >= 0.40:
                confidence_level = "Medium 💡"
            elif intent_match.confidence >= 0.30:
                confidence_level = "Low 🤖"
            else:
                confidence_level = "Very Low ❌"
            
            print(f"   Intent: {intent_match.intent_type}")
            print(f"   Confidence: {intent_match.confidence:.2f} ({confidence_level})")
            
            # Show recommendations
            if intelligence_engine.should_request_confirmation(intent_match):
                print("   Recommendation: Request confirmation")
            elif intelligence_engine.should_suggest_alternatives(intent_match):
                print("   Recommendation: Suggest alternatives")
            elif intelligence_engine.should_fallback_to_ai(intent_match):
                print("   Recommendation: Use AI processing")
            else:
                print("   Recommendation: Auto-execute")
                
        except Exception as e:
            print(f"   Error: {e}")

def main():
    """Main configuration interface."""
    while True:
        print("\n🎯 PROJECT-S Intelligence Configuration")
        print("=" * 45)
        print("1. Display current configuration")
        print("2. Configure intelligence system")
        print("3. Test current configuration")
        print("4. Reset to default")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            display_current_config()
        elif choice == '2':
            configure_intelligence_system()
        elif choice == '3':
            test_configuration()
        elif choice == '4':
            config_dir = Path("config")
            config_file = config_dir / "intelligence_config.json"
            if config_file.exists():
                config_file.unlink()
                print("✅ Configuration reset to default")
            else:
                print("ℹ️ Already using default configuration")
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
