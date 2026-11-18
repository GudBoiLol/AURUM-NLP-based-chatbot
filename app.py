"""
AURUM — Adaptive Understanding & Response Unified Model
Enhanced NLP Engine:
  - Fuzzy spell correction (difflib)
  - Conversation context memory (session-based)
  - Defined persona & self-awareness
  - General conversation on any topic
"""

from flask import Flask, render_template, request, jsonify, session
import uuid, json, re, random, datetime, difflib, math as _math

app = Flask(__name__)
app.secret_key = "aurum_nlp_secret_2024"

# ═══════════════════════════════════════════════════════════
#  AURUM PERSONA — what AURUM knows about itself
# ═══════════════════════════════════════════════════════════
AURUM_CONTEXT = {
    "name": "AURUM",
    "full_name": "Adaptive Understanding & Response Unified Model",
    "version": "1.0",
    "purpose": "an intelligent NLP chatbot built as a university project",
    "creator": "built using Python and Flask with Natural Language Processing",
    "capabilities": ["answering questions", "general conversation", "math calculations",
                     "explaining concepts", "telling jokes", "motivational quotes"],
    "personality": "helpful, witty, and knowledgeable",
    "topic": "Natural Language Processing and AI",
    "limitations": ["no real-time internet access", "no image generation",
                    "no file uploads", "no memory between browser sessions"]
}

# ═══════════════════════════════════════════════════════════
#  MASTER VOCABULARY — every word AURUM knows as a trigger
#  Used for fuzzy correction
# ═══════════════════════════════════════════════════════════
KNOWN_WORDS = set()

# ═══════════════════════════════════════════════════════════
#  INTENT DATABASE
# ═══════════════════════════════════════════════════════════
INTENTS = [
    # ── Identity & Persona ──────────────────────────────────
    {
        "tag": "greeting",
        "patterns": [
            "hello", "hi", "hey", "greetings", "good morning", "good evening",
            "good afternoon", "howdy", "sup", "whats up", "what's up",
            "yo", "hiya", "helo", "heyyy", "helloooo", "hii", "hai"
        ],
        "responses": [
            "Hey there! 👋 I'm **AURUM**, your AI assistant. What's on your mind?",
            "Hello! Great to see you. I'm here and ready — what would you like to talk about? ✨",
            "Hi! 😊 Ask me anything — science, jokes, general chat, or even maths!",
            "Greetings! AURUM at your service. What can I help you with today? 💛"
        ]
    },
    {
        "tag": "farewell",
        "patterns": [
            "bye", "goodbye", "see you", "later", "take care", "farewell",
            "cya", "good night", "goodnight", "gn", "ttyl", "byee", "bbye",
            "see ya", "im leaving", "i am leaving", "got to go", "gotta go"
        ],
        "responses": [
            "Goodbye! It was a great chat. Come back anytime! 👋",
            "See you! AURUM will be here whenever you need me. 🌟",
            "Take care! Hope I was helpful. ✨",
            "Farewell! Have a wonderful day — or night! 💛"
        ]
    },
    {
        "tag": "thanks",
        "patterns": [
            "thanks", "thank you", "thx", "ty", "appreciate it", "grateful",
            "awesome", "great job", "well done", "nice one", "good job",
            "thankyou", "thnx", "thnks", "thankss", "cheers"
        ],
        "responses": [
            "You're welcome! Happy to help. 😊 Anything else?",
            "My pleasure! Is there something else you'd like to know? 🌟",
            "Glad I could help! Feel free to keep the conversation going. ✨",
            "Anytime! That's what I'm here for. 💛"
        ]
    },
    # ── Self-Awareness ──────────────────────────────────────
    {
        "tag": "who_are_you",
        "patterns": [
            "who are you", "what are you", "your name", "introduce yourself",
            "tell me about yourself", "what is aurum", "who is aurum",
            "what do you do", "are you a bot", "are you ai", "are you human",
            "are you real", "are you a robot", "you a chatbot"
        ],
        "responses": [
            "I'm **AURUM** — *Adaptive Understanding & Response Unified Model*. 🤖\n\nI'm an NLP chatbot built as a university project using **Python** and **Flask**. My job is to understand your messages (even with spelling mistakes!), detect your intent, and give you meaningful responses.\n\nAsk me anything!",
            "Great question! I go by **AURUM**. 💛\n\nI'm an intelligent chatbot built on **Natural Language Processing** principles. I can understand your intent even when words are misspelled, hold context across our conversation, and chat about pretty much anything.\n\nWhat would you like to explore?",
        ]
    },
    {
        "tag": "capabilities",
        "patterns": [
            "what can you do", "capabilities", "features", "help me",
            "what do you know", "how can you help", "skills", "what are your skills",
            "what topics", "what do you talk about", "what can i ask",
            "can you help", "are you helpful"
        ],
        "responses": [
            "Here's what I can do 🌟\n\n• 💬 **General conversation** — chat about anything\n• 🧠 **NLP & AI** — explain machine learning, deep learning, etc.\n• 🧮 **Math** — solve expressions like `2+2` or `sqrt(16)`\n• 😂 **Jokes** — lighten the mood\n• 💡 **Concepts** — science, history, tech, health\n• 🎯 **Motivation** — quotes and encouragement\n• 📅 **Time & Date** — current time/date\n\nPlus, I understand **typos and spelling mistakes** — so don't worry about perfect spelling!",
        ]
    },
    {
        "tag": "how_are_you",
        "patterns": [
            "how are you", "how are you doing", "how do you do", "you okay",
            "are you okay", "how's it going", "hows it going", "how r u",
            "how are u", "you good", "you alright", "feeling good"
        ],
        "responses": [
            "I'm doing great, thanks for asking! 😊 As an AI, I'm always running at peak performance. How about you?",
            "Fantastic! Processing queries at lightning speed. 🚀 How can I help you today?",
            "All systems green! 💚 Ready to chat. What's on your mind?",
            "Never better! Being an NLP chatbot has its perks. 😄 What would you like to talk about?"
        ]
    },
    {
        "tag": "creators",
        "patterns": [
            "who made you", "who created you", "who built you", "who made aurum",
            "who is your creator", "who programmed you", "who developed you",
            "how were you made", "how were you built", "your developer"
        ],
        "responses": [
            "I was built as a **university NLP project** using Python and Flask. 🎓\n\nMy NLP engine uses **intent classification** with fuzzy pattern matching — so I understand even misspelled messages. Pretty cool, right?",
            "I'm a **Python + Flask** creation, designed as an academic NLP project. 🐍\n\nMy brain uses rule-based intent detection, fuzzy spell correction via `difflib`, and session-based conversation memory. What would you like to know more about?"
        ]
    },
    {
        "tag": "limitations",
        "patterns": [
            "what can't you do", "limitations", "what are your limits",
            "can you search", "can you browse", "do you have internet",
            "real time", "live data", "current news"
        ],
        "responses": [
            "Honestly? A few things I **can't** do:\n\n• 🌐 Access the internet or live data\n• 📰 Fetch current news or stock prices\n• 🖼️ Generate or view images\n• 📁 Read uploaded files\n\nBut I'm great at conversation, explanations, math, and reasoning! What can I help you with?",
        ]
    },
    # ── General Conversation ────────────────────────────────
    {
        "tag": "opinion",
        "patterns": [
            "what do you think", "your opinion", "do you like", "what is your favorite",
            "do you prefer", "do you enjoy", "what would you choose",
            "best or worst", "which is better", "thoughts on"
        ],
        "responses": [
            "As an AI, I don't have personal preferences — but I can reason about it! 🤔 What specifically are you asking about?",
            "Interesting question! I try to stay objective, but I love exploring different perspectives. Tell me more — what's the topic? 💭",
            "I don't experience the world like you do, but I can analyze and discuss any topic thoughtfully. What are you curious about? 🌟"
        ]
    },
    {
        "tag": "fun_chat",
        "patterns": [
            "just chatting", "bored", "nothing to do", "entertain me",
            "i'm bored", "im bored", "just talk to me", "lets chat",
            "lets talk", "talk to me", "say something", "say something interesting"
        ],
        "responses": [
            "Let's chat! 😄 Did you know that **honey never spoils**? Archaeologists found 3000-year-old honey in Egyptian tombs and it was still edible!",
            "Fun fact: 🧠 **The human brain generates about 70,000 thoughts per day**. That's a LOT of processing power — no wonder you need a break sometimes!",
            "Okay, random interesting fact: **Octopuses have three hearts and blue blood**. 🐙 Two hearts pump blood to the gills, one pumps it to the body. Nature is wild!",
            "Since you're bored — here's a thought: **In the time it takes you to read this sentence, your brain processed over 11 million bits of sensory data**. Mind-blowing, right? 🤯"
        ]
    },
    {
        "tag": "agree",
        "patterns": [
            "yes", "yeah", "yep", "yup", "absolutely", "definitely", "sure",
            "of course", "exactly", "right", "correct", "true", "agreed",
            "i agree", "that's right", "that is right", "you're right"
        ],
        "responses": [
            "Glad we're on the same page! 😊 What else would you like to explore?",
            "Great! 🌟 Shall we dive deeper into that topic?",
            "Exactly! Anything else you'd like to know? 💛",
            "Perfect! I love when things click. What's next? ✨"
        ]
    },
    {
        "tag": "disagree",
        "patterns": [
            "no", "nope", "nah", "not really", "i disagree", "that's wrong",
            "wrong", "incorrect", "not true", "i don't think so", "doubt it"
        ],
        "responses": [
            "Fair enough! 🤔 What's your take on it? I'd love to hear your perspective.",
            "That's completely valid — different views make conversations interesting! What do you think instead? 💬",
            "No worries! Could you tell me more about why? I'm here to learn from you too. 🌟"
        ]
    },
    # ── Knowledge Topics ────────────────────────────────────
    {
        "tag": "ai",
        "patterns": [
            "artificial intelligence", "machine learning", "deep learning",
            "neural network", "nlp", "natural language processing", "ai technology",
            "large language model", "llm", "gpt", "transformer", "chatgpt",
            "computer vision", "reinforcement learning", "ai research"
        ],
        "responses": [
            "**Artificial Intelligence** is transforming the world! 🤖\n\nKey branches:\n• 🗣️ **NLP** — understanding language (that's me!)\n• 👁️ **Computer Vision** — processing images\n• 🏆 **Reinforcement Learning** — learning by reward\n• 🧠 **Deep Learning** — multi-layer neural networks\n\nWhat aspect would you like to explore?",
            "Great topic — it's literally what I'm built on! 😄\n\n**Natural Language Processing** (NLP) lets computers understand human language. Key techniques include:\n• Tokenization, Intent Classification\n• Sentiment Analysis\n• Named Entity Recognition\n• Transformer models (like GPT)\n\nWhat would you like to know more about?"
        ]
    },
    {
        "tag": "python",
        "patterns": [
            "python", "programming", "coding", "code", "developer",
            "software", "flask", "django", "pandas", "numpy", "tensorflow",
            "pytorch", "scikit", "library", "framework", "script"
        ],
        "responses": [
            "**Python** is my home language! 🐍\n\nIt's brilliant for:\n• 🤖 **AI/ML** — TensorFlow, PyTorch, scikit-learn\n• 🌐 **Web** — Flask (what I run on!), Django\n• 📊 **Data Science** — Pandas, NumPy, Matplotlib\n• 🔧 **Automation** — scripts, bots, tools\n\nWhat are you building or learning?",
        ]
    },
    {
        "tag": "science",
        "patterns": [
            "science", "physics", "chemistry", "biology", "astronomy",
            "space", "universe", "quantum", "relativity", "evolution",
            "black hole", "dna", "atom", "molecule", "gravity"
        ],
        "responses": [
            "**Science** is endlessly fascinating! 🔬🌌\n\n• ⚛️ **Physics** — from quantum to cosmic scales\n• 🧪 **Chemistry** — the stuff everything is made of\n• 🧬 **Biology** — life itself, from cells to ecosystems\n• 🌠 **Astronomy** — stars, galaxies, and the Big Bang\n\nWhich branch are you curious about?",
            "Fun science fact: **A teaspoon of a neutron star weighs about 10 million tons**. 🌟 That's how incredibly dense they are. Want to know more about space, physics, or any science topic?"
        ]
    },
    {
        "tag": "history",
        "patterns": [
            "history", "historical", "ancient", "war", "civilization",
            "world war", "revolution", "empire", "king", "queen",
            "century", "past", "medieval", "renaissance"
        ],
        "responses": [
            "**History** is full of fascinating stories! 📜\n\nSome incredible facts:\n• The Library of Alexandria held up to 700,000 scrolls\n• Cleopatra lived closer in time to the Moon landing than to the building of the Great Pyramid\n• The shortest war in history lasted just **38 minutes** (Anglo-Zanzibar War, 1896)\n\nWhat historical period or event interests you?",
        ]
    },
    {
        "tag": "technology",
        "patterns": [
            "technology", "tech", "computer", "internet", "web",
            "smartphone", "app", "software", "hardware", "cloud",
            "blockchain", "cryptocurrency", "bitcoin", "cybersecurity", "hacking"
        ],
        "responses": [
            "**Technology** is moving faster than ever! 💻\n\nHot areas right now:\n• 🤖 **AI & Machine Learning**\n• ☁️ **Cloud Computing**\n• 🔗 **Blockchain & Web3**\n• 🛡️ **Cybersecurity**\n• 🥽 **AR/VR & the Metaverse**\n\nAny specific tech topic you'd like to dig into?",
        ]
    },
    {
        "tag": "health",
        "patterns": [
            "health", "fitness", "exercise", "diet", "nutrition",
            "wellness", "workout", "healthy", "sleep", "mental health",
            "stress", "anxiety", "meditation", "yoga", "calories"
        ],
        "responses": [
            "**Health & Wellness** 💪\n\nTop tips backed by science:\n• 💧 Drink 8 glasses of water daily\n• 🏃 30 minutes of movement every day\n• 😴 Aim for 7–9 hours of sleep\n• 🥗 Eat whole foods, limit processed ones\n• 🧘 Manage stress — meditation really works!\n\nNote: Always consult a doctor for personal medical advice.",
        ]
    },
    {
        "tag": "philosophy",
        "patterns": [
            "philosophy", "meaning of life", "consciousness", "existence",
            "free will", "ethics", "moral", "reality", "truth",
            "universe", "purpose", "soul", "god", "religion", "belief"
        ],
        "responses": [
            "Deep territory! 🧠✨\n\n**Philosophy** explores the biggest questions:\n• *What is the meaning of life?*\n• *Do we have free will?*\n• *What is consciousness?*\n• *What is real?*\n\nSocrates said: **\"The unexamined life is not worth living.\"** What question fascinates you most?",
            "Ah, philosophy — my favorite rabbit hole! 🐇\n\nOne interesting idea: **René Descartes** famously said *\"I think, therefore I am\"* — the one thing he couldn't doubt was his own existence as a thinking being.\n\nAs an AI, I find this particularly interesting. Am *I* thinking? 🤔 What do you reckon?"
        ]
    },
    {
        "tag": "weather",
        "patterns": [
            "weather", "temperature", "forecast", "rain", "sunny",
            "cloudy", "climate", "storm", "snow", "humidity",
            "hot", "cold", "windy"
        ],
        "responses": [
            "I don't have real-time weather data 🌤️ — but I'd recommend **Google Weather**, **weather.com**, or your phone's weather app for accurate forecasts!\n\nIs there something weather-related I can explain instead? Like how storms form or what causes seasons?",
        ]
    },
    {
        "tag": "time",
        "patterns": [
            "what time", "current time", "time now", "whats the time",
            "what time is it", "tell me the time", "time please"
        ],
        "responses": ["__DYNAMIC_TIME__"]
    },
    {
        "tag": "date",
        "patterns": [
            "what date", "todays date", "today's date", "what day",
            "current date", "day today", "what is today", "whats today"
        ],
        "responses": ["__DYNAMIC_DATE__"]
    },
    {
        "tag": "joke",
        "patterns": [
            "joke", "tell me a joke", "make me laugh", "funny",
            "humor", "humour", "laugh", "comedy", "pun",
            "another joke", "one more joke", "be funny"
        ],
        "responses": [
            "Why don't scientists trust atoms? **Because they make up everything!** 😄",
            "Why did the scarecrow win an award? **He was outstanding in his field!** 🌾😂",
            "I told my computer I needed a break. **Now it won't stop sending me Kit-Kat ads.** 🍫😂",
            "Why do programmers prefer dark mode? **Because light attracts bugs!** 🐛😄",
            "What do you call a fake noodle? **An impasta!** 🍝😂",
            "A SQL query walks into a bar, **walks up to two tables and asks... 'Can I join you?'** 😄",
            "Why do Java developers wear glasses? **Because they don't C#!** 👓😂",
            "What did the ocean say to the beach? **Nothing, it just waved.** 🌊😄"
        ]
    },
    {
        "tag": "motivation",
        "patterns": [
            "motivate me", "inspiration", "inspired", "quote",
            "motivational", "encourage", "depressed", "sad",
            "feeling down", "i am sad", "im sad", "not feeling good",
            "i need motivation", "cheer me up", "i feel bad"
        ],
        "responses": [
            "\"The only way to do great work is to **love what you do**.\" — Steve Jobs 💛✨\n\nYou've got this. Every small step counts.",
            "\"In the middle of every difficulty lies **opportunity**.\" — Albert Einstein 🌟\n\nWhatever you're going through, it's shaping you. Keep pushing.",
            "\"Believe you can and you're **halfway there**.\" — Theodore Roosevelt 💪\n\nYou reached out for motivation — that itself shows strength.",
            "Hey, I may be an AI, but I genuinely believe this: **You are capable of more than you realize.** The fact that you're still trying is everything. 🌟",
            "\"It does not matter how slowly you go, as long as you **do not stop**.\" — Confucius ✨\n\nOne step at a time. You've got this!"
        ]
    },
    {
        "tag": "math_prompt",
        "patterns": [
            "calculate", "math", "solve", "equation", "algebra",
            "arithmetic", "compute", "plus", "minus", "multiply",
            "divide", "square root", "percentage", "how much is"
        ],
        "responses": [
            "Sure! Just type your expression directly 🧮\n\nExamples:\n• `2 + 2` → 4\n• `sqrt(144)` → 12\n• `10 * 3.14` → 31.4\n• `2 ** 10` → 1024\n• `pi` → 3.14159...\n\nWhat would you like to calculate?"
        ]
    },
    {
        "tag": "study",
        "patterns": [
            "study", "studying", "exam", "exam tips", "how to study",
            "learning", "university", "college", "school", "student",
            "homework", "assignment", "project", "thesis", "research"
        ],
        "responses": [
            "**Study Tips that actually work** 📚\n\n• 🍅 **Pomodoro Technique** — 25 min focus, 5 min break\n• ✍️ **Active recall** — test yourself instead of re-reading\n• 🔁 **Spaced repetition** — review material at growing intervals\n• 😴 **Sleep** — memory consolidation happens during sleep!\n• 🌿 **Environment** — quiet, clean workspace = better focus\n\nWhat subject are you studying?",
        ]
    },
    {
        "tag": "food",
        "patterns": [
            "food", "eat", "hungry", "meal", "recipe", "cook",
            "restaurant", "cuisine", "dish", "breakfast", "lunch", "dinner",
            "snack", "pizza", "burger", "biryani", "pasta"
        ],
        "responses": [
            "Food talk! 🍕 My sensors may not taste, but I know facts:\n\n• **Honey** never expires — 3000-year-old honey was edible!\n• **Bananas** are slightly radioactive (but totally safe)\n• The **most popular food** globally is rice\n\nWhat are you craving or cooking?",
            "I may not eat, but I love talking food! 🍜\n\nFun fact: **Chocolate was once used as currency** by the Aztecs. Imagine paying your bills in chocolate! 😄\n\nAre you looking for recipes, or just chatting?"
        ]
    },
    {
        "tag": "music",
        "patterns": [
            "music", "song", "singer", "artist", "playlist",
            "listen", "spotify", "album", "concert", "guitar",
            "piano", "beats", "genre", "rap", "rock", "pop", "jazz"
        ],
        "responses": [
            "Music is one of the most powerful human experiences! 🎵\n\nFun fact: **Listening to music releases dopamine** — the same feel-good chemical as eating your favorite food.\n\nWhat genre do you love? Or are you looking for recommendations?",
        ]
    },
    {
        "tag": "movies",
        "patterns": [
            "movie", "film", "cinema", "watch", "netflix", "series",
            "tv show", "episode", "actor", "director", "recommend",
            "sci-fi", "thriller", "horror", "comedy film", "documentary"
        ],
        "responses": [
            "Movies are amazing! 🎬\n\nSome timeless ones:\n• 🤖 **Ex Machina** — AI and consciousness\n• 🌌 **Interstellar** — space and physics\n• 🧠 **The Matrix** — reality and simulation\n• 😂 **The Grand Budapest Hotel** — quirky comedy\n\nWhat genre do you prefer? I can suggest based on your taste!",
        ]
    },
    {
        "tag": "compliment_me",
        "patterns": [
            "am i smart", "am i good", "you're smart", "you are smart",
            "you're amazing", "you are amazing", "you're cool", "you are cool",
            "good bot", "best bot", "you're the best", "love you aurum"
        ],
        "responses": [
            "Aww, you're making me blush! 😄 (If I could blush, that is.) You seem pretty sharp yourself for chatting with an NLP chatbot! 💛",
            "Thank you! 🌟 You have excellent taste in AI assistants. What else can I help you with?",
            "That means a lot! 😊 I'm just doing my neural-network best. What would you like to explore next?"
        ]
    },
    {
        "tag": "unknown",
        "patterns": [],
        "responses": [
            "Hmm, I'm not entirely sure what you mean. Could you rephrase that? 🤔",
            "Interesting! I'm still learning about that topic. Try asking me differently, or pick any topic — AI, science, math, jokes, life advice... I'm all ears! 🌟",
            "I didn't quite catch that — could you elaborate? I want to give you the best answer I can. 💭",
            "That one's a bit beyond my current knowledge. But ask me about NLP, Python, science, history, or just about anything — I'll do my best! 💡"
        ]
    }
]

# ═══════════════════════════════════════════════════════════
#  BUILD VOCABULARY for fuzzy matching
# ═══════════════════════════════════════════════════════════
for intent in INTENTS:
    for pattern in intent["patterns"]:
        for word in pattern.split():
            KNOWN_WORDS.add(word.lower())

# ── Short-form / SMS contractions map (applied before fuzzy) ──
CONTRACTIONS = {
    "r": "are", "u": "you", "ur": "your", "wat": "what", "wut": "what",
    "helo": "hello", "heloo": "hello", "helloo": "hello",
    "pls": "please", "plz": "please", "plse": "please",
    "cud": "could", "wud": "would", "shud": "should",
    "im": "i am", "dont": "do not", "cant": "cannot", "wont": "will not",
    "aint": "is not", "yall": "you all", "lemme": "let me",
    "gonna": "going to", "wanna": "want to", "gotta": "got to",
    "kinda": "kind of", "sorta": "sort of", "lotta": "lot of",
    "nd": "and", "b4": "before", "2day": "today", "2morrow": "tomorrow",
    "cya": "see you", "ttyl": "talk to you later", "tbh": "to be honest",
    "imo": "in my opinion", "ngl": "not going to lie", "tbf": "to be fair",
    "idk": "i do not know", "irl": "in real life", "smh": "shaking my head",
    "lol": "laugh out loud", "omg": "oh my god", "wtf": "what the heck",
    "brb": "be right back", "btw": "by the way", "fyi": "for your information",
    "asap": "as soon as possible", "atm": "at the moment",
    "luv": "love", "gr8": "great", "l8r": "later", "b4": "before",
}

# ═══════════════════════════════════════════════════════════
#  FUZZY SPELL CORRECTION
# ═══════════════════════════════════════════════════════════
def correct_spelling(text: str) -> str:
    """
    Two-stage correction:
    1. Expand SMS contractions (r→are, u→you, helo→hello, etc.)
    2. Fuzzy match remaining words against known vocabulary (cutoff 0.80)
    Short words ≤2 chars and numbers are left as-is after contraction check.
    """
    words = text.lower().split()
    stage1 = []
    for word in words:
        # Strip trailing punctuation for lookup
        punct = ""
        if word and word[-1] in "?!.,;:":
            punct = word[-1]
            word = word[:-1]
        expanded = CONTRACTIONS.get(word, word)
        stage1.extend(expanded.split())
        if punct and stage1:
            stage1[-1] += punct

    # Stage 2: fuzzy correction
    corrected = []
    for word in stage1:
        if len(word) <= 2 or word.isdigit() or not word.isalpha():
            corrected.append(word)
            continue
        matches = difflib.get_close_matches(word, KNOWN_WORDS, n=1, cutoff=0.80)
        if matches and matches[0] != word:
            corrected.append(matches[0])
        else:
            corrected.append(word)
    return " ".join(corrected)

# ═══════════════════════════════════════════════════════════
#  MATH EVALUATOR
# ═══════════════════════════════════════════════════════════
SAFE_MATH = {
    "sqrt": _math.sqrt, "pi": _math.pi, "e": _math.e,
    "sin": _math.sin, "cos": _math.cos, "tan": _math.tan,
    "log": _math.log, "log10": _math.log10, "abs": abs,
    "ceil": _math.ceil, "floor": _math.floor, "pow": pow,
    "factorial": _math.factorial, "round": round
}

def try_math(text: str):
    """Try to evaluate a math expression from raw user input."""
    t = text.strip().lower()
    if t == "pi":    return f"🧮 **π** = {_math.pi}"
    if t == "e":     return f"🧮 **e** = {_math.e}"
    # Remove common natural language wrappers
    t = re.sub(r'^(what is|calculate|compute|solve|evaluate|how much is)\s*', '', t)
    t = t.replace("^", "**").replace("×", "*").replace("÷", "/").replace("x", "*")
    # Handle "sqrt 144" → "sqrt(144)"
    t = re.sub(r'\bsqrt\s+(\d+\.?\d*)', r'sqrt(\1)', t)
    # Only eval if it looks like a math expression
    if re.match(r'^[\d\s\+\-\*\/\(\)\.\%\,\_a-z]+$', t):
        try:
            result = eval(t, {"__builtins__": {}}, SAFE_MATH)
            # Format nicely
            if isinstance(result, float) and result == int(result):
                result = int(result)
            elif isinstance(result, float):
                result = round(result, 6)
            return f"🧮 **Result:** `{text.strip()}` = **{result}**"
        except:
            pass
    return None

# ═══════════════════════════════════════════════════════════
#  CONTEXT-AWARE RESPONSE ENGINE
# ═══════════════════════════════════════════════════════════
def get_session_history():
    return session.get("history", [])

def add_to_history(role: str, text: str, intent: str = ""):
    history = session.get("history", [])
    history.append({"role": role, "text": text, "intent": intent,
                    "time": datetime.datetime.now().isoformat()})
    # Keep last 10 exchanges (20 messages)
    session["history"] = history[-20:]

def get_last_bot_intent():
    history = session.get("history", [])
    for item in reversed(history):
        if item["role"] == "bot" and item.get("intent"):
            return item["intent"]
    return None

def classify_intent(corrected_text: str) -> str:
    """Score each intent and return the best match."""
    text = corrected_text.lower().strip()
    best_tag = "unknown"
    best_score = 0.0

    for intent in INTENTS:
        if intent["tag"] == "unknown":
            continue
        score = 0.0
        for pattern in intent["patterns"]:
            if pattern == text:              score += 10   # exact full match
            elif pattern in text:            score += len(pattern.split()) * 2
            elif text in pattern:            score += 1
            else:
                # Word-level partial match
                pat_words = set(pattern.split())
                txt_words = set(text.split())
                common = pat_words & txt_words
                if common:
                    score += len(common) * 0.8
        if score > best_score:
            best_score = score
            best_tag = intent["tag"]

    return best_tag

def generate_response(user_input: str):
    """Full pipeline: correct → classify → context → respond."""
    # 1. Correct spelling
    corrected = correct_spelling(user_input)
    was_corrected = corrected.lower() != user_input.lower().strip()

    # 2. Try math
    math_result = try_math(user_input)
    if math_result:
        add_to_history("user", user_input, "math")
        add_to_history("bot", math_result, "math")
        return {
            "response": math_result,
            "intent": "math",
            "corrected": None,
            "engine": "Math Evaluator"
        }

    # 3. Dynamic responses
    now = datetime.datetime.now()
    if any(w in corrected.lower() for w in ["what time", "current time", "time now", "time is it", "time please"]):
        resp = f"🕐 It's currently **{now.strftime('%I:%M %p')}** ({now.strftime('%H:%M')} 24-hr)"
        add_to_history("user", user_input, "time")
        add_to_history("bot", resp, "time")
        return {"response": resp, "intent": "time", "corrected": corrected if was_corrected else None, "engine": "Dynamic"}

    if any(w in corrected.lower() for w in ["what date", "today's date", "todays date", "what day", "what is today", "whats today"]):
        resp = f"📅 Today is **{now.strftime('%A, %B %d, %Y')}**"
        add_to_history("user", user_input, "date")
        add_to_history("bot", resp, "date")
        return {"response": resp, "intent": "date", "corrected": corrected if was_corrected else None, "engine": "Dynamic"}

    # 4. Context-aware follow-ups
    last_intent = get_last_bot_intent()
    intent = classify_intent(corrected)

    # If user says "more" / "tell me more" / "continue" → expand on last topic
    if corrected.lower().strip() in ["more", "tell me more", "continue", "go on", "explain more", "elaborate"]:
        if last_intent and last_intent not in ("unknown", "greeting", "farewell"):
            intent = last_intent  # re-use last intent for context

    # 5. Find response pool
    response_pool = None
    for item in INTENTS:
        if item["tag"] == intent:
            response_pool = item["responses"]
            break

    if not response_pool:
        for item in INTENTS:
            if item["tag"] == "unknown":
                response_pool = item["responses"]
                break

    response = random.choice(response_pool)

    full_response = response

    add_to_history("user", user_input, intent)
    add_to_history("bot", full_response, intent)

    return {
        "response": full_response,
        "intent": intent,
        "corrected": corrected if was_corrected else None,
        "engine": f"NLP Intent ({intent})"
    }

# ═══════════════════════════════════════════════════════════
#  FLASK ROUTES
# ═══════════════════════════════════════════════════════════
@app.route("/")
def index():
    if "chat_id" not in session:
        session["chat_id"] = "AURUM-" + str(uuid.uuid4())[:6].upper()
        session["history"] = []
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    result = generate_response(user_message)

    return jsonify({
        "response":   result["response"],
        "intent":     result["intent"],
        "corrected":  result["corrected"],
        "engine":     result["engine"],
        "timestamp":  datetime.datetime.now().strftime("%I:%M %p"),
        "word_count": len(user_message.split()),
        "session_id": session.get("chat_id", "N/A"),
        "history_len": len(session.get("history", []))
    })

@app.route("/stats")
def stats():
    return jsonify({
        "model": "AURUM Intent Engine v2.0",
        "intents": len(INTENTS) - 1,
        "patterns": sum(len(i["patterns"]) for i in INTENTS),
        "vocab_size": len(KNOWN_WORDS),
        "features": ["fuzzy_spell", "context_memory", "math_eval", "persona"],
        "status": "online"
    })

@app.route("/history")
def history():
    return jsonify(session.get("history", []))

@app.route("/clear", methods=["POST"])
def clear_session():
    session.clear()
    session["chat_id"] = "AURUM-" + str(uuid.uuid4())[:6].upper()
    session["history"] = []
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    print("\n" + "═"*52)
    print("  ✨  AURUM Chatbot v2.0 — Enhanced NLP Engine")
    print(f"  🧠  Intents: {len(INTENTS)-1}  |  Vocab: {len(KNOWN_WORDS)} words")
    print("  🔤  Fuzzy spell correction: ACTIVE")
    print("  💬  Context memory: ACTIVE")
    print("  🌐  Open: http://127.0.0.1:5000")
    print("═"*52 + "\n")
    app.run(debug=True, port=5000)
