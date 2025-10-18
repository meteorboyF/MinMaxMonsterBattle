# main_pygame.py

import pygame
import sys
import os
import time
import copy
import random 
from game_logic.monster import Monster, Move
from game_logic.battle import Battle
from ai.minimax import find_best_action

# --- Setup, Constants, Asset Loading ---
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
    monster_sprites = { 'Squirtle': pygame.image.load(os.path.join(assets_path, 'squirtle.png')).convert_alpha(), 'Charmander': pygame.image.load(os.path.join(assets_path, 'charmander.png')).convert_alpha(), 'Bulbasaur': pygame.image.load(os.path.join(assets_path, 'bulbasaur.png')).convert_alpha(), 'Pidgeotto': pygame.image.load(os.path.join(assets_path, 'pidgeotto.png')).convert_alpha(), 'Pikachu': pygame.image.load(os.path.join(assets_path, 'pikachu.png')).convert_alpha() }
except (pygame.error, FileNotFoundError) as e: 
    print(f"FATAL ERROR: Unable to load an asset. Please check file paths and names.\nError: {e}"); pygame.quit(); sys.exit()

def get_sprite(name): return pygame.transform.scale(monster_sprites.get(name), (250, 250))

# --- Drawing Functions (condensed for brevity) ---
def draw_text(text, font, color, surface, rect, aa=False, center=False):
    if center: text_surf = font.render(text, aa, color); text_rect = text_surf.get_rect(center=rect.center); surface.blit(text_surf, text_rect)
    else:
        words = text.split(' '); lines = []; current_line = ""
        for word in words:
            test_line = current_line + word + " ";
            if font.size(test_line)[0] < rect.width: current_line = test_line
            else: lines.append(current_line); current_line = word + " "
        lines.append(current_line); y = rect.top
        for line in lines: line_surf = font.render(line, aa, color); surface.blit(line_surf, (rect.left, y)); y += font.get_height()

def draw_health_bar(monster, x, y):
    bar_rect = pygame.Rect(x, y, 200, 25); ratio = max(0, monster.display_hp / monster.max_hp)
    pygame.draw.rect(screen, GRAY, bar_rect); pygame.draw.rect(screen, BLACK, bar_rect, 2)
    health_color = GREEN if ratio > 0.5 else (255, 255, 0) if ratio > 0.2 else RED
    if ratio > 0: pygame.draw.rect(screen, health_color, (x, y, bar_rect.width * ratio, bar_rect.height))
    hp_text = f"{int(monster.display_hp)}/{monster.max_hp}"; hp_surf = small_font.render(hp_text, True, WHITE)
    draw_text("HP", small_font, WHITE, screen, bar_rect.inflate(-10, -10)); screen.blit(hp_surf, (bar_rect.right - hp_surf.get_width() - 5, bar_rect.y + 2))
    
def draw_ui(player_mon, ai_mon):
    pygame.draw.rect(screen,GRAY,(20,20,300,110),border_radius=10);pygame.draw.rect(screen,BLACK,(20,20,300,110),3,10)
    draw_text(ai_mon.name,main_font,WHITE,screen,pygame.Rect(40,30,280,110)); draw_health_bar(ai_mon,40,70) 
    pygame.draw.rect(screen,GRAY,(480,340,300,110),border_radius=10);pygame.draw.rect(screen,BLACK,(480,340,300,110),3,10)
    draw_text(player_mon.name,main_font,WHITE,screen,pygame.Rect(500,350,280,110)); draw_health_bar(player_mon,500,390) 

def draw_bottom_panel(message, mouse_pos, monster_list, player_mon, mode='message'):
    box_rect=pygame.Rect(10,460,780,130); pygame.draw.rect(screen,GRAY,box_rect,border_radius=10); pygame.draw.rect(screen,BLACK,box_rect,3,10)
    buttons, switch_buttons = [], []
    if mode=='message': draw_text(message,small_font,WHITE,screen,pygame.Rect(30,470,740,110))
    elif mode=='moves':
        draw_text(f"What will {player_mon.name} do?",small_font,WHITE,screen,pygame.Rect(30,470,360,110))
        for i,move in enumerate(player_mon.moves):
            rect=pygame.Rect(420+(i%2)*180,470+(i//2)*55,170,50); buttons.append(rect)
            color=BUTTON_HOVER_COLOR if rect.collidepoint(mouse_pos) else BUTTON_COLOR; pygame.draw.rect(screen,color,rect,border_radius=5)
            draw_text(move.name,small_font,WHITE,screen,rect,center=True)
    elif mode in ['switch', 'choose_starter', 'pre_battle_switch']:
        title="Choose your starter" if mode=='choose_starter' else "Choose your next Pokémon"
        draw_text(title,main_font,WHITE,screen,pygame.Rect(30, 470, 740, 40))
        for i,mon in enumerate(monster_list):
            rect=pygame.Rect(30+(i%4)*190,520,180,60); switch_buttons.append((rect,mon))
            color=BUTTON_HOVER_COLOR if rect.collidepoint(mouse_pos) else BUTTON_COLOR; pygame.draw.rect(screen,color,rect,border_radius=5)
            text_color = WHITE if not mon.is_fainted else (150,150,150)
            draw_text(mon.name,small_font,text_color,screen,rect,center=True)
    return buttons, switch_buttons

def draw_menu(title, options, mouse_pos):
    buttons = []; draw_text(title, pygame.font.Font(None, 72), WHITE, screen, screen.get_rect(center=(SCREEN_WIDTH // 2, 150)), center=True)
    for i, option in enumerate(options):
        rect = pygame.Rect(SCREEN_WIDTH/2 - 150, 250 + i * 80, 300, 60); buttons.append(rect)
        color = BUTTON_HOVER_COLOR if rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, color, rect, border_radius=10); draw_text(option, main_font, WHITE, screen, rect, center=True)
    return buttons

# --- GameManager Class ---
class GameManager:
    def __init__(self): self.all_monsters = self.create_all_monsters(); self.reset()
    def create_all_monsters(self):
        return { 'Squirtle': Monster("Squirtle", ('Water',), 100, 50, 65, 45, [Move("Tackle", 'Normal', 40), Move("Water Gun", 'Water', 55), Move("Bubble", 'Water', 20), Move("Bite", 'Normal', 60)]), 'Charmander': Monster("Charmander", ('Fire',), 95, 60, 45, 65, [Move("Scratch", 'Normal', 40), Move("Ember", 'Fire', 40), Move("Fire Fang", 'Fire', 65), Move("Smokescreen", 'Normal', 0)]), 'Bulbasaur': Monster("Bulbasaur", ('Grass', 'Poison'), 105, 50, 50, 45, [Move("Tackle", 'Normal', 40), Move("Vine Whip", 'Grass', 45), Move("Absorb", 'Grass', 20), Move("PoisonPowder", 'Poison', 0)]), 'Pidgeotto': Monster("Pidgeotto", ('Normal', 'Flying'), 110, 60, 55, 70, [Move("Quick Attack", 'Normal', 35), Move("Gust", 'Flying', 40), Move("Wing Attack", 'Flying', 60), Move("Roost", 'Flying', 0)]), 'Pikachu': Monster("Pikachu", ('Electric',), 90, 55, 40, 90, [Move("Quick Attack", 'Normal', 35), Move("Thunder Shock", 'Electric', 40), Move("Thunderbolt", 'Electric', 90), Move("Iron Tail", 'Steel', 100, 75)]) }
    def reset(self):
        self.player_team, self.player_mon = [], None
        self.opponent_pool = [copy.deepcopy(self.all_monsters[name]) for name in ['Charmander', 'Pidgeotto', 'Pikachu']]
        self.ai_mon = self.opponent_pool[0]; self.ai_team = [self.ai_mon]
        self.current_opponent_idx = 0
    def set_player_starter(self, name): self.player_team = [copy.deepcopy(self.all_monsters[name])]; self.player_mon = self.player_team[0]
    def add_defeated_to_roster(self, defeated_mon):
        if defeated_mon.name not in [m.name for m in self.player_team]: self.player_team.append(copy.deepcopy(defeated_mon))
    def set_next_opponent(self):
        self.current_opponent_idx += 1
        if self.current_opponent_idx < len(self.opponent_pool):
            self.ai_mon = self.opponent_pool[self.current_opponent_idx]; self.ai_team = [self.ai_mon]; return True
        return False
    def heal_team(self, team):
        for mon in team: mon.current_hp = mon.max_hp; mon.is_fainted = False; mon.display_hp = mon.max_hp

# --- Animator Class ---
class Animator:
    def __init__(self,is_ai):self.monster=None;self.is_ai=is_ai;self.base_pos=(50,240)if not is_ai else(500,30);self.offset=[0,0];self.is_active=False;self.flash_color=(255,255,255,0);self.animation_start_time=0;self.animation_duration=0
    def set_monster(self,monster):self.monster=monster
    def start_attack(self):self.is_active=True;self.animation_start_time=time.time();self.animation_duration=0.5
    def start_damage(self):self.is_active=True;self.animation_start_time=time.time();self.animation_duration=0.3
    def update(self):
        if not self.is_active:return
        elapsed=time.time()-self.animation_start_time
        if elapsed>self.animation_duration:self.is_active=False;self.offset=[0,0];self.flash_color=(255,255,255,0);return
        if self.animation_duration==0.5:prog=elapsed/self.animation_duration;self.offset[0]=50*(prog*2 if prog<0.5 else(1-prog)*2)*(-1 if self.is_ai else 1)
        if self.animation_duration==0.3:prog=1-abs(0.5-elapsed/self.animation_duration)*2;self.flash_color=(255,255,255,180*prog)
    def draw(self,surface):
        if not self.monster:return
        pos=(self.base_pos[0]+self.offset[0],self.base_pos[1]+self.offset[1]);sprite=get_sprite(self.monster.name)
        if self.is_ai:sprite=pygame.transform.flip(sprite,True,False)
        if self.flash_color[3]>0:flash_surf=pygame.Surface(sprite.get_size(),pygame.SRCALPHA);flash_surf.fill(self.flash_color);sprite.blit(flash_surf,(0,0))
        surface.blit(sprite,pos)

# --- Main Game Loop ---
def main():
    gm, battle = GameManager(), Battle(); state='MAIN_MENU'; msg=""; buttons,m_btns,s_btns=[],[],[]
    p_anim, ai_anim = Animator(False), Animator(True); turn_q, anim_timer = [], 0
    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and not p_anim.is_active and not ai_anim.is_active and time.time() > anim_timer:
                if state=='MAIN_MENU':
                    if buttons and buttons[0].collidepoint(mouse_pos): state='CHOOSE_STARTER'
                elif state == 'BATTLE_WON':
                    state = 'PRE_BATTLE_SWITCH'
                    msg = "Choose your Pokémon for the next battle!"
                elif state == 'PRE_BATTLE_SWITCH':
                    for rect, mon in s_btns:
                        if rect.collidepoint(mouse_pos):
                            gm.player_mon = mon
                            p_anim.set_monster(gm.player_mon)
                            if gm.set_next_opponent():
                                state = 'BATTLE_INTRO'
                                msg = f"A new challenger appears: {gm.ai_mon.name}!"
                            else:
                                state = 'GAME_OVER'
                                msg = "You defeated all opponents! You are the champion!"
                elif state in ['RULES', 'GAME_OVER']: gm.reset(); state='MAIN_MENU'
                elif state in ['CHOOSE_STARTER', 'PLAYER_FORCED_SWITCH']:
                    for rect,mon in s_btns:
                        if rect.collidepoint(mouse_pos) and not mon.is_fainted:
                            if state == 'CHOOSE_STARTER': gm.set_player_starter(mon.name)
                            else: gm.player_mon = mon
                            p_anim.set_monster(gm.player_mon);msg=f"Go! {gm.player_mon.name}!";anim_timer=time.time()+1.0
                            state = 'BATTLE_INTRO' if state == 'CHOOSE_STARTER' else 'AWAITING_INPUT'
                elif state=='AWAITING_INPUT':
                    for i,button in enumerate(m_btns):
                        if button.collidepoint(mouse_pos): turn_q=[('PLAYER_ATTACK',gm.player_mon.moves[i]),('CHECK_FAINT',gm.ai_mon),('AI_DECISION',),('CHECK_FAINT',gm.player_mon),('END_TURN',)]; state='NEXT_ACTION'
                elif state in ['PLAYER_MESSAGE', 'AI_MESSAGE']: state='NEXT_ACTION'
        
        p_anim.update(); ai_anim.update()
        for mon in gm.player_team + gm.ai_team:
            if mon.display_hp != mon.current_hp: step = max(1, int(abs(mon.display_hp-mon.current_hp)*0.1)); mon.display_hp += -step if mon.display_hp > mon.current_hp else step

        screen.blit(background_img,(0,0))
        if state=='MAIN_MENU': buttons=draw_menu("Minimax Monster Battle",["Start Game"],mouse_pos)
        else:
            ai_anim.draw(screen)
            if gm.player_mon: p_anim.draw(screen); draw_ui(gm.player_mon, gm.ai_mon)
            if state=='AWAITING_INPUT': m_btns,s_btns=draw_bottom_panel(msg,mouse_pos,[],gm.player_mon,mode='moves')
            elif state=='CHOOSE_STARTER': m_btns,s_btns=draw_bottom_panel(msg,mouse_pos,[gm.all_monsters['Squirtle'],gm.all_monsters['Charmander'],gm.all_monsters['Bulbasaur']],None,mode='choose_starter')
            elif state == 'PLAYER_FORCED_SWITCH': m_btns,s_btns=draw_bottom_panel(msg,mouse_pos,gm.player_team,None,mode='switch')
            elif state == 'PRE_BATTLE_SWITCH': m_btns,s_btns=draw_bottom_panel(msg,mouse_pos,gm.player_team,None,mode='pre_battle_switch')
            else: m_btns,s_btns=draw_bottom_panel(msg,mouse_pos,[],None,mode='message')
        pygame.display.flip()

        if time.time() < anim_timer or p_anim.is_active or ai_anim.is_active: continue
        if state=='BATTLE_INTRO': p_anim.set_monster(gm.player_mon);ai_anim.set_monster(gm.ai_mon);anim_timer=time.time()+1.5;state='AWAITING_INPUT'
        elif state=='NEXT_ACTION' and turn_q:
            action, *args = turn_q.pop(0)
            if action=='PLAYER_ATTACK':
                move=args[0];msg=f"{gm.player_mon.name} uses {move.name}!";p_anim.start_attack();anim_timer=time.time()+0.5;turn_q.insert(0,('PLAYER_DAMAGE',move))
            elif action=='PLAYER_DAMAGE':
                move=args[0];info=battle.calculate_damage(gm.player_mon,gm.ai_mon,move);gm.ai_mon.take_damage(info['damage']);msg=info['effectiveness_msg'] or f"Dealt {info['damage']} damage.";ai_anim.start_damage();anim_timer=time.time()+1.5;state='PLAYER_MESSAGE'
            elif action=='CHECK_FAINT':
                mon=args[0]
                if mon.is_fainted:
                    turn_q.clear(); msg=f"{mon.name} fainted!"; anim_timer=time.time()+1.5
                    if mon is gm.ai_mon:
                        gm.add_defeated_to_roster(mon); gm.heal_team(gm.player_team); state = 'BATTLE_WON'
                    elif any(not m.is_fainted for m in gm.player_team): state='PLAYER_FORCED_SWITCH'
                    else: state='GAME_OVER'; msg = "Your team has fainted. Game Over."
            elif action=='AI_DECISION':
                if not gm.ai_mon.is_fainted: turn_q.insert(0, ('AI_ATTACK', find_best_action(gm.ai_team, gm.player_team, gm.ai_mon, gm.player_mon)))
            elif action=='AI_ATTACK':
                move=args[0];msg=f"{gm.ai_mon.name} uses {move.name}!";ai_anim.start_attack();anim_timer=time.time()+0.5;turn_q.insert(0,('AI_DAMAGE',move))
            elif action=='AI_DAMAGE':
                move=args[0];info=battle.calculate_damage(gm.ai_mon,gm.player_mon,move);gm.player_mon.take_damage(info['damage']);msg=info['effectiveness_msg'] or f"Dealt {info['damage']} damage.";p_anim.start_damage();anim_timer=time.time()+1.5;state='AI_MESSAGE'
            elif action=='END_TURN': state='AWAITING_INPUT'
        clock.tick(FPS)

if __name__=="__main__":main()