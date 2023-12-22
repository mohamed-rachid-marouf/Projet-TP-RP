"""
 main_s = game online
 """

from os import listdir
from os.path import isfile, join
import pickle
import pygame
from const import *
import socket
from _thread import *

pygame.init() # On initialise pygame

pygame.display.set_caption("VS") # On définit le titre de la fenêtre

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # On crée le socket client


selected_world = -1 # On définit la map sélectionnée

window = pygame.display.set_mode((WIDTH, HEIGHT)) # On crée la fenêtre

font = pygame.font.SysFont("arialblack", 40) # On définit la police d'écriture

"""
    On définit les chemins vers les sprites des cartes
"""
maps = [pygame.image.load("PART 3/assets/maps/plain.png"), pygame.image.load("PART 3/assets/maps/oak_wood.png"), pygame.image.load("PART 3/assets/maps/stringstar.png")]



player_1 = None # On définit le joueur 1
player_2 = None # On définit le joueur 2

controls_to_send = None # On définit les contrôles à envoyer
controls_received = None # On définit les contrôles reçus



game_started = False # On définit le flag de début de jeu

whoami = 0 # On définit le numéro du joueur

def draw_text(text, font, text_col, x ,y):
    """
        Fonction qui affiche du texte

        Args:
            text (str): texte à afficher
            font (pygame.font.Font): police d'écriture
            text_col (tuple): couleur du texte
            x (int): position x du texte
            y (int): position y du texte
    """
    img = font.render(text, True, text_col) # On crée l'image du texte
    window.blit(img, (x, y)) # On affiche l'image du texte


config_state = Config_state.Map # On définit l'état de la configuration
global_state = Game_state.Main_menu # On définit l'état du jeu
menu_state = Menu_state.Main # On définit l'état du menu
m_state = None # On définit l'état du mode multijoueur
is_connected = False # On définit le flag de connexion



class HealthBar:
    """
        Classe qui définit la barre de vie
    """
    def __init__(self, x, player):
        """
            Constructeur de la classe

            Args:
                x (int): position x de la barre de vie
                player (Player): joueur associé à la barre de vie
        """
        self.player = player
        self.x = x
        self.y = HEALTH_BAR_Y

    def draw(self):
        """
            Fonction qui dessine la barre de vie
        """
        ratio = self.player.health / 100 # On calcule le ratio de vie
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y, 250, 30)) # On dessine le contour de la barre de vie
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y, 250 * ratio, 30)) # On dessine la barre de vie

def read_pos(str):
    """
        Fonction qui lit la position
    """
    str = str.split(",") # On sépare la position en x et y
    return int(str[0]), int(str[1]) # On retourne la position

class Button:
    """
        Classe qui définit un bouton    
    """
    def __init__(self, text, x, y, color):
        """
            Constructeur de la classe

            Args:
                text (str): texte du bouton
                x (int): position x du bouton
                y (int): position y du bouton
                color (tuple): couleur du bouton
        """
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.width = 200
        self.height = 100

    def draw(self, win):
        """
            Fonction qui dessine le bouton
            
            Args:
                win (pygame.Surface): fenêtre sur laquelle dessiner le bouton
        """
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height)) # On dessine le bouton
        font = pygame.font.SysFont("comicsans", 40) # On définit la police d'écriture
        text = font.render(self.text, 1, (255,255,255)) # On crée l'image du texte
        win.blit(text, (self.x + round(self.width/2) - round(text.get_width()/2), self.y + round(self.height/2) - round(text.get_height()/2))) # On affiche le texte

    def click(self, pos):
        """
            Fonction qui vérifie si le bouton a été cliqué
        
            Args:
                pos (tuple): position du clic

            Returns:
                bool: True si le bouton a été cliqué, False sinon
        """
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False



def flip(sprites):
    """
        Fonction qui retourne les sprites inversés horizontalement
        
        Args:
            sprites (list): liste des sprites à inverser
            
        Returns:
            list: liste des sprites inversés
    """
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, sprite_sizes, scale_factor=3, direction=True):
    """
        Fonction qui charge les sprites depuis un dossier et les redimensionne selon un facteur d'échelle et une direction donnée (gauche ou droite) 
        
        Args:
            dir1 (str): nom du dossier contenant les sprites
            sprite_sizes (dict): dictionnaire contenant les tailles des sprites
            scale_factor (int): facteur d'échelle
            direction (bool): direction des sprites (True = droite, False = gauche)
            
        Returns:
            dict: dictionnaire contenant les sprites
    """
    path = join("PART 3/assets", dir1) # On définit le chemin vers le dossier contenant les sprites
    images = [f for f in listdir(path) if isfile(join(path, f))] # On récupère les noms des fichiers contenus dans le dossier
    
    all_sprites = {} # On définit le dictionnaire contenant les sprites

    for image in images: # On parcourt les images
        sprite_sheets = pygame.image.load(join(path, image)).convert_alpha() # On charge l'image
        img_name = image.replace(".png", "") # On récupère le nom de l'image

        sprites = [] # On définit la liste des sprites
        for i in range(sprite_sheets.get_width() // sprite_sizes[img_name][0]): # On parcourt les sprites de l'image
            surface = pygame.Surface(sprite_sizes[img_name], pygame.SRCALPHA, 32) # On crée une surface
            rect = pygame.Rect(i * sprite_sizes[img_name][0], 0, sprite_sizes[img_name][0], sprite_sizes[img_name][1]) # On définit le rectangle
            surface.blit(sprite_sheets, (0, 0), rect) # On dessine le sprite sur la surface
            scaled_surface = pygame.transform.scale(surface, (sprite_sizes[img_name][0] * scale_factor, sprite_sizes[img_name][1] * scale_factor)) # On redimensionne la surface
            sprites.append(scaled_surface) # On ajoute le sprite à la liste des sprites
        
        if direction: # Si y'a une direction
            all_sprites[image.replace(".png", "") + "_right"] = sprites # On ajoute les sprites à la liste des sprites orientés vers la droite
            all_sprites[image.replace(".png", "") + "_left"] = [pygame.transform.flip(sprite, True, False) for sprite in sprites] # On ajoute les sprites à la liste des sprites orientés vers la gauche
        else: # Sinon
            all_sprites[image.replace(".png", "")] = sprites # On ajoute les sprites à la liste des sprites sans direction

    return all_sprites # On retourne le dictionnaire contenant les sprites



class Player(pygame.sprite.Sprite):
    """
        Classe qui définit le joueur
    """
    COLOR = (255, 0, 0)
    PLAYER_VEL = 5
    GRAVITY = 1

    SPRITES = load_sprite_sheets("Player", SPRITES_SIZES)
    ANIMATION_DELAY = 10

    def __init__(self, x, y, width, height):
        """
            Constructeur de la classe

            Args:
                x (int): position x du joueur
                y (int): position y du joueur
                width (int): largeur du joueur
                height (int): hauteur du joueur
        """
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit_count = 0
        self.got_hit = False
        self.attacking = False
        self.attack_cooldown = 0
        self.health = 100
        self.alive = True
        self.death_anim = False

    def jump(self):
        """
            Fonction qui fait sauter le joueur
        """
        self.y_vel = -self.GRAVITY * 5 # la vitesse en y est négative donc le joueur monte
        self.animation_count = 0 # On réinitialise le compteur d'animation
        self.jump_count += 1 # On incrémente le compteur de saut
        if self.jump_count == 1: # Si le joueur a sauté une fois
            self.fall_count = 0 # On réinitialise le compteur de chute

    def move(self, dx, dy):
        """
            Fonction qui déplace le joueur
            
            Args:
                dx (int): déplacement en x
                dy (int): déplacement en y
        """
        self.rect.x += dx # On déplace le joueur en x
        self.rect.y += dy # On déplace le joueur en y

    def move_left(self, vel):
        """
            Fonction qui déplace le joueur vers la gauche
            
            Args:
                vel (int): vitesse du joueur
        """
        self.x_vel = -vel # On définit la vitesse en x du joueur comme étant négative (vers la gauche)
        if self.direction != "left": # Si le joueur ne regarde pas vers la gauche
            self.direction = 'left' # On définit la direction du joueur comme étant la gauche
            self.animation_count = 0 # On réinitialise le compteur d'animation

    def move_right(self, vel):
        """
            Fonction qui déplace le joueur vers la droite
        
            Args:
                vel (int): vitesse du joueur
        """
        self.x_vel = vel # On définit la vitesse en x du joueur comme étant positive (vers la droite)
        if self.direction != "right": # Si le joueur ne regarde pas vers la droite
            self.direction = 'right' # On définit la direction du joueur comme étant la droite
            self.animation_count = 0 # On réinitialise le compteur d'animation

    def loop(self, fps):
        """
            Fonction qui boucle le joueur
            
            Args:
                fps (int): nombre d'images par seconde
        """
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY) # On définit la vitesse en y du joueur
        self.move(self.x_vel, self.y_vel) # On déplace le joueur

        self.fall_count += 1 # On incrémente le compteur de chute
        self.update() # On met à jour le joueur

    def update(self):
        """
            Fonction qui met à jour le joueur
        """
        sprite_sheet = "death" # On définit l'animation par defaut comme étant la mort
        if self.alive: # Si le joueur est vivant
            sprite_sheet = "idle" # On définit l'animation comme étant l'attente
            if self.y_vel < 0: # Si la vitesse en y du joueur est négative
                if self.jump_count == 1: # Si le joueur a sauté une fois
                    sprite_sheet = "jump" # On définit l'animation comme étant le saut
                elif self.jump_count == 2: # Si le joueur a sauté deux fois
                    sprite_sheet = "double_jump" # On définit l'animation comme étant le double saut
            elif self.y_vel >  self.GRAVITY * 2: # Si la vitesse en y du joueur est positive
                sprite_sheet = "fall" # On définit l'animation comme étant la chute
            elif self.x_vel != 0: # Si la vitesse en x du joueur est différente de 0
                sprite_sheet = "run" # On définit l'animation comme étant la course

            if self.attack_cooldown > 0: # Si le cooldown d'attaque est supérieur à 0
                if self.attack_cooldown > ANIM_DELAY["attack"] * 7: # Si le cooldown d'attaque est supérieur à 7 fois le delay de l'animation d'attaque
                    sprite_sheet = "attack" # On définit l'animation comme étant l'attaque
                self.attack_cooldown -= 1 # On décrémente le cooldown d'attaque
            else: # Sinon
                self.attacking = False # On définit le joueur comme n'attaquant pas

            if self.hit_count > 0: # Si le cooldown de hit est supérieur à 0
                sprite_sheet = "hit" # On définit l'animation comme étant le hit
                self.hit_count -= 1 # On décrémente le cooldown de hit

            self.reduce_health() # On réduit la vie du joueur
        
        else: # Sinon
            if not self.death_anim: # Si l'animation de mort n'est pas en cours
                self.death_anim = True # On définit l'animation de mort comme étant en cours
                self.animation_count = 0 # On réinitialise le compteur d'animation

        sprite_sheet_name = sprite_sheet + "_" + self.direction # On définit le nom de la feuille de sprite
        sprites = self.SPRITES[sprite_sheet_name] # On récupère les sprites de la feuille de sprite
        if sprite_sheet == "death" and (self.animation_count // ANIM_DELAY[sprite_sheet]) >= len(sprites): # Si l'animation est celle de la mort et qu'on est sur la dernière frame de l'animation
            sprite_index = len(sprites) - 1  # On définit l'index du sprite comme étant le dernier sprite de l'animation
        else: # Sinon
            sprite_index = (self.animation_count // ANIM_DELAY[sprite_sheet]) % len(sprites) # On définit l'index du sprite comme étant le sprite courant de l'animation
            self.animation_count += 1  # On incrémente le compteur d'animation
        self.sprite = sprites[sprite_index] # On définit le sprite comme étant le sprite courant de l'animation
        self.update_mask() # On met à jour le masque

    
    def update_mask(self):
        """
            Fonction qui met à jour le masque
        """
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y)) # On définit le rectangle du joueur
        self.mask = pygame.mask.from_surface(self.sprite) # On définit le masque du joueur

    def draw(self, win):
        """
            Fonction qui dessine le joueur
            
            Args:
                win (pygame.Surface): fenêtre sur laquelle dessiner le joueur
        """
        win.blit(self.sprite, (self.rect.x, self.rect.y)) # On affiche le sprite du joueur

    def attack(self):
        """
            Fonction qui fait attaquer le joueur    
        """
        self.attack_cooldown = ATTACK_CD # On définit le cooldown d'attaque

    def landed(self):
        """
            Fonction qui simule l'atterrissage du joueur
        """
        self.fall_count = 0 # On réinitialise le compteur de chute
        self.y_vel = 0 # On définit la vitesse en y du joueur comme étant nulle
        self.jump_count = 0 # On réinitialise le compteur de saut

    def hit_head(self):
        """
            Fonction qui simule le fait que le joueur ait touché un plafond
        """
        self.count = 0 # On réinitialise le compteur de chute
        self.y_vel *= -1 # On inverse la vitesse en y du joueur (il tombe)

    def reduce_health(self, damage=10):
        """
            Fonction qui réduit la vie du joueur
            
            Args:
                damage (int): dégâts infligés au joueur (10 par défaut)
        """
        if self.got_hit and self.alive: # Si le joueur a été touché et qu'il est vivant
            self.health -= damage # On réduit la vie du joueur
            self.hit_count = 80 # On définit le cooldown de hit du joueur (pour qu'il ne puisse pas être touché en boucle)
            self.animation_count = 0 # On réinitialise le compteur d'animation
            
            self.got_hit = False # On définit le joueur comme n'etant plus touché
            print("health reduced, health now is :", self.health) 
            if self.health <= 0: # Si la vie du joueur est inférieure ou égale à 0
                self.alive = False # On définit le joueur comme étant mort
        

    def handle_vertical_collision(self, objects):
        """
            Fonction qui gère les collisions verticales
            
            Args:
                objects (list): liste des objets avec lesquels le joueur peut entrer en collision

            Returns:
                list: liste des objets avec lesquels le joueur est entré en collision
        """
        if self.y_vel < 0: # Si la vitesse en y du joueur est négative
            return None # On retourne None
        collided_objects = [] # On définit la liste des objets avec lesquels le joueur est entré en collision
        for object in objects: # On parcourt les objets
            if pygame.sprite.collide_mask(self, object): # Si le joueur est entré en collision avec l'objet
                if self.y_vel > 0: # Si la vitesse en y du joueur est positive
                    self.rect.bottom = object.rect.top # On définit le bas du joueur comme étant le haut de l'objet
                    self.landed() # On simule l'atterrissage du joueur

                elif self.y_vel < 0: # Si la vitesse en y du joueur est négative
                    self.rect.top = object.rect.bottom # On définit le haut du joueur comme étant le bas de l'objet
                    self.hit_head() # On simule le fait que le joueur ait touché un plafond

                collided_objects.append(object) # On ajoute l'objet à la liste des objets avec lesquels le joueur est entré en collision
        return collided_objects
    
    def collide(self, objects, dx):
        """
            Fonction qui gère les collisions
            
            Args:
                objects (list): liste des objets avec lesquels le joueur peut entrer en collision
                dx (int): déplacement en x
                
            Returns:
                Object: objet avec lequel le joueur est entré en collision
        """
        self.move(dx, 0) # On déplace le joueur en x de dx pour predire si il va entrer en collision avec un objet
        self.update() # On met à jour le joueur (pour mettre à jour le masque)
        collided_object = None # On définit l'objet avec lequel le joueur est entré en collision comme étant None
        for object in objects: # On parcourt les objets
            if pygame.sprite.collide_mask(self, object): # Si le joueur est entré en collision avec l'objet
                if isinstance(object, Player): # Si l'objet est un joueur
                    if self.attacking == True: # Si le joueur attaque
                        if not object.hit_count > 0: # Si le cooldown de hit de l'objet est inférieur ou égal à 0
                            object.got_hit = True # On définit l'objet comme étant touché
                collided_object = object # On définit l'objet avec lequel le joueur est entré en collision comme étant l'objet actuel
                break
        self.move(-dx, 0) # On déplace le joueur en x de -dx pour revenir à sa position initiale
        self.update() # On met à jour le joueur (pour mettre à jour le masque)
        return collided_object


    def listen_online(self, objects, has_controls):
        """
            Fonction qui gère les contrôles du joueur et les collisions en ligne
            
            Args:
                objects (list): liste des objets avec lesquels le joueur peut entrer en collision
                has_controls (bool): True si le joueur a les contrôles, False sinon
        """
        global controls_received, controls_to_send, can_send_moves # On récupère les contrôles reçus, les contrôles à envoyer et le flag de possibilité d'envoyer les contrôles
    
        collide_left = self.collide(objects, -PLAYER_VEL * 2) # On vérifie si le joueur est entré en collision avec un objet à sa gauche
        collide_right = self.collide(objects, PLAYER_VEL * 2) # On vérifie si le joueur est entré en collision avec un objet à sa droite
        
        
        if has_controls: # Si le joueur a les contrôles
            controls_to_send = pygame.key.get_pressed() # On récupère les contrôles du joueur
            if controls_to_send[pygame.K_LEFT] and not collide_left: # Si le joueur appuie sur la touche gauche et qu'il n'est pas entré en collision avec un objet à sa gauche
                self.move_left(self.PLAYER_VEL) # On déplace le joueur vers la gauche
            elif controls_to_send[pygame.K_RIGHT] and not collide_right: # Si le joueur appuie sur la touche droite et qu'il n'est pas entré en collision avec un objet à sa droite
                self.move_right(self.PLAYER_VEL) # On déplace le joueur vers la droite
            elif controls_to_send[pygame.K_UP]: # Si le joueur appuie sur la touche haut
                if not self.attacking: # Si le joueur n'attaque pas
                    self.attacking = True # On définit le joueur comme étant en train d'attaquer
                    self.animation_count = 0 # On réinitialise le compteur d'animation
                    self.attack() # On fait attaquer le joueur
            else: # Sinon
                self.x_vel = 0 # On définit la vitesse en x du joueur comme étant nulle
            
        else: # Sinon (si le joueur n'a pas les contrôles)
            if controls_received is not None: # Si des contrôles ont été reçus
                if controls_received[pygame.K_LEFT] and not collide_left: # Si le joueur appuie sur la touche gauche et qu'il n'est pas entré en collision avec un objet à sa gauche
                    self.move_left(self.PLAYER_VEL) # On déplace le joueur vers la gauche
                elif controls_received[pygame.K_RIGHT] and not collide_right: # Si le joueur appuie sur la touche droite et qu'il n'est pas entré en collision avec un objet à sa droite
                    self.move_right(self.PLAYER_VEL) # On déplace le joueur vers la droite
                elif controls_received[pygame.K_UP]: # Si le joueur appuie sur la touche haut
                    if not self.attacking: # Si le joueur n'attaque pas
                        self.attacking = True # On définit le joueur comme étant en train d'attaquer
                        self.animation_count = 0 # On réinitialise le compteur d'animation
                        self.attack() # On fait attaquer le joueur
                else: # Sinon
                    self.x_vel = 0 # On définit la vitesse en x du joueur comme étant nulle
                
        self.handle_vertical_collision([object for object in objects if not isinstance(object, Player)]) # On gère les collisions verticales


def game_online(p1, p2):
    """
        Fonction qui gère le jeu en ligne
        
        Args:
            p1 (Player): joueur 1
            p2 (Player): joueur 2
    """
    terrain = Block(0, HEIGHT - TERRAIN_SIZES[selected_world], "terrain", TERRAIN_SIZES[selected_world]) # On définit le terrain
    window.blit(pygame.transform.scale_by(maps[selected_world], 4), (0, 0)) # On affiche la map
    hp_1 = HealthBar(50, p1) # On définit la barre de vie du joueur 1
    hp_2 = HealthBar(900, p2) # On définit la barre de vie du joueur 2

    p1.loop(FPS) # On boucle le joueur 1
    p1.draw(window) # On affiche le joueur 1
    p2.loop(FPS) # On boucle le joueur 2
    p2.draw(window) # On affiche le joueur 2
    
    if whoami == 1: # Si le joueur est le joueur 1
        p1.listen_online([terrain, p2], True) # On gère les contrôles du joueur 1 (qui a les contrôles)
        p2.listen_online([terrain, p1], False) # On gère les contrôles du joueur 2 (qui n'a pas les contrôles)
    else: # Sinon (si le joueur est le joueur 2)
        p2.listen_online([terrain, p1], True) # On gère les contrôles du joueur 2 (qui a les contrôles)
        p1.listen_online([terrain, p2], False) # On gère les contrôles du joueur 1 (qui n'a pas les contrôles)
    
    hp_1.draw() # On affiche la barre de vie du joueur 1
    hp_2.draw() # On affiche la barre de vie du joueur 2
class Object(pygame.sprite.Sprite):
    """
        Classe qui définit un objet
    """
    def __init__(self, x, y, width, height, name=""):
        """
            Constructeur de la classe

            Args:
                x (int): position x de l'objet
                y (int): position y de l'objet
                width (int): largeur de l'objet
                height (int): hauteur de l'objet
                name (str): nom de l'objet
        """
        super().__init__()
        self.name = name
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win):
        """
            Fonction qui dessine l'objet
            
            Args:
                win (pygame.Surface): fenêtre sur laquelle dessiner l'objet
        """
        win.blit(self.image, (self.rect.x, self.rect.y)) # On affiche l'image de l'objet


class Block(Object):
    """
        Classe qui définit un bloc (hérite de la classe Object)
    """
    def __init__(self, x, y, name, height, width=WIDTH):
        """
            Constructeur de la classe

            Args:
                x (int): position x du bloc
                y (int): position y du bloc
                name (str): nom du bloc
                height (int): hauteur du bloc
                width (int): largeur du bloc
        """
        super().__init__(x, y, width, height, name)
        """
            On définit le masque du bloc avec une surface transparente de la taille du bloc pour pouvoir gérer les collisions
        """
        self.image = pygame.Surface((width, height))  # On crée une surface
        self.image.fill((255, 255, 255))  # On remplit la surface avec du blanc
        self.image.set_alpha(0)  # On définit la transparence de la surface
        self.mask = pygame.mask.from_surface(self.image) # On définit le masque de l'objet



def listen_server(arg1, arg2):
    """
        Fonction qui écoute le serveur
        
        Args:
            arg1 (None): argument 1
            arg2 (None): argument 2
    """
    global game_started, whoami, player_1, player_2, controls_to_send, controls_received, can_send_moves # On récupère le flag de début de jeu, le numéro du joueur, le joueur 1, le joueur 2, les contrôles à envoyer, les contrôles reçus et le flag de possibilité d'envoyer les contrôles
    """
        Boucle infinie qui écoute le serveur :
        
        - Si le jeu n'a pas commencé :
            on reçoit le message du serveur et on le décode puis on le split pour récupérer le type de l'instruction
            - Si le message est de type player :
                on récupère le numéro du joueur
            - Si le message est de type pos :
                si le joueur est le joueur 1 :
                    on récupère la position du joueur 1
                    on définit le joueur 1
                    on affiche la position du joueur 1
                sinon :
                    on récupère la position du joueur 2
                    on définit le joueur 2
                    on affiche la position du joueur 2
            - Si le message est de type last_pos :
                si le joueur est le joueur 1 :
                    on récupère la position du joueur 2
                    on définit le joueur 2
                    on affiche la position du joueur 2
                sinon :
                    on affiche que le joueur est le joueur 2 et qu'il va recevoir la position du joueur 1
                    on récupère la position du joueur 1
                    on définit le joueur 1
                    on affiche la position du joueur 1
            si les deux joueurs sont définis :
                on affiche que le jeu va commencer
                on envoie un message au serveur pour lui dire qu'on a reçu les positions des joueurs
                on définit le flag de début de jeu comme étant True
        - Sinon (si le jeu a commencé) :
            on envoie les contrôles au serveur
            on reçoit les contrôles du serveur
            on charge les contrôles reçus        
    """
    while True: # Boucle infinie
        if not game_started: # Si le jeu n'a pas commencé
            message = client.recv(1024).decode("utf-8").split(".")[0] # On reçoit le message du serveur et on le décode puis on le split pour récupérer le type de l'instruction 
            if message.split(":")[0].strip().lower() == "player": # Si le message est de type player
                whoami = int(message.split(":")[1].strip()) # On récupère le numéro du joueur
            elif message.split(":")[0].strip().lower() == "pos": # Si le message est de type pos
                if whoami == 1: # Si le joueur est le joueur 1
                    pos = read_pos(message.split(":")[1].strip()) # On récupère la position du joueur 1
                    player_1 = Player(pos[0], pos[1], 96, 96) # On définit le joueur 1
                    print("you are player one and your pos are :", pos) # On affiche la position du joueur 1
                else: # Sinon (si le joueur est le joueur 2)
                    pos = read_pos(message.split(":")[1].strip()) # On récupère la position du joueur 2
                    player_2 = Player(pos[0], pos[1], 96, 96) # On définit le joueur 2 
                    print("you are player two and your pos are: ", pos) # On affiche la position du joueur 2
            elif message.split(":")[0].strip().lower() == "last_pos": # Si le message est de type last_pos
                if whoami == 1: # Si le joueur est le joueur 1
                    pos = read_pos(message.split(":")[1].strip()) # On récupère la position du joueur 2
                    player_2 = Player(pos[0], pos[1], 96, 96) # On définit le joueur 2
                    print("your ennemy (2) pos are: ", pos) # On affiche la position du joueur 2
                else: # Sinon (si le joueur est le joueur 2)
                    print("you are player 2 and you'll receive the pos of p1") # On affiche que le joueur est le joueur 2 et qu'il va recevoir la position du joueur 1
                    pos = read_pos(message.split(":")[1].strip()) # On récupère la position du joueur 1
                    player_1 = Player(pos[0], pos[1], 96, 96) # On définit le joueur 1
                    print("your ennemy (1) pos are: ", pos) # On affiche la position du joueur 1
            if player_1 != None and player_2 != None: # Si les deux joueurs sont définis
                print("game should start") # On affiche que le jeu va commencer
                client.send("received.".encode("utf-8")) # On envoie un message au serveur pour lui dire qu'on a reçu les positions des joueurs
                game_started = True # On définit le flag de début de jeu comme étant True
        else: # Sinon (si le jeu a commencé)
            client.send(pickle.dumps(controls_to_send)) # On envoie les contrôles au serveur
            controls = client.recv(4096) # On reçoit les contrôles du serveur
            controls_received = pickle.loads(controls) # On charge les contrôles reçus

def main(window):
    """
        Fonction principale
    """
    global global_state, menu_state, game_started, is_connected # On récupère l'état global, l'état du menu, le flag de début de jeu et le flag de connexion
    #players def for testing locally
    player = Player(100, 528 , 96, 96) # On définit le joueur 1 (local non en ligne)
    p2 = Player(250, HEIGHT - 96 - TERRAIN_SIZES[selected_world], 96, 96) # On définit le joueur 2 (local non en ligne)
    clock = pygame.time.Clock() # On définit l'horloge
    if not is_connected: # Si le client n'est pas encore connecté
        client.connect((HOST, PORT)) # On se connecte au serveur
        start_new_thread(listen_server, (None, None)) # On lance la fonction qui écoute le serveur
        is_connected = True # On définit le flag de connexion comme étant True

    run = True # On définit le flag de boucle principale comme étant True
    while run: # Boucle principale
        clock.tick(FPS) # On définit le nombre d'images par seconde
        window.fill(BG_COLOR) # On remplit la fenêtre avec la couleur de fond

        if game_started: # Si le jeu a commencé
            game_online(player_1, player_2) # On lance le jeu en ligne
                    
        
        for event in pygame.event.get(): # On parcourt les événements pygame
            if event.type == pygame.QUIT: # Si l'événement est de type QUIT
                run = False # On définit le flag de boucle principale comme étant False
                break

        pygame.display.update() # On met à jour l'affichage

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)