from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)


vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning",
    embedding=embeddings
)

model = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    temperature=0,
)

agent = create_agent(
    model=model,
)


def process_query(query:str):
    print("Searching Chunks")
    search_result = vector_db.similarity_search(query=query)
    context = "\n\n".join(
        doc.page_content for doc in search_result
    )
    SYSTEM_PROMPT = f"""
    Answer the question using the context below.

    Context:
    {context}

    Question:
    {query}

    If the answer cannot be found in the context, say that you don't
    have enough information from the provided document.
    """
    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT ,
                },
                {
                    "role" : "user",
                    "content": query
                }
            ]
        }
    )

    print("Printing")

    return response["messages"][-1].content