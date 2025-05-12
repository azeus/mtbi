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
            return None

        if not openai_api_key:
            st.error("Missing OpenAI API key. Please set OPENAI_API_KEY.")
            return None

        # Import weaviate
        import weaviate
        from weaviate.auth import AuthApiKey

        # Initialize client using v3.x API which is more compatible with LlamaIndex
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
                auth_client=auth_config,
                additional_headers=additional_headers
            )

            # Verify connection
            if client.is_ready():
                st.success("Connected to Weaviate successfully!")
                return client
            else:
                st.error("Could not connect to Weaviate. Please check your credentials and network.")
                return None

        except Exception as e:
            st.error(f"Error connecting to Weaviate: {str(e)}")
            return None

    except ImportError:
        st.error("Weaviate client library not installed. Please run: pip install weaviate-client==3.26.7")
        return None
    except Exception as e:
        st.error(f"Error connecting to Weaviate: {str(e)}")
        return None