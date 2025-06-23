#!/usr/bin/env python3
"""
Unicode Encoding Fix for Project-S
This fixes Hungarian character encoding issues on Windows terminals
"""

import os
import sys
import logging
import locale

def fix_unicode_encoding():
    """
    Fix Unicode encoding issues for Windows terminals
    """
    # Set UTF-8 encoding for stdout/stderr
    if sys.platform.startswith('win'):
        # Set console code page to UTF-8
        try:
            os.system('chcp 65001 > nul')
        except:
            pass
        
        # Set environment variables for UTF-8
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # Reconfigure stdout/stderr with UTF-8
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        
        # Set locale to UTF-8 if possible
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except:
            try:
                locale.setlocale(locale.LC_ALL, 'C.UTF-8')
            except:
                pass

def setup_utf8_logging():
    """
    Setup logging with UTF-8 encoding to prevent character encoding errors
    """
    # Remove all existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Create new handler with UTF-8 encoding
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    
    # Set UTF-8 encoding for the handler
    if hasattr(handler.stream, 'reconfigure'):
        handler.stream.reconfigure(encoding='utf-8', errors='replace')
    
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Configure root logger
    logging.root.addHandler(handler)
    logging.root.setLevel(logging.INFO)
    
    return handler

def safe_log_message(logger, level, message):
    """
    Safely log a message with fallback for encoding issues
    """
    try:
        getattr(logger, level)(message)
    except UnicodeEncodeError:
        # Fallback: replace problematic characters
        safe_message = message.encode('ascii', errors='replace').decode('ascii')
        getattr(logger, level)(f"[ENCODING_FIXED] {safe_message}")

# Apply fixes when module is imported
def apply_all_fixes():
    """Apply all Unicode and encoding fixes"""
    fix_unicode_encoding()
    setup_utf8_logging()

# Automatically apply fixes when imported
apply_all_fixes()
