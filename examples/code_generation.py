"""
Example demonstrating code generation using the Project-S agent.
This example shows how to use the VSCodeInterface to generate and execute code.
"""

import asyncio
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import the necessary components
from integrations.vscode_interface import VSCodeInterface

async def code_generation_example():
    """Demonstrate code generation using the VS Code interface."""
    logger.info("Starting code generation example")
    
    # Create a VS Code interface
    vscode = VSCodeInterface()
    
    # Example 1: Generate a simple function
    logger.info("Example 1: Generating a simple function")
    spec = "Create a Python function that calculates the factorial of a number"
    result = await vscode.generate_code(spec)
    
    if result.get("status") == "success":
        generated_code = result.get("result", {}).get("code", "")
        logger.info(f"Generated code:\n{generated_code}")
        
        # Example 2: Save the generated code to a file
        logger.info("Example 2: Saving the generated code to a file")
        file_path = "examples/generated/factorial.py"
        save_result = await vscode.create_file(file_path, generated_code)
        
        if save_result.get("status") == "success":
            logger.info(f"Code saved to {file_path}")
            
            # Example 3: Execute the generated code
            logger.info("Example 3: Executing the generated code")
            test_code = f"""
# Import the factorial function
from generated.factorial import factorial

# Test the function
result = factorial(5)
print(f"Factorial of 5 is: {{result}}")
assert result == 120
print("Test passed!")
"""
            execute_result = await vscode.execute_code(test_code)
            
            if execute_result.get("status") == "success":
                output = execute_result.get("result", {}).get("output", "")
                logger.info(f"Execution output:\n{output}")
            else:
                logger.error(f"Error executing code: {execute_result.get('message')}")
        else:
            logger.error(f"Error saving code: {save_result.get('message')}")
    else:
        logger.error(f"Error generating code: {result.get('message')}")
    
    logger.info("Code generation example completed")

if __name__ == "__main__":
    try:
        asyncio.run(code_generation_example())
    except KeyboardInterrupt:
        logger.info("Example interrupted by user")
    except Exception as e:
        logger.error(f"Error running example: {str(e)}")