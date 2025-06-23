#!/usr/bin/env python3
"""
Test script to verify AI functionality and check for API requests
"""
import subprocess
import sys
import time
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_ai_test_interactive():
    """Run interactive AI test to see if API requests are made"""
    logger.info("🚀 Starting AI functionality test...")
    
    try:
        # Test 1: Simple AI query
        logger.info("Test 1: Testing AI with simple question...")
        process = subprocess.Popen(
            ['python', 'main.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd='.',
            bufsize=1
        )
        
        # Wait for system to initialize
        time.sleep(5)
        
        # Send AI query
        test_query = "What is artificial intelligence? Give a brief answer.\n"
        logger.info(f"Sending query: {test_query.strip()}")
        
        process.stdin.write(test_query)
        process.stdin.flush()
        
        # Wait for response
        logger.info("Waiting for AI response...")
        time.sleep(30)  # Give time for API call
        
        # Try to get output
        try:
            stdout, stderr = process.communicate(timeout=5)
            logger.info(f"STDOUT: {stdout}")
            if stderr:
                logger.warning(f"STDERR: {stderr}")
        except subprocess.TimeoutExpired:
            logger.info("Process still running - checking for partial output")
            process.terminate()
        
        logger.info("✅ AI test completed")
        
    except Exception as e:
        logger.error(f"❌ AI test failed: {e}")

def test_model_listing():
    """Test model listing functionality"""
    logger.info("🔍 Testing model listing...")
    
    try:
        # Import the model manager directly
        sys.path.append('.')
        from integrations.model_manager import ModelManager
        
        manager = ModelManager()
        models = manager.list_available_models()
        
        logger.info(f"Available models: {models}")
        
        # Test default model
        default_model = manager.get_default_model()
        logger.info(f"Default model: {default_model}")
        
        logger.info("✅ Model listing test completed")
        
    except Exception as e:
        logger.error(f"❌ Model listing test failed: {e}")

def test_api_key_config():
    """Test API key configuration"""
    logger.info("🔑 Testing API key configuration...")
    
    try:
        import os
        
        # Check for API keys
        openrouter_key = os.environ.get('OPENROUTER_API_KEY')
        if openrouter_key:
            logger.info(f"✅ OpenRouter API key found: {openrouter_key[:8]}...")
        else:
            logger.warning("⚠️ OpenRouter API key not found in environment")
        
        # Check for API key file
        try:
            sys.path.append('./docs')
            from openrouter_api_key import OPENROUTER_API_KEY
            if OPENROUTER_API_KEY:
                logger.info(f"✅ OpenRouter API key found in file: {OPENROUTER_API_KEY[:8]}...")
        except ImportError:
            logger.warning("⚠️ OpenRouter API key file not found")
        
        logger.info("✅ API key configuration test completed")
        
    except Exception as e:
        logger.error(f"❌ API key test failed: {e}")

def monitor_network_activity():
    """Monitor for network activity that might indicate API requests"""
    logger.info("🌐 Monitoring network activity...")
    
    try:
        import psutil
        
        # Get network stats before
        net_before = psutil.net_io_counters()
        logger.info(f"Network stats before: bytes_sent={net_before.bytes_sent}, bytes_recv={net_before.bytes_recv}")
        
        # Wait a bit
        time.sleep(10)
        
        # Get network stats after
        net_after = psutil.net_io_counters()
        logger.info(f"Network stats after: bytes_sent={net_after.bytes_sent}, bytes_recv={net_after.bytes_recv}")
        
        # Calculate difference
        sent_diff = net_after.bytes_sent - net_before.bytes_sent
        recv_diff = net_after.bytes_recv - net_before.bytes_recv
        
        if sent_diff > 1000 or recv_diff > 1000:
            logger.info(f"🌐 Network activity detected: sent={sent_diff} bytes, received={recv_diff} bytes")
        else:
            logger.info("🌐 No significant network activity detected")
        
    except ImportError:
        logger.warning("psutil not available for network monitoring")
    except Exception as e:
        logger.error(f"❌ Network monitoring failed: {e}")

if __name__ == "__main__":
    logger.info("🧪 PROJECT-S AI Functionality Test")
    logger.info("=" * 50)
    
    # Run tests
    test_api_key_config()
    test_model_listing()
    monitor_network_activity()
    run_ai_test_interactive()
    
    logger.info("🎉 All tests completed!")
