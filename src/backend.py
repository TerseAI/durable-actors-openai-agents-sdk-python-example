"""Serve the page and grant permission to connect directly to an actor."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from durable_actors import AsyncClient
from fastapi import FastAPI
from fastapi import Path as PathParam
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from generated import async_actors

load_dotenv()
STATIC = Path(__file__).resolve().parent.parent / "static"
ChatId = Annotated[str, PathParam(pattern=r"^[a-zA-Z0-9_-]{1,64}$")]


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncClient() as client:
        app.state.client = client
        yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.post("/api/chat/{chat_id}/socket")
async def grant_socket(chat_id: ChatId):
    chat = async_actors.ChatHistory.get(chat_id, app.state.client)
    grant = await chat.prepare_websocket(metadata=None)
    return JSONResponse(grant.model_dump(by_alias=True), headers={"Cache-Control": "no-store"})
