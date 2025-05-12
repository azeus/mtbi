import os
import weaviate
from weaviate.auth import AuthApiKey
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()


def get_weaviate_client():
    """
    Create and return a connection to your Weaviate cluster.
    Uses Streamlit secrets or environment variables for credentials.

    Returns:
        A Weaviate client instance connected to your cluster.
    """
    # Check for Streamlit secrets (for Streamlit Cloud deployment)
    if hasattr(st, 'secrets') and 'WEAVIATE_URL' in st.secrets:
        weaviate_url = st.secrets['WEAVIATE_URL']
        weaviate_api_key = st.secrets['WEAVIATE_API_KEY']
        openai_api_key = st.secrets['OPENAI_API_KEY']
    else:
        # Fall back to environment variables (for local development)
        weaviate_url = os.getenv("WEAVIATE_URL")
        weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")

    # Validate required credentials
    if not weaviate_url or not weaviate_api_key:
        st.error("Missing Weaviate credentials. Please set WEAVIATE_URL and WEAVIATE_API_KEY.")
        st.stop()

    if not openai_api_key:
        st.error("Missing OpenAI API key. Please set OPENAI_API_KEY.")
        st.stop()

    try:
        # Create authentication object
        auth_config = AuthApiKey(api_key=weaviate_api_key)

        # Additional headers for OpenAI integration
        additional_headers = {
            "X-OpenAI-Api-Key": openai_api_key
        }

        # Initialize client
        client = weaviate.Client(
            url=weaviate_url,
            auth=auth_config,
            additional_headers=additional_headers
        )

        # Verify connection
        if not client.is_ready():
            st.error("Could not connect to Weaviate. Please check your credentials and network.")
            st.stop()

        return client

    except Exception as e:
        st.error(f"Error connecting to Weaviate: {str(e)}")
        st.stop()