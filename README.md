# Minimax Monster Battle 2.0

An enhanced AI-powered Monster Battle game using Pygame and Minimax algorithm.

## Features

- **Smart AI**: The opponent uses a Minimax algorithm with Alpha-Beta pruning to decide the best moves, including switching monsters when at a disadvantage.
- **Expanded Roster**: Choose from and battle against a variety of monsters including:
  - Starters: Squirtle, Charmander, Bulbasaur
  - Classics: Pikachu, Pidgeotto, Geodude, Gastly, Oddish, Vulpix, Snorlax
- **Strategic Combat**: 
  - **Type Effectiveness**: Complex type chart implementation (Water > Fire, ghost immunity to Normal, etc.).
  - **Status Effects**: Poison and Paralysis mechanics.
  - **Stat Modifiers**: Moves can buff/debuff stats.
  - **Switching**: Strategic switching for both Player and AI.
- **Campaign Mode**: Battle through a series of opponents to become the champion.

## Installation & Running

1. **Install Dependencies**:
   ```bash
   pip install pygame
   ```

2. **Run the Game**:
   ```bash
   python main_pygame.py
   ```

## Controls

- **Mouse**: Select moves, switch monsters, and navigate menus.

## Technical Details

- **AI Engine**: `ai/minimax.py` implements a depth-limited Minimax search with heuristic evaluation of HP, status, and stats.
- **Game Logic**: Separated into `game_manager.py`, `battle.py`, and `monster.py`.
- **Assets**: Custom pixel art sprites for monsters.

Enjoy the battle!
