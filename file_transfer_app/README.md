# File Transfer Application

## Program Description

This is a **TCP-based client-server file transfer application** built in Python. The application allows clients to connect to a server and download files reliably over a network.

### Key Features:
- **Multi-client support**: Server handles multiple clients simultaneously using threading
- **Reliable file transfer**: Uses TCP sockets for guaranteed delivery
- **Progress tracking**: Real-time progress display during file transfers
- **Error handling**: Comprehensive error handling for various failure scenarios
- **Security**: Prevents directory traversal attacks
- **User-friendly interface**: Interactive client interface

## Architecture

### Server-Side (`server.py`)
- Listens on `localhost:5000` (configurable)
- Accepts multiple client connections
- Handles file requests in separate threads
- Sends file size first, then transfers file in chunks
- Returns appropriate error messages for missing files

### Client-Side (`client.py`)
- Connects to server at `localhost:5000`
- Prompts user for filename
- Receives file size from server
- Downloads file in chunks
- Saves file locally in `downloaded_files/` directory
- Displays download progress

## Technical Specifications

- **Protocol**: TCP/IP
- **Buffer Size**: 1024 bytes
- **Chunk Size**: 4096 bytes (for file transfer)
- **Default Host**: localhost
- **Default Port**: 5000
- **Threading**: Multi-threaded server for concurrent client handling

## Installation & Setup

### Requirements
- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

### Directory Structure
```
file_transfer_app/
├── server.py                 # Server application
├── client.py                 # Client application
├── server_files/             # Directory containing files to share (auto-created)
├── downloaded_files/         # Directory for downloaded files (auto-created)
├── README.md                 # This file
├── DOCUMENTATION.md          # Detailed technical documentation
├── test_sample_files/        # Sample files for testing
│   ├── sample_text.txt
│   ├── sample_image.png
│   ├── sample_large.bin
│   └── sample_document.pdf
└── SCREENSHOTS.md            # Screenshots and sample outputs
```

## How to Run

### Step 1: Prepare Server Files
1. Place files you want to share in the `server_files/` directory
2. Or use the provided sample files from `test_sample_files/`

```bash
cp test_sample_files/* file_transfer_app/server_files/
```

### Step 2: Start the Server

```bash
python3 server.py
```

**Expected Output:**
```
[SERVER] Started on localhost:5000
[SERVER] Serving files from: /path/to/file_transfer_app/server_files
[SERVER] Waiting for incoming connections...
```

### Step 3: Run the Client (in another terminal)

```bash
python3 client.py
```

**Expected Output:**
```
[CLIENT] Connected to localhost:5000

==================================================
File Transfer Client - Interactive Mode
==================================================
Commands:
  - Type filename to download
  - Type 'quit' to exit

Enter filename to download (or 'quit' to exit): 
```

### Step 4: Download Files

When prompted, enter the filename you want to download:

```
Enter filename to download (or 'quit' to exit): sample_text.txt
[REQUEST] Requesting file: sample_text.txt
[DOWNLOAD] File size: 1024 bytes
[DOWNLOAD] Saving to: /path/to/downloaded_files/sample_text.txt
[DOWNLOAD] Progress: 100.00% (1024/1024 bytes)
[SUCCESS] File downloaded successfully: sample_text.txt
```

## Configuration

### Change Host/Port

Edit the configuration section in `server.py` and `client.py`:

```python
SERVER_HOST = 'localhost'    # Change to server IP
SERVER_PORT = 5000           # Change to desired port
```

## Error Handling

The application handles the following scenarios:

| Error | Handling |
|-------|----------|
| **File Not Found** | Server sends "ERROR: File not found" message |
| **Connection Issues** | Client displays error and suggests checking connection |
| **Partial Transfer** | Failed transfers are cleaned up automatically |
| **Directory Traversal** | Security check prevents access outside allowed directory |
| **Invalid Protocol** | Server validates all requests |

## Sample Outputs

### Successful Transfer
```
[CONNECTION] Client 1 connected from ('127.0.0.1', 54321)
[CLIENT 1] Requested file: sample_text.txt
[CLIENT 1] Sending file size: 1024 bytes
[CLIENT 1] Progress: 100.00% (1024/1024 bytes)
[CLIENT 1] File transfer completed: sample_text.txt (1024 bytes)
```

### File Not Found
```
[CONNECTION] Client 2 connected from ('127.0.0.1', 54322)
[CLIENT 2] Requested file: nonexistent.txt
[CLIENT 2] File not found: nonexistent.txt
[CLIENT 2] Connection closed
```

## Challenges Faced & Solutions

### Challenge 1: Handling Multiple Clients
**Problem**: Server needs to handle multiple clients simultaneously without blocking
**Solution**: Implemented multi-threading - each client runs in a separate thread

### Challenge 2: Reliable File Transfer
**Problem**: Large files may not transfer in one packet
**Solution**: Implemented chunked transfer with file size validation

### Challenge 3: Progress Tracking
**Problem**: Users want to see download progress
**Solution**: Track bytes received and calculate percentage progress

### Challenge 4: Security
**Problem**: Prevent clients from accessing files outside the allowed directory
**Solution**: Implemented path validation using `os.path.abspath()` checks

### Challenge 5: Connection Errors
**Problem**: Handle various network and I/O errors gracefully
**Solution**: Comprehensive try-except blocks with appropriate error messages

## Additional Features Implemented

1. **Multi-client Support** ✓
   - Server handles multiple concurrent clients using threading
   - Each client gets a unique ID for logging

2. **Progress Bar** ✓
   - Real-time progress display during file transfer
   - Shows percentage, bytes transferred, and total bytes

3. **Logging System** ✓
   - Comprehensive logging for all operations
   - Timestamps embedded in log messages
   - Both server and client provide detailed feedback

4. **Error Handling** ✓
   - File not found errors
   - Connection error handling
   - Graceful error recovery
   - Automatic cleanup of failed transfers

## Testing Recommendations

1. **Small Files**: Test with text files (few KB)
2. **Large Files**: Test with binary files (several MB)
3. **Multiple Clients**: Connect multiple clients simultaneously
4. **Non-existent Files**: Request files that don't exist
5. **Connection Issues**: Kill client while downloading
6. **Special Characters**: Use filenames with spaces and special characters

## Troubleshooting

### "Connection refused"
- Ensure server is running
- Check if port 5000 is available
- Try changing to a different port

### "File not found" when file exists
- Ensure file is in `server_files/` directory
- Check filename spelling and case sensitivity
- Verify file permissions

### Slow Transfer
- Check network conditions
- Try with smaller files first
- Monitor system resources

## License

This assignment was completed as part of a socket programming coursework.

## Author Notes

This implementation demonstrates:
- Proper TCP socket programming
- Multi-threading for concurrent connections
- File I/O operations
- Error handling and validation
- User interface design
- Network protocol implementation
