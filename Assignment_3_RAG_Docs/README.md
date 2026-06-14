# 📄 Chat with Your Document — RAG-Powered QA System

A Gradio-based web application that lets users upload a `.docx` file and ask questions about its content using a Retrieval-Augmented Generation (RAG) pipeline powered by OpenAI's LLM and ChromaDB vector storage.

---

## 🚀 Features

- **Upload any `.docx` file** and instantly index its contents
- **Ask natural-language questions** about the document
- **Receive AI-generated answers** grounded in the document's actual text
- **View source snippets** — see exactly which chunks the answer came from
- **Trivial question filtering** — prevents low-effort formatting/metadata questions

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| UI Framework | [Gradio](https://gradio.app/) |
| Document Loading | `Docx2txtLoader` (LangChain Community) |
| Text Splitting | `RecursiveCharacterTextSplitter` |
| Vector Database | [ChromaDB](https://www.trychroma.com/) |
| Embeddings | `OpenAIEmbeddings` (text-embedding-ada-002) |
| LLM | `ChatOpenAI` (gpt-4o-mini) |
| Orchestration | [LangChain](https://www.langchain.com/) `RetrievalQA` chain |

---

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate the environment**
   - Windows (PowerShell):
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up your OpenAI API key** ⬇️ *(see detailed instructions below)*

6. **Run the app**
   ```bash
   python app.py
   ```

   Then open the local URL shown in the terminal (usually `http://127.0.0.1:7860`).

---

## 🔑 Environment Variables Setup

This application requires an **OpenAI API key** to function. The key is loaded from a `.env` file in the project root.

### Step-by-step:

1. **Get your OpenAI API key**
   - Go to [platform.openai.com](https://platform.openai.com/)
   - Sign in or create an account
   - Navigate to **API Keys** in the left sidebar
   - Click **"Create new secret key"**
   - Copy the key (it starts with `sk-`)

2. **Create the `.env` file**

   In the project root folder, create a file named `.env` (no extension):

   ```bash
   # Windows (PowerShell)
   New-Item .env -type file

   # macOS/Linux
   touch .env
   ```

3. **Add your API key**

   Open `.env` in any text editor and paste:
   ```env
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

   Replace `sk-your-actual-key-here` with your real key.

4. **Verify it works**

   When you run `python app.py`, you should see the app start without any API key errors. If you see:
   ```
   ValueError: OpenAI API key not found. Please check your .env file.
   ```
   Double-check that:
   - The file is named exactly `.env` (with the dot)
   - It's in the same folder as `app.py`
   - The key is spelled correctly as `OPENAI_API_KEY`
   - There are no extra spaces or quotes around the key

> ⚠️ **Security Note:** Never commit your `.env` file to GitHub! It contains your private API key. The `.gitignore` file in this repo automatically excludes it.

---

## 🎯 Usage

1. Upload a `.docx` file using the file picker
2. Wait for the status to show `✅ Document loaded successfully — X chunks indexed.`
3. Type a substantive question about the document's **content, ideas, or arguments**
4. The AI will answer based solely on the document, with source snippets attached

---

## ⚠️ Challenges & Lessons Learned

During the development of this project, I faced several key technical challenges that shaped the final implementation:

### 1. Document Chunking Strategy
One of the first hurdles was loading the Word document correctly, splitting its content into appropriately sized chunks, and maintaining overlap between chunks to improve retrieval quality and answer accuracy. Finding the right balance between `chunk_size` and `chunk_overlap` was critical — too small and context gets fragmented; too large and retrieval becomes imprecise.

### 2. Building the Full RAG Pipeline
I needed to define a complete RAG workflow: generating embeddings with OpenAI, storing them in ChromaDB, retrieving relevant text chunks based on semantic similarity, and feeding those chunks into the LLM for answer generation. Each step had to work seamlessly with the next.

### 3. Preventing Hallucinations
A major challenge was ensuring answers were based **only** on the document content, without the model inventing information that did not appear in the text. My first prompt was too strict — it told the LLM to refuse whenever it couldn't find a direct answer. The result? Even simple questions like *"What is this document about?"* were rejected because the retrieved chunks didn't contain that exact phrasing.

The fix was rewriting the prompt to allow **inference from partial matches** — instructing the LLM to synthesize answers from relevant context rather than demanding exact keyword alignment. I also increased the retriever's `k` value from 3 to 5 chunks and bumped chunk size from 500 to 1000 tokens to preserve more context per piece. These changes transformed a broken system into a functional one.

### 4. Adding Transparency with Source Chunks
To improve reliability and trust, I added a display of the retrieved source chunks next to each answer. This lets users verify that the response is actually grounded in the document and see exactly which passages the model used.

### 5. User Experience & Interface Design
I needed to improve the app's UX, including dynamic Word file upload, working with the Gradio interface, and presenting results in a clear, user-friendly way. This involved designing intuitive layouts, adding helpful placeholder text, and providing example questions to guide users.

### 6. Aligning with Assignment Requirements
Part of the work involved aligning the project with grading criteria: choosing relevant and non-trivial questions, printing the retrieved context alongside answers, and improving the code structure so it would be cleaner, easier to run, and easier to maintain. I added a trivial-question validator to enforce substantive queries and restructured the code into clear, well-commented sections.

---

## 📁 Project Structure

```
.
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── .env.example        # Template for environment variables
├── .env                # Your actual API key (NOT tracked by git)
├── .gitignore          # Files excluded from version control
├── chroma_docx_db/     # Auto-generated vector database storage
└── README.md           # This file
```

---

## 📝 Notes

- Requires **Python 3.10+** (uses `tuple[bool, str]` type hints)
- The `chroma_docx_db/` folder is auto-created and stores embeddings per document
- Old databases are automatically cleared on re-upload of the same file

---

## 📄 License

MIT License — feel free to use and modify.
