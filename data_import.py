# data_import_v4.py
# Updated for Weaviate v4 with rate limiting for OpenAI

import uuid
import streamlit as st
import os
import time
from weaviate_connection_v4 import get_weaviate_client
from utils import MBTI_TYPES

# Categories of MBTI information
CATEGORIES = [
    "communication_style",
    "cognitive_functions",
    "values_and_motivations",
    "stress_reactions",
    "career_preferences",
    "relationship_patterns"
]


def generate_mbti_data(client):
    """
    Generate MBTI data using OpenAI and store it in Weaviate.
    Updated for Weaviate v4 and with rate limiting.
    """
    # Get the OpenAI API key
    if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
        openai_api_key = st.secrets['OPENAI_API_KEY']
    else:
        openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        st.error("OpenAI API key is required to generate data.")
        return False

    # Initialize OpenAI client
    try:
        from openai import OpenAI
        # Only pass the API key, no other parameters
        openai_client = OpenAI(api_key=openai_api_key)

        if st.session_state.get('debug_mode', False):
            st.sidebar.success("OpenAI client initialized successfully")
    except ImportError:
        st.error("OpenAI package not installed. Please run: pip install openai==1.3.0")
        return False
    except Exception as e:
        st.error(f"Error initializing OpenAI client: {str(e)}")
        return False

    progress_bar = st.progress(0)
    status_text = st.empty()

    total_items = len(MBTI_TYPES) * len(CATEGORIES)
    completed = 0

    # Create a batch configurator using v4 API
    batch_size = 10

    # Using context manager for Weaviate v4 batch processing
    with client.batch.dynamic() as batch:
        batch.batch_size = batch_size

        for mbti_type in MBTI_TYPES:
            for category in CATEGORIES:
                status_text.text(f"Generating data for {mbti_type} - {category}...")

                # Check if data already exists using v4 API
                try:
                    # Using v4 query API
                    query_result = (
                        client.query
                        .get("MBTIPersonality", ["content"])
                        .with_where({
                            "operator": "And",
                            "operands": [
                                {
                                    "path": ["type"],
                                    "operator": "Equal",
                                    "valueString": mbti_type
                                },
                                {
                                    "path": ["category"],
                                    "operator": "Equal",
                                    "valueString": category
                                }
                            ]
                        })
                        .do()
                    )

                    # Skip if data already exists
                    existing_data = query_result.get('data', {}).get('Get', {}).get('MBTIPersonality', [])
                    if existing_data:
                        st.info(f"Data already exists for {mbti_type} - {category}, skipping...")
                        completed += 1
                        progress_bar.progress(completed / total_items)
                        continue
                except Exception as e:
                    st.warning(f"Error checking existing data: {str(e)}")
                    # Continue anyway - we'll try to add the data

                prompt = f"""
                Create a detailed description of the {mbti_type} personality type's {category.replace('_', ' ')}.
                Include specific traits, tendencies, strengths, weaknesses, and examples.
                Write approximately 500-800 words in an educational, informative style.
                """

                # Implement rate limiting and retry logic for OpenAI
                max_retries = 5
                for attempt in range(max_retries):
                    try:
                        response = openai_client.chat.completions.create(
                            model="gpt-3.5-turbo",  # Using 3.5 to reduce costs
                            messages=[
                                {"role": "system", "content": "You are an expert on MBTI personality psychology."},
                                {"role": "user", "content": prompt}
                            ],
                            max_tokens=1200
                        )

                        content = response.choices[0].message.content

                        # Add to Weaviate using v4 API
                        data_object = {
                            "content": content,
                            "type": mbti_type,
                            "category": category,
                            "source": "generated_by_gpt35"
                        }

                        # Add the object to batch using v4 API
                        batch.add_data_object(
                            data_object=data_object,
                            class_name="MBTIPersonality",
                            uuid=str(uuid.uuid4())
                        )

                        st.success(f"Generated and added: {mbti_type} - {category}")
                        break  # Success, exit retry loop

                    except Exception as e:
                        error_message = str(e).lower()
                        if "rate limit" in error_message or "429" in error_message:
                            retry_wait = (2 ** attempt) + 1  # Exponential backoff: 1, 3, 5, 9, 17
                            if attempt < max_retries - 1:  # Not the last attempt
                                st.warning(
                                    f"Rate limited by OpenAI. Waiting {retry_wait} seconds before retry {attempt + 1}/{max_retries}...")
                                time.sleep(retry_wait)
                            else:
                                st.error(f"Failed after {max_retries} attempts: {error_message}")
                        else:
                            st.error(f"Error generating content for {mbti_type} - {category}: {error_message}")
                            break  # Non-rate limit error, exit retry loop

                completed += 1
                progress_bar.progress(completed / total_items)

    progress_bar.progress(1.0)
    status_text.text("Data generation complete!")

    return True


def check_data_exists(client):
    """
    Check if MBTI data already exists in the Weaviate database.
    Updated for Weaviate v4.

    Returns:
        bool: True if data exists, False otherwise
    """
    try:
        # Using v4 query API
        result = (
            client.query
            .get("MBTIPersonality", ["content"])
            .with_limit(1)
            .do()
        )

        return bool(result.get('data', {}).get('Get', {}).get('MBTIPersonality', []))
    except Exception as e:
        st.warning(f"Error checking data: {str(e)}")
        return False


def initialize_data():
    """
    Initialize the MBTI data in Weaviate if it doesn't exist.
    """
    client = get_weaviate_client()
    if client is None:
        return False

    # Check if data exists
    if check_data_exists(client):
        st.info("MBTI data already exists in the database")
        return True

    # Generate data
    return generate_mbti_data(client)


if __name__ == "__main__":
    # You can run this file directly to import data
    initialize_data()