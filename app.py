import streamlit as st
import random
import os

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
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Define MBTI types and functions
MBTI_TYPES = [
    "INTJ", "INTP", "ENTJ", "ENTP",
    "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ",
    "ISTP", "ISFP", "ESTP", "ESFP"
]


def get_type_nickname(mbti_type):
    """Get the nickname for an MBTI type."""
    nicknames = {
        "INTJ": "The Architect",
        "INTP": "The Logician",
        "ENTJ": "The Commander",
        "ENTP": "The Debater",
        "INFJ": "The Advocate",
        "INFP": "The Mediator",
        "ENFJ": "The Protagonist",
        "ENFP": "The Campaigner",
        "ISTJ": "The Inspector",
        "ISFJ": "The Defender",
        "ESTJ": "The Executive",
        "ESFJ": "The Consul",
        "ISTP": "The Virtuoso",
        "ISFP": "The Artist",
        "ESTP": "The Entrepreneur",
        "ESFP": "The Entertainer"
    }
    return nicknames.get(mbti_type, "")


def get_type_description(mbti_type):
    """Get a short description for an MBTI type."""
    descriptions = {
        "INTJ": "Strategic, independent thinkers with a focus on systems and innovation.",
        "INTP": "Logical, analytical minds that enjoy theoretical concepts and possibilities.",
        "ENTJ": "Decisive leaders who organize people and resources to achieve objectives.",
        "ENTP": "Quick-thinking debaters who enjoy intellectual challenges and possibilities.",
        "INFJ": "Insightful, principled individuals with a focus on helping others and society.",
        "INFP": "Idealistic, authentic individuals who value harmony and personal growth.",
        "ENFJ": "Charismatic leaders who inspire others and facilitate personal development.",
        "ENFP": "Enthusiastic, creative people who see possibilities in everything and everyone.",
        "ISTJ": "Practical, detail-oriented individuals who value tradition and responsibility.",
        "ISFJ": "Loyal, compassionate people who protect and support those they care about.",
        "ESTJ": "Organized, efficient managers who ensure systems and people operate effectively.",
        "ESFJ": "Warm, sociable people who create harmony and take care of practical needs.",
        "ISTP": "Hands-on problem solvers who excel in understanding how things work.",
        "ISFP": "Gentle, artistic souls who live in the moment and value aesthetic experiences.",
        "ESTP": "Energetic, practical people who thrive in dynamic situations and love action.",
        "ESFP": "Spontaneous, fun-loving performers who bring joy and energy to others."
    }
    return descriptions.get(mbti_type, "")


def get_type_cognitive_functions(mbti_type):
    """Get the cognitive functions for an MBTI type."""
    functions = {
        "INTJ": "Ni-Te-Fi-Se (Introverted Intuition, Extraverted Thinking, Introverted Feeling, Extraverted Sensing)",
        "INTP": "Ti-Ne-Si-Fe (Introverted Thinking, Extraverted Intuition, Introverted Sensing, Extraverted Feeling)",
        "ENTJ": "Te-Ni-Se-Fi (Extraverted Thinking, Introverted Intuition, Extraverted Sensing, Introverted Feeling)",
        "ENTP": "Ne-Ti-Fe-Si (Extraverted Intuition, Introverted Thinking, Extraverted Feeling, Introverted Sensing)",
        "INFJ": "Ni-Fe-Ti-Se (Introverted Intuition, Extraverted Feeling, Introverted Thinking, Extraverted Sensing)",
        "INFP": "Fi-Ne-Si-Te (Introverted Feeling, Extraverted Intuition, Introverted Sensing, Extraverted Thinking)",
        "ENFJ": "Fe-Ni-Se-Ti (Extraverted Feeling, Introverted Intuition, Extraverted Sensing, Introverted Thinking)",
        "ENFP": "Ne-Fi-Te-Si (Extraverted Intuition, Introverted Feeling, Extraverted Thinking, Introverted Sensing)",
        "ISTJ": "Si-Te-Fi-Ne (Introverted Sensing, Extraverted Thinking, Introverted Feeling, Extraverted Intuition)",
        "ISFJ": "Si-Fe-Ti-Ne (Introverted Sensing, Extraverted Feeling, Introverted Thinking, Extraverted Intuition)",
        "ESTJ": "Te-Si-Ne-Fi (Extraverted Thinking, Introverted Sensing, Extraverted Intuition, Introverted Feeling)",
        "ESFJ": "Fe-Si-Ne-Ti (Extraverted Feeling, Introverted Sensing, Extraverted Intuition, Introverted Thinking)",
        "ISTP": "Ti-Se-Ni-Fe (Introverted Thinking, Extraverted Sensing, Introverted Intuition, Extraverted Feeling)",
        "ISFP": "Fi-Se-Ni-Te (Introverted Feeling, Extraverted Sensing, Introverted Intuition, Extraverted Thinking)",
        "ESTP": "Se-Ti-Fe-Ni (Extraverted Sensing, Introverted Thinking, Extraverted Feeling, Introverted Intuition)",
        "ESFP": "Se-Fi-Te-Ni (Extraverted Sensing, Introverted Feeling, Extraverted Thinking, Introverted Intuition)"
    }
    return functions.get(mbti_type, "")


def simulate_mbti_response(mbti_type, user_query):
    """
    Simulate a response from a specific MBTI type.
    This is a simplified mock function - in the full version, this would use LLM + Weaviate.
    """
    # Simple responses based on MBTI type - in a real app, this would use OpenAI or similar
    responses = {
        "INTJ": f"As an architect, I see this from a strategic perspective. {user_query}? This requires careful analysis of systems and long-term implications.",
        "INTP": f"Interesting question about '{user_query}'. Let me analyze the logical framework behind this concept...",
        "ENTJ": f"Let's address '{user_query}' efficiently. Here's my executive assessment and plan of action...",
        "ENTP": f"'{user_query}'? That's a fascinating topic with multiple possibilities! Have you considered these perspectives?",
        "INFJ": f"I sense there's deeper meaning behind your question about '{user_query}'. Let me share my insights...",
        "INFP": f"Your question about '{user_query}' resonates with my values. Here's my authentic perspective...",
        "ENFJ": f"I appreciate you asking about '{user_query}'. Let me guide you through my thoughts while considering how this impacts everyone...",
        "ENFP": f"Oh, '{user_query}'! That opens up so many exciting possibilities! Let's explore this together!",
        "ISTJ": f"Regarding '{user_query}', here are the concrete facts and reliable information based on experience...",
        "ISFJ": f"I care about how '{user_query}' affects people. Based on what's worked before, here's my thoughtful response...",
        "ESTJ": f"Let's be practical about '{user_query}'. The most efficient approach based on established procedures is...",
        "ESFJ": f"I want to help with your question about '{user_query}'. Here's what will work best for everyone involved...",
        "ISTP": f"Let me troubleshoot '{user_query}' by breaking it down into its practical components...",
        "ISFP": f"'{user_query}' makes me feel... Here's my personal, in-the-moment response that feels right...",
        "ESTP": f"Let's take action on '{user_query}'! Here's my straightforward, pragmatic approach based on what's happening now...",
        "ESFP": f"'{user_query}'? How fun! Here's my enthusiastic take that brings energy to this conversation..."
    }

    return responses.get(mbti_type, f"Thinking about {user_query}...")


# Sidebar options
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Myers-Briggs_Type_Indicator.svg/1200px-Myers-Briggs_Type_Indicator.svg.png",
    width=200)
st.sidebar.header("Chat Options")

chat_mode = st.sidebar.radio(
    "Select Chat Mode",
    ["Single Personality", "Multi-Personality Chat", "Group Discussion"]
)

# Display connection status
st.sidebar.markdown("---")
if hasattr(st, 'secrets') and 'WEAVIATE_URL' in st.secrets:
    st.sidebar.success("✅ Credentials configured")
else:
    st.sidebar.warning("⚠️ Weaviate credentials not configured")

# Different UI based on selected mode
if chat_mode == "Single Personality":
    col1, col2 = st.columns([1, 3])

    with col1:
        # MBTI type selection with brief descriptions
        selected_type = st.selectbox(
            "Select MBTI Type",
            MBTI_TYPES,
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
            # Add user message to history
            if "user" not in st.session_state.chat_history[-1] if st.session_state.chat_history else True:
                st.session_state.chat_history.append({"user": user_input})

            # Display user message
            st.chat_message("user").write(user_input)

            # Generate response
            with st.spinner(f"{selected_type} is thinking..."):
                response = simulate_mbti_response(selected_type, user_input)

            # Add response to history
            st.session_state.chat_history.append({"response": {selected_type: response}})

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
            MBTI_TYPES,
            format_func=lambda x: f"{x} - {get_type_nickname(x)}"
        )

    # Display chat history
    for message in st.session_state.chat_history:
        if "user" in message:
            st.chat_message("user").write(message["user"])

        if "response" in message and isinstance(message["response"], dict):
            for mbti_type, resp in message["response"].items():
                with st.chat_message("assistant", avatar=f"{mbti_type}"):
                    st.write(f"**{mbti_type}** - {get_type_nickname(mbti_type)}: {resp}")

    # User input
    user_input = st.chat_input("Ask something...")

    if user_input:
        # Add user message
        if "user" not in st.session_state.chat_history[-1] if st.session_state.chat_history else True:
            st.session_state.chat_history.append({"user": user_input})

        # Display user message
        st.chat_message("user").write(user_input)

        # Get responses from multiple personalities
        with st.spinner("Multiple personalities are responding..."):
            types_to_use = selected_types if selected_types else random.sample(MBTI_TYPES, num_personalities)
            responses = {mbti_type: simulate_mbti_response(mbti_type, user_input) for mbti_type in types_to_use}

        # Add responses to history
        st.session_state.chat_history.append({"response": responses})

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
            MBTI_TYPES,
            format_func=lambda x: f"{x} - {get_type_nickname(x)}"
        )
        num_rounds = st.slider("Discussion rounds", 1, 5, 3)

    # Start discussion button
    if st.button("Start New Discussion"):
        if not topic:
            st.error("Please enter a discussion topic")
        else:
            with st.spinner("Discussion in progress... This may take a minute."):
                # Select participants
                participants = selected_participants if selected_participants else random.sample(MBTI_TYPES,
                                                                                                 num_participants)

                # Initialize discussion
                discussion = [f"Group discussion on: {topic}\nParticipants: {', '.join(participants)}"]

                # First round
                round_responses = {}
                for mbti_type in participants:
                    response = simulate_mbti_response(mbti_type, topic)
                    round_responses[mbti_type] = response
                    discussion.append(f"{mbti_type}: {response}")

                # Additional rounds
                for round_num in range(2, num_rounds + 1):
                    new_responses = {}

                    for mbti_type in participants:
                        context = "\n".join([
                            f"{other_type}: {round_responses[other_type]}"
                            for other_type in participants if other_type != mbti_type
                        ])

                        prompt = f"Topic: {topic}\n\nOthers' comments:\n{context}"
                        response = simulate_mbti_response(mbti_type, prompt)
                        new_responses[mbti_type] = response
                        discussion.append(f"{mbti_type} (Round {round_num}): {response}")

                    round_responses = new_responses

                # Store in session state
                st.session_state.current_discussion = discussion

            # Force a rerun to update the display
            st.experimental_rerun()

    # Display current discussion
    if "current_discussion" in st.session_state:
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
        <p>Created with ❤️ using Streamlit</p>
        <p>MBTI personalities are simulated for educational purposes</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Show a note about the full version
st.sidebar.markdown("---")
st.sidebar.info("""
**Note:** This is a demo version with simulated responses. 
The full version uses:
- Weaviate vector database
- LlamaIndex for retrieval
- OpenAI for natural responses
""")