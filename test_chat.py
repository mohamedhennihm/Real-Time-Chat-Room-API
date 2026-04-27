#!/usr/bin/env python3
"""
Test script for the Real-Time Chat Room API
Tests the ConnectionManager without needing FastAPI running
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List


# ==================== Test ConnectionManager ====================
class MockWebSocket:
    """Mock WebSocket for testing"""
    def __init__(self, name):
        self.name = name
        self.messages = []
    
    async def accept(self):
        print(f"  ✓ {self.name} accepted")
    
    async def send_json(self, data):
        self.messages.append(data)
        print(f"    → {self.name} received: {data.get('message', data.get('type', 'unknown'))}")
    
    async def receive_text(self):
        return '{"type": "message", "message": "test"}'


class ConnectionManager:
    """Manages WebSocket connections and broadcasts messages across rooms"""

    def __init__(self):
        self.active_connections: Dict[str, Dict[str, MockWebSocket]] = {}

    async def connect(self, websocket, room_name: str, username: str):
        """Add a new user connection to a room"""
        await websocket.accept()
        if room_name not in self.active_connections:
            self.active_connections[room_name] = {}
        self.active_connections[room_name][username] = websocket

    async def disconnect(self, room_name: str, username: str):
        """Remove a user connection from a room"""
        if room_name in self.active_connections:
            if username in self.active_connections[room_name]:
                del self.active_connections[room_name][username]
            if not self.active_connections[room_name]:
                del self.active_connections[room_name]

    async def broadcast_to_room(self, room_name: str, message: dict, exclude_user: str = None):
        """Broadcast a message to all users in a room"""
        if room_name not in self.active_connections:
            return

        tasks = []
        for username, connection in self.active_connections[room_name].items():
            if exclude_user and username == exclude_user:
                continue
            tasks.append(self._send_message(connection, message))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_message(self, connection, message: dict):
        """Send a message to a specific connection"""
        try:
            await connection.send_json(message)
        except Exception as e:
            print(f"    ✗ Error sending message: {e}")

    def get_active_rooms(self) -> List[str]:
        """Get list of all active rooms"""
        return list(self.active_connections.keys())

    def get_room_users(self, room_name: str) -> List[str]:
        """Get list of users in a specific room"""
        if room_name not in self.active_connections:
            return []
        return list(self.active_connections[room_name].keys())

    def room_exists(self, room_name: str) -> bool:
        """Check if a room exists"""
        return room_name in self.active_connections


# ==================== Tests ====================
async def test_basic_connection():
    """Test: User can connect to a room"""
    print("\n📝 Test 1: Basic Connection")
    print("=" * 50)
    
    manager = ConnectionManager()
    ws = MockWebSocket("alice")
    
    await manager.connect(ws, "general", "alice")
    assert manager.room_exists("general"), "Room should exist"
    assert "alice" in manager.get_room_users("general"), "User should be in room"
    print("✅ PASSED: User connected successfully")


async def test_join_broadcast():
    """Test: All users receive join notification"""
    print("\n📝 Test 2: Join Broadcast Notification")
    print("=" * 50)
    
    manager = ConnectionManager()
    alice_ws = MockWebSocket("alice")
    bob_ws = MockWebSocket("bob")
    
    # Alice joins first
    print("  Alice joining...")
    await manager.connect(alice_ws, "general", "alice")
    
    # Bob joins
    print("  Bob joining...")
    await manager.connect(bob_ws, "general", "bob")
    
    # Broadcast join message
    join_msg = {
        "type": "system",
        "message": "bob joined the room",
        "timestamp": datetime.now().isoformat(),
    }
    await manager.broadcast_to_room("general", join_msg)
    
    assert len(bob_ws.messages) > 0, "Bob should receive notification"
    print("✅ PASSED: Join notification broadcasted")


async def test_message_broadcast():
    """Test: Messages are broadcast to all room users"""
    print("\n📝 Test 3: Message Broadcast")
    print("=" * 50)
    
    manager = ConnectionManager()
    alice_ws = MockWebSocket("alice")
    bob_ws = MockWebSocket("bob")
    charlie_ws = MockWebSocket("charlie")
    
    # Connect all users
    print("  Connecting users...")
    await manager.connect(alice_ws, "general", "alice")
    await manager.connect(bob_ws, "general", "bob")
    await manager.connect(charlie_ws, "general", "charlie")
    
    # Alice sends a message
    print("  Alice sending message...")
    chat_msg = {
        "from": "alice",
        "message": "Hello everyone!",
        "timestamp": datetime.now().isoformat(),
    }
    await manager.broadcast_to_room("general", chat_msg)
    
    assert len(bob_ws.messages) > 0, "Bob should receive message"
    assert len(charlie_ws.messages) > 0, "Charlie should receive message"
    print("✅ PASSED: Message broadcasted to all users")


async def test_leave_broadcast():
    """Test: Users notified when someone leaves"""
    print("\n📝 Test 4: Leave Broadcast Notification")
    print("=" * 50)
    
    manager = ConnectionManager()
    alice_ws = MockWebSocket("alice")
    bob_ws = MockWebSocket("bob")
    
    print("  Connecting users...")
    await manager.connect(alice_ws, "general", "alice")
    await manager.connect(bob_ws, "general", "bob")
    
    print("  Alice leaving...")
    await manager.disconnect("general", "alice")
    
    # Broadcast leave message
    leave_msg = {
        "type": "system",
        "message": "alice left the room",
        "timestamp": datetime.now().isoformat(),
    }
    await manager.broadcast_to_room("general", leave_msg)
    
    assert "alice" not in manager.get_room_users("general"), "Alice should be removed"
    assert len(bob_ws.messages) > 0, "Bob should receive leave notification"
    print("✅ PASSED: Leave notification broadcasted")


async def test_auto_room_deletion():
    """Test: Room is deleted when last user leaves"""
    print("\n📝 Test 5: Automatic Room Deletion")
    print("=" * 50)
    
    manager = ConnectionManager()
    alice_ws = MockWebSocket("alice")
    
    print("  Alice joining room...")
    await manager.connect(alice_ws, "general", "alice")
    assert manager.room_exists("general"), "Room should exist"
    
    print("  Alice leaving room...")
    await manager.disconnect("general", "alice")
    assert not manager.room_exists("general"), "Room should be deleted"
    print("✅ PASSED: Room deleted when empty")


async def test_get_active_rooms():
    """Test: Get list of active rooms"""
    print("\n📝 Test 6: Get Active Rooms")
    print("=" * 50)
    
    manager = ConnectionManager()
    
    # Create rooms
    print("  Creating rooms...")
    await manager.connect(MockWebSocket("alice"), "general", "alice")
    await manager.connect(MockWebSocket("bob"), "general", "bob")
    await manager.connect(MockWebSocket("charlie"), "dev", "charlie")
    
    rooms = manager.get_active_rooms()
    assert "general" in rooms, "general room should exist"
    assert "dev" in rooms, "dev room should exist"
    assert len(rooms) == 2, "Should have 2 rooms"
    print(f"  Active rooms: {rooms}")
    print("✅ PASSED: Get active rooms works")


async def test_get_room_users():
    """Test: Get list of users in a room"""
    print("\n📝 Test 7: Get Room Users")
    print("=" * 50)
    
    manager = ConnectionManager()
    
    # Create room with users
    print("  Adding users to room...")
    await manager.connect(MockWebSocket("alice"), "general", "alice")
    await manager.connect(MockWebSocket("bob"), "general", "bob")
    await manager.connect(MockWebSocket("charlie"), "general", "charlie")
    
    users = manager.get_room_users("general")
    assert len(users) == 3, "Should have 3 users"
    assert "alice" in users, "alice should be in room"
    assert "bob" in users, "bob should be in room"
    assert "charlie" in users, "charlie should be in room"
    print(f"  Room users: {users}")
    print("✅ PASSED: Get room users works")


async def test_multiple_rooms():
    """Test: Users in different rooms don't interfere"""
    print("\n📝 Test 8: Multiple Rooms Isolation")
    print("=" * 50)
    
    manager = ConnectionManager()
    
    print("  Setting up rooms...")
    general_alice = MockWebSocket("alice")
    general_bob = MockWebSocket("bob")
    dev_charlie = MockWebSocket("charlie")
    random_dave = MockWebSocket("dave")
    
    await manager.connect(general_alice, "general", "alice")
    await manager.connect(general_bob, "general", "bob")
    await manager.connect(dev_charlie, "dev", "charlie")
    await manager.connect(random_dave, "random", "dave")
    
    # Send message in general room
    print("  Broadcasting to general room...")
    msg = {
        "from": "alice",
        "message": "Hello general!",
        "timestamp": datetime.now().isoformat(),
    }
    await manager.broadcast_to_room("general", msg)
    
    assert len(general_bob.messages) > 0, "Bob should receive message"
    assert len(dev_charlie.messages) == 0, "Charlie should NOT receive message"
    assert len(random_dave.messages) == 0, "Dave should NOT receive message"
    print("✅ PASSED: Room isolation works correctly")


async def test_exclude_sender():
    """Test: Broadcast can exclude sender"""
    print("\n📝 Test 9: Exclude Sender Option")
    print("=" * 50)
    
    manager = ConnectionManager()
    
    print("  Setting up chat...")
    alice_ws = MockWebSocket("alice")
    bob_ws = MockWebSocket("bob")
    
    await manager.connect(alice_ws, "general", "alice")
    await manager.connect(bob_ws, "general", "bob")
    
    # Clear previous messages
    alice_ws.messages = []
    bob_ws.messages = []
    
    # Broadcast excluding alice
    print("  Broadcasting excluding alice...")
    msg = {
        "from": "alice",
        "message": "Only bob should see this",
        "timestamp": datetime.now().isoformat(),
    }
    await manager.broadcast_to_room("general", msg, exclude_user="alice")
    
    assert len(alice_ws.messages) == 0, "Alice should be excluded"
    assert len(bob_ws.messages) > 0, "Bob should receive message"
    print("✅ PASSED: Exclude sender works correctly")


# ==================== Run All Tests ====================
async def main():
    print("\n" + "=" * 50)
    print("🧪 Real-Time Chat Room API - Test Suite")
    print("=" * 50)
    
    tests = [
        test_basic_connection,
        test_join_broadcast,
        test_message_broadcast,
        test_leave_broadcast,
        test_auto_room_deletion,
        test_get_active_rooms,
        test_get_room_users,
        test_multiple_rooms,
        test_exclude_sender,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            await test()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    if failed == 0:
        print("\n✅ All tests passed! Ready for deployment.")
    else:
        print(f"\n❌ {failed} test(s) failed.")


if __name__ == "__main__":
    asyncio.run(main())
