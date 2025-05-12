import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_weaviate_client():
    """
    Create and return a connection to your Weaviate cluster.
    Uses Streamlit secrets or environment variables for credentials.
    Works with both Weaviate v3.x and v4.x client libraries.

    Returns:
        A Weaviate client instance connected to your cluster.
    """
    try:
        # Get credentials (first try Streamlit secrets, then environment variables)
        if hasattr(st, 'secrets') and 'WEAVIATE_URL' in st.secrets:
            weaviate_url = st.secrets['WEAVIATE_URL']
            weaviate_api_key = st.secrets['WEAVIATE_API_KEY']
            openai_api_key = st.secrets['OPENAI_API_KEY']
        else:
            # Fall back to environment variables
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

        # Import weaviate and try to detect version
        import weaviate

        # Check for Weaviate v4.x (has the WeaviateClient class)
        if hasattr(weaviate, 'WeaviateClient'):
            from weaviate import WeaviateClient
            from weaviate.auth import AuthApiKey

            # New Weaviate client v4.x
            st.info("Using Weaviate Client v4.x")
            client = WeaviateClient(
                connection_params=weaviate.connect.ConnectionParams.from_url(
                    url=weaviate_url,
                    auth_credentials=AuthApiKey(api_key=weaviate_api_key),
                    headers={
                        "X-OpenAI-Api-Key": openai_api_key
                    }
                )
            )

            # Test connection
            try:
                client.collections.list()
                st.success("Connected to Weaviate")
                return client
            except Exception as e:
                st.error(f"Error connecting to Weaviate v4.x: {str(e)}")
                st.stop()

        # Older Weaviate v3.x client
        else:
            from weaviate.auth import AuthApiKey

            st.info("Using Weaviate Client v3.x")

            # Create authentication object
            auth_config = AuthApiKey(api_key=weaviate_api_key)

            # Additional headers for OpenAI integration
            additional_headers = {
                "X-OpenAI-Api-Key": openai_api_key
            }

            # Initialize client
            client = weaviate.Client(
                url=weaviate_url,
                auth_client=auth_config,
                additional_headers=additional_headers
            )

            # Verify connection
            if not client.is_ready():
                st.error("Could not connect to Weaviate v3.x. Please check your credentials and network.")
                st.stop()

            st.success("Connected to Weaviate")
            return client

    except ImportError:
        st.error("Weaviate client library not installed. Please run: pip install weaviate-client")
        st.stop()
    except Exception as e:
        st.error(f"Error connecting to Weaviate: {str(e)}")
        st.stop()