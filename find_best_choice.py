import os
import time
import itertools
from sapai import Team
from sapai.pets import Pet
from sapai.battle import Battle
from sapai.foods import Food  # 🌟 記得引入 Food 類別！

# ==========================================
# 🛠️ 輔助工具：動物製造機與格式化工具
# ==========================================
def parse_pet_str(ps):
    """將文字格式例如 'dolphin-[garlic](14/16/L1)' 轉換為藍圖 Tuple"""
    ps = ps.strip()
    name, atk, hp, lvl, eq = ps, None, None, None, None
    
    # 解析數值 (例如: 14/16/L1)
    if '(' in ps and ps.endswith(')'):
        name_eq_part, stats_part = ps.split('(')
        stats_part = stats_part[:-1] # 移除右括號
        name = name_eq_part
        
        parts = stats_part.split('/')
        if len(parts) == 3:
            atk = int(parts[0]) if parts[0] != '?' else None
            hp = int(parts[1]) if parts[1] != '?' else None
            lvl = int(parts[2].replace('L', '')) if parts[2] != '?' else None
            
    # 解析裝備 (例如: dolphin-[garlic])
    if '-[' in name:
        name_part, eq_part = name.split('-[')
        name = name_part
        eq = eq_part.replace(']', '')
        
    if eq:
        return (name, atk, hp, lvl, eq)
    else:
        return (name, atk, hp, lvl)

def parse_team_file(filepath):
    """讀取 txt 檔案，並轉換為敵人陣容池"""
    teams = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            
            # 移除最外層的陣列括號 []
            if line.startswith('[') and line.endswith(']'):
                line = line[1:-1]
                
            pet_strings = line.split(', ')
            team_setup = [parse_pet_str(ps) for ps in pet_strings]
            teams.append(team_setup)
    return teams

def make_pet(pet_blueprint):
    # 動態解析藍圖：支援 4 個參數 (無裝備) 或 5 個參數 (有裝備)
    if len(pet_blueprint) == 5:
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
                
    # 吃下裝備 (必須在修改基礎數值前執行)
    if eq is not None:
        p.eat(Food(eq))
                
    # 暴力覆寫數值
    if atk is not None:
        p._attack = atk
    if hp is not None:
        p._health = hp
        
    return p

def format_team_name(blueprint_list):
    names = []
    for bp in blueprint_list:
        if len(bp) == 5:
            name, atk, hp, lvl, eq = bp
        else:
            name, atk, hp, lvl = bp
            eq = None
            
        if atk is None and hp is None and lvl is None and eq is None:
            names.append(name)
        else:
            atk_str = "?" if atk is None else atk
            hp_str = "?" if hp is None else hp
            lvl_str = "1" if lvl is None else lvl
            eq_str = f"-[{eq}]" if eq else ""
            names.append(f"{name}{eq_str}({atk_str}/{hp_str}/L{lvl_str})")
            
    return "[" + ", ".join(names) + "]"

# ==========================================
# 🌟 商店階段 (EndOfTurn) 鸚鵡變身器 (靜音版)
# ==========================================
def simulate_end_of_turn(team):
    for i, slot in enumerate(team):
        if slot.empty:
            continue
            
        p = slot.pet
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

# ==========================================
# ⚙️ 參數區域 (定義你的神仙陣容)
# ==========================================
a = 5   # 己方隊伍總人數
n = 50  # 每一組己方陣容，將對戰【每一個敵人】各 n 次

# 📝 敵人檔案設定
enemy_file = "turn7_setup.txt" # 請將真實對戰記錄存於此檔案，留空 "" 則使用下方預設單一陣容

# 1. 固定班底 (核心陣容)
fixed_members = [
    ("ant", 8, 8, 3),
    ("dodo", 8, 5, None, "garlic"),
    ("giraffe", None, None, None),
    ("dog", 4, 3, None),
    ("spider", 4, 4, None)
]
# 2. 動物候選池
candidate_pool = []

# 3. 🍖 食物分配池
food_pool = [
]

# 預設敵方陣容 (檔案讀取失敗或未提供時使用)
enemy_setup = [
    ('elephant', 4, 8, 1, None),
    ('peacock', 4, 7, 2, None),
    ('hippo', 4, 6, 1, None),
    ('ant', 6, 7, 2, None),
    ('otter', 3, 7, 1, None)
]

# ==========================================
# 📂 讀取敵方天梯挑戰池 (Gauntlet)
# ==========================================
enemy_pool = []
if enemy_file and os.path.exists(enemy_file):
    print(f"📥 正在讀取敵方陣容檔案: {enemy_file}")
    enemy_pool = parse_team_file(enemy_file)
    print(f"✅ 成功載入 {len(enemy_pool)} 組敵方挑戰陣容！")
else:
    print(f"⚠️ 未找到檔案 '{enemy_file}'，使用腳本內建單一敵方陣容。")
    enemy_pool = [enemy_setup]

# ==========================================
# 🔍 產生並過濾所有排列組合 (互斥雙引擎)
# ==========================================
all_permutations = set()

if candidate_pool and food_pool:
    print("⚠️ 錯誤：為避免維度爆炸，『動物候選池』與『食物分配池』請擇一使用 (將另一個設為空陣列 [])！")
    exit()

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
        print("⚠️ 錯誤：固定成員的數量超過了隊伍總人數！")
        exit()

elif food_pool:
    if len(fixed_members) != a:
        print(f"⚠️ 錯誤：使用食物分配模式時，請先將 fixed_members 填滿 {a} 人！")
        exit()
        
    padded_foods = food_pool + [None] * (a - len(food_pool))
    unique_food_perms = set(itertools.permutations(padded_foods, a))
    
    for food_perm in unique_food_perms:
        equipped_team = []
        for pet_bp, new_food in zip(fixed_members, food_perm):
            base_stats = pet_bp[:4]
            original_food = pet_bp[4] if len(pet_bp) == 5 else None
            final_food = new_food if new_food is not None else original_food
            equipped_team.append((*base_stats, final_food))
            
        for perm in itertools.permutations(equipped_team, a):
            all_permutations.add(perm)

else:
    for perm in itertools.permutations(fixed_members, a):
        all_permutations.add(perm)

print("=" * 60)
print("🧠 系統初始化中...")
print(f"己方陣容總數: {len(all_permutations)} 種不重複的排兵布陣方式")
print(f"天梯敵人數: {len(enemy_pool)} 組不同隊伍")
print("=" * 60)

# ==========================================
# ⚔️ 執行大規模模擬
# ==========================================
results = []
# 總戰鬥次數 = 己方陣容數 * 敵方隊伍數 * 模擬次數 n
total_battles = len(all_permutations) * len(enemy_pool) * n

print(f"🚀 開始暴力破解，預計執行 {total_battles} 場對戰...\n")

start_time = time.time()

for combo_tuple in all_permutations:
    my_wins = 0
    enemy_wins = 0
    draws = 0
    
    # 🌟 對陣天梯裡面的【每一支敵方隊伍】
    for enemy_bp in enemy_pool:
        for _ in range(n):
            my_team_pets = [make_pet(blueprint) for blueprint in combo_tuple]
            enemy_team_pets = [make_pet(blueprint) for blueprint in enemy_bp]
            
            my_team = Team(my_team_pets)
            enemy_team = Team(enemy_team_pets)
            
            # 建立 Battle 物件並施加變身魔法
            battle = Battle(my_team, enemy_team)
            simulate_end_of_turn(battle.t0)
            simulate_end_of_turn(battle.t1)
            
            winner = battle.battle()
            
            if winner == 0:
                my_wins += 1
            elif winner == 1:
                enemy_wins += 1
            else:
                draws += 1
                
    # 計算這個排陣對抗「所有敵人」的綜合勝率
    total_matches_for_this_combo = len(enemy_pool) * n
    win_rate = (my_wins / total_matches_for_this_combo) * 100
    
    results.append({
        "combo_str": format_team_name(combo_tuple),
        "win_rate": win_rate,
        "wins": my_wins,
        "draws": draws,
        "losses": enemy_wins
    })

end_time = time.time()

# ==========================================
# 📊 結算與找出最佳解
# ==========================================
# 🌟 完全依照純勝率排序！(若勝率一模一樣，才用平手數當作同分的比較標準)
results.sort(key=lambda x: (x["win_rate"], x["draws"]), reverse=True)

total_time = end_time - start_time
avg_time_per_combo = total_time / len(all_permutations)
avg_time_per_battle = total_time / total_battles

top_k = 20
actual_display_count = min(top_k, len(results))

print(f"🏆 【Top {actual_display_count} 最佳組合揭曉】")
print("=" * 60)

top_results = results[:top_k]

for i, best_combo in enumerate(top_results):
    rank = i + 1
    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "🏅"
    
    print(f"{medal} 第 {rank} 名 (排頭在左): {best_combo['combo_str']}")
    print(f"   📈 勝率: {best_combo['win_rate']:.1f}% ({best_combo['wins']}勝 {best_combo['draws']}平 {best_combo['losses']}敗)\n")

print("-" * 60)
print("📊 【效能與耗時統計】")
print(f"⏱️ 總耗時: {total_time:.4f} 秒")
print(f"⏱️ 己方陣容總數: {len(all_permutations)} 種")
print(f"⏱️ 平均耗時 (每種陣容對抗全天梯): {avg_time_per_combo:.4f} 秒")
print(f"⏱️ 平均耗時 (每場對戰): {avg_time_per_battle:.6f} 秒")
print("=" * 60)