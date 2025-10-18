# game_logic/monster.py

class Move:
    """A class to represent a move with a name, type, power, and accuracy."""
    def __init__(self, name: str, move_type: str, power: int, accuracy: int = 100):
        self.name = name
        self.type = move_type
        self.power = power
        self.accuracy = accuracy

class Monster:
    """A class to represent a monster with stats, types, and moves."""
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

    def take_damage(self, damage: int):
        """Applies damage and checks if the monster has fainted."""
        self.current_hp -= damage
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_fainted = True

    def __repr__(self):
        return f"<Monster: {self.name}, HP: {self.current_hp}/{self.max_hp}>"