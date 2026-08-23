#!/usr/bin/env python3
"""
File Transfer Server Application
Provides file transfer functionality to connected clients over TCP sockets.
"""

import socket
import os
import sys
import threading
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
HOST = 'localhost'
PORT = 5000
BUFFER_SIZE = 4096
FILE_DIR = './files'  # Directory containing files to serve


class FileTransferServer:
    """
    A TCP server that handles file transfer requests from clients.
    Supports multi-client connections using threading.
    """

    def __init__(self, host=HOST, port=PORT):
        """
        Initialize the server socket.
        
        Args:
            host (str): Server host address
            port (int): Server port number
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False

    def start(self):
        """
        Start the server and listen for incoming connections.
        """
        try:
            # Create a TCP socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind the socket to the port
            self.server_socket.bind((self.host, self.port))

            # Listen for incoming connections
            self.server_socket.listen(5)
            self.running = True

            logger.info(f"Server started on {self.host}:{self.port}")
            logger.info(f"Waiting for incoming connections...")
            logger.info(f"Serving files from: {os.path.abspath(FILE_DIR)}")

            # Accept client connections
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    logger.info(f"New connection from {client_address}")

                    # Handle client in a separate thread for multi-client support
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()

                except KeyboardInterrupt:
                    logger.info("Server interrupted by user")
                    self.running = False
                except Exception as e:
                    if self.running:
                        logger.error(f"Error accepting connection: {e}")

        except Exception as e:
            logger.error(f"Server startup error: {e}")
        finally:
            self.stop()

    def handle_client(self, client_socket, client_address):
        """
        Handle a client connection and process file requests.
        
        Args:
            client_socket (socket): Client socket connection
            client_address (tuple): Client address information
        """
        try:
            while True:
                # Receive file request from client
                file_request = client_socket.recv(BUFFER_SIZE).decode('utf-8').strip()

                if not file_request:
                    logger.info(f"Client {client_address} disconnected")
                    break

                logger.info(f"File request from {client_address}: {file_request}")

                # Process the file request
                self.send_file(client_socket, client_address, file_request)

        except Exception as e:
            logger.error(f"Error handling client {client_address}: {e}")
        finally:
            client_socket.close()
            logger.info(f"Connection closed with {client_address}")

    def send_file(self, client_socket, client_address, filename):
        """
        Send a file to the client in chunks.
        
        Args:
            client_socket (socket): Client socket connection
            client_address (tuple): Client address
            filename (str): Name of the file to send
        """
        try:
            # Construct the full file path
            file_path = os.path.join(FILE_DIR, filename)

            # Security: Prevent directory traversal attacks
            file_path = os.path.abspath(file_path)
            file_dir_abs = os.path.abspath(FILE_DIR)

            if not file_path.startswith(file_dir_abs):
                error_msg = "ERROR: Access denied"
                client_socket.send(error_msg.encode('utf-8'))
                logger.warning(f"Directory traversal attempt from {client_address}: {filename}")
                return

            # Check if file exists
            if not os.path.isfile(file_path):
                error_msg = "ERROR: File not found"
                client_socket.send(error_msg.encode('utf-8'))
                logger.warning(f"File not found: {filename} (from {client_address})")
                return

            # Get file size
            file_size = os.path.getsize(file_path)
            logger.info(f"Sending file: {filename} ({file_size} bytes) to {client_address}")

            # Send file size
            file_size_msg = f"OK:{file_size}"
            client_socket.send(file_size_msg.encode('utf-8'))

            # Send file in chunks
            bytes_sent = 0
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(BUFFER_SIZE)
                    if not chunk:
                        break
                    client_socket.sendall(chunk)
                    bytes_sent += len(chunk)

            logger.info(f"File transfer completed: {filename} ({bytes_sent} bytes) to {client_address}")

        except IOError as e:
            error_msg = f"ERROR: {str(e)}"
            try:
                client_socket.send(error_msg.encode('utf-8'))
            except:
                pass
            logger.error(f"IO Error while sending file {filename}: {e}")
        except Exception as e:
            logger.error(f"Error sending file to {client_address}: {e}")

    def stop(self):
        """
        Gracefully stop the server.
        """
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            logger.info("Server stopped")


def main():
    """
    Main entry point for the server.
    """
    # Create files directory if it doesn't exist
    Path(FILE_DIR).mkdir(exist_ok=True)

    # Create and start server
    server = FileTransferServer(HOST, PORT)
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        server.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
