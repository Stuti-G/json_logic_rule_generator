import logging
import os

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

env_path = ".env.development"
breakpoint()
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY is None:
    logger.critical("Please add an API key for the Genai model...")
