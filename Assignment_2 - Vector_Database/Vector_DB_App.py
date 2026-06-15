import chromadb
from chromadb.utils import embedding_functions

documents = [
    {"id": "1",  "text": "A leading technology company known for its innovative consumer electronics, software ecosystem, and strong brand loyalty.", 
     "metadata": {"company": "Apple", "ticker": "AAPL", "sector": "Technology", "founded": 1976}},
    {"id": "2",  "text": "The dominant search engine and advertising platform with significant investments in artificial intelligence and cloud computing.", 
     "metadata": {"company": "Google", "ticker": "GOOGL", "sector": "Technology", "founded": 1998}},
    {"id": "3",  "text": "A multinational technology giant focused on cloud services, enterprise software, and artificial intelligence.", 
     "metadata": {"company": "Microsoft", "ticker": "MSFT", "sector": "Technology", "founded": 1975}},
    {"id": "4",  "text": "The world's largest online retailer and cloud computing leader through Amazon Web Services (AWS).", 
     "metadata": {"company": "Amazon", "ticker": "AMZN", "sector": "Consumer Cyclical", "founded": 1994}},
    {"id": "5",  "text": "A social media and digital advertising powerhouse that connects billions of users worldwide.", 
     "metadata": {"company": "Meta", "ticker": "META", "sector": "Technology", "founded": 2004}},
    {"id": "6",  "text": "An electric vehicle and clean energy company known for rapid innovation and ambitious long-term vision.", 
     "metadata": {"company": "Tesla", "ticker": "TSLA", "sector": "Consumer Cyclical", "founded": 2003}},
    {"id": "7",  "text": "A financial services company that revolutionized online trading and offers commission-free stock trading.", 
     "metadata": {"company": "Robinhood", "ticker": "HOOD", "sector": "Financial Services", "founded": 2013}},
    {"id": "8",  "text": "The leading semiconductor company powering AI, data centers, and gaming graphics.", 
     "metadata": {"company": "NVIDIA", "ticker": "NVDA", "sector": "Technology", "founded": 1993}},
    {"id": "9",  "text": "A multinational conglomerate known for its diverse investments and strong insurance and railroad businesses.", 
     "metadata": {"company": "Berkshire Hathaway", "ticker": "BRK.B", "sector": "Financial Services", "founded": 1839}},
    {"id": "10", "text": "A premium coffeehouse chain with strong global brand presence and consistent customer loyalty.", 
     "metadata": {"company": "Starbucks", "ticker": "SBUX", "sector": "Consumer Cyclical", "founded": 1971}},
    {"id": "11", "text": "A leading pharmaceutical company with a strong pipeline of innovative drugs and vaccines.", 
     "metadata": {"company": "Pfizer", "ticker": "PFE", "sector": "Healthcare", "founded": 1849}},
    {"id": "12", "text": "The world's largest streaming entertainment service with massive investment in original content.", 
     "metadata": {"company": "Netflix", "ticker": "NFLX", "sector": "Communication Services", "founded": 1997}},
    {"id": "13", "text": "A dominant player in e-commerce and digital payments in the Chinese market.", 
     "metadata": {"company": "Alibaba", "ticker": "BABA", "sector": "Consumer Cyclical", "founded": 1999}},
    {"id": "14", "text": "A major chip manufacturer known for processors used in personal computers and servers.", 
     "metadata": {"company": "Intel", "ticker": "INTC", "sector": "Technology", "founded": 1968}},
    {"id": "15", "text": "The leading electric vehicle manufacturer in China with aggressive global expansion plans.", 
     "metadata": {"company": "BYD", "ticker": "BYDDF", "sector": "Consumer Cyclical", "founded": 1995}},
    {"id": "16", "text": "A fast-growing fintech company offering banking, credit cards, and investment services.", 
     "metadata": {"company": "SoFi", "ticker": "SOFI", "sector": "Financial Services", "founded": 2011}},
    {"id": "17", "text": "A major aerospace and defense company involved in commercial aviation and space exploration.", 
     "metadata": {"company": "Boeing", "ticker": "BA", "sector": "Industrials", "founded": 1916}}
]


queries = [
    "stocks of companies leading in artificial intelligence and technology innovation",
    "companies with strong brand loyalty and consistent customer experience",
    "high growth stocks in electric vehicles and clean energy sector",
    "financial services and fintech companies disrupting traditional banking",
    "stocks known for long-term value investing and strong business moats"
]

#
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.Client()
collection_name = "stocks_semantic_search"

# Delete existing collection if it exists and creating new one
try:
    client.delete_collection(collection_name)
except:
    pass

collection = client.create_collection(
    name=collection_name,
    embedding_function=embedding_function
)

# Add documents
collection.add(
    ids=[doc["id"] for doc in documents],
    documents=[doc["text"] for doc in documents],
    metadatas=[doc["metadata"] for doc in documents]
)

print()
print("VECTOR DATABASE CREATED SUCCESSFULLY")
print(f"Collection Name : {collection_name}")
print(f"Total Documents : {collection.count()}")
print()

#RUN SEMANTIC SEARCH 
for i, query in enumerate(queries, start=1):
    results = collection.query(
        query_texts=[query],
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )
    
    print(f"\nQuery {i}: {query}")
    print()
    
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]
    ids = results["ids"][0]
    
    for rank, (doc_id, doc_text, meta, dist) in enumerate(zip(ids, docs, metas, distances), start=1):
        print(f"{rank}. {meta['company']} ({meta['ticker']}) | Sector: {meta['sector']} | Founded: {meta['founded']}")
        print(f"   Distance: {dist:.4f}")
        print(f"   Text: {doc_text}")
        print()

