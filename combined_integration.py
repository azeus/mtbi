# combined_integration.py
# Centralized integration with Weaviate, OpenAI, and Llama Cloud

import os
import streamlit as st
import logging
import random
import time
from typing import Dict, List, Optional, Any, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our custom modules with fallbacks
try:
    from llama_integration_robust import generate_llama_response, is_llama_available

    LLAMA_CLOUD_AVAILABLE = is_llama_available()
    if LLAMA_CLOUD_AVAILABLE:
        logger.info("Llama Cloud integration loaded successfully")
    else:
        logger.warning("Llama Cloud is not available - will use fallbacks")
except ImportError:
    logger.warning("Llama Cloud integration not found - will use fallbacks")
    LLAMA_CLOUD_AVAILABLE = False

# Check for OpenAI
try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
    logger.info("OpenAI package loaded successfully")
except ImportError:
    logger.warning("OpenAI package not available - will use fallbacks")
    OPENAI_AVAILABLE = False

# Try to import LlamaIndex components with fallbacks
try:
    # Import the core components
    from llama_index.core import VectorStoreIndex
    from llama_index.core.retrievers import VectorIndexRetriever
    from llama_index.core.query_engine import RetrieverQueryEngine
    from llama_index.core.response_synthesizers import ResponseSynthesizer

    # Import the vector store for Weaviate
    from llama_index.vector_stores.weaviate import WeaviateVectorStore

    # Import the OpenAI LLM
    from llama_index.llms.openai import OpenAI as LlamaIndexOpenAI

    LLAMA_INDEX_AVAILABLE = True
    logger.info("LlamaIndex components loaded successfully")
except ImportError as e:
    logger.warning(f"LlamaIndex import error: {e}")
    LLAMA_INDEX_AVAILABLE = False


class IntegratedMBTISystem:
    """
    Centralized class that manages all integrations for the MBTI chat system.
    """

    def __init__(self, weaviate_client=None):
        """
        Initialize the integrated system.

        Args:
            weaviate_client: Weaviate client instance (can be None)
        """
        self.weaviate_client = weaviate_client
        self.openai_client = None
        self.llama_index = None
        self.llm = None

        # Initialize available services
        self.services = {
            "weaviate": weaviate_client is not None,
            "openai": False,
            "llama_cloud": LLAMA_CLOUD_AVAILABLE,
            "llama_index": False
        }

        # Initialize model allocation strategy
        self.model_allocation = self._initialize_model_allocation()

        # Setup available services
        self._setup_openai()
        if self.services["weaviate"] and LLAMA_INDEX_AVAILABLE:
            self._setup_llama_index()

        # Log available services
        logger.info(f"Available services: {', '.join([k for k, v in self.services.items() if v])}")

    def _initialize_model_allocation(self) -> Dict[str, str]:
        """Define which model to use for each MBTI type"""
        # Default allocation
        allocation = {
            # Analytical types - use Llama Cloud if available
            "INTJ": "llama_cloud" if LLAMA_CLOUD_AVAILABLE else "openai",
            "INTP": "llama_cloud" if LLAMA_CLOUD_AVAILABLE else "openai",
            "ENTJ": "llama_cloud" if LLAMA_CLOUD_AVAILABLE else "openai",
            "ENTP": "llama_cloud" if LLAMA_CLOUD_AVAILABLE else "openai",
            "ISTJ": "llama_cloud" if LLAMA_CLOUD_AVAILABLE else "openai",
            "ESTJ": "llama_cloud" if LLAMA_CLOUD_AVAILABLE else "openai",
            "ISTP": "llama_cloud" if LLAMA_CLOUD_AVAILABLE else "openai",

            # Emotional/empathetic types - use OpenAI
            "INFJ": "openai",
            "INFP": "openai",
            "ENFJ": "openai",
            "ENFP": "openai",
            "ISFJ": "openai",
            "ESFJ": "openai",
            "ISFP": "openai",
            "ESFP": "openai",
            "ESTP": "openai"
        }

        # If OpenAI is not available, use Llama Cloud for all if available
        if not OPENAI_AVAILABLE and LLAMA_CLOUD_AVAILABLE:
            return {mbti_type: "llama_cloud" for mbti_type in allocation}

        # If neither is available, use simulation for all
        if not OPENAI_AVAILABLE and not LLAMA_CLOUD_AVAILABLE:
            return {mbti_type: "simulation" for mbti_type in allocation}

        return allocation

    def _setup_openai(self) -> None:
        """Setup OpenAI client if possible"""
        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI package not available - skipping setup")
            return

        try:
            # Get API key
            openai_api_key = None
            if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
                openai_api_key = st.secrets['OPENAI_API_KEY']
            else:
                openai_api_key = os.getenv("OPENAI_API_KEY")

            if not openai_api_key:
                logger.warning("OpenAI API key not found - OpenAI will not be available")
                return

            # Setup client
            self.openai_client = OpenAI(api_key=openai_api_key)

            # Test the connection with retry logic
            test_success = False
            for attempt in range(3):
                try:
                    # Simple test query with minimal tokens
                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "test"}],
                        max_tokens=5
                    )
                    test_success = True
                    break
                except Exception as e:
                    error_message = str(e).lower()
                    if "rate limit" in error_message or "429" in error_message:
                        if attempt < 2:  # Not the last attempt
                            wait_time = (2 ** attempt) + 1
                            logger.warning(f"OpenAI rate limit hit. Retrying in {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            logger.error(f"OpenAI rate limit persists - connection test failed")
                    else:
                        logger.error(f"OpenAI test failed: {e}")
                        break

            # Mark the service as available if test was successful
            self.services["openai"] = test_success
            if test_success:
                logger.info("OpenAI client initialized and tested successfully")

        except Exception as e:
            logger.error(f"Error setting up OpenAI: {e}")
            self.services["openai"] = False

    def _setup_llama_index(self) -> None:
        """Setup LlamaIndex if possible"""
        if not LLAMA_INDEX_AVAILABLE or not self.services["weaviate"]:
            logger.warning("LlamaIndex or Weaviate not available - skipping setup")
            return

        try:
            # Get OpenAI API key for embeddings
            openai_api_key = None
            if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
                openai_api_key = st.secrets['OPENAI_API_KEY']
            else:
                openai_api_key = os.getenv("OPENAI_API_KEY")

            if not openai_api_key:
                logger.warning("OpenAI API key not found for embeddings - LlamaIndex will not be available")
                return

            # Setup vector store
            vector_store = WeaviateVectorStore(
                weaviate_client=self.weaviate_client,
                index_name="MBTIPersonality",
                text_key="content",
                metadata_keys=["type", "category"]
            )

            # Create index from vector store
            self.llama_index = VectorStoreIndex.from_vector_store(vector_store)

            # Initialize LLM
            self.llm = LlamaIndexOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.7,
                api_key=openai_api_key
            )

            # Mark service as available
            self.services["llama_index"] = True
            logger.info("LlamaIndex initialized successfully")

        except Exception as e:
            logger.error(f"Error setting up LlamaIndex: {e}")
            self.services["llama_index"] = False

    def get_mbti_retriever(self, mbti_type: str):
        """Create a retriever for a specific MBTI type"""
        if not self.services["llama_index"] or self.llama_index is None:
            return None

        try:
            # Create metadata filter for the specific MBTI type
            filters = {"type": mbti_type}

            # Create retriever with the filter
            retriever = VectorIndexRetriever(
                index=self.llama_index,
                similarity_top_k=3,
                filters=filters
            )

            return retriever
        except Exception as e:
            logger.error(f"Error creating retriever: {e}")
            return None

    def get_type_info(self, mbti_type: str) -> str:
        """Get a description of an MBTI type for prompts"""
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

    def format_response(self, response: str, mbti_type: str) -> str:
        """Format AI response to match MBTI style"""
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

        # Ensure the response matches personality style
        if mbti_type in ["ENFP", "ESFP", "ENFJ", "ENTP"]:
            if "!" not in response and not response.endswith("?"):
                response += "!"

            # Add emoji for certain personalities
            if mbti_type in ["ENFP", "ESFP"] and random.random() < 0.5:
                emoji_options = ["😊", "✨", "💫", "🌟", "💡", "🎉", "🌈"]
                response += f" {random.choice(emoji_options)}"

        return response

    def generate_response(self, query: str, mbti_type: str) -> str:
        """Generate a response using the best available method"""
        # Determine which model to use
        model = self.model_allocation.get(mbti_type, "simulation")
        logger.info(f"Using {model} for {mbti_type}")

        # 1. Try LlamaIndex approach if available - it uses the knowledge base
        if self.services["llama_index"] and self.llama_index is not None:
            try:
                # Get retriever for this personality
                retriever = self.get_mbti_retriever(mbti_type)
                if retriever:
                    # Create the personalized query
                    personalized_query = f"""
                    Question: {query}

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

                    # Format and return
                    return self.format_response(str(response), mbti_type)
            except Exception as e:
                logger.warning(f"LlamaIndex approach failed: {e}")

        # 2. Try Llama Cloud if it's the selected model
        if model == "llama_cloud" and self.services["llama_cloud"]:
            try:
                # Get type info
                type_info = self.get_type_info(mbti_type)

                # Create system prompt
                system_prompt = f"""
                You are simulating an {mbti_type} personality type from Myers-Briggs Type Indicator.

                {mbti_type} personalities are {type_info}.

                Respond as if you are this personality type, expressing their natural style:
                - Use vocabulary and expressions typical for this type
                - Make it feel like a casual conversation with a friend, not a formal analysis
                - Do NOT mention that you are roleplaying or simulating a personality
                """

                # Get response with retry logic built into the function
                response = generate_llama_response(
                    prompt=query,
                    system_prompt=system_prompt,
                    model="llama-3-70b-instruct"
                )

                if response:
                    return self.format_response(response, mbti_type)
            except Exception as e:
                logger.warning(f"Llama Cloud approach failed: {e}")

        # 3. Try OpenAI if it's the selected model or as fallback
        if (model == "openai" or (model == "llama_cloud" and not self.services["llama_cloud"])) and self.services[
            "openai"]:
            try:
                # Get type info
                type_info = self.get_type_info(mbti_type)

                # Create system prompt
                system_prompt = f"""
                You are simulating an {mbti_type} personality type from Myers-Briggs Type Indicator.

                {mbti_type} personalities are {type_info}.

                Respond as if you are this personality type, expressing their natural style:
                - Use vocabulary and expressions typical for this type
                - Make it feel like a casual conversation with a friend, not a formal analysis
                - Do NOT mention that you are roleplaying or simulating a personality
                """

                # Implement retry logic for OpenAI
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        # Get response
                        response = self.openai_client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": query}
                            ],
                            temperature=0.7,
                            max_tokens=300
                        )

                        # Extract and format response
                        ai_response = response.choices[0].message.content.strip()
                        return self.format_response(ai_response, mbti_type)
                    except Exception as e:
                        error_message = str(e).lower()
                        if "rate limit" in error_message or "429" in error_message:
                            if attempt < max_retries - 1:  # Not the last attempt
                                wait_time = (2 ** attempt) + 1
                                logger.warning(f"OpenAI rate limit hit. Retrying in {wait_time}s...")
                                time.sleep(wait_time)
                            else:
                                logger.error("OpenAI rate limits persist - using fallback")
                        else:
                            logger.error(f"OpenAI error: {e}")
                            break  # Non-rate limit error, exit retry loop
            except Exception as e:
                logger.warning(f"OpenAI approach failed: {e}")

        # 4. Fallback to simulation
        try:
            from utils import simulate_mbti_response
            return simulate_mbti_response(mbti_type, query)
        except Exception as e:
            logger.error(f"Simulation fallback failed: {e}")
            # Ultimate fallback message
            return f"I'm sorry, I'm having trouble responding as {mbti_type} right now. Please try again later."

    def multi_chat(
            self,
            query: str,
            types_to_include: Optional[List[str]] = None,
            num_types: int = 3
    ) -> Dict[str, str]:
        """Get responses from multiple MBTI types"""
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
            response = self.generate_response(query, mbti_type)
            responses[mbti_type] = response

        return responses

    def group_discussion(
            self,
            topic: str,
            participants: Optional[List[str]] = None,
            num_rounds: int = 3
    ) -> List[str]:
        """Generate a group discussion between MBTI types"""
        from utils import MBTI_TYPES

        # Select participants if not specified
        if not participants:
            participants = random.sample(MBTI_TYPES, min(4, len(MBTI_TYPES)))

        # Start discussion
        discussion = [f"Group discussion on: {topic}\nParticipants: {', '.join(participants)}"]

        # First round - everyone responds to the topic
        round_responses = {}
        for mbti_type in participants:
            response = self.generate_response(topic, mbti_type)
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

                # Create prompt with context
                prompt = f"""
                Topic: {topic}

                Here are comments from other MBTI personalities:
                {context}

                How would you (as an {mbti_type}) respond to these comments?
                """

                response = self.generate_response(prompt, mbti_type)
                new_responses[mbti_type] = response
                discussion.append(f"{mbti_type} (Round {round_num}): {response}")

            round_responses = new_responses

        return discussion

    def get_service_status(self) -> Dict[str, bool]:
        """Get status of all integration services"""
        return self.services