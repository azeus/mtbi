from weaviate_connection import get_weaviate_client


def create_mbti_schema():
    """
    Create the MBTI personality schema in Weaviate.
    Only creates the schema if it doesn't already exist.
    """
    # Get Weaviate client
    client = get_weaviate_client()

    # Define MBTI schema
    mbti_schema = {
        "class": "MBTIPersonality",
        "description": "Data related to MBTI personality types",
        "vectorizer": "text2vec-openai",  # Using OpenAI's embeddings
        "moduleConfig": {
            "text2vec-openai": {
                "model": "ada",
                "modelVersion": "002",
                "type": "text"
            }
        },
        "properties": [
            {
                "name": "content",
                "dataType": ["text"],
                "description": "The text content about the personality type",
                "moduleConfig": {
                    "text2vec-openai": {
                        "skip": False,
                        "vectorizePropertyName": False
                    }
                }
            },
            {
                "name": "type",
                "dataType": ["string"],
                "description": "The MBTI type (e.g., INTJ, ENFP)",
                "moduleConfig": {
                    "text2vec-openai": {
                        "skip": True  # We don't need to vectorize this property
                    }
                }
            },
            {
                "name": "category",
                "dataType": ["string"],
                "description": "Category of the content (e.g., communication_style, values)",
                "moduleConfig": {
                    "text2vec-openai": {
                        "skip": True
                    }
                }
            },
            {
                "name": "source",
                "dataType": ["string"],
                "description": "Source of the information",
                "moduleConfig": {
                    "text2vec-openai": {
                        "skip": True
                    }
                }
            }
        ]
    }

    # Check if schema exists and create if needed
    try:
        client.schema.get("MBTIPersonality")
        print("Schema 'MBTIPersonality' already exists")
        return True
    except:
        # Create schema
        try:
            client.schema.create_class(mbti_schema)
            print("Schema 'MBTIPersonality' created successfully")
            return True
        except Exception as e:
            print(f"Error creating schema: {e}")
            return False


if __name__ == "__main__":
    # You can run this file directly to create the schema
    create_mbti_schema()