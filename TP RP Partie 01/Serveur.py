import socket      # socket: Fournit des classes pour la création et la gestion de sockets.
import threading   # threading: Utilisé pour gérer les connexions clientes de manière concurrente.

class ChatServer:
    # Le constructeur (__init__) : initialise les propriétés du serveur, telles que l'adresse (HOST),
    # le port (PORT), un dictionnaire (clients) pour stocker les sockets des clients avec leur nom,
    # et la socket du serveur (server_socket).
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        self.clients = {}  # Dictionnaire pour stocker les sockets des clients avec leur nom
        self.server_socket = None  # Socket du serveur

    # Les méthodes __enter__ et __exit__ : sont utilisées pour créer et fermer la socket du serveur
    def __enter__(self):
        # Création de la socket du serveur dans la méthode __enter__
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Fermeture de la socket du serveur dans la méthode __exit__
        self.server_socket.close()

    # La méthode start est responsable d'écouter les connexions entrantes,
    # d'accepter les clients, et de démarrer un thread pour chaque client
    # en appelant la méthode handle_client.
    def start(self):
        try:
            print("Le serveur écoute les connexions...\n")
            while True:
                client_socket, addr = self.server_socket.accept()

                # Demander au client de fournir un nom
                client_name = client_socket.recv(1024).decode('utf-8')
                print(f"Connexion établie depuis {addr} avec le nom {client_name}. \n")
                self.clients[client_name] = client_socket

                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_name))
                client_thread.start()
        except KeyboardInterrupt:
            print("Arrêt du serveur.")

    # La méthode broadcast : envoie un message à tous les clients sauf à l'expéditeur.
    def broadcast(self, message, sender_name):
        # Diffusion du message à tous les clients sauf à l'expéditeur
        for name, socket in self.clients.items():
            if name != sender_name:
                try:
                    socket.send(message.encode('utf-8'))
                except Exception as e:
                    print(f"Erreur lors de la diffusion du message : {e}")

    # Méthode handle_client :
    # - Elle est exécutée dans un thread distinct pour chaque client.
    # - Envoie un message de bienvenue au client.
    # - À l'intérieur d'une boucle infinie, elle reçoit les messages du client, les affiche sur le serveur,
    #   puis les diffuse à tous les autres clients en utilisant la méthode broadcast.
    # - Si une exception se produit, elle ferme la connexion avec le client, le supprime de la liste des clients,
    #   et affiche un message.
    def handle_client(self, client_socket, client_name):
        try:
            welcome_message = f"Bienvenue dans le chat, {client_name}! Tapez 'exit' si vous voulez quitter. \n"
            client_socket.send(welcome_message.encode('utf-8'))

            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                print(f"Reçu de {client_name}: {data}")
                self.broadcast(f"{client_name}: {data}", client_name)
        except Exception as e:
            print(f"Erreur lors de la gestion du client : {e}")
        finally:
            client_socket.close()
            del self.clients[client_name]
            print(f"Connexion avec {client_name} fermée.")

# - Crée une instance de ChatServer avec l'adresse IP 127.0.0.1 et le port 9001.
# - Utilise le gestionnaire de contexte with pour garantir que les ressources sont correctement libérées.
# - Appelle la méthode start pour commencer à écouter les connexions.
if __name__ == "__main__":
    with ChatServer('127.0.0.1', 9001) as chat_server:
        chat_server.start()