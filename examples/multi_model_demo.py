"""
Demonstration of multi-model capabilities in the Project-S agent.
Shows how the system intelligently switches between different AI models.
"""

import asyncio
import logging
import sys
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import necessary components
from core.model_selector import model_selector, initialize_models
from core.event_bus import event_bus
from core.central_executor import executor
from core.cognitive_core import cognitive_core

async def multi_model_demo():
    """Demonstrate the multi-model capabilities of the Project-S agent."""
    logger.info("Starting multi-model demonstration")
    
    # Initialize available models
    initialize_models()
    available_models = list(model_selector.models.keys())
    logger.info(f"Available models: {available_models}")
    
    # Example 1: Code generation (should use Qwen)
    logger.info("\nExample 1: Code generation task")
    code_task = {
        "type": "ask",
        "content": "Write a Python function to calculate the Fibonacci sequence using memoization.",
        "task_type": "code"
    }
    
    # Get the appropriate model for this task
    code_model = model_selector.select_model("code")
    logger.info(f"Selected model for code task: {code_model.__class__.__name__}")
    
    # Generate code
    code_result = await code_model.generate(code_task["content"])
    if "error" not in code_result:
        logger.info(f"Generated code:\n{code_result['text'][:500]}...")
    else:
        logger.error(f"Error generating code: {code_result['error']}")
    
    # Example 2: Creative writing (any model can handle this)
    logger.info("\nExample 2: Creative writing task")
    creative_task = {
        "type": "ask",
        "content": "Write a short poem about artificial intelligence.",
        "task_type": "creativity"
    }
    
    # Get the appropriate model for this task
    creative_model = model_selector.select_model("creativity")
    logger.info(f"Selected model for creative task: {creative_model.__class__.__name__}")
    
    # Generate creative content
    creative_result = await creative_model.generate(creative_task["content"])
    if "error" not in creative_result:
        logger.info(f"Generated creative content:\n{creative_result['text']}")
    else:
        logger.error(f"Error generating creative content: {creative_result['error']}")
    
    # Example 3: Complex reasoning (should use a strong reasoning model)
    logger.info("\nExample 3: Complex reasoning task")
    reasoning_task = {
        "type": "ask",
        "content": "Explain the implications of the halting problem in computer science and its relationship to Gödel's incompleteness theorems.",
        "task_type": "reasoning"
    }
    
    # Get the appropriate model for this task
    reasoning_model = model_selector.select_model("reasoning")
    logger.info(f"Selected model for reasoning task: {reasoning_model.__class__.__name__}")
    
    # Generate reasoning
    reasoning_result = await reasoning_model.generate(reasoning_task["content"])
    if "error" not in reasoning_result:
        logger.info(f"Generated reasoning:\n{reasoning_result['text'][:500]}...")
    else:
        logger.error(f"Error generating reasoning: {reasoning_result['error']}")
    
    # Example 4: Using specific model by preference
    logger.info("\nExample 4: Using a specific model by preference")
    if len(available_models) > 1:
        preferred_model = available_models[1]  # Use the second available model
        preferred_task = {
            "type": "ask",
            "content": "Summarize the key concepts of reinforcement learning.",
            "task_type": "factual",
            "model_preference": preferred_model
        }
        
        # Get the preferred model
        model = model_selector.select_model("factual", preference=preferred_model)
        logger.info(f"Selected preferred model: {model.__class__.__name__}")
        
        # Generate with preferred model
        preferred_result = await model.generate(preferred_task["content"])
        if "error" not in preferred_result:
            logger.info(f"Generated with preferred model:\n{preferred_result['text'][:500]}...")
        else:
            logger.error(f"Error generating with preferred model: {preferred_result['error']}")
    else:
        logger.warning("Not enough models available for preference example")
    
    # Example 5: Streaming response
    logger.info("\nExample 5: Streaming response demonstration")
    streaming_task = {
        "type": "ask",
        "content": "Explain the concept of transformers in machine learning.",
        "task_type": "factual"
    }
    
    # Get model for streaming
    streaming_model = model_selector.select_model("factual")
    logger.info(f"Selected model for streaming: {streaming_model.__class__.__name__}")
    
    # Stream generation
    logger.info("Streaming response:")
    async for chunk in streaming_model.stream_generate(streaming_task["content"]):
        if "error" not in chunk:
            # Print chunk without newline
            print(chunk.get("text", ""), end="", flush=True)
            # Slight delay to simulate real-time streaming
            await asyncio.sleep(0.01)
        else:
            logger.error(f"Error in streaming: {chunk['error']}")
            break
    print()  # Final newline
    
    logger.info("\nMulti-model demonstration completed")

if __name__ == "__main__":
    try:
        asyncio.run(multi_model_demo())
    except KeyboardInterrupt:
        logger.info("Demonstration interrupted by user")
    except Exception as e:
        logger.error(f"Error running demonstration: {str(e)}")