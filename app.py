import streamlit as st
import random
import time
from weaviate_connection import get_weaviate_client
from schema_setup import create_mbti_schema
from data_import import initialize_data
from mbti_chat import MBTIMultiChat
from utils import get_type_nickname, get_type_description, get_type_cognitive_functions

# Page configuration
st.set_page_config(
    page_title="MBTI Multi-Personality Chat",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

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


# Setup and initialization
def initialize_app():
    with st.spinner("Connecting to Weaviate..."):
        client = get_weaviate_client()

    with st.spinner("Setting up database schema..."):
        create_mbti_schema()

    with st.spinner("Initializing MBTI data..."):
        initialize_data()

    with st.spinner("Setting up chat system..."):
        st.session_state.mbti_chat = MBTIMultiChat(client)
        st.session_state.chat_initialized = True

    st.success("Setup complete! You can now start chatting with MBTI personalities.")


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

# Different UI based on selected mode
if chat_mode == "Single Personality":
    col1, col2 = st.columns([1, 3])

    with col1:
        # MBTI type selection with brief descriptions
        selected_type = st.selectbox(
            "Select MBTI Type",
            st.session_state.mbti_chat.mbti_types,
            format_func=lambda x: f"{x} - {get_type_nickname(x)}"
        )

        st.info(get_type_description(selected_type))
        st.caption(f"**Cognitive Functions**: {get_type_cognitive_functions(selected_type)}")

    with col2:
        # Chat interface
        st.subheader(f"Chatting with {selected_type} ({get_type_nickname(selected_type)})")

        # Display chat history
        for message in st.session_state.chat_history:
            if "user" in message:
                st.chat_message("user").write(message["user"])

            if "response" in message and selected_type in message["response"]:
                with st.chat_message("assistant", avatar=f"{selected_type}"):
                    st.write(message["response"][selected_type])

        # User input
        user_input = st.chat_input("Ask something...")

        if user_input:
            # Add user message
            st.chat_message("user").write(user_input)

            # Get response with spinner
            with st.spinner(f"{selected_type} is thinking..."):
                response = st.session_state.mbti_chat.chat_with_type(user_input, selected_type)

            # Display response
            with st.chat_message("assistant", avatar=f"{selected_type}"):
                st.write(response)

            # Force a rerun to update the display
            st.experimental_rerun()

elif chat_mode == "Multi-Personality Chat":
    # Multi-chat interface
    st.subheader("Multi-Personality Chat")

    # Settings
    col1, col2 = st.columns(2)
    with col1:
        num_personalities = st.slider("Number of personalities", 2, 8, 3)
    with col2:
        selected_types = st.multiselect(
            "Select specific types (optional)",
            st.session_state.mbti_chat.mbti_types,
            format_func=lambda x: f"{x} - {get_type_nickname(x)}"
        )

    # Display chat history
    for message in st.session_state.chat_history:
        if "user" in message:
            st.chat_message("user").write(message["user"])

        if "response" in message:
            for mbti_type, resp in message["response"].items():
                with st.chat_message("assistant", avatar=f"{mbti_type}"):
                    st.write(f"**{mbti_type}** - {get_type_nickname(mbti_type)}: {resp}")

    # User input
    user_input = st.chat_input("Ask something...")

    if user_input:
        # Add user message
        st.chat_message("user").write(user_input)

        # Get responses from multiple personalities
        with st.spinner("Multiple personalities are responding..."):
            if selected_types:
                responses = st.session_state.mbti_chat.multi_chat(
                    user_input,
                    types_to_include=selected_types
                )
            else:
                responses = st.session_state.mbti_chat.multi_chat(
                    user_input,
                    num_types=num_personalities
                )

        # Display responses
        for mbti_type, response in responses.items():
            with st.chat_message("assistant", avatar=f"{mbti_type}"):
                st.write(f"**{mbti_type}** - {get_type_nickname(mbti_type)}: {response}")

        # Force a rerun to update the display
        st.experimental_rerun()

elif chat_mode == "Group Discussion":
    st.subheader("MBTI Group Discussion")

    # Discussion settings
    col1, col2 = st.columns(2)

    with col1:
        topic = st.text_input("Discussion Topic", "The future of artificial intelligence")
        num_participants = st.slider("Number of participants", 2, 8, 4)

    with col2:
        selected_participants = st.multiselect(
            "Select specific participants (optional)",
            st.session_state.mbti_chat.mbti_types,
            format_func=lambda x: f"{x} - {get_type_nickname(x)}"
        )
        num_rounds = st.slider("Discussion rounds", 1, 5, 3)

    # Start discussion button
    if st.button("Start New Discussion"):
        if not topic:
            st.error("Please enter a discussion topic")
        else:
            with st.spinner("Discussion in progress... This may take a minute."):
                if selected_participants:
                    participants = selected_participants
                else:
                    participants = random.sample(
                        st.session_state.mbti_chat.mbti_types,
                        min(num_participants, len(st.session_state.mbti_chat.mbti_types))
                    )

                discussion = st.session_state.mbti_chat.group_discussion(
                    topic,
                    participants,
                    num_rounds
                )

                # Save to session state
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
                    with st.chat_message("assistant", avatar=f"{mbti_type}"):
                        st.write(f"**{mbti_type}** - {get_type_nickname(mbti_type)} ({round_info}): {content}")
                else:
                    mbti_type = mbti_part
                    with st.chat_message("assistant", avatar=f"{mbti_type}"):
                        st.write(f"**{mbti_type}** - {get_type_nickname(mbti_type)}: {content}")

# Add a footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center">
        <p>Created with ❤️ using LlamaIndex, Weaviate, and Streamlit</p>
        <p>MBTI personalities are simulated for educational purposes</p>
    </div>
    """,
    unsafe_allow_html=True
)