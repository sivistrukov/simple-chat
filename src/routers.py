from fastapi import APIRouter, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates

from ws_connection_manager import ConnectionManager

router = APIRouter()
templates = Jinja2Templates(directory='templates')

rooms: dict[str, ConnectionManager] = dict()


@router.get('/')
def get_index_page(request: Request) -> Response:
    context = {'request': request}
    return templates.TemplateResponse('index.html', context)


@router.get('/chat')
def get_chat_room_page(request: Request, room: str, username: str) -> Response:
    context = {
        'request': request,
        'room': room,
        'username': username,
    }
    return templates.TemplateResponse('room.html', context)


@router.websocket('/ws/chat')
async def ws_room(websocket: WebSocket, room: str, username: str) -> None:
    if room not in rooms:
        rooms[room] = ConnectionManager()
    manager = rooms[room]
    await manager.connect(websocket)
    await manager.broadcast(f'{username} join the chat')
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f'{username} says: {data}')
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f'{username} left the chat')
        if not manager.active_connections:
            del rooms[room]
