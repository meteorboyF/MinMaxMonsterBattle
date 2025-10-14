# ai/minimax.py

from game_logic.monster import Monster, Move
from game_logic.battle import Battle
import copy

battle_sim = Battle()

def evaluate_state(ai_monster: Monster, player_monster: Monster) -> float:
    if player_monster.is_fainted: return float('inf')
    if ai_monster.is_fainted: return float('-inf')
    hp_advantage = (ai_monster.current_hp / ai_monster.max_hp) - (player_monster.current_hp / player_monster.max_hp)
    type_advantage = 0
    best_ai_multiplier = max(battle_sim.get_type_effectiveness(move.type, player_monster.type) for move in ai_monster.moves)
    best_player_multiplier = max(battle_sim.get_type_effectiveness(move.type, ai_monster.type) for move in player_monster.moves)
    if best_ai_multiplier > best_player_multiplier: type_advantage = 0.5
    elif best_player_multiplier > best_ai_multiplier: type_advantage = -0.5
    return (hp_advantage * 2) + type_advantage

def minimax(ai_monster: Monster, player_monster: Monster, depth: int, alpha: float, beta: float, is_maximizing: bool, indent=""):
    if depth == 0 or ai_monster.is_fainted or player_monster.is_fainted:
        return evaluate_state(ai_monster, player_monster), None

    if is_maximizing:
        max_eval = float('-inf')
        best_move = None
        print(f"{indent}Maximizer Node (AI), alpha={alpha}, beta={beta}")
        for move in ai_monster.moves:
            sim_player = copy.deepcopy(player_monster)
            damage = battle_sim.calculate_damage(ai_monster, sim_player, move)['damage']
            sim_player.take_damage(damage)
            print(f"{indent}  - Considering move: {move.name}")
            evaluation, _ = minimax(ai_monster, sim_player, depth - 1, alpha, beta, False, indent + "    ")
            print(f"{indent}  - Move {move.name} scored: {evaluation}")
            if evaluation > max_eval: max_eval = evaluation; best_move = move
            alpha = max(alpha, evaluation)
            if beta <= alpha: print(f"{indent}  ** PRUNING ** (beta={beta} <= alpha={alpha})"); break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = None
        print(f"{indent}Minimizer Node (Player), alpha={alpha}, beta={beta}")
        for move in player_monster.moves:
            sim_ai = copy.deepcopy(ai_monster)
            damage = battle_sim.calculate_damage(player_monster, sim_ai, move)['damage']
            sim_ai.take_damage(damage)
            print(f"{indent}  - Considering opponent move: {move.name}")
            evaluation, _ = minimax(sim_ai, player_monster, depth - 1, alpha, beta, True, indent + "    ")
            print(f"{indent}  - Opponent move {move.name} scored: {evaluation}")
            if evaluation < min_eval: min_eval = evaluation; best_move = move
            beta = min(beta, evaluation)
            if beta <= alpha: print(f"{indent}  ** PRUNING ** (beta={beta} <= alpha={alpha})"); break
        return min_eval, best_move

def find_best_move(ai_monster: Monster, player_monster: Monster, depth: int = 3) -> Move:
    print("\n--- AI IS THINKING ---")
    _, best_move = minimax(ai_monster, player_monster, depth, float('-inf'), float('inf'), True)
    if best_move is None:
        print(f"--- MINIMAX RETURNED NONE, DEFAULTING TO FIRST MOVE ---")
        best_move = ai_monster.moves[0]
    print(f"--- AI DECIDED ON: {best_move.name} ---\n")
    return best_move