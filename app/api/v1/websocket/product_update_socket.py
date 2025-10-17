from fastapi.websockets import WebSocketState
import redis.asyncio as redis
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from app.core.config import settings
import asyncio, json
from app.db.session import get_db
from app.schemas.product import ProductBaseModel, SingleProductGetResponse
from app.services.product_service import ProductService
from sqlalchemy.orm import Session


redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
router = APIRouter()

@router.websocket("/ws/products/update")
async def websocket_product_update(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    try:
        channel = settings.PRODUCT_UPDATE_CHANNEL
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(channel)

        async def forward_redis_to_ws():
            while True:
                msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if msg and msg.get("type") == "message":
                    await websocket.send_json({"type": "update", "product": json.loads(msg.get("data"))})
                await asyncio.sleep(0)

        async def monitor_ws():
            try:
                while True:
                    await websocket.receive_text()
            except Exception:
                pass

        forward_task = asyncio.create_task(forward_redis_to_ws())
        monitor_task = asyncio.create_task(monitor_ws())
        done, pending = await asyncio.wait([forward_task, monitor_task], return_when=asyncio.FIRST_COMPLETED)
        for t in pending:
            t.cancel()
    except WebSocketDisconnect:
        print("Client disconnected")
        pass
    finally:
        try:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
        except Exception:
            pass
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()
