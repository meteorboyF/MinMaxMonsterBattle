# ai/minimax.py

from game_logic.monster import Monster, Move
from game_logic.battle import Battle
import copy
import random

battle_sim = Battle()

def evaluate_state(ai_team, player_team, ai_active_mon, player_active_mon) -> float:
    """Evaluates the state based on the entire team's health and current matchup."""
    if all(mon.is_fainted for mon in player_team): return float('inf')
    if all(mon.is_fainted for mon in ai_team): return float('-inf')

    ai_total_hp = sum(mon.current_hp / mon.max_hp for mon in ai_team)
    player_total_hp = sum(mon.current_hp / mon.max_hp for mon in player_team)
    hp_advantage = ai_total_hp - player_total_hp

    type_advantage = 0
    if not ai_active_mon.is_fainted and not player_active_mon.is_fainted:
        ai_move_types = [move.type for move in ai_active_mon.moves]
        player_move_types = [move.type for move in player_active_mon.moves]
        
        best_ai_multiplier = max((battle_sim.get_type_effectiveness(move_type, player_active_mon.type) for move_type in ai_move_types), default=1.0)
        best_player_multiplier = max((battle_sim.get_type_effectiveness(move_type, ai_active_mon.type) for move_type in player_move_types), default=1.0)

        if best_ai_multiplier > best_player_multiplier: type_advantage = 0.5
        if best_ai_multiplier > 1.0 and best_player_multiplier <= 1.0: type_advantage = 1.0
        if best_player_multiplier > best_ai_multiplier: type_advantage = -0.5
        if best_player_multiplier > 1.0 and best_ai_multiplier <= 1.0: type_advantage = -1.0
    
    return (hp_advantage * 2) + type_advantage + random.uniform(-0.01, 0.01)

def get_mon_by_name(team, mon_name):
    """Utility to safely find a monster by its name in a list of monsters."""
    for mon in team:
        if mon.name == mon_name:
            return mon
    return None

def minimax(ai_team, player_team, ai_active_mon, player_active_mon, depth, alpha, beta, is_maximizing):
    """Minimax with Alpha-Beta Pruning. Returns an identifier for switches."""
    if depth == 0 or any(all(m.is_fainted for m in team) for team in [ai_team, player_team]):
        return evaluate_state(ai_team, player_team, ai_active_mon, player_active_mon), None

    if is_maximizing:
        max_eval = float('-inf')
        best_action = None
        
        # --- Option 1: Attack ---
        if not ai_active_mon.is_fainted:
            for move in ai_active_mon.moves:
                sim_ai_team = copy.deepcopy(ai_team)
                sim_player_team = copy.deepcopy(player_team)
                sim_ai_mon = get_mon_by_name(sim_ai_team, ai_active_mon.name)
                sim_player_mon = get_mon_by_name(sim_player_team, player_active_mon.name)
                
                damage = battle_sim.calculate_damage(sim_ai_mon, sim_player_mon, move)['damage']
                sim_player_mon.take_damage(damage)
                
                evaluation, _ = minimax(sim_ai_team, sim_player_team, sim_ai_mon, sim_player_mon, depth - 1, alpha, beta, False)
                if evaluation > max_eval:
                    max_eval = evaluation
                    best_action = move
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
        
        # --- Option 2: Switch ---
        if beta > alpha:
            for mon in ai_team:
                if mon.name != ai_active_mon.name and not mon.is_fainted:
                    sim_ai_team = copy.deepcopy(ai_team)
                    sim_player_team = copy.deepcopy(player_team)
                    sim_new_ai_mon = get_mon_by_name(sim_ai_team, mon.name)
                    sim_player_mon = get_mon_by_name(sim_player_team, player_active_mon.name)
                    
                    evaluation, _ = minimax(sim_ai_team, sim_player_team, sim_new_ai_mon, sim_player_mon, depth - 1, alpha, beta, False)
                    if evaluation > max_eval:
                        max_eval = evaluation
                        # *** FIX: Return the monster's NAME, not the copied object ***
                        best_action = ('switch', mon.name)
                    alpha = max(alpha, evaluation)
                    if beta <= alpha:
                        break
        
        return max_eval, best_action
    
    else: # Minimizing Player
        min_eval = float('inf')
        best_action = None
        
        if player_active_mon.is_fainted:
            return minimax(ai_team, player_team, ai_active_mon, player_active_mon, depth - 1, alpha, beta, True)

        for move in player_active_mon.moves:
            sim_ai_team = copy.deepcopy(ai_team)
            sim_player_team = copy.deepcopy(player_team)
            sim_ai_mon = get_mon_by_name(sim_ai_team, ai_active_mon.name)
            sim_player_mon = get_mon_by_name(sim_player_team, player_active_mon.name)

            damage = battle_sim.calculate_damage(sim_player_mon, sim_ai_mon, move)['damage']
            sim_ai_mon.take_damage(damage)
            
            evaluation, _ = minimax(sim_ai_team, sim_player_team, sim_ai_mon, sim_player_mon, depth - 1, alpha, beta, True)
            if evaluation < min_eval:
                min_eval = evaluation
                best_action = move
            beta = min(beta, evaluation)
            if beta <= alpha:
                break
        
        return min_eval, best_action

def find_best_action(ai_team, player_team, ai_active_mon, player_active_mon, depth=3):
    """Finds the best action (either a Move object or a ('switch', 'monster_name') tuple)."""
    print("\n--- AI TRAINER IS THINKING ---")
    _, best_action = minimax(ai_team, player_team, ai_active_mon, player_active_mon, depth=depth, alpha=float('-inf'), beta=float('inf'), is_maximizing=True)
    
    if best_action is None:
        print(f"--- MINIMAX RETURNED NONE, DEFAULTING TO FIRST VALID ACTION ---")
        if not ai_active_mon.is_fainted:
            return ai_active_mon.moves[0]
        else:
            next_mon = next((m for m in ai_team if not m.is_fainted), None)
            if next_mon:
                return ('switch', next_mon.name)
            return ai_active_mon.moves[0] # Should be unreachable

    if isinstance(best_action, Move):
        print(f"--- AI DECIDED TO ATTACK WITH: {best_action.name} ---\n")
    elif isinstance(best_action, tuple):
        print(f"--- AI DECIDED TO SWITCH TO: {best_action[1]} ---\n")
        
    return best_action