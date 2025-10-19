# ai/minimax.py

from game_logic.monster import Monster, Move
from game_logic.battle import Battle
import copy
import random

battle_sim = Battle()

def evaluate_state(ai_team, player_team, ai_active_mon, player_active_mon) -> float:
    """Evaluates the state considering HP, stats, status, and PP."""
    if all(mon.is_fainted for mon in player_team): return float('inf')
    if all(mon.is_fainted for mon in ai_team): return float('-inf')

    # 1. HP Advantage (most important)
    ai_hp = sum(m.current_hp / m.max_hp for m in ai_team)
    player_hp = sum(m.current_hp / m.max_hp for m in player_team)
    score = (ai_hp - player_hp) * 100

    # 2. Stat Modification Advantage
    ai_stat_mod_score = sum(ai_active_mon.stat_mods.values())
    player_stat_mod_score = sum(player_active_mon.stat_mods.values())
    score += (ai_stat_mod_score - player_stat_mod_score) * 10 # Each stage is worth 10 points

    # 3. Status Effect Advantage
    status_scores = {'ok': 0, 'poisoned': -25, 'paralyzed': -30}
    score += status_scores.get(player_active_mon.status, 0)
    score -= status_scores.get(ai_active_mon.status, 0) # AI having a status is bad for it

    # 4. PP Advantage (minor consideration)
    ai_pp = sum(m.current_pp / m.max_pp for m in ai_active_mon.moves if m.power > 0)
    player_pp = sum(m.current_pp / m.max_pp for m in player_active_mon.moves if m.power > 0)
    score += (ai_pp - player_pp) * 2

    return score + random.uniform(-0.1, 0.1)


def get_mon_by_name(team, mon_name):
    for mon in team:
        if mon.name == mon_name: return mon
    return None

def minimax(ai_team, player_team, ai_active_mon, player_active_mon, depth, alpha, beta, is_maximizing, indent=""):
    if depth == 0 or any(all(m.is_fainted for m in team) for team in [ai_team, player_team]):
        return evaluate_state(ai_team, player_team, ai_active_mon, player_active_mon), None

    if is_maximizing:
        max_eval, best_action = float('-inf'), None
        print(f"{indent}AI TURN (Depth {depth}) | Alpha: {alpha:.2f}, Beta: {beta:.2f}")

        for move in sorted(ai_active_mon.moves, key=lambda m: m.power, reverse=True):
            if move.current_pp == 0: continue

            sim_ai_team, sim_player_team = copy.deepcopy(ai_team), copy.deepcopy(player_team)
            sim_ai_mon = get_mon_by_name(sim_ai_team, ai_active_mon.name)
            sim_player_mon = get_mon_by_name(sim_player_team, player_active_mon.name)
            
            sim_ai_mon_move = next(m for m in sim_ai_mon.moves if m.name == move.name)
            sim_ai_mon_move.current_pp -= 1

            print(f"{indent}  - Simulating AI use of '{move.name}'...")
            if move.power > 0:
                damage = battle_sim.calculate_damage(sim_ai_mon, sim_player_mon, move)['damage']
                sim_player_mon.take_damage(damage)
            
            battle_sim.apply_move_effects(sim_ai_mon, sim_player_mon, move)
            
            evaluation, _ = minimax(sim_ai_team, sim_player_team, sim_ai_mon, sim_player_mon, depth - 1, alpha, beta, False, indent + "    ")
            print(f"{indent}  '{move.name}' resulted in a board score of: {evaluation:.2f}")

            if evaluation > max_eval: max_eval, best_action = evaluation, move
            alpha = max(alpha, evaluation)
            if beta <= alpha: print(f"{indent}  >> PRUNING (Beta {beta:.2f} <= Alpha {alpha:.2f})"); break
        
        return max_eval, best_action or ai_active_mon.moves[0]
    
    else: # Minimizing Player
        min_eval, best_action = float('inf'), None
        print(f"{indent}PLAYER TURN (Depth {depth}) | Alpha: {alpha:.2f}, Beta: {beta:.2f}")

        for move in sorted(player_active_mon.moves, key=lambda m: m.power, reverse=True):
            if move.current_pp == 0: continue
            
            sim_ai_team, sim_player_team = copy.deepcopy(ai_team), copy.deepcopy(player_team)
            sim_ai_mon = get_mon_by_name(sim_ai_team, ai_active_mon.name)
            sim_player_mon = get_mon_by_name(sim_player_team, player_active_mon.name)
            
            sim_player_mon_move = next(m for m in sim_player_mon.moves if m.name == move.name)
            sim_player_mon_move.current_pp -= 1
            
            print(f"{indent}  - Simulating Player use of '{move.name}'...")
            if move.power > 0:
                damage = battle_sim.calculate_damage(sim_player_mon, sim_ai_mon, move)['damage']
                sim_ai_mon.take_damage(damage)

            battle_sim.apply_move_effects(sim_player_mon, sim_ai_mon, move)

            evaluation, _ = minimax(sim_ai_team, sim_player_team, sim_ai_mon, sim_player_mon, depth - 1, alpha, beta, True, indent + "    ")

            if evaluation < min_eval: min_eval, best_action = evaluation, move
            beta = min(beta, evaluation)
            if beta <= alpha: print(f"{indent}  >> PRUNING (Beta {beta:.2f} <= Alpha {alpha:.2f})"); break
        
        return min_eval, best_action or player_active_mon.moves[0]

def find_best_action(ai_team, player_team, ai_active_mon, player_active_mon, depth=3):
    print("\n--- AI IS THINKING (SIMULATION START) ---")
    _, best_move = minimax(ai_team, player_team, ai_active_mon, player_active_mon, depth=depth, alpha=float('-inf'), beta=float('inf'), is_maximizing=True)
    print(f"--- SIMULATION END: AI DECIDED TO ATTACK WITH '{best_move.name}' ---\n")
    return best_move