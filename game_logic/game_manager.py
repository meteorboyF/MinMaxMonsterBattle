
import copy
from .monster import Monster, Move

class GameManager:
    def __init__(self):
        self.all_monsters = self.create_all_monsters()
        self.reset()

    def create_all_monsters(self):
        # PP values have been adjusted for faster, more decisive battles.
        # Weaker moves are in the 10-12 range, powerful/utility moves are in the 5-8 range.
        return {
            'Squirtle': Monster("Squirtle", ('Water',), 110, 50, 65, 45, [
                Move("Tackle", 'Normal', 40, 100, 12),
                Move("Water Gun", 'Water', 55, 100, 8),
                Move("Withdraw", 'Water', 0, 100, 8, stat_change=('defense', 1), target='self'),
                Move("Bite", 'Normal', 60, 100, 8)
            ]),
            'Charmander': Monster("Charmander", ('Fire',), 100, 65, 45, 65, [
                Move("Scratch", 'Normal', 40, 100, 12),
                Move("Ember", 'Fire', 45, 100, 10),
                Move("Fire Fang", 'Fire', 70, 95, 5),
                Move("Growl", 'Normal', 0, 100, 8, stat_change=('attack', -1), target='opponent')
            ]),
            'Bulbasaur': Monster("Bulbasaur", ('Grass', 'Poison'), 115, 50, 55, 45, [
                Move("Tackle", 'Normal', 40, 100, 12),
                Move("Vine Whip", 'Grass', 50, 100, 10),
                Move("PoisonPowder", 'Poison', 0, 75, 5, status_effect=('poisoned', 100)),
                Move("Razor Leaf", 'Grass', 65, 95, 5)
            ]),
            'Pidgeotto': Monster("Pidgeotto", ('Normal', 'Flying'), 120, 60, 55, 70, [
                Move("Quick Attack", 'Normal', 40, 100, 12),
                Move("Gust", 'Flying', 45, 100, 10),
                Move("Wing Attack", 'Flying', 65, 100, 5),
                Move("Sand Attack", 'Normal', 0, 100, 8, stat_change=('defense', -1), target='opponent')
            ]),
            'Pikachu': Monster("Pikachu", ('Electric',), 95, 60, 40, 90, [
                Move("Quick Attack", 'Normal', 40, 100, 12),
                Move("Thunder Shock", 'Electric', 45, 100, 10, status_effect=('paralyzed', 10)),
                Move("Thunderbolt", 'Electric', 90, 100, 5),
                Move("Double Team", 'Normal', 0, 100, 8, stat_change=('defense', 1), target='self')
            ]),
            'Geodude': Monster("Geodude", ('Rock', 'Ground'), 100, 60, 80, 20, [
                Move("Tackle", 'Normal', 40, 100, 12),
                Move("Rock Throw", 'Rock', 50, 90, 10),
                Move("Magnitude", 'Ground', 70, 100, 5),
                Move("Defense Curl", 'Normal', 0, 100, 8, stat_change=('defense', 1), target='self')
            ]),
            'Gastly': Monster("Gastly", ('Ghost', 'Poison'), 80, 65, 30, 80, [
                Move("Lick", 'Ghost', 30, 100, 12, status_effect=('paralyzed', 30)),
                Move("Shadow Ball", 'Ghost', 80, 100, 5),
                Move("Sludge Bomb", 'Poison', 90, 100, 5, status_effect=('poisoned', 30)),
                Move("Confuse Ray", 'Ghost', 0, 100, 5, status_effect=('paralyzed', 100)) # Proxied as paralysis
            ]),
            'Oddish': Monster("Oddish", ('Grass', 'Poison'), 95, 50, 55, 30, [
                Move("Acid", 'Poison', 40, 100, 12),
                Move("Mega Drain", 'Grass', 40, 100, 10),
                Move("PoisonPowder", 'Poison', 0, 75, 5, status_effect=('poisoned', 100)),
                Move("Solar Beam", 'Grass', 120, 100, 3) # Very strong but low PP
            ]),
            'Vulpix': Monster("Vulpix", ('Fire',), 90, 45, 40, 65, [
                Move("Ember", 'Fire', 40, 100, 12),
                Move("Quick Attack", 'Normal', 40, 100, 10),
                Move("Flamethrower", 'Fire', 90, 100, 5),
                Move("Will-O-Wisp", 'Fire', 0, 85, 5, status_effect=('poisoned', 100)) # Proxied burn as poison
            ]),
            'Snorlax': Monster("Snorlax", ('Normal',), 200, 80, 65, 30, [
                Move("Body Slam", 'Normal', 85, 100, 8, status_effect=('paralyzed', 30)),
                Move("Rest", 'Psychic', 0, 100, 5, stat_change=('defense', 2), target='self'), # Pseudo heal: def up
                Move("Hyper Beam", 'Normal', 150, 90, 3),
                Move("Crunch", 'Normal', 70, 100, 8) 
            ])
        }
    
    def reset(self):
        self.player_team, self.player_mon = [], None
        # Fixed Campaign Order
        self.opponent_pool = [
            copy.deepcopy(self.all_monsters[name]) for name in 
            ['Geodude', 'Oddish', 'Vulpix', 'Gastly', 'Pidgeotto', 'Pikachu', 'Snorlax']
        ]
        self.ai_mon = self.opponent_pool[0]
        self.ai_team = [self.ai_mon]
        self.current_opponent_idx = 0
    
    def set_player_starter(self, name):
        self.player_team = [copy.deepcopy(self.all_monsters[name])]
        self.player_mon = self.player_team[0]
    
    def add_defeated_to_roster(self, defeated_mon):
        if defeated_mon.name not in [m.name for m in self.player_team]:
            self.player_team.append(copy.deepcopy(defeated_mon))
    
    def set_next_opponent(self):
        self.current_opponent_idx += 1
        if self.current_opponent_idx < len(self.opponent_pool):
            self.ai_mon = self.opponent_pool[self.current_opponent_idx]
            self.ai_team = [self.ai_mon]
            return True
        return False
    
    def full_heal_player_team(self):
        for mon in self.player_team:
            mon.current_hp = mon.max_hp
            mon.is_fainted = False
            mon.display_hp = mon.max_hp
            mon.restore_pp()
            mon.reset_battle_stats()
