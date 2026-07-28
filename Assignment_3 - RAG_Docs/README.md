# 📄 Chat with Your Document — RAG-Powered QA System

A Gradio-based web application that lets users upload a `.docx` file and ask questions about its content using a **Retrieval-Augmented Generation (RAG)** pipeline powered by OpenAI's LLM and ChromaDB vector storage.

---

## ✨ Features

- **📤 Upload & Chat** — Drop any `.docx` file and start asking questions immediately.
- **🔍 Semantic Search** — Documents are split into chunks, embedded with OpenAI embeddings, and stored in ChromaDB for fast, context-aware retrieval.
- **🧠 Deep Question Understanding** — The RAG pipeline can analyze complex, abstract, and deep questions about the document's themes, arguments, and underlying meaning.
- **🛡️ Smart Question Filtering** — Automatically rejects trivial or formatting-related questions (e.g., "What color...", "What font...", "How many pages...") and guides users toward substantive inquiries.
- **🚫 Off-Topic Guardrails** — If a question is unrelated to the document's content, the system responds with a polite message instead of hallucinating an answer.
- **📚 Cited Sources** — Every answer includes snippets from the source document so you can verify the response.

---

## 🚀 Quick Start

### 1. Clone or Download the Project

```bash
git clone https://github.com/AriessGit/Final-Course-Assignments---ECOM-2026/tree/main/Assignment_3%20-%20RAG_Docs
cd Assignment_3 - RAG_Docs
```

### 2. Configure Your Environment Variables

1. Rename the provided file:
   ```bash
   mv example.env .env
   ```
2. Open `.env` in your favorite text editor and paste your **OpenAI API key**:
   ```env
   # Your secret API key:
   OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```

> ⚠️ **Never commit your `.env` file to version control.** It contains sensitive credentials. The `.env` file is already listed in `.gitignore` by default.

### 3. Run the Application

```bash
python RAG_APP.py
```

The app will launch locally (usually at `http://127.0.0.1:7860`). Open the URL in your browser to start chatting with your documents.

---

## 🖼️ Application in Action

### Deep & Meaningful Questions
The RAG system excels at understanding **deep, conceptual questions** about the document. It doesn't just extract keywords — it interprets themes, arguments, and the broader significance of the text.

<img width="1711" height="881" alt="Image" src="https://github.com/user-attachments/assets/a4bac8a6-401a-4727-9f6c-96900c8ac137" />

> *The user asks for the "deep meaning" of the text. The system synthesizes an insightful answer about supercars as symbols of human ingenuity, ambition, and the pursuit of excellence — drawing directly from the document's themes.*

### Summarization & Source Attribution
When you ask for a summary, the model provides a concise overview and lists the exact chunks it used as sources.

<img width="1411" height="767" alt="Image" src="https://github.com/user-attachments/assets/0f1c58e7-a800-4006-a9c5-80ab7a0e25dc" />

> *The system summarizes the document and cites the specific text chunks that informed the response, ensuring transparency and verifiability.*

### Smart Handling of Trivial & Off-Topic Questions
The application includes built-in guardrails to maintain quality and relevance:

<img width="1703" height="894" alt="Image" src="https://github.com/user-attachments/assets/1463f141-3268-4be4-83d5-ff5b5de0fc62" />

- **Trivial questions** (e.g., "what color was the first car", "what font is used") are detected by pattern matching and rejected with a helpful message guiding the user to ask about the document's *content, ideas, or arguments*.
- **Off-topic questions** (e.g., "How do the sun's rays affect trees?" when the document is about supercars) trigger a fallback response:  
  > *"I can't find relevant content that answers your question. Please try rephrasing your question in a different way."*

This ensures the assistant **only answers based on the uploaded text resources** and does not hallucinate or drift outside the document's scope.

---

## 🏗️ How It Works

| Step | Description |
|------|-------------|
| **1. Upload** | User uploads a `.docx` file via the Gradio interface. |
| **2. Load & Split** | `Docx2txtLoader` extracts text, and `RecursiveCharacterTextSplitter` breaks it into overlapping chunks (1000 chars, 200 overlap). |
| **3. Embed & Store** | Chunks are embedded using `OpenAIEmbeddings` and stored in a ChromaDB vector collection. |
| **4. Retrieve** | When a question is asked, the retriever fetches the top-5 most relevant chunks from the vector store. |
| **5. Generate** | A `gpt-4o-mini` LLM receives the retrieved context + the custom prompt and generates a grounded answer. |
| **6. Validate** | Questions are pre-screened for triviality (length, keyword patterns) before being sent to the pipeline. |

---

## 📝 Prompt Engineering

The system uses a carefully crafted prompt template to enforce faithfulness to the source material:

```
1. Use ONLY the information in the context below to answer the question.
2. If the context contains relevant information, provide a clear, accurate answer.
3. If the context is partially relevant, answer with what you can infer.
4. Only if the context is completely irrelevant, reply with:
   "I can't find relevant content that answers your question. 
    Please try rephrasing your question in a different way."
```

---

## ⚙️ Configuration Notes

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `chunk_size` | 1000 | Balances granularity with context richness. |
| `chunk_overlap` | 200 | Ensures continuity between chunks and avoids losing context at boundaries. |
| `retriever_k` | 5 | Retrieves more context chunks for better answer accuracy. |
| `model` | `gpt-4o-mini` | Fast, cost-effective, and capable for document QA tasks. |
| `temperature` | 0 | Minimizes hallucination; answers are deterministic and grounded. |

---

## 📁 Project Structure

```
.
├── RAG_APP.py          # Main Gradio application & RAG pipeline
├── example.env         # Template for environment variables (rename to .env)
├── requirements.txt    # Python dependencies
├── 1.jpg               # Screenshot: Summary with sources
├── 2.jpg               # Screenshot: Deep question handling
├── 3.jpg               # Screenshot: Trivial & off-topic rejection
└── chroma_docx_db/     # Auto-generated ChromaDB persistence directory
```

---

## 🛡️ Best Practices

- **Keep your API key secret.** Always use a `.env` file and never hardcode credentials.
- **Ask substantive questions.** The system is designed for content analysis, not document metadata queries.
- **Rephrase if stuck.** If the system can't find relevant content, try rewording your question or breaking it into smaller parts.

---

## 📄 License

This project is open-source. Feel free to modify and extend it for your own document-QA needs.

---

*Built with ❤️ using [Gradio](https://gradio.app), [LangChain](https://langchain.com), [OpenAI](https://openai.com), and [ChromaDB](https://trychroma.com).*
