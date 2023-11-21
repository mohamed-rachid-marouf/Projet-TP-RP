import socket      #socket: Fournit des classes pour la création et la gestion de sockets.
import threading   #threading: Utilisé pour gérer les opérations d'envoi et de réception de messages de manière concurrente.

class ChatClient:
    # Le constructeur (__init__) : initialise les propriétés du client,
    # telles que l'adresse (HOST), le port (PORT), et la socket du client (client_socket).
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # La méthode start : est responsable de la connexion au serveur,
    # de l'envoi du nom d'utilisateur au serveur, et du démarrage
    # de deux threads distincts :
    #       - receive_thread: pour la réception continue des messages du serveur en appelant
    #         la méthode receive_messages.
    #       - send_thread: pour l'envoi continu des messages au serveur en appelant
    #         la méthode send_messages.
    # Les threads permettent au client d'envoyer et de recevoir des messages simultanément.
    def start(self):
        try:
            # Connexion au serveur
            self.client_socket.connect((self.HOST, self.PORT))

            # Demander au client de fournir un nom
            client_name = input("Entrez votre nom : \n")
            self.client_socket.send(client_name.encode('utf-8'))

            print(f"Connecté au chat en tant que {client_name}. \n")

            # Démarrage du thread pour la réception des messages du serveur
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.start()

            # Démarrage du thread pour l'envoi des messages au serveur
            send_thread = threading.Thread(target=self.send_messages)
            send_thread.start()

        except Exception as e:
            print(f"Erreur : {e}")

    # Méthode receive_messages :
    # - Elle tourne dans une boucle infinie et reçoit continuellement les messages du serveur.
    # - En cas d'erreur lors de la réception, elle affiche un message d'erreur et termine la boucle.
    def receive_messages(self):
        # Boucle pour la réception continue des messages du serveur
        while True:
            try:
                # Réception des données du serveur
                data = self.client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                # Affichage du message reçu
                print(data)
            except Exception as e:
                print(f"Erreur lors de la réception du message : {e}")
                break
    
    # Méthode send_messages :     
    # - Elle tourne également dans une boucle infinie, permettant 
    #   à l'utilisateur de saisir des messages continuellement.
    # - Les messages sont envoyés au serveur, et si l'utilisateur saisit 'exit', 
    #   la boucle est interrompue, ce qui conduit à la fermeture du thread.
    def send_messages(self):
        # Boucle pour l'envoi continu des messages au serveur
        while True:
            # Saisie utilisateur pour un nouveau message
            message = input("Saisissez votre message : \n")
            # Envoi du message au serveur
            self.client_socket.send(message.encode('utf-8'))
            # Vérification de la condition de sortie
            if message.lower() == 'exit':
                break

# - Crée une instance du client avec l'adresse IP 127.0.0.1 et le port 9001.
# - Appelle la méthode start pour initier la connexion au serveur et démarrer les threads d'envoi et de réception de messages.
if __name__ == "__main__":
    # Création d'une instance du client et démarrage
    chat_client = ChatClient('127.0.0.1', 9001)
    chat_client.start()