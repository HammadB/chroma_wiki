from typing import List
import logging
from uuid import uuid4
from fastapi import FastAPI, Response, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from config import settings
from functools import lru_cache
import json
import os
import asyncio
from query_agent import QueryAgent, ChatEntry

class SessionData(BaseModel):
    chat: List[ChatEntry]
# Just store session in memory for now
cookie_to_session: dict[str, SessionData] = {}

os.environ["OPENAI_API_KEY"] = settings.openai_api_key
agent = QueryAgent(dataframe_path=settings.wiki_db_path, index_path=settings.index_path)
app = FastAPI()
origins = ["http://localhost:3000", "https://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logging.error(f"{request}: {exc_str}")
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

@app.get("/query/{query}")
def query(query: str):
    return agent.query(query)


@app.post("/chat")
def chat(chat: List[ChatEntry]):
    return agent.chat(chat)


@app.post("/create_streaming_chat")
async def create_streaming_chat(chat: List[ChatEntry], response: Response):
    session_id = uuid4()
    data = SessionData(chat=chat)
    cookie_to_session[str(session_id)] = data
    response.set_cookie(key="session_id", value=session_id,
                        samesite='none', secure=True)

    return {"success": True}


def encode_chat_for_sse(chat: ChatEntry) -> dict:
    encoded = jsonable_encoder(chat)
    return {
        "event": "message",
        "id": "message_id",
        "retry": RETRY_TIMEOUT,
        "data": json.dumps(encoded)
    }


RETRY_TIMEOUT = 10000  # milisecond
@app.get("/get_streaming_chat_response")
async def get_streaming_chat_response(request: Request):
    session_id = request.cookies.get('session_id')
    chat = cookie_to_session[session_id].chat

    async def event_generator():
        chat_generator = agent.chat_streaming(chat)
        try:
            while True:
                if await request.is_disconnected():
                    break

                try:
                    response_chat = next(chat_generator)
                except StopIteration:
                    break
                
                yield encode_chat_for_sse(response_chat)
        except asyncio.CancelledError as e:
            print("Disconnected stream")

    return EventSourceResponse(event_generator())
