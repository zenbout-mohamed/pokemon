# Initialisation de Pygame :
import pygame
from pygame.locals import *
#offre des fonctionnalités permettant de manipuler le temps, de mesurer le temps écoulé, de suspendre l'exécution d'un programme pendant un certain laps de temps
import time
#math offre un ensemble de fonctions mathématiques et constantes
import math
#offre des fonctionnalités liées à la génération de nombres aléatoires.
import random
#requests pour envoyer des requêtes HTTP, récupérer des données à partir d'URL, gérer les session
import requests
#fournit des classes et des fonctions pour effectuer des opérations d'entrée/sortie
import io
#tilisé pour effectuer des opérations liées aux URL, telles que l'ouverture et la lecture de fichiers à partir d'URL.
from urllib.request import urlopen

pygame.init()

# Définition des couleurs et de l'URL de base de l'API :
game_width = 500
game_height = 500
size = (game_width, game_height)
game = pygame.display.set_mode(size)
pygame.display.set_caption('Pokemon Battle')

# Définitions de couleurs :
black = (0, 0, 0)
gold = (218, 165, 32)
grey = (200, 200, 200)
green = (0, 200, 0)
red = (200, 0, 0)
white = (255, 255, 255)

# l'URL de base de l'API : cle pour recupurer les informations de pokemon
base_url = 'https://pokeapi.co/api/v2'
##cette partie du code est responsable de créer une instance de la classe Move en récupérant les informations d'un mouvement à partir d'une URL en utilisant l'API Pokémon. Les détails spécifiques sur le mouvement, tels que le nom, la puissance et le type, sont extraits de la réponse JSON et stockés comme attributs de l'instance de la classe Move.
# Classes pour les mouvements et les Pokémon : Deux classes sont définies :
# Cette classe Move représente les mouvements des Pokémon.
# Ces classes contiennent des informations telles que le nom, les statistiques et les mouvements des Pokémon.
class Move():
    # cette fonction est responsable de récupérer les informations sur un mouvement (move) à partir de l'API Pokémon.
    def __init__(self, url):
        req = requests.get(url)
        self.json = req.json()
        
        self.name = self.json['name']
        self.power = self.json['power']
        self.type = self.json['type']['name']
        
# Cette classe POKEMON représente les Pokémon eux-mêmes.
class Pokemon(pygame.sprite.Sprite):
    
    def __init__(self, name, level, x, y):
        
        pygame.sprite.Sprite.__init__(self)
        
        # appeler le point de terminaison de l'API Pokémon
        req = requests.get(f'{base_url}/pokemon/{name.lower()}')
        self.json = req.json()
        
        # définir le nom et le niveau du Pokémon
        self.name = name
        self.level = level
        
        # définir la position du sprite sur l'écran
        self.x = x
        self.y = y
        
        # nombre de potions restantes
        self.num_potions = 3
        
        # récupère les statistiques du Pokémon depuis l'API
        # NB : L'API Pokémon est une interface de programmation d'application (API)
        # qui fournit un accès aux données et aux fonctionnalités liées à l'univers Pokémon.
        # Cette API permet aux développeurs d'accéder à une vaste gamme d'informations sur les Pokémon,
        # y compris leurs statistiques, leurs types, leurs capacités, leurs évolutions, etc. 
        stats = self.json['stats']
        for stat in stats:
            if stat['stat']['name'] == 'hp':
                self.current_hp = stat['base_stat'] + self.level
                self.max_hp = stat['base_stat'] + self.level
            elif stat['stat']['name'] == 'attack':
                self.attack = stat['base_stat']
            elif stat['stat']['name'] == 'defense':
                self.defense = stat['base_stat']
            elif stat['stat']['name'] == 'speed':
                self.speed = stat['base_stat']
                
        # définir les types de Pokémon
        self.types = []
        for i in range(len(self.json['types'])):
            type = self.json['types'][i]
            self.types.append(type['type']['name'])
            
        # définir la largeur du sprite
        self.size = 150
        
        # définir le sprite sur le sprite orienté vers l'avant
        self.set_sprite('front_default')
    
    def perform_attack(self, other, move):
        
        display_message(f'{self.name} used {move.name}')
        
        # pause for 2 seconds
        time.sleep(2)
        
        # calculer les dégâts
        damage = (2 * self.level + 10) / 250 * self.attack / other.defense * move.power
        
       # bonus d'attaque de même type
        if move.type in self.types:
            damage *= 1.5
            
        # coup critique (6,25 % de chances)
        random_num = random.randint(1, 10000)
        if random_num <= 625:
            damage *= 1.5
            
       # arrondir les dégâts
        damage = math.floor(damage)
        
        other.take_damage(damage)
        
    def take_damage(self, damage):
        
        self.current_hp -= damage
        
        # les points de vies ne doivent pas descendre en dessous de 0
        if self.current_hp < 0:
            self.current_hp = 0
    
    def use_potion(self):
        
       # vérifie s'il reste des potions
        if self.num_potions > 0:
            
           # ajoutez 30 ch (mais ne dépassez pas le ch max)
            self.current_hp += 30
            if self.current_hp > self.max_hp:
                self.current_hp = self.max_hp
                
            # diminuer le nombre de potions restantes
            self.num_potions -= 1
        
    def set_sprite(self, side):
        
        # définir le sprite du Pokémon
        image = self.json['sprites'][side]
        image_stream = urlopen(image).read()
        image_file = io.BytesIO(image_stream)
        self.image = pygame.image.load(image_file).convert_alpha()
        
        # redimensionner l'image
        scale = self.size / self.image.get_width()
        new_width = self.image.get_width() * scale
        new_height = self.image.get_height() * scale
        self.image = pygame.transform.scale(self.image, (new_width, new_height))
        
    def set_moves(self):
        
        self.moves = []
        
        # parcourir tous les mouvements depuis l'API
        for i in range(len(self.json['moves'])):
            
            # passez à différentes versions de jeu
            versions = self.json['moves'][i]['version_group_details']
            for j in range(len(versions)):
                
                version = versions[j]
                
                # n'obtient que les mouvements de la version rouge-bleu
                if version['version_group']['name'] != 'red-blue':
                    continue
                    
                # n'obtient que les mouvements qui peuvent être appris en passant au niveau supérieur (c'est-à-dire exclure les mouvements de MT)
                learn_method = version['move_learn_method']['name']
                if learn_method != 'level-up':
                    continue
                    
                # ajouter un mouvement si le niveau du Pokémon est suffisamment élevé
                level_learned = version['level_learned_at']
                if self.level >= level_learned:
                    move = Move(self.json['moves'][i]['move']['url'])
                    
                    # n'inclut que les mouvements d'attaque
                    if move.power is not None:
                        self.moves.append(move)
                        
        # sélection jusqu'à 4 mouvements aléatoires
        if len(self.moves) > 4:
            self.moves = random.sample(self.moves, 4)
            
        # Cette fonction consiste à dessiner un sprite avec une transparence variable
    def draw(self, alpha=255):
        
        sprite = self.image.copy()
        transparency = (255, 255, 255, alpha)
        sprite.fill(transparency, None, pygame.BLEND_RGBA_MULT)
        game.blit(sprite, (self.x, self.y))
        
    def draw_hp(self):
        
        # affichage la barre de santé
        bar_scale = 200 // self.max_hp
        for i in range(self.max_hp):
            bar = (self.hp_x + bar_scale * i, self.hp_y, bar_scale, 20)
            pygame.draw.rect(game, red, bar)
            
        for i in range(self.current_hp):
            bar = (self.hp_x + bar_scale * i, self.hp_y, bar_scale, 20)
            pygame.draw.rect(game, green, bar)
            
        # afficher le texte "HP"
        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render(f'HP: {self.current_hp} / {self.max_hp}', True, black)
        text_rect = text.get_rect()
        text_rect.x = self.hp_x
        text_rect.y = self.hp_y + 30
        game.blit(text, text_rect)
        
        # cette fonction est utilisée pour obtenir un rectangle représentant la zone occupée par le sprite sur l'écran du jeu.
    def get_rect(self):
        
        return Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

def display_message(message):
    
    
# dessine une boîte blanche avec une bordure noire
    pygame.draw.rect(game, white, (10, 350, 480, 140))
    pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
    
# afficher le message
    font = pygame.font.Font(pygame.font.get_default_font(), 20)
    text = font.render(message, True, black)
    text_rect = text.get_rect()
    text_rect.x = 30
    text_rect.y = 410
    game.blit(text, text_rect)
    
    pygame.display.update()

#  Des fonctions sont définies pour afficher des messages à l'écran et créer des boutons interactifs dans le jeu.
def create_button(width, height, left, top, text_cx, text_cy, label):
    
    # position du curseur de la souris
    mouse_cursor = pygame.mouse.get_pos()
    
    button = Rect(left, top, width, height)
    
    # mettre en surbrillance le bouton si la souris pointe dessus
    if button.collidepoint(mouse_cursor):
        pygame.draw.rect(game, gold, button)
    else:
        pygame.draw.rect(game, white, button)
        
    # ajoute le label au bouton
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render(f'{label}', True, black)
    text_rect = text.get_rect(center=(text_cx, text_cy))
    game.blit(text, text_rect)
    
    return button
# Création des Pokémon de départ : Trois Pokémon de départ sont créés avec des niveaux spécifiques et des positions sur l'écran.
# créer les pokémons de départ
level = 30
bulbasaur = Pokemon('Bulbasaur', level, 25, 150)
charmander = Pokemon('Charmander', level, 175, 150)
squirtle = Pokemon('Squirtle', level, 325, 150)
pokemons = [bulbasaur, charmander, squirtle]

# le pokémon sélectionné par le joueur et son rival
player_pokemon = None
rival_pokemon = None

# Boucle de jeu
# Le jeu fonctionne dans une boucle où différents états du jeu sont gérés,
# tels que la sélection des Pokémon, la bataille et la fin du jeu.
game_status = 'select pokemon'
while game_status != 'quit':
    
    for event in pygame.event.get():
        if event.type == QUIT:
            game_status = 'quit'
            
       # détecter la pression sur une touche
        if event.type == KEYDOWN:
            
            # rejouer
            if event.key == K_y:
                
            # réinitialiser les pokémons
                bulbasaur = Pokemon('Bulbasaur', level, 25, 150)
                charmander = Pokemon('Charmander', level, 175, 150)
                squirtle = Pokemon('Squirtle', level, 325, 150)
                pokemons = [bulbasaur, charmander, squirtle]
                game_status = 'select pokemon'
                
            # quitter
            elif event.key == K_n:
                game_status = 'quit'
            
        
        # détecter le clic de souris
        if event.type == MOUSEBUTTONDOWN:
            
            # coordonnées du clic de souris
            mouse_click = event.pos
            
            # pour sélectionner un pokémon
            if game_status == 'select pokemon':
                
                # vérifier sur quel Pokémon on a cliqué
                for i in range(len(pokemons)):
                    
                    if pokemons[i].get_rect().collidepoint(mouse_click):
                        
                        # attribuer le pokémon du joueur et de son rival
                        player_pokemon = pokemons[i]
                        rival_pokemon = pokemons[(i + 1) % len(pokemons)]
                        
                        # abaissement du niveau du Pokémon rival pour rendre la bataille plus facile
                        rival_pokemon.level = int(rival_pokemon.level * .75)
                        
                        
                        # définir les coordonnées des barres hp
                        player_pokemon.hp_x = 275
                        player_pokemon.hp_y = 250
                        rival_pokemon.hp_x = 50
                        rival_pokemon.hp_y = 50
                        
                        game_status = 'prebattle'
            
            # pour sélectionner le combat ou utiliser une potion
            elif game_status == 'player turn':
                
                # vérifier si le bouton de combat a été cliqué
                if fight_button.collidepoint(mouse_click):
                    game_status = 'player move'
                    
                # vérifier si le bouton de potion a été cliqué
                if potion_button.collidepoint(mouse_click):
                    
                    # forcer à attaquer s'il n'y a plus de potions
                    if player_pokemon.num_potions == 0:
                        display_message('No more potions left')
                        time.sleep(2)
                        game_status = 'player move'
                    else:
                        player_pokemon.use_potion()
                        display_message(f'{player_pokemon.name} used potion')
                        time.sleep(2)
                        game_status = 'rival turn'
                        
            
            # pour sélectionner un coup
            elif game_status == 'player move':
                
               # Vérifiez sur quel bouton de déplacement vous avez cliqué
                for i in range(len(move_buttons)):
                    button = move_buttons[i]
                    
                    if button.collidepoint(mouse_click):
                        move = player_pokemon.moves[i]
                        player_pokemon.perform_attack(rival_pokemon, move)
                        
                        # vérifier si le pokémon du rival s'est évanoui
                        if rival_pokemon.current_hp == 0:
                            game_status = 'fainted'
                        else:
                            game_status = 'rival turn'
            
    # écran de sélection de Pokémon
    if game_status == 'select pokemon':
        
        game.fill(white)
        
        # écran de sélection de Pokémon
        bulbasaur.draw()
        charmander.draw()
        squirtle.draw()
        
        # dessiner une boîte autour du pokémon vers lequel pointe la souris
        mouse_cursor = pygame.mouse.get_pos()
        for pokemon in pokemons:
            
            if pokemon.get_rect().collidepoint(mouse_cursor):
                pygame.draw.rect(game, black, pokemon.get_rect(), 2)
        
        pygame.display.update()
        
    # récupère les mouvements de l'API et repositionne les pokémons
    if game_status == 'prebattle':
        
        # dessine le pokémon sélectionné
        game.fill(white)
        player_pokemon.draw()
        pygame.display.update()
        
        player_pokemon.set_moves()
        rival_pokemon.set_moves()
        
        # repositionner les pokémons
        player_pokemon.x = -50
        player_pokemon.y = 100
        rival_pokemon.x = 250
        rival_pokemon.y = -50
        
        # redimensionner les sprites
        player_pokemon.size = 300
        rival_pokemon.size = 300
        player_pokemon.set_sprite('back_default')
        rival_pokemon.set_sprite('front_default')
        
        game_status = 'start battle'
        
    # démarrer l'animation de combat
    if game_status == 'start battle':
        
        
    # rival envoie son pokémon
        alpha = 0
        while alpha < 255:
            
            game.fill(white)
            rival_pokemon.draw(alpha)
            display_message(f'Rival sent out {rival_pokemon.name}!')
            alpha += .4
            
            pygame.display.update()
            
        # pause d'une seule seconde
        time.sleep(1)
        
        # joueur envoie son Pokémon
        alpha = 0
        while alpha < 255:
            
            game.fill(white)
            rival_pokemon.draw()
            player_pokemon.draw(alpha)
            display_message(f'Go {player_pokemon.name}!')
            alpha += .4
            
            pygame.display.update()
        
        # dessine les barres HP
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        # déterminer qui commence en premier
        if rival_pokemon.speed > player_pokemon.speed:
            game_status = 'rival turn'
        else:
            game_status = 'player turn'
            
        pygame.display.update()
        
        # pause pendant 1 seconde
        time.sleep(1)
        
    # afficher le combat et utiliser les boutons de potion
    if game_status == 'player turn':
        
        game.fill(white)
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        # créez le combat et utilisez les boutons de potion
        fight_button = create_button(240, 140, 10, 350, 130, 412, 'Fight')
        potion_button = create_button(240, 140, 250, 350, 370, 412, f'Use Potion ({player_pokemon.num_potions})')

        # dessine la bordure noire
        pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
        
        pygame.display.update()
        
    # afficher les boutons de déplacement
    if game_status == 'player move':
        
        game.fill(white)
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        # créer un bouton pour chaque mouvement
        move_buttons = []
        for i in range(len(player_pokemon.moves)):
            move = player_pokemon.moves[i]
            button_width = 240
            button_height = 70
            left = 10 + i % 2 * button_width
            top = 350 + i // 2 * button_height
            text_center_x = left + 120
            text_center_y = top + 35
            button = create_button(button_width, button_height, left, top, text_center_x, text_center_y, move.name.capitalize())
            move_buttons.append(button)
            
       # dessine la bordure noire
        pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
        
        pygame.display.update()
        
    # rival sélectionne un mouvement aléatoire pour attaquer
    if game_status == 'rival turn':
        
        game.fill(white)
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        # videz la boîte d'affichage et faites une pause de 2 secondes avant d'attaquer
        display_message('')
        time.sleep(2)
        
        # sélectionnez un mouvement aléatoire
        move = random.choice(rival_pokemon.moves)
        rival_pokemon.perform_attack(player_pokemon, move)
        
        # vérifier si le pokémon du joueur s'est évanoui
        if player_pokemon.current_hp == 0:
            game_status = 'fainted'
        else:
            game_status = 'player turn'
            
        pygame.display.update()
        
    # un des pokémons s'est évanoui
    if game_status == 'fainted':
        
        alpha = 255
        while alpha > 0:
            
            game.fill(white)
            player_pokemon.draw_hp()
            rival_pokemon.draw_hp()
            
            # déterminer quel Pokémon s'est évanoui
            if rival_pokemon.current_hp == 0:
                player_pokemon.draw()
                rival_pokemon.draw(alpha)
                display_message(f'{rival_pokemon.name} fainted!')
            else:
                player_pokemon.draw(alpha)
                rival_pokemon.draw()
                display_message(f'{player_pokemon.name} fainted!')
            alpha -= .4
            
            pygame.display.update()
            
        game_status = 'gameover'
        
    # écran de fin de partie
    if game_status == 'gameover':
        
        display_message('Play again (Y/N)?')
        
pygame.quit()