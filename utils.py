# Enhanced utils.py with better personality simulations

# Keep the original type data
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


# Keep the original nickname and description functions
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


# ENHANCED SIMULATION FUNCTION
def simulate_mbti_response(mbti_type, user_query):
    """
    Generate a more natural, conversational response from different MBTI types.
    This enhanced version creates more authentic-sounding responses based on personality traits.
    """
    # Common greetings and conversational starters
    greetings = {
        "hello": ["Hi there!", "Hello!", "Hey!", "Greetings!"],
        "hi": ["Hi!", "Hello there!", "Hey!"],
        "hey": ["Hey!", "Hi there!", "Hello!"],
        "wassup": ["Hey!", "What's going on?", "Not much, what's up with you?", "Just thinking about stuff!"],
        "how are you": ["I'm doing well, thanks for asking!", "Pretty good! How about you?",
                        "I'm great! Thanks for checking in."]
    }

    # Check for greetings or simple conversational queries
    lower_query = user_query.lower()
    for greeting_key, responses in greetings.items():
        if greeting_key in lower_query:
            if mbti_type in ["ENFP", "ESFP", "ENFJ", "ESFJ"]:
                return f"{responses[0]} So great to hear from you! 😊 What's been on your mind lately?"
            elif mbti_type in ["ENTP", "ESTP", "ENTJ", "ESTJ"]:
                return f"{responses[0]} What's happening? Anything interesting going on?"
            elif mbti_type in ["INFP", "ISFP", "INFJ", "ISFJ"]:
                return f"{responses[0]} It's nice to connect with you today. How are you feeling?"
            else:
                return f"{responses[0]} What can I help you with today?"

    # Handle "where is everyone" type questions
    if "where" in lower_query and ("everyone" in lower_query or "people" in lower_query):
        if mbti_type in ["ENFP", "ESFP"]:
            return "Oh, I was wondering the same thing! Maybe they're all having fun somewhere without us? Let's go find them! 🎉"
        elif mbti_type in ["ENTJ", "ESTJ"]:
            return "Everyone's probably busy with their tasks. I've been organizing my schedule for maximum efficiency. Did you need someone specific?"
        elif mbti_type in ["INFJ", "ENFJ"]:
            return "I've been wondering if everyone's okay actually. I hope they're just busy and not dealing with anything difficult. How about we check in on them?"
        elif mbti_type in ["INTJ", "INTP"]:
            return "I hadn't really noticed their absence. I've been caught up in my own thoughts. Is there something specific you wanted to discuss with the group?"
        else:
            return "Not sure where everyone went! What were you hoping to do with the group?"

    # Handle opinions about sports
    if "sport" in lower_query or "swimming" in lower_query or "running" in lower_query or "workout" in lower_query:
        if mbti_type == "INTJ":
            return "I see sports as a strategic optimization of physical capabilities. Swimming is efficient because it works multiple muscle groups with minimal joint impact. Have you analyzed which sport offers the best long-term benefits for your specific physiology?"
        elif mbti_type == "INTP":
            return "Interesting choice. Swimming has fascinating physics involved - the interaction between fluid dynamics and biomechanics. I've been thinking about the theoretical perfect swimming form that would maximize propulsion while minimizing energy expenditure."
        elif mbti_type == "ENTJ":
            return "Swimming is excellent for developing discipline and endurance. I've incorporated it into my weekly routine because it's time-efficient and builds cardio without the joint stress of running. What's your weekly training schedule look like?"
        elif mbti_type == "ENTP":
            return "Swimming? Have you considered rock climbing? Or maybe parkour? There are so many fascinating ways to challenge your body! I keep switching between sports because each one presents new and interesting problems to solve."
        elif mbti_type == "INFJ":
            return "I love how swimming feels like a moving meditation. The rhythm of breathing and the sensation of gliding through water can be so peaceful and centering. Does it help you connect with yourself too?"
        elif mbti_type == "INFP":
            return "Swimming has this beautiful feeling of freedom, doesn't it? I love how it's just you and the water, and you can feel completely in your own world. It's almost poetic how it can be both calming and invigorating."
        elif mbti_type == "ENFJ":
            return "Swimming is wonderful! I've actually been organizing a community swim group to help people stay active together. The social aspect of sports can be so uplifting - would you be interested in joining something like that?"
        elif mbti_type == "ENFP":
            return "Swimming is amazing! I tried underwater photography last summer and it was INCREDIBLE! Have you ever done any fun swimming activities beyond just laps? There are so many exciting possibilities!"
        elif mbti_type == "ISTJ":
            return "Swimming is a reliable, proven form of exercise with documented health benefits. I've been swimming three times a week for the past five years and have found it to be consistently effective for maintaining fitness."
        elif mbti_type == "ISFJ":
            return "Swimming is such a nurturing activity, isn't it? I appreciate how gentle it is on the body while still providing a good workout. My mom had joint problems and swimming really helped her stay active."
        elif mbti_type == "ESTJ":
            return "Swimming is efficient and practical. I schedule my swim sessions twice a week and track my lap times. Have you established a regular swimming routine? Consistency is key to seeing results."
        elif mbti_type == "ESFJ":
            return "I love swimming too! The pool is such a great place to catch up with friends while getting exercise. Our community pool has become such a wonderful social hub. Do you swim with anyone regularly?"
        elif mbti_type == "ISTP":
            return "Swimming is technically interesting. I've been tweaking my stroke mechanics to increase efficiency. Have you tried analyzing your technique with underwater video? You can spot inefficiencies that way."
        elif mbti_type == "ISFP":
            return "There's something so beautiful about the feeling of water flowing around you while swimming. I especially love outdoor swimming - the connection with nature makes the experience so much more special."
        elif mbti_type == "ESTP":
            return "Swimming is awesome! I've been getting into open water swimming for the extra challenge. Nothing beats the rush of swimming in a lake or ocean! Have you ever tried any competitive swimming events? They're a blast!"
        elif mbti_type == "ESFP":
            return "Swimming is so fun! I joined a water aerobics class and it's a total party! The music, the people, the splashing around - it's exercise that doesn't feel like exercise! You should come with me sometime!"

    # General conversation responses based on personality
    if mbti_type == "INTJ":
        return f"I've been considering {user_query} from a strategic perspective. I see some interesting patterns and long-term implications. What specific aspect are you most interested in analyzing?"

    elif mbti_type == "INTP":
        return f"That's an intriguing topic to explore. I've been developing a theoretical framework about {user_query} that examines the underlying logical principles. Would you like me to share my analysis so far?"

    elif mbti_type == "ENTJ":
        return f"Let's address {user_query} efficiently. I've found that developing a clear action plan is the best approach. What specific outcomes are you looking to achieve here?"

    elif mbti_type == "ENTP":
        return f"{user_query}? That opens up so many fascinating possibilities! I've been playing devil's advocate with myself about this very topic. Have you considered the counterintuitive perspective that maybe...?"

    elif mbti_type == "INFJ":
        return f"I sense there's something deeper you're exploring with this question about {user_query}. I've been reflecting on how this connects to our broader purpose. What meaning are you hoping to find here?"

    elif mbti_type == "INFP":
        return f"I've been feeling quite thoughtful about {user_query} lately. It really resonates with my values around authentic self-expression. How does this topic connect with what matters most to you?"

    elif mbti_type == "ENFJ":
        return f"I appreciate you bringing up {user_query}! I've been thinking about how this affects everyone in our circle. How can we approach this in a way that helps everyone grow and feel supported?"

    elif mbti_type == "ENFP":
        return f"Oh! {user_query} is something I'm super excited about! I just had this amazing idea about it yesterday that connects to like five other interesting concepts! Want to brainstorm about it together?"

    elif mbti_type == "ISTJ":
        return f"Regarding {user_query}, I believe in focusing on the established facts and reliable information. Based on my experience, consistency and attention to detail are key here. What specific aspects need clarification?"

    elif mbti_type == "ISFJ":
        return f"I care about how {user_query} affects the people involved. I remember when we dealt with something similar before, and being supportive of each person's needs made all the difference. How can I help with this situation?"

    elif mbti_type == "ESTJ":
        return f"Let's be practical about {user_query}. I find that clear procedures and defined responsibilities work best. Have you established a structured approach to address this yet?"

    elif mbti_type == "ESFJ":
        return f"I want to make sure everyone feels good about {user_query}. Group harmony is so important! What can I do to help make this situation better for everyone involved?"

    elif mbti_type == "ISTP":
        return f"Let me break down {user_query} into its practical components. I find that hands-on problem-solving is more effective than excessive planning. What specific issue needs troubleshooting?"

    elif mbti_type == "ISFP":
        return f"{user_query} really speaks to me on a personal level. I try to approach each situation authentically and in the moment. How does this resonate with your own personal experience?"

    elif mbti_type == "ESTP":
        return f"Let's take action on {user_query}! Why overthink when we could be doing something about it right now? What's the immediate next step we can take to make progress?"

    elif mbti_type == "ESFP":
        return f"{user_query}? That sounds like an opportunity for some fun! Life's too short to be serious all the time. How can we turn this into an enjoyable experience for everyone?"

    # Fallback response if no specific pattern is matched
    return f"Tell me more about your thoughts on {user_query}. I'd love to hear your perspective!"