import os

from fastapi import FastAPI, HTTPException, Query
from .client.rq import queue
from .queue.worker import process_query
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/chat")
def chat(query:str = Query(description="Query by user")):
    job = queue.enqueue(
        process_query,
        query
    )
    return {"status":"queued","job_id":job.id}

@app.get("/job_status")
def get_result(job_id:str=Query(description="Job ID")):
    job = queue.fetch_job(job_id=job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.is_failed:
        return {"status": "failed", "error": job.exc_info}

    if not job.is_finished:
        return {"status": job.get_status()}

    return {"status": "finished", "result": job.return_value()}
