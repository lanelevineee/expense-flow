import json
import time
import asyncio
from fastapi import APIRouter, Header, Request
from typing import Optional

from src.auth.middleware import verify_token

router = APIRouter()


@router.get("/events")
async def sse_events(request: Request, authorization: Optional[str] = Header(None)):
    if not authorization:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = verify_token(authorization.replace("Bearer ", ""))
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid token")

    from sse_starlette.sse import EventSourceResponse

    async def event_generator():
        yield {"event": "connected", "data": json.dumps({"staff_id": user.staff_id})}
        while True:
            if await request.is_disconnected():
                break
            yield {"event": "heartbeat", "data": json.dumps({"ts": int(time.time())})}
            await asyncio.sleep(30)

    return EventSourceResponse(event_generator())


@router.post("/notify")
def notify(request: Request, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    return {"success": True, "message": "Notification broadcast"}


def _require_auth(authorization: Optional[str]):
    if not authorization:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = verify_token(authorization.replace("Bearer ", ""))
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid token")
    return user
