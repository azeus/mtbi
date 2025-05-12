# Updated weaviate_connection.py with fixes for proxy error and improved debugging

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
        # First check if weaviate-client is installed
        try:
            import weaviate
            if st.session_state.get('debug_mode', False):
                st.sidebar.success("✅ Weaviate client module loaded")
        except ImportError:
            st.error("Weaviate client library not installed. Run: pip install weaviate-client==3.26.7")
            return None

        # Get credentials (first try Streamlit secrets, then environment variables)
        weaviate_url = None
        weaviate_api_key = None
        openai_api_key = None

        # First, try to get from Streamlit secrets
        if hasattr(st, 'secrets'):
            try:
                weaviate_url = st.secrets.get('WEAVIATE_URL')
                weaviate_api_key = st.secrets.get('WEAVIATE_API_KEY')
                openai_api_key = st.secrets.get('OPENAI_API_KEY')

                # Debug output if enabled
                if st.session_state.get('debug_mode', False):
                    st.sidebar.text("Secrets found:")
                    st.sidebar.text(f"- WEAVIATE_URL: {'Set' if weaviate_url else 'Not set'}")
                    st.sidebar.text(f"- WEAVIATE_API_KEY: {'Set' if weaviate_api_key else 'Not set'}")
                    st.sidebar.text(f"- OPENAI_API_KEY: {'Set' if openai_api_key else 'Not set'}")
            except Exception as e:
                if st.session_state.get('debug_mode', False):
                    st.sidebar.error(f"Error reading secrets: {str(e)}")

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

        # Fix URL format if needed
        if not weaviate_url.startswith(("http://", "https://")):
            weaviate_url = f"https://{weaviate_url}"
            if st.session_state.get('debug_mode', False):
                st.sidebar.warning(f"Added https:// prefix to Weaviate URL: {weaviate_url}")

        # Create authentication object - with fallback for different versions
        try:
            from weaviate.auth import AuthApiKey
            auth_config = AuthApiKey(api_key=weaviate_api_key)
            if st.session_state.get('debug_mode', False):
                st.sidebar.success("Using modern AuthApiKey for authentication")
        except ImportError:
            # Fallback for older versions
            auth_config = {"api_key": weaviate_api_key}
            if st.session_state.get('debug_mode', False):
                st.sidebar.info("Using legacy auth_config for authentication")

        # Additional headers for OpenAI integration
        additional_headers = {
            "X-OpenAI-Api-Key": openai_api_key
        }

        # Initialize client - handle different versions
        if st.session_state.get('debug_mode', False):
            st.sidebar.text(f"Connecting to Weaviate at: {weaviate_url}")

        try:
            # Try with newer signature
            client = weaviate.Client(
                url=weaviate_url,
                auth_client=auth_config,
                additional_headers=additional_headers
            )
            if st.session_state.get('debug_mode', False):
                st.sidebar.success("Created client with modern API")
        except TypeError as e:
            if st.session_state.get('debug_mode', False):
                st.sidebar.warning(f"Modern client failed: {str(e)}")
                st.sidebar.info("Trying with legacy API...")

            # Fallback for older versions
            try:
                client = weaviate.Client(
                    url=weaviate_url,
                    auth_config=auth_config,
                    additional_headers=additional_headers
                )
                if st.session_state.get('debug_mode', False):
                    st.sidebar.success("Created client with legacy API")
            except TypeError as e:
                if st.session_state.get('debug_mode', False):
                    st.sidebar.warning(f"Legacy client failed: {str(e)}")
                    st.sidebar.info("Trying with minimal parameters...")

                # Simplest possible call as fallback
                client = weaviate.Client(weaviate_url)
                if st.session_state.get('debug_mode', False):
                    st.sidebar.success("Created client with minimal parameters")

        # Verify connection
        try:
            if hasattr(client, 'is_ready') and callable(getattr(client, 'is_ready')):
                if st.session_state.get('debug_mode', False):
                    st.sidebar.info("Testing connection with is_ready()")

                if client.is_ready():
                    st.success("Connected to Weaviate successfully!")

                    # Get additional information if in debug mode
                    if st.session_state.get('debug_mode', False):
                        try:
                            meta = client.get_meta()
                            st.sidebar.info(f"Weaviate version: {meta.get('version', 'Unknown')}")
                        except Exception as e:
                            st.sidebar.warning(f"Could not get meta info: {str(e)}")

                    return client
                else:
                    st.error("Could not connect to Weaviate. Please check your credentials and network.")
                    return None
            else:
                # If is_ready doesn't exist, try a simple schema get as test
                if st.session_state.get('debug_mode', False):
                    st.sidebar.info("is_ready() not available, testing with schema.get()")

                # Just test if we can get the schema
                client.schema.get()
                st.success("Connected to Weaviate successfully!")
                return client
        except Exception as e:
            st.error(f"Error connecting to Weaviate: {str(e)}")
            if st.session_state.get('debug_mode', False):
                import traceback
                st.sidebar.error(f"Connection error details:\n{traceback.format_exc()}")
            return None

    except Exception as e:
        st.error(f"Unexpected error in Weaviate connection: {str(e)}")
        if st.session_state.get('debug_mode', False):
            import traceback
            st.sidebar.error(f"Unexpected error details:\n{traceback.format_exc()}")
        return None