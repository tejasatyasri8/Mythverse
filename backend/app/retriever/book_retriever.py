import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from openai import OpenAI

load_dotenv()

COLLECTION_NAME = "mythverse"

# -----------------------------------
# Model Initialization
# -----------------------------------
dense_model = SentenceTransformer("all-MiniLM-L6-v2")

# Point the OpenAI client to Groq's free endpoint
llm_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

# -----------------------------------
# Qdrant Client
# -----------------------------------
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=60,
)

import re

# -----------------------------------
# HyDE Generator
# -----------------------------------
def generate_hypothetical_document(query: str, religion: str, book: str) -> str:
    """Uses an LLM to generate a hypothetical passage in the style of the target book, 
    stripping out reasoning tags if a reasoning model is used."""
    
    system_prompt = (
        f"You are an expert theologian. The user will ask a question about the {religion} {book}. "
        f"Write a single, highly realistic hypothetical passage in the exact archaic, poetic style "
        f"of the {book} that perfectly answers the underlying intent of the question. "
        f"Do NOT answer the question directly. Do NOT include commentary. "
        f"Example: If the query is 'What does it say about hard work?', output 'And he that laboreth with his hands shall eat of the fruit thereof.'\n"
        f"Output ONLY the passage."
    )
    
    try:
        response = llm_client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
            temperature=0.5,
            max_tokens=150,
            reasoning_effort="none"
        )
        content = response.choices[0].message.content
        if not content:
            return query
            
        # Strip out reasoning tags (<think>...</think>) if present
        cleaned_content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        
        # Fallback if cleaning leaves it empty
        return cleaned_content if cleaned_content else query
        
    except Exception as e:
        print(f"HyDE Generation Failed: {e}")
        return query
# -----------------------------------
# Search Function
# -----------------------------------
def search_book(
    query: str,
    religion: str,
    book: str,
    top_k: int = 10,
):
    print("=" * 50)
    print("Original Query:", query)

    # 1. Expand query via HyDE
    hyde_text = generate_hypothetical_document(query, religion, book)
    print("HyDE Expanded Text:", hyde_text)

    # 2. Embed the hypothetical text
    dense_query = dense_model.encode(hyde_text).tolist()

    # 3. Query Qdrant
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=dense_query,
        using="dense",
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="religion",
                    match=models.MatchValue(value=religion),
                ),
                models.FieldCondition(
                    key="book",
                    match=models.MatchValue(value=book),
                ),
            ]
        ),
        limit=top_k,
    )

    output = []
    for point in results.points:
        payload = point.payload or {}
        output.append(
            {
                "text": payload.get("text", ""),
                "metadata": {
                    "religion": payload.get("religion"),
                    "book": payload.get("book"),
                    "chapter": payload.get("chapter"),
                    "verse": payload.get("verse"),
                    "reference": payload.get("reference"),
                },
                "score": point.score,
            }
        )

    return output