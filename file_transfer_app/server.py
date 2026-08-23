#!/usr/bin/env python3
"""
File Transfer Server Application
Description: A TCP-based server that listens for client connections and transfers files
"""

import socket
import os
import sys
import threading
from pathlib import Path

# Configuration
SERVER_HOST = 'localhost'
SERVER_PORT = 5000
BUFFER_SIZE = 1024
CHUNK_SIZE = 4096

class FileTransferServer:
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.server_socket = None
        self.files_directory = os.path.join(os.path.dirname(__file__), 'server_files')
        self._ensure_files_directory()
        self.client_count = 0
        self.lock = threading.Lock()
        
    def _ensure_files_directory(self):
        """Create server_files directory if it doesn't exist"""
        if not os.path.exists(self.files_directory):
            os.makedirs(self.files_directory)
            print(f"[INFO] Created files directory: {self.files_directory}")
    
    def start(self):
        """Initialize and start the server"""
        try:
            # Create TCP socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind to port
            self.server_socket.bind((self.host, self.port))
            
            # Listen for connections
            self.server_socket.listen(5)
            print(f"[SERVER] Started on {self.host}:{self.port}")
            print(f"[SERVER] Serving files from: {self.files_directory}")
            print("[SERVER] Waiting for incoming connections...\n")
            
            # Accept connections
            while True:
                client_socket, client_address = self.server_socket.accept()
                with self.lock:
                    self.client_count += 1
                    client_id = self.client_count
                
                print(f"[CONNECTION] Client {client_id} connected from {client_address}")
                
                # Handle each client in a separate thread
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address, client_id)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except Exception as e:
            print(f"[ERROR] Server error: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
                print("[SERVER] Shutdown")
    
    def handle_client(self, client_socket, client_address, client_id):
        """Handle individual client requests"""
        try:
            while True:
                # Receive file request from client
                file_request = client_socket.recv(BUFFER_SIZE).decode('utf-8').strip()
                
                if not file_request:
                    print(f"[CLIENT {client_id}] Disconnected")
                    break
                
                print(f"[CLIENT {client_id}] Requested file: {file_request}")
                
                # Process the file request
                self.send_file(client_socket, file_request, client_id)
                
        except Exception as e:
            print(f"[CLIENT {client_id}] Error: {e}")
        finally:
            client_socket.close()
            print(f"[CLIENT {client_id}] Connection closed\n")
    
    def send_file(self, client_socket, filename, client_id):
        """Send requested file to client"""
        try:
            # Construct full file path
            file_path = os.path.join(self.files_directory, filename)
            
            # Security check: ensure file is within allowed directory
            if not os.path.abspath(file_path).startswith(os.path.abspath(self.files_directory)):
                error_msg = "ERROR: Access denied"
                client_socket.send(error_msg.encode('utf-8'))
                print(f"[CLIENT {client_id}] Access denied for: {filename}")
                return
            
            # Check if file exists
            if not os.path.isfile(file_path):
                error_msg = "ERROR: File not found"
                client_socket.send(error_msg.encode('utf-8'))
                print(f"[CLIENT {client_id}] File not found: {filename}")
                return
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Send file size
            size_message = f"OK|{file_size}"
            client_socket.send(size_message.encode('utf-8'))
            print(f"[CLIENT {client_id}] Sending file size: {file_size} bytes")
            
            # Send file in chunks
            bytes_sent = 0
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    client_socket.sendall(chunk)
                    bytes_sent += len(chunk)
                    # Show progress
                    progress = (bytes_sent / file_size) * 100
                    print(f"[CLIENT {client_id}] Progress: {progress:.2f}% ({bytes_sent}/{file_size} bytes)", end='\r')
            
            print(f"[CLIENT {client_id}] File transfer completed: {filename} ({file_size} bytes)\n")
            
        except Exception as e:
            print(f"[CLIENT {client_id}] Error sending file: {e}")
            try:
                error_msg = f"ERROR: {str(e)}"
                client_socket.send(error_msg.encode('utf-8'))
            except:
                pass

if __name__ == "__main__":
    server = FileTransferServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
        sys.exit(0)
