import socket
import threading

class ChatClient:
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def play_game(self):
        try:
            while True:
                message = input("Enter your choice (Rock, Paper, Scissors) or type 'quit' to exit: ")
                self.client_socket.send(message.encode('utf-8'))
                if message.lower() == 'quit':
                    break
        except Exception as e:
            print(f"Error playing the game: {e}")

    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                print(data)
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def start(self):
        try:
            self.client_socket.connect((self.HOST, self.PORT))

            # Ask the client to provide a name
            client_name = input("Enter your name: \n")
            self.client_socket.send(client_name.encode('utf-8'))

            print(f"Connected to the chat as {client_name}.\n")

            # Start the game thread
            game_thread = threading.Thread(target=self.play_game)
            game_thread.start()

            # Start the message receiving thread
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.start()

            # Wait for threads to finish
            game_thread.join()
            receive_thread.join()

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    chat_client = ChatClient('127.0.0.1', 9001)
    chat_client.start()
