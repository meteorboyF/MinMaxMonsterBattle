# game_logic/battle.py

from .monster import Monster, Move
import random

 
TYPE_CHART = {
    'Normal': {'NoEffect': ['Ghost'], 'NotVeryEffective': ['Rock', 'Steel']},
    'Fire': {'NotVeryEffective': ['Fire', 'Water', 'Rock', 'Dragon'], 'SuperEffective': ['Grass', 'Ice', 'Bug', 'Steel']},
    'Water': {'NotVeryEffective': ['Water', 'Grass', 'Dragon'], 'SuperEffective': ['Fire', 'Ground', 'Rock']},
    'Grass': {'NotVeryEffective': ['Fire', 'Grass', 'Poison', 'Flying', 'Bug', 'Dragon', 'Steel'], 'SuperEffective': ['Water', 'Ground', 'Rock']},
    'Electric': {'NotVeryEffective': ['Grass', 'Electric', 'Dragon'], 'NoEffect': ['Ground'], 'SuperEffective': ['Water', 'Flying']},
    'Flying': {'NotVeryEffective': ['Electric', 'Rock', 'Steel'], 'SuperEffective': ['Grass', 'Fighting', 'Bug']},
    'Poison': {'NotVeryEffective': ['Poison', 'Ground', 'Rock', 'Ghost'], 'SuperEffective': ['Grass', 'Fairy'], 'NoEffect': ['Steel']},
    'Ground': {'NotVeryEffective': ['Grass', 'Bug'], 'NoEffect': ['Flying'], 'SuperEffective': ['Fire', 'Electric', 'Poison', 'Rock', 'Steel']},
    'Rock': {'NotVeryEffective': ['Fighting', 'Ground', 'Steel'], 'SuperEffective': ['Fire', 'Ice', 'Flying', 'Bug']},
}

class Battle:
    """Manages battle rules, including type effectiveness."""
    
    def get_type_effectiveness(self, move_type: str, defender_types: tuple) -> float:
        """Calculates the damage multiplier based on type."""
        multiplier = 1.0
        if move_type not in TYPE_CHART:
            return multiplier
            
        for def_type in defender_types:
            if def_type in TYPE_CHART[move_type].get('SuperEffective', []):
                multiplier *= 2.0
            elif def_type in TYPE_CHART[move_type].get('NotVeryEffective', []):
                multiplier *= 0.5
            elif def_type in TYPE_CHART[move_type].get('NoEffect', []):
                return 0.0
        return multiplier

    def calculate_damage(self, attacker: Monster, defender: Monster, move: Move) -> dict:
        """Calculates damage, including critical hits and type effectiveness."""
        if move.power == 0:
            return {'damage': 0, 'effectiveness_msg': ''}

        multiplier = self.get_type_effectiveness(move.type, defender.type)
        
     
        damage = int(((attacker.attack / defender.defense) * move.power) / 5)
        damage = int(damage * multiplier * random.uniform(0.9, 1.1))

        effectiveness_msg = ""
        if multiplier > 1.0:
            effectiveness_msg = "It's super effective!"
        elif multiplier < 1.0 and multiplier > 0:
            effectiveness_msg = "It's not very effective..."
        elif multiplier == 0:
            effectiveness_msg = "It had no effect!"

        return {'damage': max(1, damage), 'effectiveness_msg': effectiveness_msg}

    def handle_attack(self, attacker: Monster, defender: Monster, move: Move) -> str:
        """Handles a single attack and returns a descriptive message."""
        # Note: Damage calculation and message generation is now split between calculate_damage
        # and the damage application blocks in main_pygame.py for better game flow control.
        if random.randint(1, 100) > move.accuracy:
            return f"{attacker.name}'s {move.name} missed!"
        
        # handle_attack is now simplified to just check for miss, damage applied in main_pygame.py
        
        message = f"{attacker.name} uses {move.name}!"
        # The rest of the message logic is in main_pygame.py
        return message