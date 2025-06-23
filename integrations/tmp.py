async def stop_dashboard():
    """Stop the diagnostics dashboard server"""
    if not dashboard._is_running:
        logger.info("Dashboard is not running")
        return True
    
    try:
        await dashboard.stop()
        logger.info("Diagnostics dashboard stopped")
        return True
    except Exception as e:
        logger.error(f"Error stopping diagnostics dashboard: {e}")
        return False
