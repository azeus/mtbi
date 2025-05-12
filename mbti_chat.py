# mbti_chat_updated.py
# Updated for newer LlamaIndex versions (0.10.x+)

import os
import streamlit as st
from typing import List, Dict, Optional, Any
import random

# Import LlamaIndex components
try:
    # Import the core components
    from llama_index.core import VectorStoreIndex
    from llama_index.core.retrievers import VectorIndexRetriever
    from llama_index.core.query_engine import RetrieverQueryEngine
    from llama_index.core.response_synthesizers import ResponseSynthesizer

    # Import the vector store for Weaviate
    from llama_index.vector_stores.weaviate import WeaviateVectorStore

    # Import the OpenAI LLM
    from llama_index.llms.openai import OpenAI

    LLAMA_INDEX_AVAILABLE = True
except ImportError as e:
    if st.session_state.get('debug_mode', False):
        st.sidebar.warning(f"LlamaIndex import error: {str(e)}")
    LLAMA_INDEX_AVAILABLE = False


class MBTIMultiChat:
    """
    A class for chatting with different MBTI personality types.
    Updated for newer LlamaIndex versions.
    """

    def __init__(self, weaviate_client=None):
        """
        Initialize the MBTI chat system.

        Args:
            weaviate_client: Weaviate client for vector storage
        """
        self.client = weaviate_client
        self.use_llm = False
        self.index = None
        self.llm = None

        # Try to initialize LlamaIndex components if available
        if LLAMA_INDEX_AVAILABLE and self.client is not None:
            self._setup_llama_index()

    def _setup_llama_index(self):
        """Set up LlamaIndex with Weaviate and OpenAI."""
        try:
            # Get OpenAI API key
            openai_api_key = None
            if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
                openai_api_key = st.secrets['OPENAI_API_KEY']
            else:
                openai_api_key = os.getenv("OPENAI_API_KEY")

            if not openai_api_key:
                if st.session_state.get('debug_mode', False):
                    st.sidebar.warning("OpenAI API key not found. Using simulation mode.")
                return

            # Setup vector store
            vector_store = WeaviateVectorStore(
                weaviate_client=self.client,
                index_name="MBTIPersonality",
                text_key="content",
                metadata_keys=["type", "category"]
            )

            # Create index from vector store
            self.index = VectorStoreIndex.from_vector_store(vector_store)

            # Initialize LLM
            self.llm = OpenAI(
                model="gpt-3.5-turbo",
                temperature=0.7,
                api_key=openai_api_key
            )

            self.use_llm = True
            if st.session_state.get('debug_mode', False):
                st.sidebar.success("LlamaIndex initialized successfully with OpenAI")

        except Exception as e:
            self.use_llm = False
            if st.session_state.get('debug_mode', False):
                st.sidebar.error(f"Error setting up LlamaIndex: {str(e)}")
                import traceback
                st.sidebar.error(traceback.format_exc())

    def _get_mbti_retriever(self, mbti_type: str):
        """
        Create a retriever for a specific MBTI type.

        Args:
            mbti_type: The MBTI type to retrieve information for

        Returns:
            A retriever configured for the specified MBTI type
        """
        if not self.use_llm or self.index is None:
            return None

        # Create metadata filter for the specific MBTI type
        filters = {"type": mbti_type}

        # Create retriever with the filter
        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=3,
            filters=filters
        )

        return retriever

    def chat_with_type(self, user_query: str, mbti_type: str) -> str:
        """
        Generate a response from a specific MBTI type.

        Args:
            user_query: User's message
            mbti_type: MBTI type to respond as

        Returns:
            Response from the MBTI personality
        """
        # Check if we can use LlamaIndex + OpenAI
        if self.use_llm and self.index is not None and self.llm is not None:
            try:
                # Get retriever for this MBTI type
                retriever = self._get_mbti_retriever(mbti_type)

                if retriever:
                    # Personalize the query to get type-specific information
                    personalized_query = f"""
                    Question: {user_query}

                    How would an {mbti_type} personality type respond to this? 
                    Consider their cognitive functions, core values, and communication style.
                    Make your response sound like a casual friend, not an analysis.
                    """

                    # Create response synthesizer
                    response_synthesizer = ResponseSynthesizer.from_args(
                        llm=self.llm,
                        response_mode="compact"
                    )

                    # Create query engine
                    query_engine = RetrieverQueryEngine(
                        retriever=retriever,
                        response_synthesizer=response_synthesizer
                    )

                    # Generate response
                    response = query_engine.query(personalized_query)

                    # Post-process to make it more conversational
                    final_response = self._format_ai_response(str(response), mbti_type)

                    return final_response

            except Exception as e:
                if st.session_state.get('debug_mode', False):
                    st.sidebar.error(f"Error generating response with LlamaIndex: {str(e)}")
                # Fall back to simulation if there's an error

        # If we can't use LlamaIndex, try using pure OpenAI
        try:
            from openai import OpenAI

            # Get API key
            openai_api_key = None
            if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
                openai_api_key = st.secrets['OPENAI_API_KEY']
            else:
                openai_api_key = os.getenv("OPENAI_API_KEY")

            if openai_api_key:
                openai_client = OpenAI(api_key=openai_api_key)

                # Get MBTI type information
                type_info = self._get_type_info(mbti_type)

                # Create a prompt for OpenAI
                system_prompt = f"""
                You are simulating an {mbti_type} personality type from Myers-Briggs Type Indicator.

                {mbti_type} personalities are {type_info}.

                Respond as if you are this personality type, expressing their natural style:
                - Use vocabulary and expressions typical for this type
                - Make it feel like a casual conversation with a friend, not a formal analysis
                - Do NOT mention that you are roleplaying or simulating a personality
                """

                # Get response from OpenAI
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_query}
                    ],
                    temperature=0.7,
                    max_tokens=300
                )

                # Extract and format the response
                ai_response = response.choices[0].message.content.strip()
                return self._format_ai_response(ai_response, mbti_type)
        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.sidebar.error(f"Error using direct OpenAI: {str(e)}")

        # Fallback to simulation
        from utils import simulate_mbti_response
        return simulate_mbti_response(mbti_type, user_query)

    def _get_type_info(self, mbti_type: str) -> str:
        """Get a description of the MBTI type for the prompt."""
        descriptions = {
            "INTJ": "strategic, analytical, and independent with a focus on long-term plans and systems thinking",
            "INTP": "logical, theoretical, and objective with a focus on analyzing concepts and solving complex problems",
            "ENTJ": "decisive, organized, and efficient with a focus on leadership and achieving goals",
            "ENTP": "innovative, debating, and curious with a focus on exploring possibilities and challenging ideas",
            "INFJ": "insightful, idealistic, and empathetic with a focus on connecting with others and finding meaning",
            "INFP": "compassionate, creative, and authentic with a focus on personal values and helping others",
            "ENFJ": "charismatic, supportive, and inspirational with a focus on bringing out the best in people",
            "ENFP": "enthusiastic, creative, and people-oriented with a focus on possibilities and connections",
            "ISTJ": "practical, reliable, and detail-oriented with a focus on responsibility and tradition",
            "ISFJ": "nurturing, detailed, and loyal with a focus on supporting others and maintaining harmony",
            "ESTJ": "organized, practical, and direct with a focus on getting things done efficiently",
            "ESFJ": "warm, social, and conscientious with a focus on caring for others and maintaining harmony",
            "ISTP": "pragmatic, logical, and adaptable with a focus on understanding systems and solving problems",
            "ISFP": "sensitive, creative, and present-oriented with a focus on aesthetic experiences and authenticity",
            "ESTP": "energetic, practical, and adaptable with a focus on immediate experiences and problem-solving",
            "ESFP": "spontaneous, enthusiastic, and social with a focus on enjoying life and bringing joy to others"
        }
        return descriptions.get(mbti_type, "unique and interesting")

    def _format_ai_response(self, response: str, mbti_type: str) -> str:
        """
        Format the AI response to be more conversational and match the MBTI style.

        Args:
            response: Raw AI response
            mbti_type: MBTI type

        Returns:
            Formatted, conversational response
        """
        # Remove any prefixes that might indicate the personality type
        prefixes_to_remove = [
            f"{mbti_type}:",
            "As an MBTI personality, ",
            f"As an {mbti_type} personality, ",
            f"As an {mbti_type}, ",
            f"As a {mbti_type}, ",
            "Response: "
        ]

        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()

        # Ensure the response isn't too formal with the right amount of friendliness
        # based on personality type

        # Enthusiastic types get exclamation marks and emoji
        if mbti_type in ["ENFP", "ESFP", "ENFJ", "ENTP"]:
            if "!" not in response and not response.endswith("?"):
                response += "!"

            # Add emoji for certain personalities that would use them
            if mbti_type in ["ENFP", "ESFP"] and random.random() < 0.5:
                emoji_options = ["😊", "✨", "💫", "🌟", "💡", "🎉", "🌈"]
                response += f" {random.choice(emoji_options)}"

        return response

    def multi_chat(
            self,
            user_query: str,
            types_to_include: Optional[List[str]] = None,
            num_types: int = 3
    ) -> Dict[str, str]:
        """
        Get responses from multiple MBTI types.

        Args:
            user_query: User's message
            types_to_include: Specific MBTI types to include (optional)
            num_types: Number of random types to include if types_to_include is None

        Returns:
            Dictionary mapping MBTI types to their responses
        """
        from utils import MBTI_TYPES

        # Determine which types to include
        if types_to_include:
            selected_types = [t for t in types_to_include if t in MBTI_TYPES]
            if not selected_types:
                selected_types = random.sample(MBTI_TYPES, min(num_types, len(MBTI_TYPES)))
        else:
            selected_types = random.sample(MBTI_TYPES, min(num_types, len(MBTI_TYPES)))

        # Get responses from each type
        responses = {}
        for mbti_type in selected_types:
            response = self.chat_with_type(user_query, mbti_type)
            responses[mbti_type] = response

        return responses

    def group_discussion(
            self,
            topic: str,
            participants: Optional[List[str]] = None,
            num_rounds: int = 3
    ) -> List[str]:
        """
        Generate a group discussion between different MBTI types.

        Args:
            topic: Discussion topic
            participants: List of MBTI types to participate
            num_rounds: Number of discussion rounds

        Returns:
            List of discussion entries
        """
        from utils import MBTI_TYPES

        # Select participants if not specified
        if not participants:
            participants = random.sample(MBTI_TYPES, min(4, len(MBTI_TYPES)))

        # Start discussion
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

                # Create a prompt that includes the discussion context
                prompt = f"""
                Topic: {topic}

                Here are comments from other MBTI personalities:
                {context}

                How would you (as an {mbti_type}) respond to these comments?
                """

                response = self.chat_with_type(prompt, mbti_type)
                new_responses[mbti_type] = response
                discussion.append(f"{mbti_type} (Round {round_num}): {response}")

            round_responses = new_responses

        return discussion