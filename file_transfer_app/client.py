#!/usr/bin/env python3
"""
File Transfer Client Application
Description: A TCP-based client that connects to the server and downloads files
"""

import socket
import os
import sys
from pathlib import Path

# Configuration
SERVER_HOST = 'localhost'
SERVER_PORT = 5000
BUFFER_SIZE = 1024
CHUNK_SIZE = 4096

class FileTransferClient:
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.socket = None
        self.downloads_directory = os.path.join(os.path.dirname(__file__), 'downloaded_files')
        self._ensure_downloads_directory()
    
    def _ensure_downloads_directory(self):
        """Create downloaded_files directory if it doesn't exist"""
        if not os.path.exists(self.downloads_directory):
            os.makedirs(self.downloads_directory)
            print(f"[INFO] Created downloads directory: {self.downloads_directory}")
    
    def connect(self):
        """Connect to the server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"[CLIENT] Connected to {self.host}:{self.port}\n")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to connect to server: {e}")
            return False
    
    def request_file(self, filename):
        """Request a file from the server and save it locally"""
        try:
            # Send file request
            print(f"[REQUEST] Requesting file: {filename}")
            self.socket.send(filename.encode('utf-8'))
            
            # Receive response (file size or error)
            response = self.socket.recv(BUFFER_SIZE).decode('utf-8')
            
            # Check for error
            if response.startswith("ERROR"):
                print(f"[ERROR] Server response: {response}\n")
                return False
            
            # Parse file size
            try:
                status, file_size_str = response.split('|')
                file_size = int(file_size_str)
            except:
                print(f"[ERROR] Invalid server response: {response}\n")
                return False
            
            if status != "OK":
                print(f"[ERROR] Server error: {response}\n")
                return False
            
            # Receive and save file
            return self.receive_file(filename, file_size)
            
        except Exception as e:
            print(f"[ERROR] Request failed: {e}\n")
            return False
    
    def receive_file(self, filename, file_size):
        """Receive file from server and save it locally"""
        try:
            file_path = os.path.join(self.downloads_directory, filename)
            bytes_received = 0
            
            print(f"[DOWNLOAD] File size: {file_size} bytes")
            print(f"[DOWNLOAD] Saving to: {file_path}")
            
            with open(file_path, 'wb') as f:
                while bytes_received < file_size:
                    # Calculate remaining bytes
                    remaining = file_size - bytes_received
                    chunk_to_read = min(CHUNK_SIZE, remaining)
                    
                    # Receive chunk
                    chunk = self.socket.recv(chunk_to_read)
                    if not chunk:
                        print("\n[ERROR] Connection closed unexpectedly")
                        return False
                    
                    f.write(chunk)
                    bytes_received += len(chunk)
                    
                    # Show progress
                    progress = (bytes_received / file_size) * 100
                    print(f"[DOWNLOAD] Progress: {progress:.2f}% ({bytes_received}/{file_size} bytes)", end='\r')
            
            print(f"\n[SUCCESS] File downloaded successfully: {filename}\n")
            return True
            
        except Exception as e:
            print(f"\n[ERROR] File download failed: {e}\n")
            # Clean up partial file
            if os.path.exists(file_path):
                os.remove(file_path)
            return False
    
    def disconnect(self):
        """Disconnect from the server"""
        if self.socket:
            self.socket.close()
            print("[CLIENT] Disconnected from server\n")
    
    def interactive_mode(self):
        """Run client in interactive mode"""
        print("="*50)
        print("File Transfer Client - Interactive Mode")
        print("="*50)
        print("Commands:")
        print("  - Type filename to download")
        print("  - Type 'quit' to exit\n")
        
        while True:
            try:
                filename = input("Enter filename to download (or 'quit' to exit): ").strip()
                
                if filename.lower() == 'quit':
                    print("[INFO] Exiting...")
                    break
                
                if not filename:
                    print("[ERROR] Please enter a filename\n")
                    continue
                
                self.request_file(filename)
                
            except KeyboardInterrupt:
                print("\n[INFO] Interrupted by user")
                break
            except Exception as e:
                print(f"[ERROR] {e}\n")

def main():
    client = FileTransferClient()
    
    # Connect to server
    if not client.connect():
        sys.exit(1)
    
    # Run in interactive mode
    try:
        client.interactive_mode()
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
