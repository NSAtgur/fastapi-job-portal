from fastapi import WebSocket, WebSocketDisconnect



class ConnectionManager:
    def __init__(self):
        self.active_connections = {}


    async def connect(self, user_id, websocket:WebSocket):
        self.active_connections[user_id]= websocket


    def disconnect(self,user_id):
        self.active_connections.pop(user_id,None)

    async def send_to_user(self, user_id:int, message:dict):
        websocket = self.active_connections.get(user_id)

        if websocket:
            await websocket.send_json(message)

manager = ConnectionManager()


