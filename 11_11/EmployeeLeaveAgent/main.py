
import os
import uuid
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import redis

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


# --------------------------------------------------
# 1. LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

load_dotenv()

FOUNDRY_PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
FOUNDRY_AGENT_NAME = os.getenv("FOUNDRY_AGENT_NAME")

REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0"
)

SESSION_TTL = int(os.getenv("SESSION_TTL", "3600"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --------------------------------------------------
# 2. INITIALIZE FASTAPI
# --------------------------------------------------

app = FastAPI(
    title="Employee Leave Assistant API",
    description="AI-powered employee leave management assistant",
    version="1.0.0"
)


# --------------------------------------------------
# 3. CONNECT TO MICROSOFT FOUNDRY
# --------------------------------------------------

if not FOUNDRY_PROJECT_ENDPOINT or not FOUNDRY_AGENT_NAME:
    raise ValueError("Foundry environment variables are missing.")

project = AIProjectClient(
    endpoint=FOUNDRY_PROJECT_ENDPOINT,
    credential=DefaultAzureCredential()
)

# Same project-level client pattern used in the
# successful standalone Python test.
client = project.get_openai_client()


# --------------------------------------------------
# 4. CONNECT TO REDIS
# --------------------------------------------------

redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True
)


def check_redis_connection():
    try:
        redis_client.ping()
        logger.info("Redis connected successfully!")
    except redis.RedisError as e:
        logger.error("Redis connection failed: %s", e)
        raise


# --------------------------------------------------
# 5. REQUEST MODEL
# --------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


# --------------------------------------------------
# 6. HOME ENDPOINT
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "Employee Leave Assistant API is running",
        "agent": FOUNDRY_AGENT_NAME
    }


# --------------------------------------------------
# 7. HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health_check():

    try:
        redis_client.ping()

        return {
            "status": "healthy",
            "foundry": "configured",
            "redis": "connected"
        }

    except redis.RedisError:
        raise HTTPException(
            status_code=503,
            detail="Redis is unavailable"
        )


# --------------------------------------------------
# 8. CHAT ENDPOINT
# --------------------------------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    try:

        check_redis_connection()

        # Get existing session ID or create a new one
        session_id = request.session_id

        if not session_id:
            session_id = str(uuid.uuid4())

        redis_key = f"employee_leave:session:{session_id}"

        # Retrieve Foundry conversation ID from Redis
        conversation_id = redis_client.get(redis_key)

        # Create a new Foundry conversation if session
        # does not exist or has expired
        if not conversation_id:

            conversation = client.conversations.create()

            conversation_id = conversation.id

            logger.info(
                "New conversation created: %s",
                conversation_id
            )

        # Send employee message to Foundry agent
        response = client.responses.create(

            conversation=conversation_id,

            input=request.message,

            extra_body={
                "agent_reference": {
                    "name": FOUNDRY_AGENT_NAME,
                    "type": "agent_reference"
                }
            }
        )

        # Save conversation ID in Redis
        # Refresh the session expiration time
        redis_client.setex(
            redis_key,
            SESSION_TTL,
            conversation_id
        )

        return {
            "session_id": session_id,
            "conversation_id": conversation_id,
            "employee_message": request.message,
            "agent_response": response.output_text
        }

    except redis.RedisError as e:

        logger.exception("Redis error")

        raise HTTPException(
            status_code=503,
            detail="Session storage is unavailable"
        )

    except Exception as e:

        logger.exception("Foundry or application error")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# --------------------------------------------------
# 9. END SESSION
# --------------------------------------------------

@app.delete("/session/{session_id}")
def end_session(session_id: str):

    redis_key = f"employee_leave:session:{session_id}"

    deleted = redis_client.delete(redis_key)

    if deleted:
        return {
            "message": "Session ended successfully",
            "session_id": session_id
        }

    return {
        "message": "Session not found or already expired",
        "session_id": session_id
    }


# --------------------------------------------------
# 10. APPLICATION STARTUP
# --------------------------------------------------

@app.on_event("startup")
def startup_event():

    check_redis_connection()

    logger.info("Employee Leave Assistant started!")
    logger.info("Foundry Agent: %s", FOUNDRY_AGENT_NAME)
