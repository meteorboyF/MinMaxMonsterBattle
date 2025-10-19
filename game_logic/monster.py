# game_logic/monster.py

class Move:
    """A class to represent a move with PP, stat changes, and status effects."""
    def __init__(self, name: str, move_type: str, power: int, accuracy: int = 100, pp: int = 15, 
                 stat_change: tuple = None, target: str = 'opponent', status_effect: tuple = None):
        self.name = name
        self.type = move_type
        self.power = power
        self.accuracy = accuracy
        self.max_pp = pp
        self.current_pp = pp
        self.stat_change = stat_change  # e.g., ('attack', -1)
        self.target = target            # 'self' or 'opponent'
        self.status_effect = status_effect # e.g., ('poison', 30) for a 30% chance

class Monster:
    """A class to represent a monster with stats, types, moves, and conditions."""
    def __init__(self, name: str, mon_type: tuple, hp: int, attack: int, defense: int, speed: int, moves: list):
        self.name = name
        self.type = mon_type
        self.max_hp = hp
        self.current_hp = hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.moves = moves
        self.is_fainted = False
        self.display_hp = hp
        
        # New attributes for complex features
        self.status = 'ok'  # 'ok', 'poisoned', 'paralyzed'
        self.stat_mods = {'attack': 0, 'defense': 0} # Stages from -6 to 6

    def get_modified_stat(self, stat_name: str) -> int:
        """Calculates a stat after applying modifiers."""
        base_stat = getattr(self, stat_name)
        modifier = self.stat_mods.get(stat_name, 0)
        # Apply a simple percentage-based modification
        multiplier = 1.0 + (modifier * 0.25)
        return int(base_stat * multiplier)

    def apply_stat_mod(self, stat_name: str, amount: int):
        """Applies a stat modification, capping at +/- 6 stages."""
        self.stat_mods[stat_name] = max(-6, min(6, self.stat_mods[stat_name] + amount))

    def take_damage(self, damage: int):
        """Applies damage and checks if the monster has fainted."""
        self.current_hp -= damage
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_fainted = True
    
    def restore_pp(self):
        """Restores PP for all moves."""
        for move in self.moves:
            move.current_pp = move.max_pp
    
    def reset_battle_stats(self):
        """Resets status and stat mods for the next battle."""
        self.status = 'ok'
        self.stat_mods = {'attack': 0, 'defense': 0}

    def __repr__(self):
        return f"<Monster: {self.name}, HP: {self.current_hp}/{self.max_hp}, Status: {self.status}>"