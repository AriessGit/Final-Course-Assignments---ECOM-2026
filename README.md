# Final Course Assignments — ECOM 2026

Four projects, one course: a semester-long build-up from "what is an embedding?" to a full-stack AI agent that books your table and texts you a confirmation. Each assignment layers a new piece of the modern LLM-app stack — embeddings, vector search, RAG, and finally agentic tool use with real-world integrations (email, SMS, calendar).

---

## 1. Foundations — NLP & Agent Concepts Q&A

The theory behind everything else in this repo. A 12-question deep dive covering tokenization, stemming vs. lemmatization, TF-IDF, embeddings, cosine similarity, why SQL can't do semantic search, the anatomy of a RAG pipeline, Docker images vs. containers, and what actually separates a chatbot from an AI agent — plus a look at MCP and Agent Skills, the plumbing that lets AI assistants plug into real tools. Read this one first; it's the cheat sheet for assignments 2–4.

## 2. Vector DB App — Semantic Search for Stocks 📈

A ChromaDB + Sentence Transformers app that searches stocks by *meaning*, not keywords. Ask for "long-term value investing and strong business moats" and it surfaces Apple and Berkshire Hathaway — even though neither description contains those words. That's the payoff of embeddings over string matching, demonstrated in under 100 lines of Python.

## 3. Chat with Your Document — RAG-Powered QA System 📄

Upload a `.docx`, ask it anything. A Gradio app wraps a full RAG pipeline (LangChain + OpenAI + ChromaDB) that chunks your document, retrieves the most relevant pieces, and answers with citations — while politely refusing to hallucinate on off-topic or trivial questions ("what font is this?"). The README shows it reasoning about a document's *deeper meaning*, not just parroting text back.

## 4. Tasty Sea — Seafood Restaurant Chatbot 🌊🦐

The capstone: a conversational agent that actually *does things*. Built on LangChain + GPT-4o-mini with a Gradio front end and SQLite backend, it handles menu questions, recommendations, and — the fun part — full reservation booking and cancellation, wired through n8n to fire off Google Calendar events, SMTP emails, and Twilio SMS automatically. There's a full demo video in the repo showing the chain reaction: one chat message → calendar invite → email → text message.

---

### Stack across the four projects
Python · LangChain · OpenAI (GPT-4o-mini) · ChromaDB · Sentence Transformers · Gradio · SQLite · n8n · Docker · Twilio

Start with #1 for the concepts, then work through #2 → #4 to watch the same ideas turn into shipped, working apps.
