# llama_integration_robust.py
# Integration with Llama Cloud API with fallbacks and optional dependency

import os
import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
llama_client = None
LLAMA_CLOUD_AVAILABLE = False

# Try to import llama_cloud - make dependency optional
try:
    from llama_cloud import LlamaCloud

    LLAMA_CLOUD_AVAILABLE = True
    logger.info("Llama Cloud package successfully imported")
except ImportError as e:
    logger.error(f"Llama Cloud package not installed. Please run: pip install llama-cloud")
    LLAMA_CLOUD_AVAILABLE = False
except Exception as e:
    logger.error(f"Error importing Llama Cloud: {str(e)}")
    LLAMA_CLOUD_AVAILABLE = False


def get_llama_client():
    """
    Get or create a Llama Cloud client.

    Returns:
        The Llama Cloud client object or None if initialization fails
    """
    global llama_client

    if not LLAMA_CLOUD_AVAILABLE:
        return None

    if llama_client is not None:
        return llama_client

    try:
        # Get API key from Streamlit secrets or environment variables
        llama_api_key = None
        if hasattr(st, 'secrets') and 'LLAMA_CLOUD_API_KEY' in st.secrets:
            llama_api_key = st.secrets['LLAMA_CLOUD_API_KEY']
        else:
            llama_api_key = os.getenv("LLAMA_CLOUD_API_KEY")

        if not llama_api_key:
            logger.error("Missing Llama Cloud API Key. Please set LLAMA_CLOUD_API_KEY in secrets or environment.")
            return None

        # Initialize the client
        llama_client = LlamaCloud(api_key=llama_api_key)
        logger.info("Llama Cloud client initialized successfully")
        return llama_client

    except Exception as e:
        logger.error(f"Error initializing Llama Cloud client: {str(e)}")
        return None


def generate_llama_response(prompt, system_prompt=None, model="llama-3-70b-instruct"):
    """
    Generate a response using Llama Cloud with retry logic.

    Args:
        prompt (str): The user prompt
        system_prompt (str, optional): System instructions for the model
        model (str, optional): Model to use. Defaults to "llama-3-70b-instruct"

    Returns:
        str: The generated response text or None if an error occurs
    """
    # Check if Llama Cloud is available
    if not LLAMA_CLOUD_AVAILABLE:
        return None

    client = get_llama_client()
    if client is None:
        return None

    # Handle potential rate limits with retries
    max_retries = 3
    for attempt in range(max_retries):
        try:
            messages = []

            # Add system message if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            # Add user message
            messages.append({"role": "user", "content": prompt})

            # Generate response
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            # Extract and return the content
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error (attempt {attempt + 1}/{max_retries}) generating Llama Cloud response: {str(e)}")

            # If we've tried max times, give up
            if attempt == max_retries - 1:
                return None

            # Otherwise wait and retry (exponential backoff)
            import time
            wait_time = (2 ** attempt) * 0.5  # 0.5, 1, 2 seconds
            time.sleep(wait_time)

    return None


def check_llama_connection():
    """
    Check if the Llama Cloud connection is working.

    Returns:
        bool: True if connection is working, False otherwise
    """
    if not LLAMA_CLOUD_AVAILABLE:
        return False

    client = get_llama_client()
    if client is None:
        return False

    try:
        # Simple test query
        response = generate_llama_response("Hello, just testing the connection.")
        return response is not None
    except:
        return False


def is_llama_available():
    """
    Simple function to check if Llama Cloud is available.

    Returns:
        bool: True if available, False otherwise
    """
    return LLAMA_CLOUD_AVAILABLE and get_llama_client() is not None