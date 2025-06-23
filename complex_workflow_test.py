#!/usr/bin/env python3
"""
Complex Workflow Test - Step 1
==============================
Test the full intelligent workflow system with a complex multi-step request.
"""

import asyncio
from hybrid_workflow_system import HybridWorkflowSystem


async def full_system_test():
    system = HybridWorkflowSystem()
    
    print('🧠 FULL INTELLIGENT WORKFLOW SYSTEM TEST')
    print('=' * 55)
    
    # Complex multi-step request
    complex_request = """
    Create a comprehensive backup workflow:
    1. List all .py files in current directory
    2. Create a backup folder with timestamp
    3. Copy all Python files to backup folder  
    4. Generate a backup report with file count and timestamp
    5. Verify all files were copied successfully
    """
    
    print('🎯 COMPLEX WORKFLOW REQUEST:')
    print(complex_request)
    print('\n⚡ PROCESSING...')
    
    result = await system.process_user_request(complex_request)
    
    print('\n📊 SYSTEM RESPONSE:')
    print('=' * 30)
    for key, value in result.items():
        if key == 'steps' and isinstance(value, list):
            print(f'{key}: [{len(value)} steps executed]')
            for i, step in enumerate(value, 1):
                action = step.get('action', 'unknown')
                success = step.get('success', False)
                status = '✅' if success else '❌'
                print(f'  Step {i}: {action} - {status}')
        elif key == 'error':
            print(f'{key}: {value}')
        elif len(str(value)) > 200:
            print(f'{key}: {str(value)[:200]}...')
        else:
            print(f'{key}: {value}')
    
    print('\n🔍 DETAILED ANALYSIS:')
    print('=' * 25)
    
    if result.get('success'):
        print('✅ Complex workflow processed successfully!')
        print(f"📈 Processing time: {result.get('total_processing_time', 0):.2f}s")
        print(f"🧠 Strategy used: {result.get('processing_strategy', 'unknown')}")
        
        steps = result.get('steps', [])
        successful_steps = sum(1 for step in steps if step.get('success'))
        print(f"📊 Steps success rate: {successful_steps}/{len(steps)} ({(successful_steps/len(steps)*100):.0f}%)")
        
        # Show command translations used
        commands_used = [step.get('command') for step in steps if step.get('command')]
        if commands_used:
            print(f"🔧 Commands executed: {', '.join(commands_used)}")
    else:
        print('❌ Complex workflow failed!')
        print(f"❓ Error: {result.get('error', 'Unknown error')}")
    
    return result


if __name__ == "__main__":
    asyncio.run(full_system_test())
