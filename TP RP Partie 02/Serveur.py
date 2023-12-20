import socket  # Importe le module socket pour gérer les connexions réseau
import select  # Importe le module select pour la gestion des opérations d'I/O multiplexées
import threading  # Importe le module threading pour prendre en charge le multithreading

class RPSGameServer:
    def __init__(self, host, port):
        # Initialise la classe RPSGameServer avec l'hôte et le port spécifiés
        self.HOST = host  # Stocke l'adresse IP de l'hôte
        self.PORT = port  # Stocke le numéro de port du serveur
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Crée un socket pour le serveur en utilisant IPv4 et TCP
        self.connected_clients = {}  
        # Dictionnaire pour stocker les clients connectés (numéro du joueur, socket et nom du client)
        self.socket_list = [self.server_socket]  
        # Liste des sockets à surveiller (inclut le socket du serveur)

    def start(self):
        try:
            # Liaison du socket du serveur à l'adresse et au port spécifiés
            self.server_socket.bind((self.HOST, self.PORT))
            # Le serveur écoute les connexions entrantes avec une file d'attente de 2 clients
            self.server_socket.listen(2)
            print(f"Serveur en attente de connexions sur {self.HOST}:{self.PORT}")

            while True:
                # Utilisation de select pour surveiller les sockets prêts en lecture
                read_list, _, _ = select.select(self.socket_list, [], [])

                for sock in read_list:
                    if sock == self.server_socket:
                        # Nouvelle connexion entrante
                        client, address = self.server_socket.accept()
                        self.socket_list.append(client)

                        # Attribution d'un numéro au joueur et réception du nom du client
                        player_num = len(self.connected_clients) + 1
                        client_name = client.recv(1024).decode('utf-8')
                        self.connected_clients[player_num] = (client, client_name)

                        print(f"Joueur {player_num} connecté en tant que {client_name} depuis {address}\n")

                        # Démarrage du jeu lorsque deux joueurs sont connectés
                        if player_num == 1:
                            print("En attente du Joueur 2 pour se connecter...\n")
                        elif player_num == 2:
                            print("Les deux joueurs sont connectés. Démarrage du jeu...\n")
                            # Création d'un thread pour gérer le jeu avec les deux joueurs connectés
                            game_thread = threading.Thread(target=self.handle_game, args=(self.connected_clients[1], self.connected_clients[2]))
                            game_thread.start()

                    else:
                        pass  # Les actions pour les sockets clients sont gérées dans la méthode handle_game

        except Exception as e:
            print(f"Erreur : {e}")


    def send_to_player(self, player_num, message):
        # Envoie un message à un joueur spécifié
        player_socket, _ = self.connected_clients[player_num]  # Obtient le socket du joueur spécifié
        try:
            player_socket.send(message.encode("utf-8"))  # Envoie le message encodé en UTF-8 au joueur
        except Exception as e:
            # Gestion des erreurs en cas d'échec de l'envoi du message au joueur
            print(f"Erreur lors de l'envoi du message au Joueur {player_num}: {e}")


    def handle_game(self, player1, player2):
        # Initialisation des variables pour contrôler le déroulement du jeu
        continue_playing = True
        p1_pass, p2_pass = False, False
        choices = ["rock", "paper", "scissors"]

        while continue_playing:
            p1_pass, p2_pass = False, False

            # Envoi des instructions aux joueurs
            self.send_to_player(1, "Bienvenue dans le jeu Pierre-Papier-Ciseaux ! Entrez votre choix (rock, paper, scissors ou quit):")
            self.send_to_player(2, "En attente que le Joueur 1 fasse un choix...\n")

            # Attente du choix du Joueur 1
            while not p1_pass:
                choice_player1 = player1[0].recv(1024).decode("utf-8")
                if choice_player1.lower() in choices:
                    p1_pass = True
                elif choice_player1.lower().strip() == "quit":
                    break
                else:
                    self.send_to_player(1, "Choix invalide. Entrez votre choix (rock, paper, scissors ou quit):\n")

            # Envoi des instructions aux joueurs
            self.send_to_player(2, "Bienvenue dans le jeu Pierre-Papier-Ciseaux ! Entrez votre choix (rock, paper, scissors ou quit):")
            self.send_to_player(1, "En attente que le Joueur 2 fasse un choix...\n")

            # Attente du choix du Joueur 2
            while not p2_pass:
                choice_player2 = player2[0].recv(1024).decode("utf-8")
                if choice_player2.lower() in choices:
                    p2_pass = True
                elif choice_player2.lower().strip() == "quit":
                    break
                else:
                    self.send_to_player(2, "Choix invalide. Entrez votre choix (rock, paper, scissors ou quit):\n")

            # Vérification des choix et détermination du gagnant
            if "quit" in [choice_player1.lower(), choice_player2.lower()]:
                break

            self.send_to_player(1, f"Joueur 1 a choisi: {choice_player1}\n")
            self.send_to_player(2, f"Joueur 2 a choisi: {choice_player2}\n")

            if choice_player1.lower() == choice_player2.lower():
                # Les joueurs ont fait le même choix, c'est une égalité
                self.send_to_player(1, "C'est une égalité !")
                self.send_to_player(2, "C'est une égalité !")
            elif (choice_player1.lower() == "rock" and choice_player2.lower() == "scissors") or \
                (choice_player1.lower() == "paper" and choice_player2.lower() == "rock") or \
                (choice_player1.lower() == "scissors" and choice_player2.lower() == "paper"):
                # Joueur 1 gagne avec des combinaisons spécifiques de choix
                self.send_to_player(1, "Joueur 1 gagne !\n")
                self.send_to_player(2, "Joueur 1 gagne !\n")
            else:
                # Joueur 2 gagne
                self.send_to_player(1, "Joueur 2 gagne !\n")
                self.send_to_player(2, "Joueur 2 gagne !\n")

            # Demande aux joueurs s'ils veulent rejouer
            self.send_to_player(1, "Fin du jeu. Merci d'avoir joué ! (si vous voulez rejouer, entrez 'again')\n")
            self.send_to_player(2, "Fin du jeu. Merci d'avoir joué ! (si vous voulez rejouer, entrez 'again')\n")

            p1_again = player1[0].recv(1024).decode("utf-8")
            p2_again = player2[0].recv(1024).decode("utf-8")

            # Vérification si les deux joueurs veulent rejouer
            if p1_again.lower() == "again" and p2_again.lower() == "again":
                continue_playing = True
            else:
                continue_playing = False


if __name__ == "__main__":
    # Création d'une instance de RPSGameServer et démarrage du serveur
    game_server = RPSGameServer('127.0.0.1', 9001)
    game_server.start()
