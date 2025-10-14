# main_pygame.py

import pygame
import sys
import os
import time
import copy
from game_logic.monster import Monster, Move
from game_logic.battle import Battle
from ai.minimax import find_best_move

 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
WHITE, BLACK, GRAY, RED, GREEN = (255, 255, 255), (0, 0, 0), (40, 40, 40), (200, 50, 50), (50, 200, 50)
BUTTON_COLOR, BUTTON_HOVER_COLOR = (70, 70, 70), (100, 100, 100)
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Minimax Monster Battle")
clock = pygame.time.Clock()
main_font = pygame.font.Font(None, 42)
small_font = pygame.font.Font(None, 28)

try:
    assets_path = os.path.join(BASE_DIR, 'assets', 'images')
    background_img = pygame.image.load(os.path.join(assets_path, 'background.jpg')).convert()
    monster_sprites = {
        'Squirtle': pygame.image.load(os.path.join(assets_path, 'player_monster.png')).convert_alpha(),
        'Rayquaza': pygame.image.load(os.path.join(assets_path, 'ai_monster.png')).convert_alpha(),
        'Pikachu': pygame.image.load(os.path.join(assets_path, 'pikachu.png')).convert_alpha(),
        'Charmander': pygame.image.load(os.path.join(assets_path, 'charmander.png')).convert_alpha(),
        'Bulbasaur': pygame.image.load(os.path.join(assets_path, 'bulbasaur.png')).convert_alpha(),
        'Pidgeotto': pygame.image.load(os.path.join(assets_path, 'pidgeotto.png')).convert_alpha(),
    }
except pygame.error as e:
    print(f"FATAL ERROR: Unable to load asset: {e}\nMake sure you have all monster images in 'assets/images/'")
    pygame.quit()
    sys.exit()

def get_sprite(name, is_ai=False):
    sprite = monster_sprites.get(name)
    if not sprite: return
    sprite = pygame.transform.scale(sprite, (250, 250))
    if is_ai:
        sprite = pygame.transform.flip(sprite, True, False)
    return sprite

 
class GameManager:
    def __init__(self):
        self.all_monsters = self.create_all_monsters()
        self.reset()
    def create_all_monsters(self):
        return {
            'Squirtle': Monster("Squirtle", ('Water',), 100, 50, 65, 45, [Move("Tackle", 'Normal', 40), Move("Water Gun", 'Water', 55, 95)]),
            'Charmander': Monster("Charmander", ('Fire',), 95, 60, 45, 65, [Move("Scratch", 'Normal', 40), Move("Ember", 'Fire', 40)]),
            'Bulbasaur': Monster("Bulbasaur", ('Grass', 'Poison'), 105, 50, 50, 45, [Move("Tackle", 'Normal', 40), Move("Vine Whip", 'Grass', 45)]),
            'Pidgeotto': Monster("Pidgeotto", ('Normal', 'Flying'), 110, 60, 55, 70, [Move("Quick Attack", 'Normal', 35), Move("Gust", 'Flying', 40)]),
            'Pikachu': Monster("Pikachu", ('Electric',), 90, 55, 40, 90, [Move("Quick Attack", 'Normal', 35), Move("Thunder Shock", 'Electric', 40)]),
            'Rayquaza': Monster("Rayquaza", ('Dragon', 'Flying'), 200, 80, 60, 95, [Move("Dragon Breath", 'Dragon', 60), Move("Aerial Ace", 'Flying', 50)]),
        }
    def reset(self):
        self.player_team = [copy.deepcopy(self.all_monsters['Squirtle'])]
        self.opponents = [copy.deepcopy(self.all_monsters[name]) for name in ['Charmander', 'Bulbasaur', 'Pidgeotto', 'Pikachu', 'Rayquaza']]
        self.current_opponent_idx = 0; self.player_mon = self.player_team[0]; self.opponent_mon = self.opponents[self.current_opponent_idx]
    def add_mon_to_team(self):
        defeated_mon = self.opponents[self.current_opponent_idx]
        if defeated_mon.name != 'Rayquaza': self.player_team.append(copy.deepcopy(defeated_mon))
    def heal_player_team(self):
        for mon in self.player_team: mon.current_hp = mon.max_hp; mon.is_fainted = False
    def advance_to_next_opponent(self):
        self.current_opponent_idx += 1
        if self.current_opponent_idx < len(self.opponents): self.opponent_mon = self.opponents[self.current_opponent_idx]; return True
        return False

 
def draw_text(text, font, color, surface, rect, aa=False):
    words = [word.split(' ') for word in text.splitlines()]; space = font.size(' ')[0]; x, y = rect.left, rect.top
    for line in words:
        for word in line:
            word_surface = font.render(word, aa, color); word_width, word_height = word_surface.get_size()
            if x + word_width >= rect.right: x = rect.left; y += word_height
            surface.blit(word_surface, (x, y)); x += word_width + space
        x = rect.left; y += word_height

def draw_health_bar(monster, x, y):
    ratio = max(0, monster.current_hp / monster.max_hp)
    pygame.draw.rect(screen, GRAY, (x, y, 200, 25)); pygame.draw.rect(screen, RED, (x, y, 200, 25))
    if ratio > 0: pygame.draw.rect(screen, GREEN, (x, y, 200 * ratio, 25))
    draw_text(f"HP: {monster.current_hp}/{monster.max_hp}", small_font, WHITE, screen, pygame.Rect(x+5, y+2, 200, 25))
    pygame.draw.rect(screen, BLACK, (x, y, 200, 25), 2)

 
def draw_ui(player_mon, opponent_mon):
    # Opponent Panel (Top-Left)
    pygame.draw.rect(screen, GRAY, (20, 20, 300, 110), border_radius=10); pygame.draw.rect(screen, BLACK, (20, 20, 300, 110), 3, 10)
    draw_text(opponent_mon.name, main_font, WHITE, screen, pygame.Rect(40, 30, 280, 110))
    draw_health_bar(opponent_mon, 40, 70)
    
    # Player Panel  
    pygame.draw.rect(screen, GRAY, (480, 340, 300, 110), border_radius=10); pygame.draw.rect(screen, BLACK, (480, 340, 300, 110), 3, 10)
    draw_text(player_mon.name, main_font, WHITE, screen, pygame.Rect(500, 350, 280, 110))
    draw_health_bar(player_mon, 500, 390)

def draw_bottom_panel(message, mouse_pos, player_team, player_mon, mode='message'):
    box_rect = pygame.Rect(10, 460, 780, 130)
    pygame.draw.rect(screen, GRAY, box_rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, box_rect, 3, 10)

    if mode == 'message':
        draw_text(message, small_font, WHITE, screen, pygame.Rect(30, 470, 740, 110))
        return [], []  
    elif mode == 'moves':
        draw_text(message, small_font, WHITE, screen, pygame.Rect(30, 470, 400, 110))
        buttons = []
        for i, move in enumerate(player_mon.moves):
            rect = pygame.Rect(430 + (i % 2) * 180, 470 + (i // 2) * 55, 170, 50)
            buttons.append(rect)
            color = BUTTON_HOVER_COLOR if rect.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(screen, color, rect, border_radius=5)
            text_rect = rect.inflate(-10, -10); text_rect.center = rect.center
            draw_text(move.name, small_font, WHITE, screen, text_rect)
        return buttons, []

    elif mode == 'switch':
        draw_text(message, small_font, WHITE, screen, pygame.Rect(30, 470, 400, 110))
        buttons = []
        for i, mon in enumerate(player_team):
            if not mon.is_fainted:
                rect = pygame.Rect(30 + i * 190, 520, 180, 60)
                buttons.append((rect, mon))
                color = BUTTON_HOVER_COLOR if rect.collidepoint(mouse_pos) else BUTTON_COLOR
                pygame.draw.rect(screen, color, rect, border_radius=5)
                text_rect = rect.inflate(-10, -10); text_rect.center = rect.center
                draw_text(mon.name, small_font, WHITE, screen, text_rect)
        return [], buttons

def draw_menu(title, options, mouse_pos):
    buttons = []
    draw_text(title, pygame.font.Font(None, 72), WHITE, screen, pygame.Rect(0, 100, SCREEN_WIDTH, 100))
    for i, option in enumerate(options):
        rect = pygame.Rect(SCREEN_WIDTH/2 - 150, 250 + i * 80, 300, 60); buttons.append(rect)
        color = BUTTON_HOVER_COLOR if rect.collidepoint(mouse_pos) else BUTTON_COLOR; pygame.draw.rect(screen, color, rect, border_radius=10)
        text_rect = rect.inflate(0,0); text_rect.center = rect.center; draw_text(option, main_font, WHITE, screen, text_rect)
    return buttons

# --- Main Game Loop ---
def main():
    game_manager = GameManager()
    battle = Battle()
    game_state = 'MAIN_MENU'
    message = ""
    buttons, move_buttons, switch_buttons = [], [], []
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == 'MAIN_MENU':
                    if buttons[0].collidepoint(mouse_pos): game_state = 'BATTLE_INTRO'
                    elif buttons[1].collidepoint(mouse_pos): game_state = 'RULES'
                elif game_state == 'RULES' or game_state in ['BATTLE_WON', 'GAME_OVER']:
                    if game_state == 'BATTLE_WON':
                        game_manager.add_mon_to_team(); game_manager.heal_player_team()
                        if not game_manager.advance_to_next_opponent(): message = "You are a master trainer! You win!"; game_state = 'GAME_OVER'
                        else: game_state = 'BATTLE_INTRO'
                    else: game_manager.reset(); game_state = 'MAIN_MENU'
                elif game_state == 'CHOOSE_STARTER' or game_state == 'SWITCH_POKEMON':
                    for rect, mon in switch_buttons:
                        if rect.collidepoint(mouse_pos):
                            game_manager.player_mon = mon
                            if game_state == 'SWITCH_POKEMON':
                                ai_move = find_best_move(game_manager.opponent_mon, game_manager.player_mon); turn_order = [(game_manager.opponent_mon, ai_move, game_manager.player_mon)]
                                game_state = 'RUN_TURN'
                            else: game_state = 'AWAITING_INPUT'
                elif game_state == 'AWAITING_INPUT':
                    for i, button in enumerate(move_buttons):
                        if button.collidepoint(mouse_pos):
                            player_move = game_manager.player_mon.moves[i]; ai_move = find_best_move(game_manager.opponent_mon, game_manager.player_mon)
                             
                            turn_order = [(game_manager.player_mon, player_move, game_manager.opponent_mon), (game_manager.opponent_mon, ai_move, game_manager.player_mon)] if game_manager.player_mon.speed >= game_manager.opponent_mon.speed else [(game_manager.opponent_mon, ai_move, game_manager.player_mon), (game_manager.player_mon, player_move, game_manager.opponent_mon)]
                            game_state = 'RUN_TURN'

        screen.blit(background_img, (0, 0))
        if game_state == 'MAIN_MENU':
            buttons = draw_menu("Minimax Monsters", ["Start Game", "Rules"], mouse_pos)
        elif game_state == 'RULES':
            rules_text = ("How the AI Thinks (Minimax):\n\n1. The AI builds a tree of all possible future moves.\n2. It assumes you will always make the best move (Minimizer).\n3. It then chooses the move that gives IT the best outcome, even against your perfect play (Maximizer).\n4. Alpha-Beta Pruning heavily optimizes this by ignoring branches that won't change the final decision.\n\nWatch the terminal to see this in action!")
            draw_text(rules_text, small_font, WHITE, screen, pygame.Rect(50, 150, 700, 400))
            buttons = [pygame.Rect(SCREEN_WIDTH/2 - 150, 500, 300, 60)]; pygame.draw.rect(screen, BUTTON_COLOR, buttons[0], border_radius=10); draw_text("Back", main_font, WHITE, screen, buttons[0])
        else:
            screen.blit(get_sprite(game_manager.player_mon.name), (50, 240)); screen.blit(get_sprite(game_manager.opponent_mon.name, True), (500, 30)); draw_ui(game_manager.player_mon, game_manager.opponent_mon)
            if game_state == 'AWAITING_INPUT':
                move_buttons, _ = draw_bottom_panel(f"What will {game_manager.player_mon.name} do?", mouse_pos, game_manager.player_team, game_manager.player_mon, mode='moves')
            elif game_state == 'CHOOSE_STARTER':
                _, switch_buttons = draw_bottom_panel("Choose your Pokémon!", mouse_pos, game_manager.player_team, game_manager.player_mon, mode='switch')
            elif game_state == 'SWITCH_POKEMON':
                _, switch_buttons = draw_bottom_panel(f"{game_manager.player_mon.name} fainted!", mouse_pos, game_manager.player_team, game_manager.player_mon, mode='switch')
            else: draw_bottom_panel(message, mouse_pos, game_manager.player_team, game_manager.player_mon, mode='message')
        
        pygame.display.flip()

        if game_state == 'BATTLE_INTRO':
            message = f"You are challenged by {game_manager.opponent_mon.name}!"; pygame.display.flip(); time.sleep(2); game_state = 'CHOOSE_STARTER'
        elif game_state == 'RUN_TURN':
            for attacker, move, defender in turn_order:
                if not attacker.is_fainted and not defender.is_fainted:
                    message = battle.handle_attack(attacker, defender, move)
                    screen.blit(background_img, (0, 0)); screen.blit(get_sprite(game_manager.player_mon.name), (50, 240)); screen.blit(get_sprite(game_manager.opponent_mon.name, True), (500, 30)); draw_ui(game_manager.player_mon, game_manager.opponent_mon); draw_bottom_panel(message, mouse_pos, game_manager.player_team, game_manager.player_mon, mode='message'); pygame.display.flip(); time.sleep(2)
            if game_manager.opponent_mon.is_fainted: message = f"You defeated {game_manager.opponent_mon.name}!"; game_state = 'BATTLE_WON'
            elif game_manager.player_mon.is_fainted:
                message = f"{game_manager.player_mon.name} fainted!"
                if any(not mon.is_fainted for mon in game_manager.player_team if mon is not game_manager.player_mon): game_state = 'SWITCH_POKEMON'
                else: message = "You have no more Pokémon! You lose."; game_state = 'GAME_OVER'
            else: game_state = 'AWAITING_INPUT'
        
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()