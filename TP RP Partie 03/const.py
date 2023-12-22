"""
    Ce fichier contient toutes les constantes du jeu
"""

from enum import Enum, auto


BG_COLOR = (255, 255, 255) # couleur du fond d'écran
WIDTH, HEIGHT = 1280, 720 # dimensions de la fenêtre
FPS = 60 # nombre d'images par seconde
PLAYER_VEL = 5 # vitesse du joueur

HEALTH_BAR_Y = 50 # position en y de la barre de vie


HOST, PORT = "127.0.0.1", 8921 # host = adresse IP du serveur, port = port d'écoute du serveur

"""
    On définit les tailles longueur et largeur des sprites (en pixels) pour chaque animation
"""
SPRITES_SIZES = {
    "attack"        : (64, 29),
    "crouch_idle"   : (48, 21),
    "crouch_walk"   : (48, 21),
    "death"         : (64, 29),
    "double_jump"   : (48, 32),
    "fall"          : (48, 33),
    "hit"           : (48, 29),
    "idle"          : (48, 30),
    "jump"          : (48, 35),
    "land"          : (48, 29),
    "roll"          : (48, 25),
    "run"           : (48, 31),
    "wall land"     : (48, 35),
    "wall slide"    : (48, 35)
}

"""
    On définit la durée de chaque animation (en nombre de frames)
"""
ANIM_DELAY = {
    "attack"        : 15,
    "crouch_idle"   : 10,
    "crouch_walk"   : 10,
    "death"         : 15,
    "double_jump"   : 6,
    "fall"          : 10,
    "hit"           : 20,
    "idle"          : 20,
    "jump"          : 30,
    "land"          : 10,
    "roll"          : 10,
    "run"           : 20,
    "wall land"     : 10,
    "wall slide"    : 10,
    "attack_cooldown" : 20
}

"""
    ATTENTION: les constantes suivantes sont calculées automatiquement à partir des constantes ci-dessus
    ATTACK_CD =  
                len(sprites["attack"]) // on prend le nombre de frames de l'animation
                * ANIM_DELAY["attack"] // on multiplie par le delay entre chaque frame
                * 2 // on multiplie par 2 car l'animation dure la moitié du temps et l'autre moitié est le cooldown
                cooldown implementé pour que le joueur ne puisse pas attaquer en boucle
    HIT_CD =
                ANIM_DELAY["hit"] // on prend le delay entre chaque frame
                * len(sprites["hit"]) // on multiplie par le nombre de frames de l'animation
    DEATH_CD =
                ANIM_DELAY["death"] // on prend le delay entre chaque frame
                * len(sprites["death"]) // on multiplie par le nombre de frames de l'animation
    TERRAIN_SIZES = 
                [64, 96, 60] // on prend les tailles des sprites
                // scale // on divise par le scale pour avoir les tailles en pixels
                scale implementé pour que les sprites soient plus grands
"""
ATTACK_CD = 157

HIT_CD = 80

DEATH_CD = 150

TERRAIN_SIZES = [64, 96, 60]


class Game_state(Enum):
    """
        On définit les différents états du jeu

        Main_menu = menu principal
        In_game = jeu en cours
        Pause = jeu en pause
        Game_over = jeu terminé
    """
    Main_menu = auto()
    In_game = auto()
    Pause = auto()
    Game_over = auto()

class Menu_state(Enum):
    """
        On définit les différents états du menu

        Main = menu principal
        Singleplayer = menu du mode solo
        Multiplayer = menu du mode multijoueur    
    """
    Main = auto()
    Singleplayer = auto()
    Multiplayer = auto()

class Config_state(Enum):
    """
        On définit les différents états de la configuration
        
        Character = menu de choix du personnage
        Map = menu de choix de la map
    """
    Character = auto()
    Map = auto()


class Multiplayer_state(Enum):
    """
        On définit les différents états du mode multijoueur

        Welcome = menu de bienvenue
        Map = menu de choix de la map
        Pos = menu de choix de la position
        InGame = jeu en cours    
    """
    Welcome = 0
    Map = 1
    Pos = 2
    InGame = 3