# mbti_chat.py

import random
import os
import streamlit as st
from weaviate_connection import get_weaviate_client
from utils import MBTI_TYPES, get_type_nickname, simulate_mbti_response


def initialize_llama_index():
    try:
        if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            openai_api_key = st.secrets['OPENAI_API_KEY']
        else:
            openai_api_key = os.getenv("OPENAI_API_KEY")

        if not openai_api_key:
            st.warning("OpenAI API key is required.")
            return None, None

        # ✅ Updated imports for LlamaIndex 0.8.34+
        from llama_index.core import VectorStoreIndex, StorageContext, PromptTemplate
        from llama_index.core.readers import SimpleDirectoryReader
        from llama_index.vector_stores.weaviate import WeaviateVectorStore
        from llama_index.llms.openai import OpenAI

        # Get Weaviate client
        client = get_weaviate_client()
        if client is None:
            return None, None

        # Vector store
        vector_store = WeaviateVectorStore(
            weaviate_client=client,
            index_name="MBTIPersonality",
            text_key="content"
        )

        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context=storage_context
        )

        return client, index

    except Exception as e:
        st.error(f"Error initializing LlamaIndex: {str(e)}")
        return None, None


class MBTIMultiChat:
    def __init__(self, client=None):
        self.mbti_types = MBTI_TYPES
        self.conversation_history = []
        self.use_llm = False

        if client is None:
            client, index = initialize_llama_index()
        else:
            _, index = initialize_llama_index()

        self.client = client
        self.index = index

        self.engines = {}
        if self.client is not None and self.index is not None:
            self.use_llm = True
            for mbti_type in self.mbti_types:
                self.engines[mbti_type] = self._create_query_engine(mbti_type)
        else:
            st.warning("Using simulated responses. LlamaIndex/Weaviate not available.")

    def _create_query_engine(self, mbti_type):
        try:
            from llama_index.core.query_engine import QueryMode
            from llama_index.core.prompts import PromptTemplate

            mbti_filter = {"type": mbti_type}

            template = (
                f"You are a chatbot that embodies the {mbti_type} personality type from Myers-Briggs Type Indicator. "
                f"Base your responses on the personality traits, communication style, and cognitive functions of the "
                f"{mbti_type} type. Respond in first person as if you are someone with this personality type. "
                f"Be authentic to how a {mbti_type} would communicate and think."
            )

            query_engine = self.index.as_query_engine(
                query_mode=QueryMode.DEFAULT,
                filters=mbti_filter,
                similarity_top_k=5,
                response_mode="compact",
                use_async=True,
                text_qa_template=PromptTemplate(template),
            )

            return query_engine

        except Exception as e:
            st.error(f"Error creating query engine for {mbti_type}: {str(e)}")
            return None

    def chat_with_type(self, user_query, mbti_type):
        if mbti_type not in self.mbti_types:
            return f"Error: {mbti_type} is not a valid MBTI type"

        if self.use_llm and mbti_type in self.engines:
            try:
                engine = self.engines[mbti_type]
                response = engine.query(user_query)
                response_text = str(response)
            except Exception as e:
                st.warning(f"Error using LLM for {mbti_type}: {str(e)}")
                st.warning("Falling back to simulated response.")
                response_text = simulate_mbti_response(mbti_type, user_query)
        else:
            response_text = simulate_mbti_response(mbti_type, user_query)

        entry = {"user": user_query, "response": {mbti_type: response_text}}
        self.conversation_history.append(entry)

        return response_text

    def multi_chat(self, user_query, types_to_include=None, num_types=3):
        if types_to_include:
            selected_types = [t for t in types_to_include if t in self.mbti_types]
            if not selected_types:
                selected_types = random.sample(self.mbti_types, min(num_types, len(self.mbti_types)))
        else:
            selected_types = random.sample(self.mbti_types, min(num_types, len(self.mbti_types)))

        responses = {}
        for mbti_type in selected_types:
            response = self.chat_with_type(user_query, mbti_type)
            responses[mbti_type] = response

        return responses

    def group_discussion(self, topic, participants=None, num_rounds=3):
        if not participants:
            participants = random.sample(self.mbti_types, min(4, len(self.mbti_types)))

        discussion = [f"Group discussion on: {topic}\nParticipants: {', '.join(participants)}"]

        round_responses = {}
        for mbti_type in participants:
            response = self.chat_with_type(topic, mbti_type)
            round_responses[mbti_type] = response
            discussion.append(f"{mbti_type}: {response}")

        for round_num in range(2, num_rounds + 1):
            new_responses = {}

            for mbti_type in participants:
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
