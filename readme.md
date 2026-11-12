# RAG Application

This folder contains a Retrieval-Augmented Generation (RAG) application. It
retrieves relevant document chunks from a vector database and sends them to an
OpenAI model to generate an answer.

## Technologies used

- **Python 3.13+** - Application runtime.
- **FastAPI** - HTTP API server.
- **Uvicorn** - ASGI server used to run FastAPI.
- **RQ (Redis Queue)** - Runs chat requests asynchronously in a background
  worker.
- **Redis-compatible Valkey** - Stores the RQ queue and job data.
- **Qdrant** - Vector database used to store and search document embeddings.
- **LangChain** - Connects the embedding model, vector store, chat model, and
  agent.
- **OpenAI**:
  - `text-embedding-3-small` creates embeddings for search.
  - `gpt-4o-mini` generates the final answer.
- **python-dotenv** - Loads environment variables from `.env`.
- **Docker Compose** - Starts Qdrant and Valkey locally.

## Project structure

```text
rag/
├── client/
│   └── rq.py          # Redis connection and RQ queue
├── queue/
│   └── worker.py      # Retrieval and answer-generation job
├── docker-compose.yml # Qdrant and Valkey services
├── server.py          # FastAPI endpoints
└── main.py            # Starts the Uvicorn server
```

## Request flow

1. A client sends a question to `POST /chat`.
2. FastAPI places `process_query` on the RQ `default` queue.
3. An RQ worker receives the job.
4. The worker performs similarity search against the Qdrant `learning`
   collection.
5. The retrieved document contents are joined into a context string.
6. The context and question are passed to the LangChain agent.
7. OpenAI generates the answer.
8. The client polls `GET /job_status` with the returned job ID.

## Running the application

### 1. Start infrastructure

From the `rag` directory:

```bash
docker compose up -d
```

This starts:

- Qdrant at `http://localhost:6333`
- Valkey at `localhost:6379`

The Qdrant `learning` collection must already exist and contain indexed
documents.

### 2. Configure OpenAI

Create a `.env` file in the project or `rag` directory:

```env
OPENAI_API_KEY=your_openai_api_key
```

Never commit the real API key to source control. If a key is exposed, revoke it
and create a replacement.

### 3. Start the API

From the project root:

```bash
python -m rag.main
```

The API listens on port `8000`.

### 4. Start the worker

From the project root:

```bash
rq worker -w rq.worker.SimpleWorker
```

The worker listens to the `default` queue.

## API usage

Queue a question:

```http
POST http://localhost:8000/chat?query=what%20is%20rust
```

Example response:

```json
{
  "status": "queued",
  "job_id": "job-id"
}
```

Check the result:

```http
GET http://localhost:8000/job_status?job_id=job-id
```

Possible responses include:

```json
{
  "status": "finished",
  "result": "..."
}
```

```json
{
  "status": "queued"
}
```

```json
{
  "status": "failed",
  "error": "..."
}
```

## Important notes

- The API and worker must both be running.
- Valkey must be running before the API or worker connects to the queue.
- Qdrant must be running and contain the `learning` collection.
- Google model calls depend on network access and a valid API key.
- RQ jobs have a timeout. A slow Google request can cause a job to fail with
  `JobTimeoutException`; configure the worker timeout and model request timeout
  appropriately for production.