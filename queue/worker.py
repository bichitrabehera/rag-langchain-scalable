from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

load_dotenv()

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)


vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning",
    embedding=embeddings
)

model = ChatOpenAI(
    model="gpt-4o-mini",
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