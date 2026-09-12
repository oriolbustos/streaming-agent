from fastapi import FastAPI
import asyncio
from fastapi.sse import EventSourceResponse
from anthropic import AsyncAnthropic

app = FastAPI()
client = AsyncAnthropic()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/fake-stream", response_class=EventSourceResponse)
async def fake_stream():
    words = ["Hi,", "how", "can I", "assist", "you", "today?", "I am", "here,", "to", "help!"]
    for word in words:
        await asyncio.sleep(0.3)
        yield word

@app.get("/chat-test", response_class=EventSourceResponse)
async def chat_test():
    messages = [{"role":"user", "content": "how many kcals in a ravioli with pesto dish"}]

    async with client.messages.stream(
        model="claude-haiku-4-5",
        max_tokens=600,
        messages=messages,
    ) as stream:
        async for chunk in stream.text_stream:
            yield chunk
