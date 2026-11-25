
import streamlit as st
from src.rag_engine import answer_question

st.set_page_config(
    page_title="CampusGuide AI",
    page_icon="🎓",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 7rem;
    max-width: 1000px;
}

[data-testid="stSidebar"] {
    border-right: 1px solid rgba(128,128,128,0.2);
}

.hero {
    text-align: center;
    padding: 35px 20px 20px 20px;
}

.hero-icon {
    font-size: 55px;
    margin-bottom: 10px;
}

.hero-title {
    font-size: 38px;
    font-weight: 700;
    margin-bottom: 8px;
}

.hero-subtitle {
    font-size: 17px;
    opacity: 0.7;
}

.prompt-card {
    border: 1px solid rgba(128,128,128,0.25);
    padding: 18px;
    border-radius: 14px;
    margin-bottom: 10px;
}

div[data-testid="stChatMessage"] {
    border-radius: 14px;
    padding: 15px;
}

.stChatInput {
    border-radius: 15px;
}
/* Chat input font */
.stChatInput textarea {
    font-size: 18px !important;
}

/* Chat message text */
.stChatMessage p {
    font-size: 18px !important;
    line-height: 1.7 !important;
}

/* Chat input placeholder */
.stChatInput textarea::placeholder {
    font-size: 18px !important;
}

/* Sidebar readability */
[data-testid="stSidebar"] p {
    font-size: 16px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 🎓 CampusGuide AI")
    st.caption("Your university AI assistant")

    st.divider()

    st.markdown("### About")
    st.write(
        "CampusGuide AI helps students find campus information "
        "and answers general questions using AI."
    )

    st.divider()

    st.markdown("### Capabilities")
    st.markdown("""
    - 📚 University information
    - 📝 Exams & attendance
    - 🏛️ Student services
    - 💬 General conversations
    - 💡 Learning assistance
    """)

    st.divider()

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("Powered by Groq + FAISS + Streamlit")

# ---------------- CHAT HISTORY ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- WELCOME SCREEN ----------------
if not st.session_state.messages:

    st.markdown("""
    <div class="hero">
        <div class="hero-icon">🎓</div>
        <div class="hero-title">CampusGuide AI</div>
        <div class="hero-subtitle">
            Your intelligent university assistant.<br>
            Ask campus questions or explore anything.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📚 Campus information")
        st.markdown(
            '<div class="prompt-card">'
            'Find information about attendance, exams, services and more.'
            '</div>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown("#### 💡 Learn something")
        st.markdown(
            '<div class="prompt-card">'
            'Ask questions about programming, technology or other topics.'
            '</div>',
            unsafe_allow_html=True
        )

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📋 What are the attendance rules?", use_container_width=True):
            st.session_state.messages.append(
                {"role": "user", "content": "What are the attendance rules?"}
            )
            st.session_state.pending_question = "What are the attendance rules?"
            st.rerun()

        if st.button("🏛️ Tell me about student services", use_container_width=True):
            st.session_state.messages.append(
                {"role": "user", "content": "Tell me about student services"}
            )
            st.session_state.pending_question = "Tell me about student services"
            st.rerun()

    with col2:
        if st.button("💻 Explain machine learning", use_container_width=True):
            st.session_state.messages.append(
                {"role": "user", "content": "Explain machine learning"}
            )
            st.session_state.pending_question = "Explain machine learning"
            st.rerun()

        if st.button("📝 How can I prepare for exams?", use_container_width=True):
            st.session_state.messages.append(
                {"role": "user", "content": "How can I prepare for exams?"}
            )
            st.session_state.pending_question = "How can I prepare for exams?"
            st.rerun()

# ---------------- DISPLAY MESSAGES ----------------
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant" and message.get("sources"):
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.markdown(f"- {source}")

# ---------------- QUESTION PROCESSING ----------------
question = st.chat_input("Ask CampusGuide anything...")

pending_question = st.session_state.pop("pending_question", None)

if question or pending_question:

    current_question = question if question else pending_question

    # Immediately display and store the user message
    st.session_state.messages.append(
        {"role": "user", "content": current_question}
    )

    with st.chat_message("user"):
        st.markdown(current_question)

    # Generate assistant response
    with st.chat_message("assistant"):

        with st.spinner("CampusGuide is thinking..."):

            try:
                history = st.session_state.messages[:-1]

                result = answer_question(
                    current_question,
                    history=history
                )

                answer = result["answer"]
                sources = result["sources"]

            except Exception as e:
                answer = f"An error occurred: {e}"
                sources = []

        st.markdown(answer)

        if sources:
            with st.expander("📚 Sources"):
                for source in sources:
                    st.markdown(f"- {source}")

    # Save assistant response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources
        }
    )

    st.rerun()
