# Vector DB App: Semantic Search for Stocks

A Python application that uses **ChromaDB** and **Sentence Transformers** to perform semantic search on a collection of stock-related documents. This app demonstrates how to create a vector database, index stock descriptions, and retrieve the most relevant stocks based on semantic queries.

---

## 📌 Features

- **Semantic Search**: Uses the `all-MiniLM-L6-v2` embedding model to find stocks matching conceptual queries (e.g., "long-term value investing").
- **Vector Database**: ChromaDB for efficient storage and retrieval of embeddings.
- **Customizable Queries**: Predefined queries for AI/tech, brand loyalty, clean energy, fintech, and value investing.
- **Metadata Support**: Each stock includes metadata like ticker, sector, and founding year.

---

## 🛠️ Setup

### Prerequisites
- Python 3.8+
- `chromadb` library
- `sentence-transformers` library

Install dependencies:
```bash
pip install chromadb sentence-transformers
```

---

## 🚀 Usage

1. **Run the Script**:
   ```bash
   python Vector_DB_App.py
   ```

2. **Output**:
   - The script creates a ChromaDB collection named `stocks_semantic_search`.
   - For each query, it prints the top 3 matching stocks, their metadata, and the distance score (lower = more relevant).

---

## 📊 Example Queries

| Query | Description |
|-------|-------------|
| `"stocks of companies leading in artificial intelligence and technology innovation"` | Matches NVIDIA, Microsoft, Google (explicit AI/tech focus). |
| `"stocks known for long-term value investing and strong business moats"` | Matches Apple (brand loyalty) and Berkshire Hathaway (diversification). |
| `"high growth stocks in electric vehicles and clean energy sector"` | Matches Tesla, Rivian, etc. |

---

## 🔍 Analysis

- **Most Relevant Query**: `"stocks of companies leading in artificial intelligence and technology innovation"` returned the most precise matches (NVIDIA, Microsoft, Google) due to direct alignment with their descriptions.
- **Surprising Matches**: The query about "long-term value investing" matched **Apple** and **Berkshire Hathaway** despite lacking exact keyword matches, demonstrating semantic understanding.
- **Distance Threshold**: Relevance is determined by the lowest distance scores. A fixed threshold is not recommended; instead, inspect the top 1–3 results for each query.

---

## 📂 Project Structure

```
.
├── Vector_DB_App.py    # Main script
├── analysis.txt        # Analysis of query results
└── README.md           # This file
```

---

## 📝 Notes

- **Embedding Model**: `all-MiniLM-L6-v2` (lightweight, efficient for semantic tasks).
- **ChromaDB**: Local vector database; no external API required.
- **Customization**: Add/remove stocks or queries by editing the `documents` and `queries` lists in the script.

---

## 🤝 Contributing

Feel free to extend the dataset or experiment with different embedding models. Pull requests are welcome!

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.