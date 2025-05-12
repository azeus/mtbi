# utils.py

# MBTI type data
MBTI_TYPES = [
    "INTJ", "INTP", "ENTJ", "ENTP",
    "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ",
    "ISTP", "ISFP", "ESTP", "ESFP"
]

# Map MBTI types to emoji avatars
MBTI_AVATARS = {
    "INTJ": "🧠", "INTP": "🔬", "ENTJ": "👑", "ENTP": "💡",
    "INFJ": "🔮", "INFP": "🌈", "ENFJ": "🌟", "ENFP": "✨",
    "ISTJ": "📊", "ISFJ": "🏡", "ESTJ": "📝", "ESFJ": "🤝",
    "ISTP": "🛠️", "ISFP": "🎨", "ESTP": "🏄", "ESFP": "🎭"
}


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
    This is a simplified mock function for when the LLM integration is not available.
    """
    # Simple responses based on MBTI type
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