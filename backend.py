import os
import time
import itertools
import concurrent.futures
import logging
# 🌟 新增：引入 multiprocessing 用於跨進程通訊
import multiprocessing

# ==========================================
# 🛑 靜音設定：關閉 Streamlit 多核心切換時的無效警告
# ==========================================
logging.getLogger("streamlit.runtime.scriptrunner_utils.script_run_context").setLevel(logging.ERROR)
logging.getLogger("streamlit.runtime.state.session_state_proxy").setLevel(logging.ERROR)
logging.getLogger("streamlit").setLevel(logging.ERROR)
from sapai import Team
from sapai.pets import Pet
from sapai.battle import Battle
from sapai.foods import Food

# ==========================================
# 🛠️ 輔助工具：動物製造機與格式化工具
# ==========================================
def parse_pet_str(ps):
    """將文字格式轉換為藍圖 Tuple (支援新格式: name(atk/hp/lvl/eq/food))"""
    ps = ps.strip()
    name, atk, hp, lvl, eq, additional_food = ps, None, None, None, None, None
    
    if '(' in ps and ps.endswith(')'):
        name_part, stats_part = ps.split('(', 1)
        name = name_part
        stats_part = stats_part[:-1]
        
        parts = stats_part.split('/')
        if len(parts) >= 3:
            atk = int(parts[0]) if parts[0] != '?' else None
            hp = int(parts[1]) if parts[1] != '?' else None
            lvl = int(parts[2].replace('L', '')) if parts[2] != '?' else None
        if len(parts) >= 4:
            eq = parts[3] if parts[3] and parts[3] != 'none' else None
        if len(parts) >= 5:
            additional_food = parts[4] if parts[4] and parts[4] != 'none' else None
            
    if additional_food is not None:
        return (name, atk, hp, lvl, eq, additional_food)
    elif eq is not None:
        return (name, atk, hp, lvl, eq)
    else:
        return (name, atk, hp, lvl)

def parse_team_file(filepath):
    """讀取 txt 檔案，並轉換為陣容池 (自動過濾排名文字，精準擷取陣列)"""
    teams = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '勝率:' in line or '↳' in line: 
                continue
            
            start_idx = line.find('[')
            end_idx = line.rfind(']')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                inner_str = line[start_idx+1:end_idx].strip()
                if not inner_str:
                    continue
                    
                pet_strings = inner_str.split(', ')
                try:
                    team_setup = [parse_pet_str(ps) for ps in pet_strings]
                    teams.append(team_setup)
                except Exception as e:
                    print(f"⚠️ 解析陣容失敗，已跳過該行: {line}\n錯誤訊息: {e}")
    return teams

def make_pet(pet_blueprint):
    additional_food = None
    if len(pet_blueprint) == 6:
        name, atk, hp, lvl, eq, additional_food = pet_blueprint
    elif len(pet_blueprint) == 5:
        name, atk, hp, lvl, eq = pet_blueprint
    else:
        name, atk, hp, lvl = pet_blueprint
        eq = None

    p = Pet(name)
    
    if lvl is not None:
        if lvl == 2:
            for _ in range(2): p.gain_experience()
        elif lvl == 3:
            for _ in range(5): p.gain_experience()
                
    if atk is not None:
        p._attack = atk
    if hp is not None:
        p._health = hp
                
    if eq is not None:
        p.eat(Food(eq))
        
    if additional_food is not None:
        p.eat(Food(additional_food))
        
    return p

def format_team_name(blueprint_list):
    names = []
    for bp in blueprint_list:
        additional_food = None
        if len(bp) == 6:
            name, atk, hp, lvl, eq, additional_food = bp
        elif len(bp) == 5:
            name, atk, hp, lvl, eq = bp
        else:
            name, atk, hp, lvl = bp
            eq = None
            
        if atk is None and hp is None and lvl is None and eq is None and additional_food is None:
            names.append(name)
        else:
            atk_str = "?" if atk is None else atk
            hp_str = "?" if hp is None else hp
            lvl_str = "1" if lvl is None else lvl
            
            base_str = f"{name}({atk_str}/{hp_str}/L{lvl_str}"
            if additional_food:
                eq_str = eq if eq else "none"
                food_str = additional_food.replace('food-', '')
                base_str += f"/{eq_str}/{food_str}"
            elif eq:
                base_str += f"/{eq}"
                
            base_str += ")"
            names.append(base_str)
            
    return "[" + ", ".join(names) + "]"

def simulate_end_of_turn(team):
    pets_with_idx = []
    for i, slot in enumerate(team):
        if not slot.empty and slot.pet.name != "pet-none" and "EMPTY" not in slot.pet.name:
            pets_with_idx.append((slot.pet, i))
            
    pets_with_idx.sort(key=lambda x: x[0].attack, reverse=True)
    
    for original_pet, i in pets_with_idx:
        p = team[i].pet
        if p.name == "pet-parrot":
            for j in range(i - 1, -1, -1):
                front_slot = team[j]
                if not front_slot.empty:
                    front_pet = front_slot.pet
                    if front_pet.name != "pet-none" and "EMPTY" not in front_pet.name:
                        parrot_atk = p.attack
                        parrot_hp = p.health
                        parrot_lvl = p.level
                        parrot_status = p.status
                        
                        cloned_pet = Pet(front_pet.name)
                        
                        if parrot_lvl == 2:
                            for _ in range(2): cloned_pet.gain_experience()
                        elif parrot_lvl == 3:
                            for _ in range(5): cloned_pet.gain_experience()
                            
                        if parrot_status != "none":
                            cloned_pet._status = parrot_status
                        cloned_pet._attack = parrot_atk
                        cloned_pet._health = parrot_hp
                        
                        cloned_pet.team = team
                        team[i] = cloned_pet
                        break
                        
        elif p.name == "pet-monkey":
            for j in range(5):
                front_slot = team[j]
                if not front_slot.empty and front_slot.pet.name != "pet-none" and "EMPTY" not in front_slot.pet.name:
                    buff_amount = p.level * 2
                    front_slot.pet._attack += buff_amount
                    front_slot.pet._health += buff_amount
                    break
                    
        # 🦬 🌟 在這裡新增：野牛 (Bison) 能力邏輯
        elif p.name == "pet-bison":
            has_lvl3_friend = False
            # 遍歷隊伍尋找有沒有等級 3 的朋友
            for friend_slot in team:
                if not friend_slot.empty:
                    f_pet = friend_slot.pet
                    # 條件：必須是有效的動物，且「不能是野牛自己」
                    if f_pet != p and f_pet.name != "pet-none" and "EMPTY" not in f_pet.name:
                        if f_pet.level == 3:
                            has_lvl3_friend = True
                            break # 只要找到一隻符合條件就足夠了，跳出尋找迴圈
            
            # 如果有 3 等隊友，根據野牛自身的等級給予 Buff (+2/+2, +4/+4, +6/+6)
            if has_lvl3_friend:
                buff_amount = p.level * 2
                p._attack += buff_amount
                p._health += buff_amount

# ==========================================
# ⚡ 多核心工人函數：負責單一陣容的完整運算
# ==========================================
def worker_simulate_combo(args):
    """供 ProcessPool 呼叫的獨立函數，處理單一 combo_tuple 與所有敵人的對戰"""
    # 🌟 新增：接收 cancel_event 參數
    combo_tuple, enemy_pool, n, cancel_event = args
    
    my_wins = 0
    enemy_wins = 0
    draws = 0
    enemy_details = [] 
    
    for enemy_bp in enemy_pool:
        # 🌟 新增：定期檢查是否收到中止訊號
        if cancel_event is not None and cancel_event.is_set():
            return None # 收到中止訊號，丟下工作直接回傳 None
            
        sub_my_wins = 0
        sub_enemy_wins = 0
        sub_draws = 0
        
        for _ in range(n):
            my_team_pets = [make_pet(blueprint) for blueprint in combo_tuple]
            enemy_team_pets = [make_pet(blueprint) for blueprint in enemy_bp]
            
            my_team = Team(my_team_pets)
            enemy_team = Team(enemy_team_pets)
            
            battle = Battle(my_team, enemy_team)
            simulate_end_of_turn(battle.t0)
            simulate_end_of_turn(battle.t1)
            
            winner = battle.battle()
            
            if winner == 0:
                my_wins += 1; sub_my_wins += 1
            elif winner == 1:
                enemy_wins += 1; sub_enemy_wins += 1
            else:
                draws += 1; sub_draws += 1
        
        sub_win_rate = (sub_my_wins / n) * 100
        enemy_details.append({
            "enemy_str": format_team_name(enemy_bp),
            "win_rate": sub_win_rate,
            "wins": sub_my_wins,
            "draws": sub_draws,
            "losses": sub_enemy_wins
        })
                
    total_matches_for_this_combo = len(enemy_pool) * n
    win_rate = (my_wins / total_matches_for_this_combo) * 100
    
    return {
        "combo_str": format_team_name(combo_tuple),
        "win_rate": win_rate,
        "wins": my_wins,
        "draws": draws,
        "losses": enemy_wins,
        "enemy_details": enemy_details
    }

# ==========================================
# ⚙️ 後端 API: 接收 Config 並執行大數據模擬
# ==========================================
# 🌟 新增：允許前端傳入 cancel_event
def run_simulation(config, cancel_event=None):
    """
    接收前端傳入的 config 字典，進行隊伍生成與對戰模擬，
    並回傳結構化的戰報資料 (JSON-like dictionary)。
    """
    a = config.get("settings", {}).get("team_size", 5)
    n = config.get("settings", {}).get("n_simulations", 5)
    
    start_time = time.time()
    
    # ---------------------------------------------------------
    # 2. 準備敵方陣容 (Enemy Pool)
    # ---------------------------------------------------------
    enemy_pool = []
    enemy_config = config.get("enemy_team", {})
    
    if enemy_config.get("mode") == "file":
        filepath = enemy_config.get("file_path", "turn11_setup.txt")
        if os.path.exists(filepath):
            enemy_pool = parse_team_file(filepath)
        else:
            return {"status": "error", "message": f"找不到敵方陣容檔案: {filepath}"}
    else:
        fixed_enemy = enemy_config.get("fixed_members", [])
        if fixed_enemy:
            enemy_pool = [fixed_enemy]
        else:
            return {"status": "error", "message": "敵方手動陣容不可為空！"}

    # ---------------------------------------------------------
    # 3. 準備己方陣容 (My Team Pool)
    # ---------------------------------------------------------
    all_permutations = set()
    my_config = config.get("my_team", {})
    
    if my_config.get("mode") == "file":
        filepath = my_config.get("file_path", "setups.txt")
        if os.path.exists(filepath):
            loaded_teams = parse_team_file(filepath)
            all_permutations = {tuple(team) for team in loaded_teams}
        else:
            return {"status": "error", "message": f"找不到己方陣容檔案: {filepath}"}
            
    else:
        fixed_members = my_config.get("fixed_members", [])
        candidate_pool = my_config.get("candidate_pool", [])
        food_pool = my_config.get("food_pool", [])

        if candidate_pool and food_pool:
            return {"status": "error", "message": "為避免維度爆炸，動物候選池與食物分配池請擇一使用！"}

        if candidate_pool:
            slots_to_fill = a - len(fixed_members)
            if slots_to_fill > 0:
                for chosen in itertools.combinations(candidate_pool, slots_to_fill):
                    full_team = fixed_members + list(chosen)
                    for perm in itertools.permutations(full_team, a):
                        all_permutations.add(perm)
            elif slots_to_fill == 0:
                for perm in itertools.permutations(fixed_members, a):
                    all_permutations.add(perm)
            else:
                return {"status": "error", "message": "固定成員的數量超過了隊伍總人數！"}

        elif food_pool:
            if len(fixed_members) != a:
                return {"status": "error", "message": f"使用食物分配模式時，請先將固定陣容填滿 {a} 人！"}
                
            padded_foods = food_pool + [None] * (a - len(food_pool))
            unique_food_perms = set(itertools.permutations(padded_foods, a))
            
            for food_perm in unique_food_perms:
                equipped_team = []
                for pet_bp, new_food in zip(fixed_members, food_perm):
                    base_stats = pet_bp[:4]
                    original_eq = pet_bp[4] if len(pet_bp) >= 5 else None
                    equipped_team.append((*base_stats, original_eq, new_food))
                    
                for perm in itertools.permutations(equipped_team, a):
                    all_permutations.add(perm)
        else:
            for perm in itertools.permutations(fixed_members, a):
                all_permutations.add(perm)

    all_permutations = list(all_permutations)
    if not all_permutations:
        return {"status": "error", "message": "未能產生任何己方隊伍，請檢查輸入參數。"}

    # ---------------------------------------------------------
    # 4. 執行戰鬥模擬 (🚀 多核心火力全開版 - 支援手動中斷)
    # ---------------------------------------------------------
    results = []
    total_combos = len(all_permutations)
    total_battles = total_combos * len(enemy_pool) * n

    # 🌟 新增：將 cancel_event 包進去發給工人
    worker_args = [(combo, enemy_pool, n, cancel_event) for combo in all_permutations]
    
    max_workers = os.cpu_count() or 4 
    print(f"啟動多核心引擎：使用 {max_workers} 個 CPU 核心進行運算...")
    
    # 🌟 修改：使用 submit + as_completed，讓我們能即時監聽並攔截結果
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(worker_simulate_combo, arg) for arg in worker_args]
        
        for future in concurrent.futures.as_completed(futures):
            # 如果發現紅綠燈亮了（前端按了暫停）
            if cancel_event is not None and cancel_event.is_set():
                print("⚠️ 收到中斷訊號，正在緊急關閉進程池...")
                # 釋放資源，取消還沒開始的任務
                executor.shutdown(wait=False, cancel_futures=True)
                return {
                    "status": "cancelled", 
                    "message": "🚫 模擬已被手動中斷，已安全釋放 CPU 資源。"
                }
                
            res = future.result()
            if res is not None:
                results.append(res)

    # ---------------------------------------------------------
    # 5. 打包並回傳結構化資料
    # ---------------------------------------------------------
    end_time = time.time()
    total_time = end_time - start_time
    
    results.sort(key=lambda x: (x["win_rate"], x["draws"]), reverse=True)

    return {
        "status": "success",
        "stats": {
            "total_time": round(total_time, 4),
            "total_combinations": total_combos,
            "total_battles": total_battles,
            "avg_time_per_combo": round(total_time / total_combos if total_combos else 0, 4),
            "avg_time_per_battle": round(total_time / total_battles if total_battles else 0, 6)
        },
        "top_results": results[:20] 
    }

if __name__ == "__main__":
    print("ℹ️ backend.py 已改為後端模組，請透過前端 UI 呼叫 run_simulation() 函數。")