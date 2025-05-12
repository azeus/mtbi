# weaviate_connection.py - Simplified with better error reporting

import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_weaviate_client():
    """
    Create and return a connection to your Weaviate cluster.
    Simplified for better reliability.
    """
    # First check if the weaviate module is available
    try:
        import weaviate
        if st.session_state.get('debug_mode', False):
            st.sidebar.success("✅ Weaviate client module loaded")
    except ImportError:
        st.error("Weaviate client library not installed. Run: pip install weaviate-client==3.26.7")
        return None

    # Get credentials from secrets or environment
    weaviate_url = None
    weaviate_api_key = None
    openai_api_key = None

    # Check Streamlit secrets
    if hasattr(st, 'secrets'):
        weaviate_url = st.secrets.get('WEAVIATE_URL')
        weaviate_api_key = st.secrets.get('WEAVIATE_API_KEY')
        openai_api_key = st.secrets.get('OPENAI_API_KEY')

        if st.session_state.get('debug_mode', False):
            st.sidebar.text("Credentials check:")
            st.sidebar.text(f"- WEAVIATE_URL: {'Found' if weaviate_url else 'Not found'}")
            st.sidebar.text(f"- WEAVIATE_API_KEY: {'Found' if weaviate_api_key else 'Not found'}")
            st.sidebar.text(f"- OPENAI_API_KEY: {'Found' if openai_api_key else 'Not found'}")

    # Fallback to environment variables
    if not weaviate_url:
        weaviate_url = os.getenv("WEAVIATE_URL")
    if not weaviate_api_key:
        weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
    if not openai_api_key:
        openai_api_key = os.getenv("OPENAI_API_KEY")

    # Validate required credentials
    if not weaviate_url:
        st.error("Missing Weaviate URL. Please set WEAVIATE_URL in your secrets.toml file.")
        return None

    if not weaviate_api_key:
        st.error("Missing Weaviate API Key. Please set WEAVIATE_API_KEY in your secrets.toml file.")
        return None

    # Fix URL format if needed (this is critical)
    if not weaviate_url.startswith(("http://", "https://")):
        if st.session_state.get('debug_mode', False):
            st.sidebar.warning(f"Adding https:// prefix to URL: {weaviate_url}")
        weaviate_url = f"https://{weaviate_url}"

    # Try to connect with different approaches
    try:
        import weaviate

        # Try modern auth approach
        try:
            # Create authentication object
            from weaviate.auth import AuthApiKey
            auth_config = AuthApiKey(api_key=weaviate_api_key)

            # Set up headers
            headers = {}
            if openai_api_key:
                headers["X-OpenAI-Api-Key"] = openai_api_key

            # Create client with modern auth
            if st.session_state.get('debug_mode', False):
                st.sidebar.info(f"Connecting to Weaviate at {weaviate_url}")

            client = weaviate.Client(
                url=weaviate_url,
                auth_client=auth_config,
                additional_headers=headers
            )

            # Test connection
            if client.is_ready():
                if st.session_state.get('debug_mode', False):
                    st.sidebar.success("Connected to Weaviate successfully!")
                return client
            else:
                if st.session_state.get('debug_mode', False):
                    st.sidebar.error("Weaviate server is not ready")
                st.error("Could not connect to Weaviate: Server not ready")
                return None

        except (ImportError, AttributeError, TypeError) as e:
            # Try legacy auth approach
            if st.session_state.get('debug_mode', False):
                st.sidebar.warning(f"Modern auth failed: {str(e)}")
                st.sidebar.info("Trying legacy auth approach...")

            try:
                headers = {}
                if openai_api_key:
                    headers["X-OpenAI-Api-Key"] = openai_api_key

                client = weaviate.Client(
                    url=weaviate_url,
                    auth_config={"api_key": weaviate_api_key},
                    additional_headers=headers
                )

                # Test connection (using schema.get which is available in older versions)
                try:
                    schema = client.schema.get()
                    if st.session_state.get('debug_mode', False):
                        st.sidebar.success("Connected with legacy client successfully!")
                    return client
                except Exception as e:
                    if st.session_state.get('debug_mode', False):
                        st.sidebar.error(f"Schema test failed: {str(e)}")
                    st.error(f"Could not connect to Weaviate: {str(e)}")
                    return None

            except Exception as e:
                if st.session_state.get('debug_mode', False):
                    st.sidebar.error(f"Legacy auth failed: {str(e)}")
                st.error(f"Could not connect to Weaviate: {str(e)}")
                return None

    except Exception as e:
        # Catch-all for any other errors
        st.error(f"Error connecting to Weaviate: {str(e)}")
        if st.session_state.get('debug_mode', False):
            import traceback
            st.sidebar.error(f"Error details:\n{traceback.format_exc()}")
        return None