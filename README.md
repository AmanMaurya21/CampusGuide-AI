# 🎓 CampusGuide AI

An AI-powered university information assistant built using Retrieval-Augmented Generation (RAG). CampusGuide AI helps students retrieve information from university documents while also supporting general knowledge questions, learning assistance, programming help and everyday conversations.

## ✨ Features

- **Document-based Q&A:** Answers university-related questions using uploaded documents.
- **Retrieval-Augmented Generation (RAG):** Retrieves relevant information before generating answers.
- **Semantic Search:** Finds relevant document content based on meaning rather than just keywords.
- **General AI Conversations:** Handles general knowledge, programming, learning and everyday questions.
- **Conversation Context:** Supports contextual follow-up questions.
- **Source Transparency:** Displays source documents used to generate answers.
- **Interactive Chat Interface:** Built with Streamlit.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Web-based chat interface |
| Groq API | AI response generation |
| FAISS | Vector similarity search |
| Sentence Transformers | Text embeddings |
| PyPDF | PDF document extraction |
| Python-dotenv | Environment variable management |

## 🏗️ System Architecture

1. User submits a question through the Streamlit interface.
2. Query routing determines whether the question is campus-related or general.
3. Campus-related questions are processed through the RAG pipeline.
4. Relevant document chunks are retrieved using semantic search and FAISS.
5. Retrieved context is sent to the Groq LLM.
6. The LLM generates a context-based answer.
7. The answer and relevant source documents are displayed to the user.

General questions are handled directly by the LLM without document retrieval.

## 📂 Project Structure

```text
CampusGuide AI/
│
├── data/
│   └── documents/
│
├── src/
│   ├── document_processor.py
│   ├── rag_engine.py
│   ├── test_retrieval.py
│   └── vector_store.py
│
├── vector_store/
│   ├── campusguide.index
│   └── metadata.pkl
│
├── app.py
├── requirements.txt
├── .env
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/CampusGuide-AI.git
cd CampusGuide-AI
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows:**

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure API Key

Create a `.env` file in the project root directory:

```env
GROQ_API_KEY=your_groq_api_key
```

Replace the placeholder with your actual Groq API key.

### 6. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## 🧠 How RAG Works

Retrieval-Augmented Generation combines document retrieval with language model generation.

- **Document Processing:** Extracts text from PDF and TXT files.
- **Chunking:** Splits documents into smaller text segments.
- **Embedding Generation:** Converts text segments into numerical vectors using Sentence Transformers.
- **Vector Storage:** Stores embeddings in FAISS.
- **Retrieval:** Searches for relevant chunks based on the user's query.
- **Generation:** Uses the retrieved context to generate a relevant answer through the Groq API.

## 🎯 Project Objective

The objective of CampusGuide AI is to provide students with a convenient AI-powered assistant capable of answering university-specific questions using available documents while also supporting general conversational and educational queries.

## ⚠️ Limitations

- Answers to university-specific questions depend on the documents available in the system.
- Missing or outdated documents may affect answer accuracy.
- General AI responses may occasionally contain inaccurate information.
- The system requires an internet connection for Groq API inference.

## 👨‍💻 Developed As

An academic project demonstrating Retrieval-Augmented Generation, semantic search, vector databases, large language model integration and AI chatbot development.