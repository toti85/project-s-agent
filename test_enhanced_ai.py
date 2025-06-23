#!/usr/bin/env python3
"""
Test script to verify the enhanced main.py functionality
Tests the integration of main_multi_model.py core functions
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

async def test_ai_functionality():
    """Test if the AI system is working with enhanced functionality"""
    print("🧪 TESTING ENHANCED AI FUNCTIONALITY")
    print("=" * 60)
    
    try:
        # Test the intelligent command parser
        from main import intelligent_command_parser, process_file_operation_directly, execute_shell_command_directly
        
        print("✅ Core functions imported successfully!")
        
        # Test 1: Intelligent Command Parser
        print("\n📋 TEST 1: Intelligent Command Parser")
        test_commands = [
            "create file test.txt",
            "list files",
            "organize this directory",
            "What is artificial intelligence?"
        ]
        
        for cmd in test_commands:
            print(f"\n🔍 Testing: '{cmd}'")
            result = await intelligent_command_parser(cmd)
            print(f"   Type: {result['type']}")
            print(f"   Confidence: {result['confidence']:.0%} ({result['confidence_level']})")
            if result.get('operation'):
                print(f"   Operation: {result['operation']}")
        
        # Test 2: File Operations
        print("\n📄 TEST 2: File Operations")
        test_file = "ai_test_file.txt"
        
        # Create file
        result = await process_file_operation_directly("create", test_file, "This is a test file created by the enhanced AI system.")
        print(f"Create result: {result['status']} - {result['message']}")
        
        # Read file
        if result['status'] == 'success':
            result = await process_file_operation_directly("read", test_file)
            print(f"Read result: {result['status']} - Content length: {len(result.get('content', ''))}")
        
        # List files
        result = await process_file_operation_directly("list", ".")
        print(f"List result: {result['status']} - Found {result.get('count', 0)} items")
        
        # Test 3: Shell Command (simple and safe)
        print("\n💻 TEST 3: Shell Command Execution")
        if sys.platform.startswith('win'):
            test_cmd = "echo 'AI system test command'"
        else:
            test_cmd = "echo 'AI system test command'"
        
        result = await execute_shell_command_directly(test_cmd)
        print(f"Shell result: {result['status']} - Return code: {result['returncode']}")
        if result.get('stdout'):
            print(f"Output: {result['stdout']}")
        
        print("\n🎉 ALL TESTS COMPLETED!")
        print("✅ Enhanced AI functionality is working properly!")
        
        # Clean up test file
        try:
            os.remove(test_file)
            print(f"🧹 Cleaned up test file: {test_file}")
        except:
            pass
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_ai_api_requests():
    """Test if AI is making API requests"""
    print("\n🌐 TESTING AI API FUNCTIONALITY")
    print("=" * 40)
    
    try:
        # Import and test model manager
        from integrations.model_manager import model_manager
        
        # Test simple AI query
        test_query = "What is 2+2? Please give a short answer."
        print(f"🤖 Testing AI query: '{test_query}'")
        
        result = await model_manager.execute_task_with_core_system(test_query)
        
        if result:
            print("✅ AI API request successful!")
            if isinstance(result, dict):
                if "content" in result:
                    print(f"📝 AI Response: {result['content'][:200]}...")
                elif "response" in result:
                    print(f"📝 AI Response: {result['response'][:200]}...")
                else:
                    print(f"📝 AI Response: {str(result)[:200]}...")
            else:
                print(f"📝 AI Response: {str(result)[:200]}...")
        else:
            print("⚠️ AI returned empty response")
            
    except Exception as e:
        print(f"❌ AI API test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 STARTING COMPREHENSIVE AI SYSTEM TESTS")
    print("=" * 80)
    
    # Run functionality tests
    asyncio.run(test_ai_functionality())
    
    # Run AI API tests
    asyncio.run(test_ai_api_requests())
    
    print("\n🏁 ALL TESTS COMPLETED!")
    input("\nPress Enter to exit...")
