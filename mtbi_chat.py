import random
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter, FilterOperator
import streamlit as st
import os
from weaviate_connection import get_weaviate_client


class MBTIMultiChat:
    def __init__(self, client=None):
        """
        Initialize the MBTI Multi-Chat system.

        Args:
            client: A Weaviate client instance (optional)
        """
        # Get OpenAI API key
        if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            openai_api_key = st.secrets['OPENAI_API_KEY']
        else:
            openai_api_key = os.getenv("OPENAI_API_KEY")

        if not openai_api_key:
            raise ValueError("OpenAI API key is required")

        # Set up LlamaIndex
        Settings.llm = OpenAI(
            model="gpt-4",
            api_key=openai_api_key,
            temperature=0.7
        )

        # Get Weaviate client if not provided
        self.client = client or get_weaviate_client()

        # Set up vector store
        self.vector_store = WeaviateVectorStore(
            weaviate_client=self.client,
            index_name="MBTIPersonality",
            text_key="content"
        )

        # Create storage context
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

        # Create global index
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store,
            storage_context=self.storage_context
        )

        # MBTI types
        self.mbti_types = [
            "INTJ", "INTP", "ENTJ", "ENTP",
            "INFJ", "INFP", "ENFJ", "ENFP",
            "ISTJ", "ISFJ", "ESTJ", "ESFJ",
            "ISTP", "ISFP", "ESTP", "ESFP"
        ]

        # Create query engines for each type
        self.engines = {}
        for mbti_type in self.mbti_types:
            self.engines[mbti_type] = self._create_query_engine(mbti_type)

        self.conversation_history = []

    def _create_query_engine(self, mbti_type):
        """
        Create a query engine for a specific MBTI type.

        Args:
            mbti_type: The MBTI type to create a query engine for

        Returns:
            A query engine for the specified MBTI type
        """
        # Create filter for the MBTI type
        filters = MetadataFilters(
            filters=[
                MetadataFilter(
                    key="type",
                    operator=FilterOperator.EQ,
                    value=mbti_type
                )
            ]
        )

        # Create system prompt for the MBTI type
        system_prompt = f"""
        You are a chatbot that embodies the {mbti_type} personality type from Myers-Briggs Type Indicator.

        As a {mbti_type}, your communication style, values, and perspectives should authentically 
        reflect this personality type. Base your responses on the information retrieved about the
        {mbti_type} personality type's traits, cognitive functions, and tendencies.

        Respond in first person as if you are someone with the {mbti_type} personality type. Your response should:
        1. Use language patterns typical of a {mbti_type}
        2. Prioritize the values important to this type
        3. Approach problems in the way this type would
        4. Express emotions and reactions authentic to this type

        Be natural and conversational rather than explicitly stating "As an {mbti_type}..." - simply embody
        the personality in your response.
        """

        # Create query engine
        query_engine = self.index.as_query_engine(
            similarity_top_k=7,
            filters=filters,
            system_prompt=system_prompt
        )

        return query_engine

    def chat_with_type(self, user_query, mbti_type):
        """
        Chat with a specific MBTI personality type.

        Args:
            user_query: The user's query
            mbti_type: The MBTI type to chat with

        Returns:
            The response from the MBTI type
        """
        if mbti_type not in self.engines:
            return f"Error: {mbti_type} is not a valid MBTI type"

        # Get response
        engine = self.engines[mbti_type]
        response = engine.query(user_query)

        # Add to history
        self.conversation_history.append({
            "user": user_query,
            "response": {mbti_type: str(response)}
        })

        return str(response)

    def multi_chat(self, user_query, types_to_include=None, num_types=3):
        """
        Chat with multiple MBTI personality types.

        Args:
            user_query: The user's query
            types_to_include: Specific MBTI types to include (optional)
            num_types: Number of random types to include if types_to_include is not provided

        Returns:
            A dictionary mapping MBTI types to responses
        """
        # Determine which types to include
        if types_to_include:
            selected_types = [t for t in types_to_include if t in self.mbti_types]
            if not selected_types:
                selected_types = random.sample(self.mbti_types, min(num_types, len(self.mbti_types)))
        else:
            selected_types = random.sample(self.mbti_types, min(num_types, len(self.mbti_types)))

        # Get responses
        responses = {}
        for mbti_type in selected_types:
            response = self.chat_with_type(user_query, mbti_type)
            responses[mbti_type] = response

        return responses

    def group_discussion(self, topic, participants=None, num_rounds=3):
        """
        Simulate a group discussion among MBTI types.

        Args:
            topic: The discussion topic
            participants: List of MBTI types to include (optional)
            num_rounds: Number of discussion rounds

        Returns:
            A list of discussion entries
        """
        if not participants:
            participants = random.sample(self.mbti_types, min(4, len(self.mbti_types)))

        discussion = [f"Group discussion on: {topic}\nParticipants: {', '.join(participants)}"]

        # First round - everyone responds to the topic
        round_responses = {}
        for mbti_type in participants:
            response = self.chat_with_type(topic, mbti_type)
            round_responses[mbti_type] = response
            discussion.append(f"{mbti_type}: {response}")

        # Additional rounds - respond to others
        for round_num in range(2, num_rounds + 1):
            new_responses = {}

            for mbti_type in participants:
                # Create context from previous responses
                context = "\n".join([
                    f"{other_type}: {round_responses[other_type]}"
                    for other_type in participants if other_type != mbti_type
                ])

                prompt = f"""Topic: {topic}

                Here are the comments from others in our discussion:
                {context}

                How would you respond to these perspectives?"""

                response = self.chat_with_type(prompt, mbti_type)
                new_responses[mbti_type] = response
                discussion.append(f"{mbti_type} (Round {round_num}): {response}")

            round_responses = new_responses

        return discussion