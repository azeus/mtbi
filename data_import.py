# data_import.py

import uuid
import streamlit as st
import os
from weaviate_connection import get_weaviate_client
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
        openai_client = OpenAI(api_key=openai_api_key)
    except ImportError:
        st.error("OpenAI package not installed. Please run: pip install openai")
        return False

    progress_bar = st.progress(0)
    status_text = st.empty()

    total_items = len(MBTI_TYPES) * len(CATEGORIES)
    completed = 0

    with client.batch as batch:
        batch.batch_size = 10

        for mbti_type in MBTI_TYPES:
            for category in CATEGORIES:
                status_text.text(f"Generating data for {mbti_type} - {category}...")

                # Check if data already exists
                try:
                    result = client.query.get(
                        "MBTIPersonality",
                        ["content"]
                    ).with_where({
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
                    }).do()

                    # Skip if data already exists
                    if result.get('data', {}).get('Get', {}).get('MBTIPersonality', []):
                        st.info(f"Data already exists for {mbti_type} - {category}, skipping...")
                        completed += 1
                        progress_bar.progress(completed / total_items)
                        continue
                except:
                    pass  # Continue if query fails

                prompt = f"""
                Create a detailed description of the {mbti_type} personality type's {category.replace('_', ' ')}.
                Include specific traits, tendencies, strengths, weaknesses, and examples.
                Write approximately 500-800 words in an educational, informative style.
                """

                try:
                    response = openai_client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are an expert on MBTI personality psychology."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=1200
                    )

                    content = response.choices[0].message.content

                    # Add to Weaviate
                    data_object = {
                        "content": content,
                        "type": mbti_type,
                        "category": category,
                        "source": "generated_by_gpt4"
                    }

                    batch.add_data_object(
                        data_object=data_object,
                        class_name="MBTIPersonality",
                        uuid=uuid.uuid4()
                    )

                    st.success(f"Generated and added: {mbti_type} - {category}")

                except Exception as e:
                    st.error(f"Error generating content for {mbti_type} - {category}: {e}")

                completed += 1
                progress_bar.progress(completed / total_items)

    progress_bar.progress(1.0)
    status_text.text("Data generation complete!")

    return True


def check_data_exists(client):
    """
    Check if MBTI data already exists in the Weaviate database.

    Returns:
        bool: True if data exists, False otherwise
    """
    try:
        result = client.query.get(
            "MBTIPersonality",
            ["content"]
        ).with_limit(1).do()

        return bool(result.get('data', {}).get('Get', {}).get('MBTIPersonality', []))
    except:
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