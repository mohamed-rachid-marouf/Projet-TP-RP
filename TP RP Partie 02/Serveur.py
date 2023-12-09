import socket
import threading

class ChatServer:
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        self.clients = {}
        self.server_socket = None

    def __enter__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.server_socket.close()

    def start(self):
        try:
            print("Server is listening for connections...\n")
            while True:
                client_socket, addr = self.server_socket.accept()

                # Ask the client to provide a name
                client_name = client_socket.recv(1024).decode('utf-8')
                print(f"Connection established from {addr} with the name {client_name}.\n")
                self.clients[client_name] = client_socket

                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_name))
                client_thread.start()
        except KeyboardInterrupt:
            print("Server is shutting down.")

    def broadcast(self, message, sender_name):
        for name, socket in self.clients.items():
            if name != sender_name:
                try:
                    socket.send(message.encode('utf-8'))
                except Exception as e:
                    print(f"Error broadcasting message: {e}")

    def handle_game(self, client_name):
        try:
            welcome_message = f"Welcome to the game, {client_name}! Please choose Rock, Paper, Scissors, or type 'quit' to exit the game.\n"
            self.clients[client_name].send(welcome_message.encode('utf-8'))

            choices = ["Rock", "Paper", "Scissors"]

            # Wait for both players to make a choice
            choices_made = {}
            while len(choices_made) < 2:
                data = self.clients[client_name].recv(1024).decode('utf-8')
                if data.lower() == 'quit':
                    break
                elif data in choices and client_name not in choices_made:
                    choices_made[client_name] = data
                    self.broadcast(f"{client_name} has chosen {data}", client_name)

            if len(choices_made) == 2:
                # Determine the winner
                player1, choice1 = choices_made.items()[0]
                player2, choice2 = choices_made.items()[1]
                result = self.determine_winner(choice1, choice2)
                self.broadcast(f"The result is: {result}", client_name)

        except Exception as e:
            print(f"Error handling game for {client_name}: {e}")

    def determine_winner(self, player1, player2):
        if player1 == player2:
            return "It's a tie!"
        elif (player1 == "Rock" and player2 == "Scissors") or \
             (player1 == "Paper" and player2 == "Rock") or \
             (player1 == "Scissors" and player2 == "Paper"):
            return f"{player1} wins!"
        else:
            return f"{player2} wins!"

    def handle_client(self, client_socket, client_name):
        try:
            self.handle_game(client_name)
        except Exception as e:
            print(f"Error handling client {client_name}: {e}")
        finally:
            client_socket.close()
            del self.clients[client_name]
            print(f"Connection with {client_name} closed.")

if __name__ == "__main__":
    with ChatServer('127.0.0.1', 9001) as chat_server:
        chat_server.start()
