import json
import asyncio
from datetime import datetime
from typing import Dict, List, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import uvicorn


# ==================== Pydantic Models ====================
class Message(BaseModel):
    """Schema for chat messages"""
    from_user: str = Field(..., alias="from")
    message: str
    timestamp: str


class SystemMessage(BaseModel):
    """Schema for system messages (join/leave)"""
    type: str  # 'system'
    message: str
    timestamp: str


class RoomInfo(BaseModel):
    """Schema for room information"""
    room_name: str
    user_count: int


class UserList(BaseModel):
    """Schema for list of users in a room"""
    room_name: str
    users: List[str]
    user_count: int


# ==================== Connection Manager ====================
class ConnectionManager:
    """Manages WebSocket connections and broadcasts messages across rooms"""

    def __init__(self):
        # Structure: {room_name: {username: websocket_connection}}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_name: str, username: str):
        """Add a new user connection to a room"""
        await websocket.accept()

        # Create room if it doesn't exist
        if room_name not in self.active_connections:
            self.active_connections[room_name] = {}

        # Add user to room
        self.active_connections[room_name][username] = websocket

    async def disconnect(self, room_name: str, username: str):
        """Remove a user connection from a room"""
        if room_name in self.active_connections:
            if username in self.active_connections[room_name]:
                del self.active_connections[room_name][username]

            # Delete room if empty
            if not self.active_connections[room_name]:
                del self.active_connections[room_name]

    async def broadcast_to_room(self, room_name: str, message: dict, exclude_user: str = None):
        """Broadcast a message to all users in a room"""
        if room_name not in self.active_connections:
            return

        # Create a list of tasks for concurrent sending
        tasks = []
        for username, connection in self.active_connections[room_name].items():
            # Skip excluded user if specified
            if exclude_user and username == exclude_user:
                continue

            tasks.append(self._send_message(connection, message))

        # Send all messages concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_message(self, connection: WebSocket, message: dict):
        """Send a message to a specific connection"""
        try:
            await connection.send_json(message)
        except Exception as e:
            print(f"Error sending message: {e}")

    def get_active_rooms(self) -> List[RoomInfo]:
        """Get list of all active rooms with user counts"""
        rooms = []
        for room_name, users in self.active_connections.items():
            rooms.append(RoomInfo(room_name=room_name, user_count=len(users)))
        return rooms

    def get_room_users(self, room_name: str) -> List[str]:
        """Get list of users in a specific room"""
        if room_name not in self.active_connections:
            return []
        return list(self.active_connections[room_name].keys())

    def room_exists(self, room_name: str) -> bool:
        """Check if a room exists"""
        return room_name in self.active_connections


# ==================== FastAPI App ====================
app = FastAPI(title="Real-Time Chat Room API")
manager = ConnectionManager()


# ==================== Routes ====================

@app.get("/", response_class=HTMLResponse)
async def get_html_test_page():
    """Serve HTML test page for WebSocket chat"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Real-Time Chat Room</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                width: 100%;
                max-width: 600px;
                display: flex;
                flex-direction: column;
                height: 80vh;
                max-height: 700px;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 15px 15px 0 0;
                text-align: center;
            }
            .header h1 {
                font-size: 24px;
                margin-bottom: 10px;
            }
            .status {
                font-size: 14px;
                opacity: 0.9;
            }
            .chat-area {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: #f8f9fa;
            }
            .message {
                margin-bottom: 15px;
                animation: slideIn 0.3s ease-out;
            }
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            .message.system {
                text-align: center;
                color: #999;
                font-size: 12px;
                font-style: italic;
            }
            .message.user {
                background: white;
                padding: 12px 15px;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }
            .message.user .username {
                font-weight: bold;
                color: #667eea;
                font-size: 12px;
                margin-bottom: 5px;
            }
            .message.user .timestamp {
                font-size: 10px;
                color: #999;
                margin-top: 5px;
            }
            .input-area {
                padding: 20px;
                background: white;
                border-top: 1px solid #e0e0e0;
                display: flex;
                gap: 10px;
            }
            input[type="text"] {
                flex: 1;
                padding: 12px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 25px;
                font-size: 14px;
                transition: border-color 0.3s;
            }
            input[type="text"]:focus {
                outline: none;
                border-color: #667eea;
            }
            button {
                padding: 12px 25px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-weight: bold;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            button:active {
                transform: translateY(0);
            }
            button:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            .setup-area {
                padding: 20px;
                background: white;
                border-bottom: 1px solid #e0e0e0;
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }
            .setup-area input {
                flex: 1;
                min-width: 150px;
                padding: 10px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                font-size: 14px;
            }
            .setup-area button {
                padding: 10px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-weight: bold;
            }
            .connected {
                background: #4caf50 !important;
            }
            .error {
                color: #f44336;
                padding: 10px;
                background: #ffebee;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💬 Real-Time Chat Room</h1>
                <div class="status" id="status">Disconnected</div>
            </div>

            <div class="setup-area" id="setupArea">
                <input type="text" id="roomInput" placeholder="Enter room name" />
                <input type="text" id="usernameInput" placeholder="Enter your username" />
                <button onclick="connectToChat()">Connect</button>
            </div>

            <div id="errorArea"></div>

            <div class="chat-area" id="chatArea"></div>

            <div class="input-area" id="inputArea" style="display: none;">
                <input type="text" id="messageInput" placeholder="Type a message..." />
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>

        <script>
            let ws = null;
            let isConnected = false;

            function connectToChat() {
                const room = document.getElementById('roomInput').value.trim();
                const username = document.getElementById('usernameInput').value.trim();

                if (!room || !username) {
                    showError('Please enter both room name and username');
                    return;
                }

                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws/${room}/${username}`;

                try {
                    ws = new WebSocket(wsUrl);

                    ws.onopen = () => {
                        isConnected = true;
                        document.getElementById('status').textContent = `Connected as ${username} in #${room}`;
                        document.getElementById('status').parentElement.style.background = '#4caf50';
                        document.getElementById('setupArea').style.display = 'none';
                        document.getElementById('inputArea').style.display = 'flex';
                        document.getElementById('chatArea').innerHTML = '';
                        document.getElementById('errorArea').innerHTML = '';
                    };

                    ws.onmessage = (event) => {
                        const data = JSON.parse(event.data);
                        displayMessage(data);
                    };

                    ws.onerror = (error) => {
                        showError('WebSocket error: ' + error);
                        console.error('WebSocket error:', error);
                    };

                    ws.onclose = () => {
                        isConnected = false;
                        document.getElementById('status').textContent = 'Disconnected';
                        document.getElementById('setupArea').style.display = 'flex';
                        document.getElementById('inputArea').style.display = 'none';
                        showError('Connection closed. Please reconnect.');
                    };
                } catch (error) {
                    showError('Failed to connect: ' + error.message);
                    console.error('Connection error:', error);
                }
            }

            function sendMessage() {
                const messageInput = document.getElementById('messageInput');
                const message = messageInput.value.trim();

                if (!message || !isConnected) {
                    return;
                }

                ws.send(JSON.stringify({
                    type: 'message',
                    message: message
                }));

                messageInput.value = '';
                messageInput.focus();
            }

            function displayMessage(data) {
                const chatArea = document.getElementById('chatArea');
                const messageDiv = document.createElement('div');

                if (data.type === 'system') {
                    messageDiv.className = 'message system';
                    messageDiv.textContent = data.message;
                } else {
                    messageDiv.className = 'message user';
                    const timestamp = new Date(data.timestamp).toLocaleTimeString();
                    messageDiv.innerHTML = `
                        <div class="username">${data.from}</div>
                        <div>${data.message}</div>
                        <div class="timestamp">${timestamp}</div>
                    `;
                }

                chatArea.appendChild(messageDiv);
                chatArea.scrollTop = chatArea.scrollHeight;
            }

            function showError(message) {
                const errorArea = document.getElementById('errorArea');
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error';
                errorDiv.textContent = message;
                errorArea.innerHTML = '';
                errorArea.appendChild(errorDiv);
            }

            // Allow Enter key to send message
            document.addEventListener('keypress', function(event) {
                if (event.key === 'Enter' && isConnected && document.activeElement.id === 'messageInput') {
                    sendMessage();
                }
            });

            // Allow Enter key to connect
            document.addEventListener('keypress', function(event) {
                if (event.key === 'Enter' && !isConnected) {
                    const focused = document.activeElement;
                    if (focused.id === 'roomInput' || focused.id === 'usernameInput') {
                        connectToChat();
                    }
                }
            });
        </script>
    </body>
    </html>
    """


@app.websocket("/ws/{room_name}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_name: str, username: str):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket, room_name, username)

    # Broadcast join message
    join_message = {
        "type": "system",
        "message": f"{username} joined the room",
        "timestamp": datetime.now().isoformat(),
    }
    await manager.broadcast_to_room(room_name, join_message)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Broadcast message to all users in the room
            chat_message = {
                "from": username,
                "message": message_data.get("message", ""),
                "timestamp": datetime.now().isoformat(),
            }
            await manager.broadcast_to_room(room_name, chat_message)

    except WebSocketDisconnect:
        # Remove user from room
        await manager.disconnect(room_name, username)

        # Broadcast leave message
        leave_message = {
            "type": "system",
            "message": f"{username} left the room",
            "timestamp": datetime.now().isoformat(),
        }
        await manager.broadcast_to_room(room_name, leave_message)


@app.get("/rooms", response_model=List[RoomInfo])
async def get_active_rooms():
    """Get list of all active rooms and their user counts"""
    return manager.get_active_rooms()


@app.get("/rooms/{room_name}/users", response_model=UserList)
async def get_room_users(room_name: str):
    """Get list of users in a specific room"""
    if not manager.room_exists(room_name):
        raise HTTPException(status_code=404, detail="Room not found")

    users = manager.get_room_users(room_name)
    return UserList(
        room_name=room_name,
        users=users,
        user_count=len(users)
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
