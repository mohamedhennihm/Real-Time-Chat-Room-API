# Real-Time Chat Room API - Project Index

## 📂 Project Directory Structure

```
Real-Time Chat Room API/
├── main.py                    ← Start here! Main FastAPI application
├── test_chat.py              ← Comprehensive unit tests (9 tests, all passing)
├── requirements.txt          ← Python dependencies to install
├── README.md                 ← Complete API documentation
├── FEATURES.md               ← Feature list and implementation details
├── QUICKSTART.txt            ← Quick start guide (30 seconds)
└── INDEX.md                  ← This file
```

---

## 🚀 Getting Started (Choose One)

### Option 1: Super Quick (30 seconds)
1. Read: `QUICKSTART.txt`
2. Run: `pip install -r requirements.txt`
3. Run: `python main.py`
4. Open: `http://localhost:8000`

### Option 2: Detailed Setup
1. Read: `README.md` (full documentation)
2. Follow installation steps
3. Run tests with: `python test_chat.py`
4. Start server with: `python main.py`

### Option 3: Learning Approach
1. Read: `FEATURES.md` (architecture overview)
2. Review: `main.py` (source code with comments)
3. Run tests: `python test_chat.py`
4. Try web client at: `http://localhost:8000`

---

## 📚 Documentation Guide

| File | Purpose | Read Time |
|------|---------|-----------|
| **INDEX.md** | You are here - navigation guide | 2 min |
| **QUICKSTART.txt** | 30-second setup and examples | 5 min |
| **README.md** | Complete API documentation | 15 min |
| **FEATURES.md** | Architecture and features | 10 min |
| **main.py** | Source code with comments | 20 min |
| **test_chat.py** | Unit tests (learn by example) | 10 min |

---

## 🎯 What You'll Find Here

### Implemented Features ✅

- **WebSocket Real-Time Chat** - Instant messaging via `/ws/{room}/{username}`
- **Auto-Room Management** - Rooms created/deleted automatically
- **Multi-Room Support** - Users can be in different rooms simultaneously
- **Join/Leave Notifications** - System messages when users connect/disconnect
- **REST API** - Get active rooms and user lists
- **Beautiful Web UI** - Responsive HTML5 client built-in
- **Pydantic Validation** - Type-safe message schemas
- **Production Ready** - Full error handling and async/await

### Files Overview

**main.py (492 lines)**
```python
# Contains:
- Pydantic models (Message, SystemMessage, RoomInfo, UserList)
- ConnectionManager class (core logic)
- FastAPI app setup
- WebSocket endpoint
- REST API endpoints
- HTML web client
```

**test_chat.py (360 lines)**
```python
# 9 tests covering:
- Basic connection
- Join notifications
- Message broadcasting
- Leave notifications
- Auto room deletion
- Get active rooms
- Get room users
- Room isolation
- Exclude sender option
```

**requirements.txt**
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
websockets==12.0
```

---

## 🔧 How to Use

### 1. Install and Run
```bash
pip install -r requirements.txt
python main.py
```

### 2. Access the Web Client
```
Open browser: http://localhost:8000
```

### 3. Test in Terminal
```bash
# Run unit tests
python test_chat.py

# Or test with curl
curl http://localhost:8000/rooms
```

### 4. API Examples

**Get Active Rooms:**
```bash
curl http://localhost:8000/rooms
# Returns: [{"room_name": "general", "user_count": 2}]
```

**Get Users in Room:**
```bash
curl http://localhost:8000/rooms/general/users
# Returns: {"room_name": "general", "users": ["alice", "bob"], "user_count": 2}
```

---

## 💡 Key Concepts

### ConnectionManager Class
Manages all WebSocket connections:
- `connect()` - Add user to room
- `disconnect()` - Remove user from room
- `broadcast_to_room()` - Send message to all in room
- `get_active_rooms()` - List all rooms
- `get_room_users()` - List room members

### Room Lifecycle
1. **Create** - Automatically when first user joins
2. **Active** - Users can send/receive messages
3. **Delete** - Automatically when last user leaves

### Message Flow
```
User A connects
  ↓
Broadcast "A joined" to all in room
  ↓
User A sends message
  ↓
Broadcast message to all in room
  ↓
User A disconnects
  ↓
Broadcast "A left" to all in room
  ↓
Delete room if empty
```

---

## 🧪 Test Results

All 9 tests passing ✅

```
Test 1: Basic Connection              ✅ PASSED
Test 2: Join Broadcast Notification   ✅ PASSED
Test 3: Message Broadcast             ✅ PASSED
Test 4: Leave Broadcast Notification  ✅ PASSED
Test 5: Automatic Room Deletion       ✅ PASSED
Test 6: Get Active Rooms              ✅ PASSED
Test 7: Get Room Users                ✅ PASSED
Test 8: Multiple Rooms Isolation      ✅ PASSED
Test 9: Exclude Sender Option         ✅ PASSED

Results: 9 passed, 0 failed
```

Run tests: `python test_chat.py`

---

## 📊 Project Statistics

- **Total Lines of Code**: 852
  - main.py: 492 lines
  - test_chat.py: 360 lines
- **API Endpoints**: 4 (1 WebSocket, 3 REST)
- **Pydantic Models**: 4
- **Unit Tests**: 9 (all passing)
- **Documentation Pages**: 4

---

## 🎓 What You'll Learn

By studying this project, you'll understand:

1. **FastAPI WebSocket** - Real-time communication
2. **Async/Await** - Python concurrent programming
3. **Pydantic** - Data validation and serialization
4. **Connection Management** - Handling multiple clients
5. **REST API Design** - Proper endpoint structure
6. **Testing** - Unit test patterns
7. **HTML5 + JavaScript** - Frontend integration
8. **Production Code** - Best practices

---

## 🚀 Next Steps

### To Get Started:
1. **Quick**: Read `QUICKSTART.txt`
2. **Detailed**: Read `README.md`
3. **Deep Dive**: Read `FEATURES.md` then review `main.py`

### To Run:
```bash
pip install -r requirements.txt
python main.py
# Open: http://localhost:8000
```

### To Test:
```bash
python test_chat.py
```

### To Deploy:
See "Deployment" section in `README.md`

---

## 🆘 Quick Troubleshooting

**Q: "Connection refused"**
A: Run `python main.py` first

**Q: "ModuleNotFoundError"**
A: Run `pip install -r requirements.txt`

**Q: Port 8000 in use**
A: Edit `main.py` line 492: `port=8001`

**Q: Can't see messages**
A: Ensure both users are in same room name

See `README.md` for more troubleshooting

---

## 📞 Support

- **Documentation**: See README.md
- **Examples**: See QUICKSTART.txt and FEATURES.md
- **Code**: See main.py with inline comments
- **Tests**: See test_chat.py for usage examples

---

**Ready to code?** Start with: `python main.py` 🚀

