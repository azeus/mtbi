# app.py

import streamlit as st
st.set_page_config(
    page_title="MBTI Multi-Personality Chat",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)
import random
import time
import os
from utils import MBTI_TYPES, MBTI_AVATARS, get_type_nickname, get_type_description, get_type_cognitive_functions, simulate_mbti_response


# Optional imports - will be used if files exist
ADVANCED_MODE = False

try:
    from weaviate_connection import get_weaviate_client
except ImportError as e:
    st.warning(f"⚠️ Failed to import `weaviate_connection`: {e}")
else:
    try:
        from schema_setup import create_mbti_schema
    except ImportError as e:
        st.warning(f"⚠️ Failed to import `schema_setup`: {e}")
    else:
        try:
            from data_import import initialize_data
        except ImportError as e:
            st.warning(f"⚠️ Failed to import `data_import`: {e}")
        else:
            try:
                from mbti_chat import MBTIMultiChat
                ADVANCED_MODE = True
                st.info("✅ Advanced mode activated.")
            except ImportError as e:
                st.warning(f"⚠️ Failed to import `mbti_chat`: {e}")

try:
    from llama_integration import check_llama_connection
    LLAMA_CLOUD_AVAILABLE = True
except ImportError:
    LLAMA_CLOUD_AVAILABLE = False
    st.warning("⚠️ Failed to import `llama_integration`. Llama Cloud features will be unavailable.")




# App title and description
st.title("MBTI Multi-Personality Chat System")
st.markdown("""
This application allows you to chat with different Myers-Briggs Type Indicator (MBTI) personalities. 
Experience how different personality types might respond to the same questions!
""")

# Initialize session state
if 'chat_initialized' not in st.session_state:
    st.session_state.chat_initialized = False

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'current_discussion' not in st.session_state:
    st.session_state.current_discussion = None

if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False


# Debug logging function
def debug_log(message):
    if st.session_state.debug_mode:
        st.sidebar.text(f"[DEBUG] {message}")


# Setup and initialization
def initialize_app():
    if ADVANCED_MODE:
        with st.spinner("Setting up Weaviate connection..."):
            client = get_weaviate_client()

        if client is not None:
            debug_log("Weaviate connection successful")
            with st.spinner("Setting up database schema..."):
                create_mbti_schema()

            with st.spinner("Initializing MBTI data..."):
                initialize_data()

            with st.spinner("Setting up chat system..."):
                st.session_state.mbti_chat = MBTIMultiChat(client)
                st.session_state.chat_initialized = True

            st.success("Setup complete! You can now chat with MBTI personalities.")
        else:
            debug_log("Weaviate connection failed")
            st.warning("Weaviate connection failed. Using simulation mode instead.")
            st.session_state.mbti_chat = None
            st.session_state.chat_initialized = True
    else:
        debug_log("Advanced mode not available, using simulation")
        st.info("Running in simulation mode (no Weaviate/LlamaIndex)")
        st.session_state.mbti_chat = None
        st.session_state.chat_initialized = True


# Initialize the app if not already done
if not st.session_state.chat_initialized:
    initialize_app()

# Sidebar options
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Myers-Briggs_Type_Indicator.svg/1200px-Myers-Briggs_Type_Indicator.svg.png",
    width=200)
st.sidebar.header("Chat Options")

chat_mode = st.sidebar.radio(
    "Select Chat Mode",
    ["Single Personality", "Multi-Personality Chat", "Group Discussion"]
)

# System Status Dashboard
with st.sidebar.expander("System Status", expanded=False):
    if st.button("Run Diagnostics"):
        # Check Weaviate
        with st.spinner("Checking Weaviate..."):
            if ADVANCED_MODE:
                client = get_weaviate_client()
                if client is not None and hasattr(client, 'is_ready') and client.is_ready():
                    st.success("✅ Weaviate: Connected")
                    # Show additional cluster info
                    try:
                        meta = client.get_meta()
                        st.info(f"Weaviate version: {meta['version']}")
                    except:
                        pass
                else:
                    st.error("❌ Weaviate: Not connected")
            else:
                st.warning("⚠️ Weaviate: Module not available")

        # Check OpenAI
        with st.spinner("Checking OpenAI..."):
            try:
                from openai import OpenAI

                openai_api_key = None
                if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
                    openai_api_key = st.secrets['OPENAI_API_KEY']
                else:
                    openai_api_key = os.getenv("OPENAI_API_KEY")

                if openai_api_key:
                    # Only pass the API key, no other parameters
                    openai_client = OpenAI(api_key=openai_api_key)

                    response = openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "test"}],
                        max_tokens=5
                    )
                    st.success("✅ OpenAI API: Connected")
                else:
                    st.error("❌ OpenAI API: Missing API key")
            except Exception as e:
                st.error(f"❌ OpenAI API: Error - {str(e)}")

        with st.spinner("Checking Llama Cloud..."):
            if LLAMA_CLOUD_AVAILABLE:
                if check_llama_connection():
                    st.success("✅ Llama Cloud API: Connected")
                else:
                    st.error("❌ Llama Cloud API: Not connected or missing API key")
            else:
                st.warning("⚠️ Llama Cloud API: Module not available")

        # Check MBTI Data
        if ADVANCED_MODE and 'client' in locals() and client is not None:
            with st.spinner("Checking MBTI data..."):
                try:
                    result = client.query.aggregate("MBTIPersonality").with_meta_count().do()
                    count = result.get('data', {}).get('Aggregate', {}).get('MBTIPersonality', [{}])[0].get('meta',
                                                                                                            {}).get(
                        'count', 0)
                    if count > 0:
                        st.success(f"✅ MBTI Data: {count} objects")
                        # Show sample types
                        types_result = client.query.get("MBTIPersonality", ["type"]).with_limit(100).do()
                        types = list(set([obj.get('type') for obj in
                                          types_result.get('data', {}).get('Get', {}).get('MBTIPersonality', [])]))
                        st.info(f"👤 Types found: {', '.join(types)}")
                    else:
                        st.warning("⚠️ MBTI Data: No data found")
                except Exception as e:
                    st.error(f"❌ MBTI Data: Error - {str(e)}")

    # Debug Mode Toggle
    st.session_state.debug_mode = st.checkbox("Enable Debug Logs", value=st.session_state.debug_mode)

# Display connection status
st.sidebar.markdown("---")
if ADVANCED_MODE:
    if hasattr(st, 'secrets') and 'WEAVIATE_URL' in st.secrets and 'OPENAI_API_KEY' in st.secrets:
        if hasattr(st, 'secrets') and 'LLAMA_CLOUD_API_KEY' in st.secrets:
            st.sidebar.success("✅ All credentials configured")
        else:
            st.sidebar.warning("⚠️ Weaviate and OpenAI configured, but Llama Cloud API key missing")
    else:
        st.sidebar.warning("⚠️ Some credentials not configured")
else:
    st.sidebar.info("💡 Basic simulation mode active")

# Simple chat functions for when not using LlamaIndex/Weaviate
def simple_chat_with_type(user_query, mbti_type):
    debug_log(f"Simulating response for {mbti_type}")
    response = simulate_mbti_response(mbti_type, user_query)
    return response


def simple_multi_chat(user_query, types_to_include=None, num_types=3):
    # Determine which types to include
    if types_to_include:
        selected_types = [t for t in types_to_include if t in MBTI_TYPES]
        if not selected_types:
            selected_types = random.sample(MBTI_TYPES, min(num_types, len(MBTI_TYPES)))
    else:
        selected_types = random.sample(MBTI_TYPES, min(num_types, len(MBTI_TYPES)))

    debug_log(f"Simulating responses for {', '.join(selected_types)}")

    # Get responses
    responses = {}
    for mbti_type in selected_types:
        response = simple_chat_with_type(user_query, mbti_type)
        responses[mbti_type] = response

    return responses


def simple_group_discussion(topic, participants=None, num_rounds=3):
    if not participants:
        participants = random.sample(MBTI_TYPES, min(4, len(MBTI_TYPES)))

    debug_log(f"Starting simulated group discussion with {', '.join(participants)}")

    discussion = [f"Group discussion on: {topic}\nParticipants: {', '.join(participants)}"]

    # First round - everyone responds to the topic
    round_responses = {}
    for mbti_type in participants:
        response = simple_chat_with_type(topic, mbti_type)
        round_responses[mbti_type] = response
        discussion.append(f"{mbti_type}: {response}")

    # Additional rounds - respond to others
    for round_num in range(2, num_rounds + 1):
        new_responses = {}
        debug_log(f"Starting discussion round {round_num}")

        for mbti_type in participants:
            # Create context from previous responses
            context = "\n".join([
                f"{other_type}: {round_responses[other_type]}"
                for other_type in participants if other_type != mbti_type
            ])

            prompt = f"Topic: {topic}\n\nOthers' comments:\n{context}"
            response = simple_chat_with_type(prompt, mbti_type)
            new_responses[mbti_type] = response
            discussion.append(f"{mbti_type} (Round {round_num}): {response}")

        round_responses = new_responses

    return discussion


# Different UI based on selected mode
if chat_mode == "Single Personality":
    # MBTI type selection outside of columns
    selected_type = st.selectbox(
        "Select MBTI Type",
        MBTI_TYPES,
        format_func=lambda x: f"{x} - {get_type_nickname(x)}"
    )

    # Information about selected type
    st.info(get_type_description(selected_type))
    st.caption(f"**Cognitive Functions**: {get_type_cognitive_functions(selected_type)}")

    # Chat interface
    st.subheader(f"Chatting with {selected_type} ({get_type_nickname(selected_type)})")

    # Display chat history
    for message in st.session_state.chat_history:
        if "user" in message:
            st.chat_message("user").write(message["user"])

        if "response" in message and selected_type in message["response"]:
            with st.chat_message("assistant", avatar=MBTI_AVATARS[selected_type]):
                st.write(message["response"][selected_type])

    # User input - must be outside of columns
    user_input = st.chat_input("Ask something...")

    if user_input:
        debug_log(f"User input: {user_input}")
        # Add user message to history
        if not st.session_state.chat_history or "user" not in st.session_state.chat_history[-1]:
            st.session_state.chat_history.append({"user": user_input})

        # Display user message
        st.chat_message("user").write(user_input)

        # Generate response
        with st.spinner(f"{selected_type} is thinking..."):
            if st.session_state.mbti_chat is not None:
                try:
                    debug_log(f"Using MBTIMultiChat for {selected_type}")
                    response = st.session_state.mbti_chat.chat_with_type(user_input, selected_type)
                except Exception as e:
                    debug_log(f"Error with MBTIMultiChat: {str(e)}")
                    st.warning(f"Error getting response from advanced system. Falling back to simulation.")
                    response = simple_chat_with_type(user_input, selected_type)
            else:
                response = simple_chat_with_type(user_input, selected_type)

        # Add response to history
        st.session_state.chat_history.append({"response": {selected_type: response}})

        # Display response
        with st.chat_message("assistant", avatar=MBTI_AVATARS[selected_type]):
            st.write(response)

        # Force a rerun to update the display
        st.experimental_rerun()

elif chat_mode == "Multi-Personality Chat":
    # Multi-chat interface
    st.subheader("Multi-Personality Chat")

    # Settings
    num_personalities = st.slider("Number of personalities", 2, 8, 3)
    selected_types = st.multiselect(
        "Select specific types (optional)",
        MBTI_TYPES,
        format_func=lambda x: f"{x} - {get_type_nickname(x)}"
    )

    # Display chat history
    for message in st.session_state.chat_history:
        if "user" in message:
            st.chat_message("user").write(message["user"])

        if "response" in message and isinstance(message["response"], dict):
            for mbti_type, resp in message["response"].items():
                with st.chat_message("assistant", avatar=MBTI_AVATARS[mbti_type]):
                    st.write(f"**{mbti_type}** - {get_type_nickname(mbti_type)}: {resp}")

    # User input - must be outside of any container
    user_input = st.chat_input("Ask something...")

    if user_input:
        debug_log(f"User input (multi-chat): {user_input}")
        # Add user message
        if not st.session_state.chat_history or "user" not in st.session_state.chat_history[-1]:
            st.session_state.chat_history.append({"user": user_input})

        # Display user message
        st.chat_message("user").write(user_input)

        # Get responses from multiple personalities
        with st.spinner("Multiple personalities are responding..."):
            if st.session_state.mbti_chat is not None:
                try:
                    debug_log("Using MBTIMultiChat for multi-chat")
                    responses = st.session_state.mbti_chat.multi_chat(
                        user_input,
                        types_to_include=selected_types if selected_types else None,
                        num_types=num_personalities
                    )
                except Exception as e:
                    debug_log(f"Error with MBTIMultiChat multi-chat: {str(e)}")
                    st.warning(f"Error getting responses from advanced system. Falling back to simulation.")
                    responses = simple_multi_chat(
                        user_input,
                        types_to_include=selected_types if selected_types else None,
                        num_types=num_personalities
                    )
            else:
                responses = simple_multi_chat(
                    user_input,
                    types_to_include=selected_types if selected_types else None,
                    num_types=num_personalities
                )

        # Add responses to history
        st.session_state.chat_history.append({"response": responses})

        # Display responses
        for mbti_type, response in responses.items():
            with st.chat_message("assistant", avatar=MBTI_AVATARS[mbti_type]):
                st.write(f"**{mbti_type}** - {get_type_nickname(mbti_type)}: {response}")

        # Force a rerun to update the display
        st.experimental_rerun()

elif chat_mode == "Group Discussion":
    st.subheader("MBTI Group Discussion")

    # Discussion settings
    topic = st.text_input("Discussion Topic", "The future of artificial intelligence")
    num_participants = st.slider("Number of participants", 2, 8, 4)
    selected_participants = st.multiselect(
        "Select specific participants (optional)",
        MBTI_TYPES,
        format_func=lambda x: f"{x} - {get_type_nickname(x)}"
    )
    num_rounds = st.slider("Discussion rounds", 1, 5, 3)

    # Start discussion button
    if st.button("Start New Discussion"):
        if not topic:
            st.error("Please enter a discussion topic")
        else:
            debug_log(f"Starting group discussion on: {topic}")
            with st.spinner("Discussion in progress... This may take a minute."):
                # Select participants
                participants = selected_participants if selected_participants else random.sample(MBTI_TYPES,
                                                                                                 num_participants)

                # Generate discussion
                if st.session_state.mbti_chat is not None:
                    try:
                        debug_log(f"Using MBTIMultiChat for group discussion with {len(participants)} participants")
                        discussion = st.session_state.mbti_chat.group_discussion(
                            topic,
                            participants,
                            num_rounds
                        )
                    except Exception as e:
                        debug_log(f"Error with MBTIMultiChat group discussion: {str(e)}")
                        st.warning(f"Error generating discussion with advanced system. Falling back to simulation.")
                        discussion = simple_group_discussion(
                            topic,
                            participants,
                            num_rounds
                        )
                else:
                    discussion = simple_group_discussion(
                        topic,
                        participants,
                        num_rounds
                    )

                # Store in session state
                st.session_state.current_discussion = discussion

            # Force a rerun to update the display
            st.experimental_rerun()

    # Display current discussion
    if st.session_state.current_discussion:
        st.info(st.session_state.current_discussion[0])

        for entry in st.session_state.current_discussion[1:]:
            parts = entry.split(":", 1)
            if len(parts) == 2:
                mbti_part = parts[0].strip()
                content = parts[1].strip()

                # Extract just the MBTI type code
                if "Round" in mbti_part:
                    mbti_type = mbti_part.split()[0]
                    round_info = mbti_part.split("(")[1].split(")")[0]
                    with st.chat_message("assistant", avatar=MBTI_AVATARS[mbti_type]):
                        st.write(f"**{mbti_type}** - {get_type_nickname(mbti_type)} ({round_info}): {content}")
                else:
                    mbti_type = mbti_part
                    with st.chat_message("assistant", avatar=MBTI_AVATARS[mbti_type]):
                        st.write(f"**{mbti_type}** - {get_type_nickname(mbti_type)}: {content}")

# Add a footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center">
        <p>Created with ❤️ using Streamlit</p>
        <p>MBTI personalities are simulated for educational purposes</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Show a note about the mode
st.sidebar.markdown("---")
if st.session_state.mbti_chat is not None:
    if hasattr(st.session_state.mbti_chat, 'use_vector_db') and st.session_state.mbti_chat.use_vector_db:
        services = []
        if st.session_state.mbti_chat.use_vector_db:
            services.append("- Weaviate vector database")
        if st.session_state.mbti_chat.use_llama:
            services.append("- Llama Cloud for analytical types")
        if st.session_state.mbti_chat.use_openai:
            services.append("- OpenAI for emotional types")

        if services:
            st.sidebar.success(f"""
            **Advanced Mode Active**
            Using:
            {chr(10).join(services)}
            """)
        else:
            st.sidebar.warning("**Limited functionality in Advanced Mode**")
    else:
        st.sidebar.info("""
        **Simulation Mode Active**
        The full version would use:
        - Weaviate vector database
        - Llama Cloud for analytical types
        - OpenAI for emotional types
        """)

