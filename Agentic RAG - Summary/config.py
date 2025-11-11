"""
Configuration file for Model White Paper Summary System
"""
import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class LLMConfig(BaseModel):
    """LLM API Configuration"""
    cohere_api_key: Optional[str] = Field(default_factory=lambda: os.getenv('COHERE_API_KEY'))
    default_provider: str = Field(default="cohere")
    model_name: str = Field(default="command-a-03-2025")  # Cohere Command A
    temperature: float = Field(default=0.1)  # Low for consistent outputs
    max_tokens: int = Field(default=8000)
    # Cohere Compass settings
    compass_dataset_id: Optional[str] = Field(default_factory=lambda: os.getenv('COMPASS_DATASET_ID'))

class AppConfig(BaseModel):
    """Main Application Configuration"""
    llm: LLMConfig = LLMConfig()
    
    # File paths
    upload_dir: str = Field(default="uploads")
    output_dir: str = Field(default="outputs")
    
    # Logging
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="logs/app.log")

# Global configuration instance
config = AppConfig()
