import socket
from _thread import *
from const import *
import random

server = "127.0.0.1" # adresse ip du serveur
port = 8921 # port d'écoute du serveur

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # on crée un socket pour le serveur (AF_INET = adresse ip, SOCK_STREAM = TCP)

try: # on essaie de lier le socket à l'adresse ip et au port
    s.bind((server, port))
except socket.error as e: # si on ne peut pas, on affiche l'erreur
    print(str(e))

players = [] # liste des joueurs connectés

    
s.listen(2) # on écoute les connexions entrantes (2 = nombre de connexions max)
print("Waiting for a connection, Server Started") # on affiche un message pour dire que le serveur est lancé

def read_pos(str):
    """
        Fonction qui prend une position sous forme de string et la transforme en tuple
        
        Args:
            str : position sous forme de string
            
        Returns:
            tuple : position sous forme de tuple
    """
    str = str.split(",") # on sépare la position en x et y (séparés par une virgule) et on met les deux dans une liste (ex: "100,200" -> ["100", "200"])
    return int(str[0]), int(str[1]) # on retourne un tuple avec les deux valeurs converties en int (ex: ["100", "200"] -> (100, 200))

def make_pos(tup):
    """
        Fonction qui prend une position sous forme de tuple et la transforme en string
        
        Args:
            tup : position sous forme de tuple
            
        Returns:
            str : position sous forme de string
    """
    return str(tup[0]) + "," + str(tup[1]) # on retourne un string avec les deux valeurs séparées par une virgule (ex: (100, 200) -> "100,200")

pos = [100, 1100] # position x initiale des joueurs
map = random.choice([0, 1, 2]) # on choisit une map aléatoire

game_started = False # booléen qui indique si la partie a commencé ou non

def player_id(socket):
    """
        Fonction qui prend un socket et retourne l'index du joueur correspondant dans la liste des joueurs
        
        Args:
            socket : socket du joueur
        
        Returns:
            int : index du joueur dans la liste des joueurs
    """
    return players.index(socket)

def broadcast(message, socket=None):
    """
        Fonction qui envoie un message à tous les clients connectés
        
        Args:
            message : message à envoyer
            socket : socket du joueur qui envoie le message (par défaut None)
    """
    for client_socket in players: # on parcourt tous les sockets des joueurs
        if socket is None or client_socket != socket: # si le socket est None ou si le socket est différent du socket du joueur qui envoie le message
            try: # on essaie d'envoyer le message
                client_socket.send(message) 
            except Exception as e: # si on ne peut pas, on affiche l'erreur
                print(f"Error broadcasting message: {e}")



def listen_to_clients(socket):
    """
        Fonction qui écoute les messages envoyés par les clients
        
        Args:
            socket : socket du joueur
    """
    global map, game_started # on utilise les variables globales map et game_started
    p1_done = False # booléen qui indique si le joueur 1 a reçu toutes les informations
    p2_done = False # booléen qui indique si le joueur 2 a reçu toutes les informations
    """
        Boucle infinie qui écoute les messages envoyés par les clients:
            - si les deux joueurs n'ont pas reçu toutes les informations:
                - si le joueur est le joueur 1 et que le joueur 1 n'a pas reçu toutes les informations:
                    - on envoie au joueur son numéro de joueur
                    - on envoie au joueur sa position
                - si le joueur est le joueur 2 et que le joueur 2 n'a pas reçu toutes les informations:
                    - on envoie au joueur son numéro de joueur
                    - on envoie au joueur sa position
                    - on envoie au joueur 1 la position du joueur 2
                    - on envoie au joueur 2 la position du joueur 1
            - si les deux joueurs ont reçu toutes les informations:
                - on reçoit les données du joueur
                - on envoie les données à tous les joueurs
    """
    while True: # boucle infinie
        if not p1_done and  not p2_done: # si les deux joueurs n'ont pas reçu toutes les informations
            if player_id(socket) == 0 and not p1_done: # si le joueur est le joueur 1 et que le joueur 1 n'a pas reçu toutes les informations
                socket.send("player : 1.".encode("utf-8")) # on envoie au joueur son numéro de joueur
                p1_pos = "pos : " + make_pos((pos[player_id(socket)], HEIGHT - 96 - TERRAIN_SIZES[map])) + "." # on crée un string avec la position du joueur
                socket.send(p1_pos.encode("utf-8")) # on envoie la position du joueur au joueur
                print("sent p1 his pos") # on affiche un message pour dire qu'on a envoyé la position du joueur au joueur
            else: # si le joueur est le joueur 2 et que le joueur 2 n'a pas reçu toutes les informations
                socket.send("player : 2 .".encode("utf-8")) # on envoie au joueur son numéro de joueur
                p2_pos = "pos : " + make_pos((pos[player_id(socket)], HEIGHT - 96 - TERRAIN_SIZES[map])) + "." # on crée un string avec la position du joueur
                socket.send(p2_pos.encode("utf-8")) # on envoie la position du joueur au joueur
                p1_pos = "last_pos : " + make_pos((pos[0], HEIGHT - 96 - TERRAIN_SIZES[map])) + "." # on crée un string avec la position du joueur 1
                print("will send the p1 pos to p2") # on affiche un message pour dire qu'on va envoyer la position du joueur 1 au joueur 2
                socket.send(p1_pos.encode("utf-8")) # on envoie la position du joueur 1 au joueur 2
                print("sent the p1 pos to p2") # on affiche un message pour dire qu'on a envoyé la position du joueur 1 au joueur 2
                p2_pos = "last_pos : " + make_pos((pos[player_id(socket)], HEIGHT - 96 - TERRAIN_SIZES[map])) + "." # on crée un string avec la position du joueur 2
                print("will send the p2 pos to p1") # on affiche un message pour dire qu'on va envoyer la position du joueur 2 au joueur 1
                players[0].send(p2_pos.encode("utf-8")) # on envoie la position du joueur 2 au joueur 1
                print("sent the p2 pos to p1") # on affiche un message pour dire qu'on a envoyé la position du joueur 2 au joueur 1

            message = socket.recv(4096).decode("utf-8").split(".")[0] # on reçoit le message du joueur et on le split pour ne garder que le message
            if message.strip() == "received": # si le message est "received"
                if player_id(socket) == 0: # si le joueur est le joueur 1
                    p1_done = True # on indique que le joueur 1 a reçu toutes les informations
                    print("received from 1") # on affiche un message pour dire qu'on a reçu du joueur 1
                else: # si le joueur est le joueur 2
                    p2_done = True # on indique que le joueur 2 a reçu toutes les informations
                    print("received from 2") # on affiche un message pour dire qu'on a reçu du joueur 2
        else: # si les deux joueurs ont reçu toutes les informations
            data = socket.recv(2048) # on reçoit les données du joueur
            broadcast(data, socket) # on envoie les données à tous les joueurs
            




while True:
    conn, addr = s.accept()
    players.append(conn)
    start_new_thread(listen_to_clients, (conn, addr))



