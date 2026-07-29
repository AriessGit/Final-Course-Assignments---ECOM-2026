1.

Q:	What is tokenization? Give an example — show how the sentence "I'm learning NLP in 2025!" would be tokenized.

A:	Tokenization is just chopping text into bite sized pieces called "tokens", usually words or punctuation. It's the first step because computers can't read sentences.  they need a list of individual items to work with.

For "I'm learning NLP in 2025!", its will  give you: 

["I", "'m", "learning", "NLP", "in", "2025", "!"]



2. 

Q:	What is the difference between stemming and lemmatization? Apply both to the words "running" and "better" and explain which preserves more linguistic meaning.	

A: 	Both try to reduce words to their root form, but they work differently.

Stemming is like using scissors, it just hacks off the ending.

Fast but also messy.

"running" --> "run"

"better" --> "better" (stemming often fails on irregular words)

Lemmatization is like using a dictionary, it looks up the actual base word.

"running" --> "run"

"better" --> "good"

Lemmatization preserves more meaning because it understands that "better" comes from "good," not just some letters tacked on.



3.

Q: 	What does TF-IDF stand for? Explain in plain language why the word "the" scores almost zero in TF-IDF, while the word "photosynthesis" would score high.



A: 	TF-IDF stands for Term Frequency – Inverse Document Frequency. 

It measures how important a word is to a specific document compared to all documents.

"the" scores near zero because it appears in almost every document ever. it's useless for telling documents apart.

"photosynthesis" scores high because it shows up a lot in this document but rarely in others, so it's a strong signal that this document is about biology.

4.

Q:	What is a sentence embedding? How is it fundamentally different from one-hot encoding? Give one advantage embeddings have that one-hot vectors don't.

A:	A sentence embedding is a dense list of numbers that captures the meaning of a sentence. One hot encoding is a sparse list where each word gets its own 1 and everything else is 0.  It knows nothing about meaning.

The big advantage of embeddings: you can measure similarity. You can ask "How close is this sentence to that sentence?" With one hot vectors, every word is equally unrelated to every other word. 

"king" and "queen" are just as different as "king" and "pizza."



5.

Q:	Explain cosine similarity in plain language. If two document vectors point in almost the same direction, what does that tell us about the documents they represent?

A:	Cosine similarity ignores how long the arrows are and only cares about the angle between them. So the documents are talking about the same thing.

Bonus: Euclidean distance can be a poor choice because it cares about length. A 500-word essay and a 50 word summary about the same topic might be far apart in Euclidean space just because one vector is longer, even though they mean the same thing.



6.

Q:	Why can't a regular SQL query like WHERE description LIKE '%pizza%' find semantically similar documents? What does a vector index solve that SQL can't?



A:	WHERE description LIKE '%pizza%' is literally just string matching, it only finds documents containing the exact letters "pizza."

 It has zero understanding that "Italian food" or "pasta and risotto" are about the same topic.

A vector index stores the meaning of documents as embeddings.

So when searching for "pizza," it finds documents about pizza even if they never use that exact word, because their vectors point in a similar direction.







7.

Q:	What problem does RAG solve that a plain LLM (without RAG) cannot? Give a concrete example of when you would choose RAG over just prompting the LLM directly.

A:	LLM only knows what it was trained on. It has a knowledge cutoff, its can't access your private files and it might just make things up (hallucinate).

Example: You want to ask questions about your company's internal Q4 sales report from last week. The LLM never seen it. RAG lets you load that report, find the relevant chunks, and feed them to the LLM so it answers based on your actual data.



8.

Q:	Describe the 3 main steps of a RAG pipeline in the correct order. Be clear about what happens at ingestion time (when you load documents) vs query time (when a user asks a question).

A:	At ingestion time -happens once, when you set things up:

Chunk - break your documents into smaller pieces.

Embed - turn each chunk into a vector (embedding).

Store - save those vectors in a vector database.

At query time -happens every time someone asks a question:

Embed query - turn the user's question into a vector.

Retrieve - find the most similar chunks from your database.

Generate - feed those chunks + the question to the LLM and get an answer grounded in your documents.





9.

Q:	What is the difference between a Docker image and a Docker container? Use an analogy to explain.

A:	Assume that Docker image as a recipe for a cake,  it's the instructions and ingredients, sitting there, ready to be used. A Docker container is the actual cake you baked from that recipe. 









10.

Q:	What is the difference between a simple LLM chatbot and an AI agent with tools? Give one concrete example of a "tool" and explain why it makes the agent more capable.

A:	Chatbot can only talk. An AI agent with tools can do things in the real world.

For example:  A web search tool. If you ask "What's the weather in Tel-Aviv right now?" a plain LLM can't know . it has no internet access. An agent can call the search tool, look it up, and give you the current answer. Other tools: run code, query a database, send an email, book a flight and etc.



11.

Q:	What is MCP (Model Context Protocol)? What problem does it solve for AI coding assistants like GitHub Copilot? Name two examples of things an MCP server might expose to an AI assistant.

A:	MCP is a standard way for AI assistants to plug into external systems like files, database, or GitHub.

Without it, the AI is basically blind to actual workspace.

It only knows what to paste into the chat.

Two examples of what an MCP server might expose:

Filesystem access : "Read the contents of file "

Database queries : "Run this SQL and tell me how many users signed up today."

It solves the problem of every tool needing its own custom integration. MCP is the universal adapter.







12.

Q:	What are Agent Skills in the context of AI coding assistants? How are they different from just writing instructions in a plain prompt? Show a minimal example of what a skill's .md metadata block might look like.



A: 	Agent skills are reusable skills bundled into an AI system, which it calls up when required. In contrast to a regular prompt that includes all instructions at once, a skill is tagged with metadata like its name, description, and conditions for triggering it.	

Minimal example of skill metadata:

<skill>

  <name>mongodb-query-optimizer</name>

  <description>Help with MongoDB query optimization and indexing.

  Use when the user asks "How do I optimize this query?"

  or "Why is this query slow?"</description>

  <file>path/to/skills/mongodb-query-optimizer/SKILL.md</file>

</skill>

The AI sees this, recognizes the user is asking about slow MongoDB queries,and loads the detailed skill instructions automatically ,no manual prompting needed.



