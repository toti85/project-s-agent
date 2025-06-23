import asyncio
from hybrid_workflow_system import HybridWorkflowSystem
import os
from datetime import datetime

async def patched_system_test():
    system = HybridWorkflowSystem()

    print('PATCHED SYSTEM VALIDATION - REAL EXECUTION TEST')
    print('=' * 60)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print('Test started:', timestamp)

    # Test 1: Directory listing (ls → dir translation)
    print('Step 1: Directory listing (translation test)...')
    result1 = await system.process_user_request('list current directory contents using ls command')
    status1 = 'SUCCESS' if result1.get('success') else 'FAIL'
    print('Status:', status1, '- Translation: ls → dir')

    # Test 2: Create folder (mkdir test)
    print('Step 2: Creating real_test_folder...')
    result2 = await system.process_user_request('create folder named real_test_folder')
    status2 = 'SUCCESS' if result2.get('success') else 'FAIL'
    print('Status:', status2)

    folder_exists = os.path.exists('real_test_folder')
    print('Folder verification:', 'EXISTS' if folder_exists else 'MISSING', '- real_test_folder exists:', folder_exists)

    # Test 3: Copy operation (cp → copy translation)
    print('Step 3: Copy file with cp command...')
    result3 = await system.process_user_request('copy timestamp_test.txt to real_test_folder using cp command')
    status3 = 'SUCCESS' if result3.get('success') else 'FAIL'
    print('Status:', status3, '- Translation: cp → copy')

    # Verify copy actually happened
    copy_exists = os.path.exists('real_test_folder/timestamp_test.txt')
    print('Copy verification:', 'EXISTS' if copy_exists else 'MISSING', '- File copied:', copy_exists)

    print()
    print('PATCHED SYSTEM RESULTS:')
    tests_passed = sum([
        result1.get('success', False),
        result2.get('success', False),
        folder_exists,
        result3.get('success', False),
        copy_exists
    ])
    print(f'Tests + Verifications: {tests_passed}/5')
    print(f'Success rate: {(tests_passed/5)*100:.1f}%')
    if tests_passed == 5:
        print('PATCH SUCCESS: Real execution confirmed!')
    else:
        print('Needs further investigation')

if __name__ == "__main__":
    asyncio.run(patched_system_test())
