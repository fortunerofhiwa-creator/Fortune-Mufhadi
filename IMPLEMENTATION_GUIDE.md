# Implementation Guide - File Transfer Application

## Session Overview (300 minutes)

This guide breaks down the implementation into phases to complete within the 300-minute session.

## Phase 1: Setup & Environment (30 minutes)

### Step 1: Verify Python Installation
```bash
python3 --version  # Should be 3.6+
```

### Step 2: Create Project Structure
```bash
mkdir file-transfer-app
cd file-transfer-app
mkdir files downloads
```

### Step 3: Create Test Files
```bash
# Small text file
echo "Hello, World! This is test file 1." > files/test1.txt

# Another test file
echo "This file contains important data for testing." > files/test2.txt

# Medium file (1MB)
dd if=/dev/zero bs=1M count=1 2>/dev/null | tr '\0' 'a' > files/medium.txt

# Large file (10MB)
dd if=/dev/zero bs=1M count=10 2>/dev/null | tr '\0' 'b' > files/large.bin
```

### Step 4: Initialize Git
```bash
git init
git add .
git commit -m "Initial project setup"
```

## Phase 2: Server Implementation (90 minutes)

### Step 5: Create Basic Server Socket (20 min)

Create `server.py` with basic socket initialization:

```python
import socket

HOST = 'localhost'
PORT = 5000

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"Server listening on {HOST}:{PORT}")
    
    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr}")
    client_socket.close()
    server_socket.close()

if __name__ == '__main__':
    main()
```

### Step 6: Add File Request Handling (30 min)

Extend server to handle file requests:

```python
def handle_client(client_socket):
    filename = client_socket.recv(4096).decode('utf-8')
    print(f"File requested: {filename}")
    
    # Check if file exists
    file_path = f'files/{filename}'
    if not os.path.isfile(file_path):
        client_socket.send(b'ERROR: File not found')
        return
    
    # Get file size
    file_size = os.path.getsize(file_path)
    size_msg = f'OK:{file_size}'
    client_socket.send(size_msg.encode('utf-8'))
    
    # Send file
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            client_socket.sendall(chunk)
```

### Step 7: Add Multi-client Support with Threading (25 min)

Implement threading for multiple concurrent clients:

```python
import threading

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}")
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"New connection from {addr}")
        
        # Handle in separate thread
        thread = threading.Thread(
            target=handle_client,
            args=(client_socket, addr)
        )
        thread.daemon = True
        thread.start()
```

### Step 8: Add Logging (15 min)

Integrate logging for debugging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
```

## Phase 3: Client Implementation (90 minutes)

### Step 9: Create Basic Client Socket (20 min)

Create `client.py` with socket connection:

```python
import socket

HOST = 'localhost'
PORT = 5000

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print(f"Connected to {HOST}:{PORT}")
    
    client_socket.close()

if __name__ == '__main__':
    main()
```

### Step 10: Add File Request Logic (25 min)

```python
def request_file(client_socket, filename):
    # Send file request
    client_socket.send(filename.encode('utf-8'))
    
    # Receive response
    response = client_socket.recv(4096).decode('utf-8')
    
    if response.startswith('ERROR'):
        print(f"Error: {response}")
        return False
    
    # Parse file size
    file_size = int(response.split(':')[1])
    print(f"Receiving file: {file_size} bytes")
    
    return True
```

### Step 11: Add File Receive Logic (25 min)

```python
def receive_file(client_socket, filename, file_size):
    os.makedirs('downloads', exist_ok=True)
    file_path = f'downloads/{filename}'
    
    bytes_received = 0
    with open(file_path, 'wb') as f:
        while bytes_received < file_size:
            chunk = client_socket.recv(min(4096, file_size - bytes_received))
            if not chunk:
                print("Connection closed unexpectedly")
                return False
            
            f.write(chunk)
            bytes_received += len(chunk)
            
            # Progress
            progress = (bytes_received / file_size) * 100
            print(f"Progress: {progress:.1f}%")
    
    print(f"File saved to {file_path}")
    return True
```

### Step 12: Add Interactive Mode (20 min)

```python
def interactive_mode(client_socket):
    while True:
        cmd = input("Enter command (download/quit): ").strip()
        
        if cmd == 'quit':
            break
        elif cmd.startswith('download '):
            filename = cmd.split(' ', 1)[1]
            request_file(client_socket, filename)
```

## Phase 4: Testing (60 minutes)

### Step 13: Unit Testing (20 min)

Create `test_connection.py`:

```python
import socket
import time

def test_server_connection():
    """Test basic server connection"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('localhost', 5000))
        print("✓ Server connection successful")
        return True
    except:
        print("✗ Server connection failed")
        return False
    finally:
        s.close()

if __name__ == '__main__':
    test_server_connection()
```

### Step 14: Integration Testing (25 min)

**Test Case 1: Download small file**
```bash
# Terminal 1
python3 server.py

# Terminal 2
python3 client.py
# > download test1.txt
# Verify: ls -la downloads/test1.txt
```

**Test Case 2: Multiple downloads**
```
# > download test1.txt
# > download test2.txt
# > download medium.txt
```

**Test Case 3: Error handling**
```
# > download nonexistent.txt
# Should show: ERROR: File not found
```

**Test Case 4: Large file**
```
# > download large.bin
# Check download speed and integrity
```

### Step 15: Multi-client Testing (15 min)

```bash
# Terminal 1: Server
python3 server.py

# Terminal 2: Client 1
python3 client.py
# > download large.bin

# Terminal 3: Client 2 (while client 1 downloading)
python3 client.py
# > download test1.txt
# > download test2.txt
```

## Phase 5: Documentation & Cleanup (30 minutes)

### Step 16: Code Documentation

Add docstrings and comments:
- Class docstrings
- Method docstrings  
- Inline comments for complex logic

### Step 17: Create README

Include:
- Project overview
- Installation steps
- Usage examples
- Troubleshooting

### Step 18: Test Screenshots

Capture and document:
```bash
# Server startup
screenshot1.png

# Client connection
screenshot2.png

# File download
screenshot3.png

# Error handling
screenshot4.png
```

### Step 19: Final Testing

Run complete test suite:
```bash
# Clean start
rm -rf downloads/*.txt
rm -rf downloads/*.bin

# Run tests
python3 server.py &
sleep 1
python3 test_connection.py
# Manual tests...
kill %1
```

## Completion Checklist

- [ ] Server implementation complete
- [ ] Client implementation complete
- [ ] Multi-client support working
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] All test cases pass
- [ ] README documentation complete
- [ ] Code commented and documented
- [ ] No uncommitted changes
- [ ] Git history clean and organized

## Time Breakdown

| Phase | Time | Status |
|-------|------|--------|
| Setup | 30m | ⏱️ |
| Server | 90m | ⏱️ |
| Client | 90m | ⏱️ |
| Testing | 60m | ⏱️ |
| Docs | 30m | ⏱️ |
| **Total** | **300m** | |

## Additional Tips

1. **Test frequently** - Don't wait until the end
2. **Commit often** - Save progress with meaningful messages
3. **Read error logs** - server.log and client.log are your friends
4. **Start simple** - Get basic functionality working first
5. **Then enhance** - Add features once core works

## Quick Start (Fast Track)

If running behind:

1. Copy provided complete files (server.py, client.py)
2. Focus on testing phase
3. Document what you did
4. Complete README with explanations

## Need Help?

Common issues:

```
"Address already in use" → Change PORT or kill old process
"Connection refused" → Make sure server is running
"File not found" → Check files/ directory exists with test files
"Permission denied" → Run chmod +x *.py
```

Good luck! 🚀
