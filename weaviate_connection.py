# weaviate_connection.py

import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_weaviate_client():
    """
    Create and return a connection to your Weaviate cluster.
    Compatible with both Weaviate v3.x and v4.x.
    """
    try:
        # Check if weaviate-client is installed
        try:
            import weaviate
        except ImportError:
            st.error("Weaviate client library not installed. Run: pip install weaviate-client==3.26.7")
            return None

        # Get credentials (first try Streamlit secrets, then environment variables)
        weaviate_url = None
        weaviate_api_key = None
        openai_api_key = None

        # First, try to get from Streamlit secrets
        if hasattr(st, 'secrets'):
            weaviate_url = st.secrets.get('WEAVIATE_URL')
            weaviate_api_key = st.secrets.get('WEAVIATE_API_KEY')
            openai_api_key = st.secrets.get('OPENAI_API_KEY')

        # If not in secrets, try environment variables
        if not weaviate_url:
            weaviate_url = os.getenv("WEAVIATE_URL")
        if not weaviate_api_key:
            weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
        if not openai_api_key:
            openai_api_key = os.getenv("OPENAI_API_KEY")

        # Validate required credentials
        if not weaviate_url:
            st.error("Missing Weaviate URL. Please set WEAVIATE_URL in secrets or environment.")
            return None

        if not weaviate_api_key:
            st.error("Missing Weaviate API Key. Please set WEAVIATE_API_KEY in secrets or environment.")
            return None

        if not openai_api_key:
            st.error("Missing OpenAI API key. Please set OPENAI_API_KEY in secrets or environment.")
            return None

        # Create authentication object - with fallback for different versions
        try:
            from weaviate.auth import AuthApiKey
            auth_config = AuthApiKey(api_key=weaviate_api_key)
        except ImportError:
            # Fallback for older versions
            auth_config = {"api_key": weaviate_api_key}

        # Additional headers for OpenAI integration
        additional_headers = {
            "X-OpenAI-Api-Key": openai_api_key
        }

        # Initialize client - handle different versions
        try:
            # Try with newer signature
            client = weaviate.Client(
                url=weaviate_url,
                auth_client=auth_config,
                additional_headers=additional_headers
            )
        except TypeError:
            # Fallback for older versions
            try:
                client = weaviate.Client(
                    url=weaviate_url,
                    auth_config=auth_config,
                    additional_headers=additional_headers
                )
            except TypeError:
                # Simplest possible call as fallback
                client = weaviate.Client(weaviate_url)

        # Verify connection
        try:
            if hasattr(client, 'is_ready') and callable(client.is_ready):
                if client.is_ready():
                    st.success("Connected to Weaviate successfully!")
                    return client
                else:
                    st.error("Could not connect to Weaviate. Please check your credentials and network.")
                    return None
            else:
                # If is_ready doesn't exist, try a simple schema get as test
                client.schema.get()
                st.success("Connected to Weaviate successfully!")
                return client
        except Exception as e:
            st.error(f"Error verifying Weaviate connection: {str(e)}")
            return None

    except Exception as e:
        st.error(f"Error in Weaviate connection setup: {str(e)}")
        return None