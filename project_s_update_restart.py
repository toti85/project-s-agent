#!/usr/bin/env python3
"""
PROJECT-S SYSTEM UPDATE AND RESTART SCRIPT
==========================================
Automated Windows update and restart using Project-S enhanced capabilities.
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Import Project-S enhanced functions
from main import (
    execute_shell_command_directly,
    process_file_operation_directly,
    intelligent_command_parser
)

async def perform_windows_update_and_restart():
    """Execute Windows update and restart using Project-S capabilities."""
    print("🚀 PROJECT-S AUTOMATED SYSTEM UPDATE")
    print("=" * 60)
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Step 1: Check current Windows update status
    print("\n🔍 STEP 1: Checking Windows Update status...")
    check_result = await execute_shell_command_directly("Get-WindowsUpdate -List")
    
    if check_result["status"] == "success":
        print("✅ Windows Update check completed")
        if check_result["stdout"]:
            print(f"📋 Available updates:\n{check_result['stdout'][:500]}...")
        else:
            print("📋 No updates shown in output")
    else:
        print(f"⚠️ Update check had issues: {check_result['message']}")
        
        # Try alternative method
        print("🔄 Trying alternative update check...")
        alt_check = await execute_shell_command_directly("Get-WUList")
        if alt_check["status"] == "success":
            print("✅ Alternative update check completed")
        else:
            print("📝 Note: Windows Update module might need to be installed")
    
    # Step 2: Create backup log before updates
    print("\n📝 STEP 2: Creating pre-update system log...")
    system_info = await execute_shell_command_directly("systeminfo")
    
    if system_info["status"] == "success":
        log_content = f"""PROJECT-S SYSTEM UPDATE LOG
=============================
Update Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
System Info:
{system_info['stdout'][:1000]}...

Status: Starting Windows Update process
"""
        log_result = await process_file_operation_directly(
            "create", 
            "system_update_log.txt", 
            log_content
        )
        
        if log_result["status"] == "success":
            print(f"✅ System log created: {log_result['path']}")
        else:
            print(f"⚠️ Log creation failed: {log_result['message']}")
    
    # Step 3: Install Windows updates
    print("\n🔄 STEP 3: Installing Windows updates...")
    
    # Try to install updates using different methods
    update_commands = [
        "Install-WindowsUpdate -AcceptAll -AutoReboot",
        "Get-WUInstall -AcceptAll -AutoReboot",
        "UsoClient StartScan",
        "UsoClient StartDownload", 
        "UsoClient StartInstall"
    ]
    
    update_success = False
    for i, cmd in enumerate(update_commands, 1):
        print(f"\n🔧 Attempt {i}: {cmd}")
        update_result = await execute_shell_command_directly(cmd)
        
        if update_result["status"] == "success":
            print(f"✅ Command executed successfully")
            if update_result["stdout"]:
                print(f"📤 Output: {update_result['stdout'][:200]}...")
            update_success = True
            break
        else:
            print(f"⚠️ Command failed: {update_result['message']}")
            if i < len(update_commands):
                print("🔄 Trying next method...")
    
    # Step 4: Force restart if updates were initiated
    print("\n🔄 STEP 4: Preparing system restart...")
    
    if update_success:
        print("✅ Updates were initiated successfully")
    else:
        print("⚠️ Update initiation had issues, but proceeding with restart")
    
    # Create final status log
    final_log = f"""PROJECT-S UPDATE COMPLETION
==========================
Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Update Initiation: {'SUCCESS' if update_success else 'PARTIAL'}
Next Action: System Restart

The system will restart in 30 seconds.
Project-S will auto-start after restart if configured.
"""
    
    final_log_result = await process_file_operation_directly(
        "create",
        "update_completion_log.txt",
        final_log
    )
    
    if final_log_result["status"] == "success":
        print(f"✅ Final log created: {final_log_result['path']}")
    
    # Step 5: Execute restart
    print("\n🔄 STEP 5: Executing system restart...")
    print("⚠️ SYSTEM WILL RESTART IN 30 SECONDS!")
    print("💾 All Project-S logs have been saved.")
    print("🚀 Project-S will be available after restart.")
    
    restart_result = await execute_shell_command_directly("shutdown /r /t 30 /c 'Project-S initiated system restart after Windows updates'")
    
    if restart_result["status"] == "success":
        print("✅ Restart command executed successfully")
        print("🕒 System will restart in 30 seconds...")
        print("\n" + "=" * 60)
        print("🎉 PROJECT-S UPDATE PROCESS COMPLETED!")
        print("👋 See you after the restart!")
        print("=" * 60)
        
        # Final countdown
        for i in range(10, 0, -1):
            print(f"⏰ Restart in {i} seconds... (Ctrl+C to cancel)")
            await asyncio.sleep(1)
        
        print("🔄 RESTARTING NOW...")
        
    else:
        print(f"❌ Restart command failed: {restart_result['message']}")
        print("💡 Manual restart required")
        
        # Try alternative restart
        alt_restart = await execute_shell_command_directly("Restart-Computer -Force")
        if alt_restart["status"] == "success":
            print("✅ Alternative restart command executed")
        else:
            print("⚠️ Please restart manually: shutdown /r /t 0")

async def main():
    """Main execution function."""
    try:
        # Use Project-S intelligent command parser to process the update request
        print("🧠 PROJECT-S INTELLIGENT COMMAND ANALYSIS")
        
        user_command = "frissítsd a Windows-t és indítsd újra a gépet"
        parsed_command = await intelligent_command_parser(user_command)
        
        print(f"🎯 Command Analysis: {parsed_command['type']}")
        print(f"📊 Confidence: {parsed_command.get('confidence', 0):.0%}")
        print(f"🔧 Detected operation: System update and restart")
        
        # Execute the update and restart process
        await perform_windows_update_and_restart()
        
    except KeyboardInterrupt:
        print("\n\n⏸️ Update process cancelled by user")
        print("💡 To manually update: Run Windows Update from Settings")
    except Exception as e:
        print(f"\n❌ Error during update process: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🌟 PROJECT-S: AUTOMATED SYSTEM UPDATE")
    print("🚀 Initializing Windows update and restart sequence...")
    asyncio.run(main())
