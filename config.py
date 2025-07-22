"""
Configuration file for the Marksheet AI Agent
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Perplexity API Configuration
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
    PERPLEXITY_BASE_URL = "https://api.perplexity.ai/chat/completions"
    
    # Model Configuration
    MODEL = "llama-3.1-sonar-large-128k-online"  # or use "llama-3.1-sonar-small-128k-online"
    
    # File Configuration
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'bmp', 'tiff']
    
    # Output Configuration
    OUTPUT_DIR = "output"
    
    @staticmethod
    def validate_config():
        """Validate if all required configurations are set"""
        if not Config.PERPLEXITY_API_KEY:
            raise ValueError("PERPLEXITY_API_KEY is not set. Please add it to your .env file")
        
        # Create output directory if it doesn't exist
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        
        return True