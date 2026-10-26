import os
import sys
import logging
import subprocess
import pkg_resources

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('prompt_enhancer')

def install_package(package_name):
    try:
        # Check if package is already installed
        pkg_resources.get_distribution(package_name)
    except pkg_resources.DistributionNotFound:
        logger.info(f"Installing required package: {package_name}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            logger.info(f"Successfully installed {package_name}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {package_name}: {e}")
            return False
    return True

try:
    # Try relative import first
    try:
        from .prompt_enhancer_llm import PromptEnhancer
    except ImportError:
        # If that fails, try direct import
        from prompt_enhancer_llm import PromptEnhancer
    try:
        from . import models
    except ImportError:
        import models

    from aiohttp import web
    from server import PromptServer

    @PromptServer.instance.routes.post("/prompt_enhancer/anthropic_models")
    async def refresh_anthropic_models(request):
        body = await request.json()
        api_key = body.get("api_key", "").strip() or os.environ.get("ANTHROPIC_API_KEY", "")
        if models.anthropic is None:
            return web.json_response({"error": "anthropic package is not installed"}, status=500)
        if not api_key:
            return web.json_response({"error": "Set anthropic_key or ANTHROPIC_API_KEY first"}, status=400)
        try:
            fetched = models.fetch_anthropic_models(api_key)
        except models.anthropic.APIError as e:
            return web.json_response({"error": str(e)}, status=502)
        # Update in place so prompt validation accepts the new choices.
        models.ANTHROPIC_MODELS[:] = fetched
        return web.json_response({"models": fetched})
    
    logger.info("Successfully imported PromptEnhancer class")

    NODE_CLASS_MAPPINGS = {
        "PromptEnhancer": PromptEnhancer
    }

    NODE_DISPLAY_NAME_MAPPINGS = {
        "PromptEnhancer": "Prompt Enhancer LLM ✨"
    }

    WEB_DIRECTORY = "./js"

    __all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
    
    logger.info("Node registration complete")
    logger.info(f"Python path: {sys.path}")
    logger.info(f"Current directory: {os.getcwd()}")

except Exception as e:
    logger.error(f"Error during node initialization: {e}")
    NODE_CLASS_MAPPINGS = {}
    NODE_DISPLAY_NAME_MAPPINGS = {}
