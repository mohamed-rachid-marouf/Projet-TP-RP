import socket  # Importe le module socket pour gérer les connexions réseau
import threading  # Importe le module threading pour prendre en charge le multithreading

class RPSGameClient:
    def __init__(self, host, port):
        # Initialise la classe RPSGameClient avec l'hôte et le port spécifiés
        self.HOST = host  # Stocke l'adresse IP de l'hôte
        self.PORT = port  # Stocke le numéro de port du serveur
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Crée un socket pour le client en utilisant IPv4 et TCP


    def start(self):
        try:
            # Connexion au serveur à l'adresse et au port spécifiés
            self.client_socket.connect((self.HOST, self.PORT))

            # Saisie du nom du client
            client_name = input("Entrez votre nom :\n")
            self.client_socket.send(client_name.encode('utf-8'))

            print(f"Connecté au jeu en tant que {client_name}\n")  # Tapez 'ready' lorsque vous êtes prêt à jouer.

            # Démarrage des threads pour la réception et l'envoi des messages
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.start()

            send_thread = threading.Thread(target=self.send_messages)
            send_thread.start()

        except Exception as e:
            print(f"Erreur : {e}")

    def receive_messages(self):
        # Boucle pour recevoir les messages du serveur
        while True:
            try:
                # Reçoit les données du serveur (maximum 1024 octets) et les décode en UTF-8
                data = self.client_socket.recv(1024).decode('utf-8')

                # Vérifie si les données sont vides, ce qui pourrait signifier une déconnexion
                if not data:
                    break

                # Affiche le message reçu du serveur
                print(data)

            except Exception as e:
                # Gestion des erreurs en cas d'échec de la réception du message
                print(f"Erreur lors de la réception du message : {e}")
                break


    def send_messages(self):
        # Boucle pour envoyer les messages au serveur
        while True:
            try:
                # Saisie du message depuis l'utilisateur
                message = input("Entrez votre choix :\n")

                # Envoie du message encodé en UTF-8 au serveur
                self.client_socket.send(message.encode('utf-8'))

                # Vérifie si l'utilisateur a saisi 'exit' pour quitter la boucle
                if message.lower() == 'exit':
                    break
                # Vérifie si l'utilisateur a saisi 'ready' pour afficher un message spécifique
                elif message.lower() == 'ready':
                    print("En attente des autres joueurs...")

            except Exception as e:
                # Gestion des erreurs en cas d'échec de l'envoi du message
                print(f"Erreur lors de l'envoi du message : {e}")
                break


if __name__ == "__main__":
    # Création d'une instance de RPSGameClient et démarrage du client
    game_client = RPSGameClient('127.0.0.1', 9001)
    game_client.start()
