
import os
from dotenv import load_dotenv
from groq import Groq

from src.vector_store import search_documents

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise RuntimeError("GROQ_API_KEY not found in .env file")

client = Groq(api_key=API_KEY)
MODEL_NAME = "openai/gpt-oss-20b"


def is_campus_related(question, history=None):
    """Identify university-related questions without misrouting general follow-ups."""

    campus_keywords = [
        "university", "campus", "college",
        "attendance", "exam", "examination",
        "semester", "timetable", "schedule",
        "library", "hostel", "student services",
        "student service", "fee", "fees", "scholarship",
        "faculty", "professor", "vc", "vice chancellor",
        "registrar", "admission", "placement",
        "placement cell", "id card", "certificate",
        "academic", "department", "course",
        "classroom", "wifi", "wi-fi", "helpdesk",
        "administration", "disciplinary", "policy",
        "result", "marks", "grade", "credit"
    ]

    question_lower = question.lower()

    # Explicit campus-related questions go directly to RAG
    if any(keyword in question_lower for keyword in campus_keywords):
        return True

    # Check only the most recent user question for campus context
    # instead of scanning the entire conversation.
    if history:
        previous_user_messages = [
            message["content"].lower()
            for message in history
            if message["role"] == "user"
        ]

        if previous_user_messages:
            last_user_question = previous_user_messages[-1]

            if any(keyword in last_user_question for keyword in campus_keywords):
                follow_up_phrases = [
                   "what about",
                   "how about",
                   "tell me more",
                   "what if",
                   "make it simpler",
                   "simplify",
                   "more details",
                ]

                if any(phrase in question_lower for phrase in follow_up_phrases):
                    return True

    return False


def rewrite_question(question, history):
    """Convert a follow-up into a standalone question."""

    if not history:
        return question

    conversation = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in history[-6:]
    )

    prompt = f"""
Rewrite the latest question so it can be understood independently.

Use the conversation to understand references and follow-up questions.
Preserve the student's actual intent.
Do not answer the question.
Return only the rewritten question.

Conversation:
{conversation}

Latest question:
{question}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
    )

    return response.choices[0].message.content.strip()


def answer_general_question(question, history=None):
    """Answer general questions and maintain conversational context."""

    messages = [
        {
            "role": "system",
            "content": (
                "You are CampusGuide AI, a friendly and helpful AI assistant. "
                "You can answer general knowledge questions, explain concepts, "
                "help with programming, learning, technology and everyday "
                "conversation. Be clear, natural and helpful. "
                "Do not claim to know university-specific information "
                "unless it is provided to you."
            )
        }
    ]

    if history:
        for message in history[-8:]:
            if message["role"] in ["user", "assistant"]:
                messages.append({
                    "role": message["role"],
                    "content": message["content"]
                })

    messages.append({
        "role": "user",
        "content": question
    })

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.5,
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": []
    }


def answer_campus_question(question):
    """Answer university questions using retrieved documents."""

    results = search_documents(question, top_k=3)

    if not results:
        return {
            "answer": (
                "I couldn't find relevant information in the "
                "available campus documents."
            ),
            "sources": []
        }

    context = "\n\n".join(
        f"Source: {result['source']}\n{result['content']}"
        for result in results
    )

    system_prompt = """
You are CampusGuide AI, a university information assistant.

Answer university-related questions using the provided campus document context.

Rules:
- Use the supplied context as your primary source.
- Do not invent university policies, dates, fees or facts.
- If the answer is not present in the context, clearly say that the
  available documents do not contain that information.
- You may explain the information in simple and natural language.
- Be helpful but avoid unnecessarily long answers.
"""

    user_prompt = f"""
Campus document context:

{context}

Student question:
{question}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    answer = response.choices[0].message.content

    sources = list(set(result["source"] for result in results))

    return {
        "answer": answer,
        "sources": sources
    }


def answer_question(question, history=None):
    """Route questions and use conversation history."""

    history = history or []

    # Handle simple greetings
    greetings = [
        "hi", "hello", "hey",
        "good morning", "good afternoon",
        "good evening"
    ]

    if question.lower().strip().rstrip("!.") in greetings:
        return {
            "answer": (
                "Hello! I'm CampusGuide AI 👋 "
                "How can I help you today?"
            ),
            "sources": []
        }

    # Handle chatbot capability questions
    capability_questions = [
        "what can you do",
        "what do you do",
        "what can you help me with",
        "what is your purpose",
        "how can you help me",
        "what you do for me"
    ]

    if question.lower().strip().rstrip("?.!") in capability_questions:
        return {
            "answer": (
                "I'm CampusGuide AI 🎓! I can help you with university "
                "information such as attendance, examinations, library "
                "services and student services using campus documents. "
                "I can also answer general questions, explain concepts, "
                "help with programming and have normal conversations."
            ),
            "sources": []
        }

    # Decide whether the question is campus-related
    campus_question = is_campus_related(question, history)

    if campus_question:

        # Rewrite follow-up questions when conversation history exists
        standalone_question = rewrite_question(question, history)

        return answer_campus_question(standalone_question)

    # Handle general conversation and knowledge questions
    return answer_general_question(question, history)


if __name__ == "__main__":
    question = input("\nAsk CampusGuide AI: ")

    result = answer_question(question)

    print("\nCampusGuide AI:")
    print(result["answer"])

    if result["sources"]:
        print("\nSources:")
        for source in result["sources"]:
            print("-", source)
