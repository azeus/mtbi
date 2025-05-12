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