import time
import functools
from datetime import datetime
from typing import Callable, Any, TypeVar, cast

# Type variable for the decorated function
F = TypeVar('F', bound=Callable[..., Any])

def monitor_performance(func: F) -> F:
    """
    Decorator to monitor the execution time of async functions.
    
    Measures and prints the execution time of the decorated async function.
    Can be applied to any async function in the Project-S system.
    
    Args:
        func (Callable): The async function to be decorated
        
    Returns:
        Callable: The wrapped function with performance monitoring
        
    Example:
        @monitor_performance
        async def some_slow_function(param1, param2):
            # function implementation
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Record start time
        start_time = time.time()
        
        # Get function details for better logging
        func_name = func.__name__
        module_name = func.__module__
        
        # Format current time for log readability
        current_time = datetime.now().strftime("%H:%M:%S")
        
        print(f"[{current_time}] Starting execution of {module_name}.{func_name}")
        
        try:
            # Execute the actual function
            result = await func(*args, **kwargs)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Print performance information
            print(f"[{current_time}] Completed {module_name}.{func_name} in {execution_time:.4f} seconds")
            
            return result
        except Exception as e:
            # Calculate execution time until exception
            execution_time = time.time() - start_time
            
            # Print performance information with exception
            print(f"[{current_time}] Error in {module_name}.{func_name} after {execution_time:.4f} seconds: {str(e)}")
            
            # Re-raise the exception
            raise
    
    # Cast is used to maintain the type signature for better IDE support
    return cast(F, wrapper)

# Example usage:
# 
# @monitor_performance
# async def generate_response(prompt: str) -> str:
#     # Some time-consuming operation
#     await asyncio.sleep(2)  # Simulate work
#     return "Generated response"