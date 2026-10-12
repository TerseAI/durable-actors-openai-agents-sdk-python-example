# Durable Actors + OpenAI Agents SDK

A small Python adaptation of the [actor-hosted chat in the durable-actors README](https://github.com/TerseAI/durable-actors#quickstart-multiplayer-ai-chat), using the OpenAI Agents SDK.

## Run

Requires Python 3.11+, [uv](https://docs.astral.sh/uv/), and your own OpenAI API key.

```sh
uv sync --locked
cp .env.example .env
```

Set `OPENAI_API_KEY` in `.env` before starting the actors. The actor uses `OPENAI_MODEL`, defaulting to `gpt-5-mini`. Every reply calls OpenAI.

Start the actors:

```sh
uv run durable-actors dev
```

Then, in another terminal:

```sh
uv run uvicorn src.backend:app --host 127.0.0.1 --port 8000
```

Open [localhost:8000](http://127.0.0.1:8000).

## Architecture

### Before: app-managed architecture

An illustrative FastAPI design coordinates chat through a socket layer, a per-conversation queue, agent workers, and object storage.

```text
+-------------------+                     +----------------------------+
| Browser           |        HTTP         | FastAPI Servers            |
|                   |<------------------->| - Serves UI                |
+-------------------+                     +----------------------------+
          ^                                             |
          | direct WebSocket                            |
          v                                             v
+----------------------------------------------------------------------+
| Socket layer                                                         |
| - Dedicated socket servers (optional)                                |
| - Connects and disconnects clients                                   |
| - Tracks connections by conversation                                 |
| - Redis Pub/Sub for broadcasts across servers                        |
+----------------------------------------------------------------------+
          ^                          |
          |                          | enqueue by conversation
          |                          v
          |             +----------------------------------+
          |             | Conversation queue               |
          |             | - Keyed by conversation ID       |
          |             | - One active turn per chat       |
          |             +----------------------------------+
          |                          |
          |                          v
          |             +----------------------------------+
          | broadcasts  | Agent workers                    |       +--------------+
          +-------------| - Loads conversation history     |       | OpenAI API   |
                        | - Runs OpenAI Agents SDK         |<----->|              |
                        | - Saves updated history          |       +--------------+
                        +----------------------------------+
                                     ^
                                     |
                                     v
                        +----------------------------------+
                        | Object storage                   |
                        | - Conversation history           |
                        +----------------------------------+
```

### Before: message flow

A worker loads history, streams the reply through Redis Pub/Sub, saves the conversation, and acknowledges the queued turn.

```text
Browser       Socket layer      Queue          Worker       Object storage     OpenAI
   |               |         (chat ID)            |                |              |
   |-- message --->|             |                |                |              |
   |               |-- enqueue ->|                |                |              |
   |               |             |-- next turn -->|                |              |
   |               |             |                |-- load history>|              |
   |               |             |                |<-- history ----|              |
   |               |             |                |-- Agents SDK ---------------->|
   |               |             |                |<-- streamed text -------------|
   |               |<-- Redis Pub/Sub ------------|                |              |
   |<-- chunks ----|             |                |                |              |
   |               |             |                |-- save history>|              |
   |               |             |                |<-- saved ------|              |
   |               |<-- done via Redis -----------|                |              |
   |<-- done ------|             |                |                |              |
   |               |             |<-- acknowledge-|                |              |
   |               |             |                |                |              |
```

### After: durable-actors architecture

FastAPI serves the UI and grants connections while durable-actors handles WebSockets, ordered agent turns, and persistence.

```text
+-------------------+                     +----------------------------+
| Browser           |        HTTP         | FastAPI Server             |
|                   |<------------------->| - Serves UI                |
|                   |                     | - Grants socket access     |
+-------------------+                     +----------------------------+
          ^                                             |
          | direct WebSocket                            |
          v                                             v
+----------------------------------------------------------------------+
| durable-actors runtime                                               |
|                                                                      |
| - websockets                                                         |
| - ordered turns                                                      |
| - persistence                                                        |
| - OpenAI Agents SDK runs                                             |
+----------------------------------------------------------------------+
                                    ^
                                    |
                                    v
                             +--------------+
                             | OpenAI API   |
                             +--------------+
```

### After: message flow

The browser connects directly to its chat actor, which streams the agent reply and persists the conversation when the handler returns.

```text
Browser              FastAPI           ChatHistory actor          OpenAI
   |                    |               (one per chat ID)            |
   |-- request socket ->|                      |                     |
   |                    |-- prepare socket --->|                     |
   |                    |<-- grant connection -|                     |
   |<-- WebSocket URL --|                      |                     |
   |                                           |                     |
   |========== direct WebSocket ==============>|                     |
   |<------------- saved history --------------|                     |
   |                                           |                     |
   |--------------- user message ------------->|                     |
   |<-------------- start event ---------------|                     |
   |                                           |-- Agents SDK ------>|
   |                                           |   history + prompt  |
   |                                           |<-- streamed text ---|
   |<-------------- text chunks ---------------|                     |
   |<-------------- done event ----------------|                     |
   |                                           |                     |
   |                                    Persist conversation         |
   |                                    when handler returns         |
```
