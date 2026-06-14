import os
import gradio as gr
from dotenv import load_dotenv
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate

try:
    from langchain.chains import RetrievalQA
except Exception:
    from langchain_classic.chains import RetrievalQA


load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OpenAI API key not found. Please check your .env file.")

#Global state to hold the QA chain after loading a document. This allows the ask_question function to access the chain without needing to rebuild it for every question.
qa_chain = None

# Prompt Template
CUSTOM_PROMPT = PromptTemplate(
    template="""You are a helpful assistant answering questions based on the provided document context.

Instructions:
1. Use ONLY the information in the context below to answer the question.
2. If the context contains relevant information, provide a clear, accurate answer based on it.
3. If the context is partially relevant, answer with what you can infer from the available information.
4. Only if the context is completely irrelevant to the question, reply with:
"I can't find relevant content that answers your question. Please try rephrasing your question in a different way."

Context: {context}
Question: {question}

Answer:""",
    input_variables=["context", "question"]
)

# Trivial question validator
TRIVIAL_PATTERNS = [
    "what color", "what font", "page number", "how many pages",
    "what size", "what style", "bold", "italic", "underline",
    "margin", "spacing", "header", "footer", "date mentioned",
    "who wrote", "author name", "file name", "word count"
]

MIN_QUESTION_LENGTH = 10

#Function that checks if a question is trivial based on patterns and length.
def is_trivial_question(question: str) -> tuple[bool, str]:
    """Returns (is_trivial, reason_message)"""
    q_lower = question.lower().strip()

    if len(q_lower) < MIN_QUESTION_LENGTH:
        return True, f"⚠️ Question too short. Please ask something more detailed (min {MIN_QUESTION_LENGTH} chars)."

    for pattern in TRIVIAL_PATTERNS:
        if pattern in q_lower:
            return True, f'⚠️ "{pattern}" questions are too trivial. Please ask about the document\'s content, ideas, or arguments.'

    # Check for single-word or very simple questions
    word_count = len(q_lower.split())
    if word_count < 3:
        return True, "⚠️ Question too simple. Please ask a more substantive question about the document."

    return False, ""


# Build QA chain from a loaded .docx file 
def build_chain(docx_path: str):
    loader = Docx2txtLoader(docx_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    #chunk_size=1000, chunk_overlap=200 instead of 500 and 100 to reduce the number of chunks and improve context for the model.
    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=os.path.join("./chroma_docx_db", os.path.splitext(os.path.basename(docx_path))[0])
    )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        #k=5 insread of 3 to provide more context for the model to answer questions accurately.
        return_source_documents=True,
        chain_type_kwargs={"prompt": CUSTOM_PROMPT}
    )
    return chain, len(chunks)


# Gradio handler: called when user uploads a docx file
def upload_docx(file):
    global qa_chain

    if file is None:
        return "⚠️ No file uploaded.", []

    try:
        chain, n_chunks = build_chain(file.name)
        qa_chain = chain
        status = f"✅ Document loaded successfully — {n_chunks} chunks indexed."
    except Exception as e:
        status = f"❌ Error loading document: {e}"

    return status, []


# Gradio handler: called when user submits a question 
def ask_question(user_msg: str, history: list):
    if not user_msg.strip():
        return history

    if qa_chain is None:
        history.append({"role": "assistant", "content": "⚠️ Please upload a .docx file first."})
        return history

    # Validate question is non-trivial
    is_trivial, reason = is_trivial_question(user_msg)
    if is_trivial:
        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": reason})
        return history

    try:
        result = qa_chain.invoke({"query": user_msg})
        answer = result["result"]

        sources = result.get("source_documents", [])
        if sources:
            snippets = "\n\n---\n📚 Sources:\n"
            for i, doc in enumerate(sources, 1):
                snippet = doc.page_content[:120].replace("\n", " ")
                snippets += f"\n[{i}] ...{snippet}..."
            answer += snippets

    except Exception as e:
        answer = f"❌ Error: {e}"

    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": answer})
    return history


# Build the Gradio UI
with gr.Blocks(title="Chat with Your Document") as demo:
    gr.Markdown("## 📄 Chat with Your Word Document\nUpload a `.docx` file, then ask questions.")

    gr.Markdown(
        """### 💡 Question Guidelines
Ask substantive questions about the document's **content, ideas, arguments, or conclusions**.  
Avoid trivial questions about formatting, colors, fonts, page numbers, or basic metadata."""
    )

    with gr.Row():
        docx_input = gr.File(label="Upload .docx", file_types=[".docx"])
        status = gr.Textbox(label="Status", interactive=False)

    chatbot = gr.Chatbot(
        label="Conversation",
        height=450,
    )

    question_input = gr.Textbox(
        placeholder="Ask a substantive question about your document's content, ideas, or arguments…",
        label="Your question"
    )

    docx_input.change(
        fn=upload_docx,
        inputs=docx_input,
        outputs=[status, chatbot]
    )

    question_input.submit(
        fn=ask_question,
        inputs=[question_input, chatbot],
        outputs=chatbot
    ).then(
        fn=lambda: "",
        outputs=question_input
    )

    gr.Examples(
        examples=[
            ["What is this document about?"],
            ["What challenges are mentioned?"],
            ["Summarize this document."],
            ["Who is the intended audience for this text?"],
            ["What are the key takeaways or main points discussed?"]
        ],
        inputs=question_input
    )

if __name__ == "__main__":
    demo.launch()