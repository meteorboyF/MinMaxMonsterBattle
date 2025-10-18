# ai/minimax.py

from game_logic.monster import Monster, Move
from game_logic.battle import Battle
import copy
import random

battle_sim = Battle()

def evaluate_state(ai_team, player_team, ai_active_mon, player_active_mon) -> float:
    """Evaluates the state based on team health and the current active matchup."""
    if all(mon.is_fainted for mon in player_team): return float('inf')
    if all(mon.is_fainted for mon in ai_team): return float('-inf')

    ai_total_hp = sum(mon.current_hp / mon.max_hp for mon in ai_team)
    player_total_hp = sum(mon.current_hp / mon.max_hp for mon in player_team)
    hp_advantage = ai_total_hp - player_total_hp

    type_advantage = 0
    if not ai_active_mon.is_fainted and not player_active_mon.is_fainted:
        ai_move_types = [move.type for move in ai_active_mon.moves]
        best_ai_multiplier = max((battle_sim.get_type_effectiveness(move_type, player_active_mon.type) for move_type in ai_move_types), default=1.0)
        
        player_move_types = [move.type for move in player_active_mon.moves]
        best_player_multiplier = max((battle_sim.get_type_effectiveness(move_type, ai_active_mon.type) for move_type in player_move_types), default=1.0)
        
        type_advantage = best_ai_multiplier - best_player_multiplier

    return (hp_advantage * 100) + (type_advantage * 10) + random.uniform(-0.1, 0.1)

def get_mon_by_name(team, mon_name):
    """Utility to find a monster by its name in a list of monsters."""
    for mon in team:
        if mon.name == mon_name: return mon
    return None

def minimax(ai_team, player_team, ai_active_mon, player_active_mon, depth, alpha, beta, is_maximizing, indent=""):
    """Minimax with a more nuanced heuristic to favor stronger moves."""
    if depth == 0 or any(all(m.is_fainted for m in team) for team in [ai_team, player_team]):
        return evaluate_state(ai_team, player_team, ai_active_mon, player_active_mon), None

    if is_maximizing:
        max_eval = float('-inf')
        best_action = None
        print(f"{indent}AI TURN (Depth {depth}) | Alpha: {alpha:.2f}, Beta: {beta:.2f}")

        for move in sorted(ai_active_mon.moves, key=lambda m: m.power, reverse=True): # Prioritize checking stronger moves
            sim_ai_team = copy.deepcopy(ai_team)
            sim_player_team = copy.deepcopy(player_team)
            sim_ai_mon = get_mon_by_name(sim_ai_team, ai_active_mon.name)
            sim_player_mon = get_mon_by_name(sim_player_team, player_active_mon.name)

            damage = battle_sim.calculate_damage(sim_ai_mon, sim_player_mon, move)['damage']
            sim_player_mon.take_damage(damage)
            
            print(f"{indent}  - Simulating AI attack with '{move.name}' (Power: {move.power})...")
            
            evaluation, _ = minimax(sim_ai_team, sim_player_team, sim_ai_mon, sim_player_mon, depth - 1, alpha, beta, False, indent + "    ")
            
            # *** NEW: Add a small bonus for using a more powerful move ***
            evaluation += move.power * 0.01 
            
            print(f"{indent}  '{move.name}' resulted in a board score of: {evaluation:.2f}")

            if evaluation > max_eval:
                max_eval = evaluation
                best_action = move
            
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                print(f"{indent}  >> PRUNING! (Beta {beta:.2f} <= Alpha {alpha:.2f}).")
                break
        
        return max_eval, best_action or ai_active_mon.moves[0]
    
    else: # Minimizing Player
        min_eval = float('inf')
        best_action = None
        print(f"{indent}PLAYER TURN (Depth {depth}) | Alpha: {alpha:.2f}, Beta: {beta:.2f}")

        for move in sorted(player_active_mon.moves, key=lambda m: m.power, reverse=True):
            sim_ai_team = copy.deepcopy(ai_team)
            sim_player_team = copy.deepcopy(player_team)
            sim_ai_mon = get_mon_by_name(sim_ai_team, ai_active_mon.name)
            sim_player_mon = get_mon_by_name(sim_player_team, player_active_mon.name)

            damage = battle_sim.calculate_damage(sim_player_mon, sim_ai_mon, move)['damage']
            sim_ai_mon.take_damage(damage)

            print(f"{indent}  - Simulating Player counter-attack with '{move.name}'...")
            
            evaluation, _ = minimax(sim_ai_team, sim_player_team, sim_ai_mon, sim_player_mon, depth - 1, alpha, beta, True, indent + "    ")

            if evaluation < min_eval:
                min_eval = evaluation
                best_action = move
            
            beta = min(beta, evaluation)
            if beta <= alpha:
                print(f"{indent}  >> PRUNING! (Beta {beta:.2f} <= Alpha {alpha:.2f}).")
                break
        
        return min_eval, best_action or player_active_mon.moves[0]

def find_best_action(ai_team, player_team, ai_active_mon, player_active_mon, depth=3):
    """Finds the best ATTACK move for the AI."""
    print("\n--- AI IS THINKING (SIMULATION START) ---")
    _, best_move = minimax(ai_team, player_team, ai_active_mon, player_active_mon, depth=depth, alpha=float('-inf'), beta=float('inf'), is_maximizing=True)
    
    print(f"--- SIMULATION END: AI DECIDED TO ATTACK WITH '{best_move.name}' ---\n")
    return best_move