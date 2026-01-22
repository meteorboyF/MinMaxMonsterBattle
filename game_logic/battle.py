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
    'Ghost': {'NotVeryEffective': ['Dark'], 'NoEffect': ['Normal'], 'SuperEffective': ['Ghost', 'Psychic']},
    'Ice': {'NotVeryEffective': ['Fire', 'Water', 'Ice', 'Steel'], 'SuperEffective': ['Grass', 'Ground', 'Flying', 'Dragon']},
    'Dragon': {'NotVeryEffective': ['Steel'], 'NoEffect': ['Fairy'], 'SuperEffective': ['Dragon']},
    'Fighting': {'NotVeryEffective': ['Poison', 'Flying', 'Psychic', 'Bug', 'Fairy'], 'NoEffect': ['Ghost'], 'SuperEffective': ['Normal', 'Ice', 'Rock', 'Dark', 'Steel']},
    'Psychic': {'NotVeryEffective': ['Psychic', 'Steel'], 'NoEffect': ['Dark'], 'SuperEffective': ['Fighting', 'Poison']},
    'Bug': {'NotVeryEffective': ['Fire', 'Fighting', 'Poison', 'Flying', 'Ghost', 'Steel', 'Fairy'], 'SuperEffective': ['Grass', 'Psychic', 'Dark']},
}

class Battle:
    def get_type_effectiveness(self, move_type: str, defender_types: tuple) -> float:
        """Calculates the damage multiplier based on type."""
        multiplier = 1.0
        if move_type not in TYPE_CHART: return multiplier
        for def_type in defender_types:
            if def_type in TYPE_CHART[move_type].get('SuperEffective', []): multiplier *= 2.0
            elif def_type in TYPE_CHART[move_type].get('NotVeryEffective', []): multiplier *= 0.5
            elif def_type in TYPE_CHART[move_type].get('NoEffect', []): return 0.0
        return multiplier

    def calculate_damage(self, attacker: Monster, defender: Monster, move: Move) -> dict:
        """Calculates damage, now using modified stats."""
        if move.power == 0: return {'damage': 0, 'effectiveness_msg': ''}

        # Use modified stats instead of base stats
        attack_stat = attacker.get_modified_stat('attack')
        defense_stat = defender.get_modified_stat('defense')
        
        multiplier = self.get_type_effectiveness(move.type, defender.type)
        damage = int(((attack_stat / defense_stat) * move.power) / 5)
        damage = int(damage * multiplier * random.uniform(0.9, 1.1))

        effectiveness_msg = ""
        if multiplier > 1.0: effectiveness_msg = "It's super effective!"
        elif 0 < multiplier < 1.0: effectiveness_msg = "It's not very effective..."
        elif multiplier == 0: effectiveness_msg = "It had no effect!"
        return {'damage': max(1, damage), 'effectiveness_msg': effectiveness_msg}

    def apply_move_effects(self, attacker: Monster, defender: Monster, move: Move) -> str:
        """Applies non-damage effects like stat changes and status conditions."""
        message = ""
        # Apply Stat Changes
        if move.stat_change:
            target = attacker if move.target == 'self' else defender
            stat, amount = move.stat_change
            target.apply_stat_mod(stat, amount)
            change = "rose" if amount > 0 else "fell"
            message += f"{target.name}'s {stat} {change}!\n"
        
        # Apply Status Effects
        if move.status_effect and defender.status == 'ok':
            status, chance = move.status_effect
            if random.randint(1, 100) <= chance:
                defender.status = status
                message += f"{defender.name} is now {status}!\n"
        
        return message.strip()