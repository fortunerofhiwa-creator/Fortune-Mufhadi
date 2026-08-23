#!/usr/bin/env python3
"""
File Transfer Client Application
Connects to a file transfer server and requests files.
"""

import socket
import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('client.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
BUFFER_SIZE = 4096
DOWNLOAD_DIR = './downloads'  # Directory to save downloaded files


class FileTransferClient:
    """
    A TCP client that connects to a file transfer server.
    Allows users to request and download files.
    """

    def __init__(self, host, port):
        """
        Initialize the client.
        
        Args:
            host (str): Server host address
            port (int): Server port number
        """
        self.host = host
        self.port = port
        self.client_socket = None
        self.connected = False

    def connect(self):
        """
        Connect to the file transfer server.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Create a TCP socket
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect to the server
            logger.info(f"Connecting to server at {self.host}:{self.port}...")
            self.client_socket.connect((self.host, self.port))
            self.connected = True

            logger.info("Successfully connected to server")
            return True

        except ConnectionRefusedError:
            logger.error(f"Connection refused. Is the server running at {self.host}:{self.port}?")
            return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False

    def request_file(self, filename):
        """
        Request a file from the server and save it locally.
        
        Args:
            filename (str): Name of the file to request
            
        Returns:
            bool: True if file downloaded successfully, False otherwise
        """
        if not self.connected:
            logger.error("Not connected to server")
            return False

        try:
            # Send file request to server
            logger.info(f"Requesting file: {filename}")
            self.client_socket.send(filename.encode('utf-8'))

            # Receive response from server
            response = self.client_socket.recv(BUFFER_SIZE).decode('utf-8')

            if response.startswith('ERROR'):
                logger.error(f"Server error: {response}")
                return False

            if not response.startswith('OK'):
                logger.error(f"Unexpected response: {response}")
                return False

            # Parse file size from response (format: "OK:size")
            try:
                file_size = int(response.split(':')[1])
            except (IndexError, ValueError):
                logger.error(f"Invalid response format: {response}")
                return False

            logger.info(f"File size: {file_size} bytes")

            # Receive and save file
            return self.receive_file(filename, file_size)

        except Exception as e:
            logger.error(f"Error requesting file: {e}")
            return False

    def receive_file(self, filename, file_size):
        """
        Receive file data from server and save it locally.
        
        Args:
            filename (str): Name of the file
            file_size (int): Size of the file in bytes
            
        Returns:
            bool: True if file received successfully, False otherwise
        """
        try:
            # Create download directory if it doesn't exist
            Path(DOWNLOAD_DIR).mkdir(exist_ok=True)

            # Create full file path
            file_path = os.path.join(DOWNLOAD_DIR, filename)

            # Receive file in chunks
            bytes_received = 0
            logger.info(f"Downloading to: {os.path.abspath(file_path)}")

            with open(file_path, 'wb') as f:
                while bytes_received < file_size:
                    # Calculate remaining bytes to receive
                    remaining = file_size - bytes_received
                    chunk_size = min(BUFFER_SIZE, remaining)

                    # Receive chunk
                    chunk = self.client_socket.recv(chunk_size)
                    if not chunk:
                        logger.error("Connection closed unexpectedly")
                        return False

                    f.write(chunk)
                    bytes_received += len(chunk)

                    # Progress indicator
                    progress = (bytes_received / file_size) * 100
                    logger.info(f"Progress: {progress:.1f}% ({bytes_received}/{file_size} bytes)")

            logger.info(f"File download completed: {filename} ({bytes_received} bytes)")
            return True

        except IOError as e:
            logger.error(f"Error saving file: {e}")
            return False
        except Exception as e:
            logger.error(f"Error receiving file: {e}")
            return False

    def disconnect(self):
        """
        Disconnect from the server.
        """
        if self.client_socket:
            self.client_socket.close()
            self.connected = False
            logger.info("Disconnected from server")

    def interactive_mode(self):
        """
        Run the client in interactive mode.
        """
        print("\n" + "="*50)
        print("File Transfer Client")
        print("="*50)
        print("Commands:")
        print("  download <filename>  - Download a file from server")
        print("  quit                 - Exit the client")
        print("="*50 + "\n")

        while self.connected:
            try:
                user_input = input("Enter command: ").strip()

                if not user_input:
                    continue

                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()

                if command == 'quit':
                    print("Exiting...")
                    break
                elif command == 'download':
                    if len(parts) < 2:
                        print("Usage: download <filename>")
                    else:
                        filename = parts[1]
                        self.request_file(filename)
                else:
                    print(f"Unknown command: {command}")

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                logger.error(f"Error: {e}")


def main():
    """
    Main entry point for the client.
    """
    if len(sys.argv) > 2:
        host = sys.argv[1]
        port = int(sys.argv[2])
    else:
        host = 'localhost'
        port = 5000

    logger.info(f"Starting client for server at {host}:{port}")

    # Create client and connect
    client = FileTransferClient(host, port)

    if client.connect():
        client.interactive_mode()
    else:
        logger.error("Failed to connect to server")
        sys.exit(1)

    # Cleanup
    client.disconnect()


if __name__ == '__main__':
    main()
