# # llm/gemini_client.py for 1 file at a time 

# from langchain_google_genai import ChatGoogleGenerativeAI
# from dotenv import load_dotenv
# from utils.logger import get_logger
# import os

# load_dotenv()
# logger = get_logger()

# SMALL_DOC_THRESHOLD = 5000


# def get_llm():
#     api_key = os.getenv("GEMINI_API_KEY")
#     if not api_key:
#         raise ValueError("GEMINI_API_KEY not found. Check your .env file.")

#     llm = ChatGoogleGenerativeAI(
#         model="gemma-3-4b-it",
#         google_api_key=api_key,
#         temperature=0.3,
#     )
#     return llm


# def ask_question(question: str, retrieved_chunks: list[dict], full_text: str = "") -> str:
#     logger.info(f"Generating answer for: '{question[:60]}...'")
#     llm = get_llm()

#     if full_text and len(full_text) < SMALL_DOC_THRESHOLD:
#         logger.debug("Small document — using full text as context")
#         context = f"FULL DOCUMENT CONTENT:\n{full_text}"
#     else:
#         logger.debug(f"Large document — using {len(retrieved_chunks)} retrieved chunks")
#         context = ""
#         for chunk in retrieved_chunks:
#             context += f"\n--- Source: {chunk['source']} ---\n"
#             context += chunk["text"] + "\n"

#     prompt = f"""You are DocuMind AI, a helpful assistant that answers questions 
# strictly based on the provided document context.

# RULES:
# - Only answer using information found in the context below
# - Search carefully through ALL the context before answering
# - If the answer is not in the context, say "I couldn't find that information in the uploaded document."
# - Cite the document name as source but NEVER mention chunk numbers or chunk indices
# - If there are multiple points or tips, list ALL of them completely — never truncate
# - Be thorough and complete — do not say "and more" or leave information out
# - Format your answer cleanly with bullet points where appropriate
# - If the context contains URLs or hyperlinks relevant to the answer, include them

# CONTEXT:
# {context}

# QUESTION:
# {question}

# ANSWER:"""

#     response = llm.invoke(prompt)
#     logger.info("Answer generated successfully")
#     return response.content

# llm/gemini_client.py for multiple files at a time. 

from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from utils.logger import get_logger
import time
import os

load_dotenv()
logger = get_logger()

SMALL_DOC_THRESHOLD = 5000

# ─────────────────────────────────────────
# GREETING DETECTION
# Handles small talk without hitting LLM or DB
# Returns a response string or None
# ─────────────────────────────────────────
GREETING_RESPONSES = {
    "greeting": "👋 Hello! I'm DocuMind AI. Upload a document and ask me anything about it!",
    "bye": "👋 Goodbye! Come back anytime you need help with your documents!",
    "thanks": "😊 You're welcome! Let me know if you have more questions about your documents.",
    "how_are_you": "😊 I'm doing great and ready to help! Ask me anything about your uploaded documents.",
    "positive": "😊 Glad to hear that! What else would you like to know from your documents?",
    "default": "👋 Hi there! I'm DocuMind AI. Ask me anything about your uploaded documents."
}


# def detect_greeting(text: str):
#     """
#     Checks if input is a greeting or small talk.
#     Returns a response string if it's a greeting,
#     or None if it's a real document question.

#     This runs BEFORE any DB or LLM call — instant response.
#     """
#     text_lower = text.lower().strip().rstrip('!').rstrip('.').rstrip('?')

#     # Goodbye
#     if text_lower in {
#         "bye", "goodbye", "see you", "see ya", "cya",
#         "later", "good night", "goodnight", "take care"
#     }:
#         return GREETING_RESPONSES["bye"]

#     # Thanks
#     if text_lower in {
#         "thanks", "thank you", "thankyou", "thank u",
#         "ty", "thx", "thnx", "thnks", "many thanks"
#     }:
#         return GREETING_RESPONSES["thanks"]

#     # How are you
#     if text_lower in {
#         "how are you", "how r u", "how are u",
#         "what's up", "wassup", "sup", "whats up",
#         "how do you do", "how's it going", "hows it going"
#     }:
#         return GREETING_RESPONSES["how_are_you"]

#     # Positive affirmations
#     if text_lower in {
#         "ok", "okay", "great", "cool", "nice", "awesome",
#         "perfect", "wonderful", "excellent", "brilliant",
#         "good", "fine", "alright", "sounds good", "got it",
#         "understood", "noted", "sure", "yep", "yes", "yup"
#     }:
#         return GREETING_RESPONSES["positive"]

#     # Greetings
#     if text_lower in {
#         "hi", "hello", "hey", "hii", "hiii", "helo",
#         "heya", "howdy", "greetings", "good morning",
#         "good afternoon", "good evening", "morning",
#         "afternoon", "evening"
#     }:
#         return GREETING_RESPONSES["greeting"]

#     return None  # not a greeting — proceed with RAG

def detect_greeting(text: str):
    """
    Detects greetings and small talk.
    Handles multi-word combos like 'okay thankyou', 'hi thanks' etc.
    """
    text_lower = text.lower().strip()
    # Remove punctuation
    for char in ['!', '.', '?', ',']:
        text_lower = text_lower.replace(char, '')
    text_lower = text_lower.strip()

    word_count = len(text_lower.split())

    # Long messages are real questions — skip
    if word_count > 10:
        return None

    # --- Exact single word/phrase sets ---
    bye_set = {
        "bye", "goodbye", "see you", "see ya", "cya",
        "later", "good night", "goodnight", "take care"
    }
    thanks_set = {
        "thanks", "thank you", "thankyou", "thank u",
        "ty", "thx", "thnx", "thnks", "many thanks",
        "thank you so much", "thanks a lot", "thanks a ton"
    }
    how_set = {
        "how are you", "how r u", "how are u",
        "whats up", "what's up", "wassup", "sup",
        "how do you do", "hows it going", "how's it going"
    }
    greeting_set = {
        "hi", "hello", "hey", "hii", "hiii", "helo",
        "heya", "howdy", "greetings", "good morning",
        "good afternoon", "good evening", "morning", "afternoon",
        # Add these help-related phrases
        "can you help me", "can you help", "help me",
        "are you there", "you there", "anyone there",
        "what can you do", "what do you do",
        "who are you", "what are you"
    }
    positive_set = {
        "ok", "okay", "great", "cool", "nice", "awesome",
        "perfect", "wonderful", "excellent", "brilliant",
        "good", "fine", "alright", "sounds good", "got it",
        "understood", "noted", "sure", "yep", "yes", "yup",
        "no", "nope", "interesting", "i see", "makes sense"
    }

    # --- Check exact match first ---
    if text_lower in bye_set:
        return GREETING_RESPONSES["bye"]
    if text_lower in thanks_set:
        return GREETING_RESPONSES["thanks"]
    if text_lower in how_set:
        return GREETING_RESPONSES["how_are_you"]
    if text_lower in greeting_set:
        return GREETING_RESPONSES["greeting"]
    if text_lower in positive_set:
        return GREETING_RESPONSES["positive"]

    # --- Check combinations like "okay thankyou", "hi thanks" ---
    # Split into words and check if ALL words are small talk words
    all_small_talk = bye_set | thanks_set | greeting_set | positive_set | {
        "okay", "ok", "sure", "yes", "no", "that", "is", "was",
        "very", "much", "so", "really", "quite", "too", "also",
        "and", "for", "the", "a", "it", "this", "your", "you",
        "me", "my", "i", "we", "our", "to", "of", "in", "on"
    }
    words = text_lower.split()

    # If all words in message belong to small talk vocabulary
    if all(w in all_small_talk for w in words):
        # Determine best response based on which category dominates
        if any(w in thanks_set or w in {"thanks", "thankyou", "ty", "thx"} for w in words):
            return GREETING_RESPONSES["thanks"]
        if any(w in bye_set for w in words):
            return GREETING_RESPONSES["bye"]
        if any(w in greeting_set for w in words):
            return GREETING_RESPONSES["greeting"]
        return GREETING_RESPONSES["positive"]

    # --- Starts with greeting ---
    for w in greeting_set:
        if text_lower.startswith(w + " ") or text_lower.startswith(w + ","):
            return GREETING_RESPONSES["greeting"]

    return None

# ─────────────────────────────────────────
# LLM SETUP
# ─────────────────────────────────────────
def get_llm(model: str = "gemini-2.5-flash"):
    """
    Initializes and returns a Gemini LLM instance.
    Default model is gemini-2.5-flash (fast, free tier).
    Falls back to gemma-3-4b-it if quota exhausted.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Check your .env file.")

    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0.3,
        # temperature 0.3 = mostly factual with slight natural variation
        # 0.0 = fully deterministic
        # 1.0 = creative but may hallucinate
    )


# ─────────────────────────────────────────
# CONTEXT BUILDER
# ─────────────────────────────────────────
def build_context(retrieved_chunks: list[dict], full_texts: dict = None) -> str:
    """
    Builds context string for the LLM prompt.

    Smart routing:
    - Small documents (< 5000 chars) → full text used directly
    - Large documents → only retrieved chunks used
    - Works for both single and multiple documents
    """
    if not full_texts:
        context = ""
        for chunk in retrieved_chunks:
            context += f"\n--- From: {chunk['source']} ---\n"
            context += chunk["text"] + "\n"
        return context

    # Group chunks by source document
    sources_in_chunks = set(c["source"] for c in retrieved_chunks)
    context = ""

    for source in sources_in_chunks:
        full_text = full_texts.get(source, "")

        if full_text and len(full_text) < SMALL_DOC_THRESHOLD:
            # Small doc — feed entire text so nothing is missed
            logger.debug(f"Using full text for small doc: {source}")
            context += f"\n=== FULL CONTENT OF: {source} ===\n"
            context += full_text + "\n"
        else:
            # Large doc — use only the relevant retrieved chunks
            logger.debug(f"Using retrieved chunks for large doc: {source}")
            source_chunks = [c for c in retrieved_chunks if c["source"] == source]
            context += f"\n=== EXCERPTS FROM: {source} ===\n"
            for chunk in source_chunks:
                context += chunk["text"] + "\n"

    return context


# ─────────────────────────────────────────
# MAIN ANSWER FUNCTION
# ─────────────────────────────────────────
def ask_question(
    question: str,
    retrieved_chunks: list[dict],
    full_text: str = "",       # Phase 1 compatibility
    full_texts: dict = None    # Phase 2 multi-doc
) -> str:
    """
    Main entry point for generating answers.

    Flow:
    1. Check for greeting → instant response, no LLM/DB call
    2. Build context from retrieved chunks
    3. Try gemini-2.5-flash first (fast)
    4. Auto-fallback to gemma-3-4b-it if quota exhausted
    5. Retry on 503 model overload errors

    Args:
        question: User's question string
        retrieved_chunks: Output from retrieve_relevant_chunks()
        full_text: Single doc full text (Phase 1 compatibility)
        full_texts: Dict of {source_name: full_text} (Phase 2)

    Returns:
        Answer string
    """

    # ── Step 1: Greeting check — no API call needed ──
    greeting_response = detect_greeting(question)
    if greeting_response:
        logger.info("Greeting detected — skipping RAG pipeline")
        return greeting_response

    logger.info(f"Generating answer for: '{question[:60]}...'")

    # ── Step 2: Handle Phase 1 backward compatibility ──
    if full_texts is None and full_text:
        source_name = (
            retrieved_chunks[0]["source"]
            if retrieved_chunks else "document"
        )
        full_texts = {source_name: full_text}

    # ── Step 3: Build context ──
    context = build_context(retrieved_chunks, full_texts)

    # ── Step 4: Build prompt ──
    unique_sources = set(c["source"] for c in retrieved_chunks)
    multi_doc = len(unique_sources) > 1

    prompt = f"""You are DocuMind AI, a helpful assistant that answers questions
strictly based on the provided document context below.

RULES:
- Only answer using information found in the context
- Search carefully through ALL context before answering
- NEVER put source citations inside the answer text
- NEVER write (filename) or (source) mid-sentence
- Write the full answer naturally first, then at the very end
  add a single line: Source: [document name(s)]
- List ALL relevant points completely — never truncate
- If a section has sub-points, include ALL of them
- Include URLs or hyperlinks exactly as they appear in context
- Format URLs as: text (url)
- If the answer is not found say exactly:
  "I couldn't find that information in the uploaded document(s)."
- Format your answer cleanly with bullet points where appropriate

{"NOTE: Answer may come from multiple documents. List all sources at the end." if multi_doc else ""}

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""

    # ── Step 5: Try models with auto-fallback ──
    # Try fast model first, fall back to slower free model
    models_to_try = ["gemma-3-4b-it", "gemini-2.5-flash"]

    for model_name in models_to_try:
        logger.info(f"Trying model: {model_name}")

        for attempt in range(2):  # 2 attempts per model
            try:
                llm = get_llm(model=model_name)
                response = llm.invoke(prompt)
                logger.info(f"✅ Answer generated using {model_name}")
                return response.content

            except Exception as e:
                err = str(e)

                # Rate limit — try next model
                if "429" in err or "RESOURCE_EXHAUSTED" in err:
                    logger.warning(
                        f"{model_name} quota exhausted — "
                        f"{'trying next model' if model_name != models_to_try[-1] else 'all models exhausted'}"
                    )
                    break  # move to next model

                # Model overloaded — retry once after 10s
                elif "503" in err or "UNAVAILABLE" in err:
                    if attempt == 0:
                        logger.warning(
                            f"{model_name} unavailable — "
                            f"retrying in 10s (attempt {attempt + 1}/2)"
                        )
                        time.sleep(10)
                        continue
                    else:
                        logger.warning(
                            f"{model_name} still unavailable — trying next model"
                        )
                        break  # try next model

                # SSL / network error — no point retrying
                elif "SSL" in err or "certificate" in err.lower():
                    logger.error(f"SSL error: {err}")
                    return "⚠️ Network SSL error. Please check your connection."

                # Unknown error
                else:
                    logger.error(f"Unexpected error with {model_name}: {err}")
                    break  # try next model

    # All models failed
    logger.error("All models failed to generate answer")
    return (
        "⚠️ Could not generate an answer right now. "
        "All models are either rate limited or unavailable. "
        "Please wait a minute and try again."
    )