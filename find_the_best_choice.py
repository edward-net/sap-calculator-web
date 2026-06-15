import os
import time
import itertools
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
        # 用 1 限制分割次數，確保不會被意外的多餘括號干擾
        name_part, stats_part = ps.split('(', 1)
        name = name_part
        stats_part = stats_part[:-1]  # 移除最後的 ')'
        
        parts = stats_part.split('/')
        # 1. 解析基礎數值 (攻擊/血量/等級)
        if len(parts) >= 3:
            atk = int(parts[0]) if parts[0] != '?' else None
            hp = int(parts[1]) if parts[1] != '?' else None
            lvl = int(parts[2].replace('L', '')) if parts[2] != '?' else None
        
        # 2. 解析原有裝備 (如果長度 >= 4)
        if len(parts) >= 4:
            eq = parts[3] if parts[3] and parts[3] != 'none' else None
            
        # 3. 解析額外分配的食物 (如果長度 >= 5)
        if len(parts) >= 5:
            additional_food = parts[4] if parts[4] and parts[4] != 'none' else None
            
    # 根據取得的資訊，回傳對應長度的 Tuple
    if additional_food is not None:
        return (name, atk, hp, lvl, eq, additional_food)
    elif eq is not None:
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
            
            if line.startswith('[') and line.endswith(']'):
                line = line[1:-1]
                
            pet_strings = line.split(', ')
            team_setup = [parse_pet_str(ps) for ps in pet_strings]
            teams.append(team_setup)
    return teams

def make_pet(pet_blueprint):
    # 🌟 動態解析藍圖：支援 4(無), 5(有裝備), 或 6(有裝備+額外食物) 個參數
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
                
    # 1️⃣ 先暴力覆寫基礎數值 
    if atk is not None:
        p._attack = atk
    if hp is not None:
        p._health = hp
                
    # 2️⃣ 吃下固定的裝備 (例如: food-meat-bone)
    if eq is not None:
        p.eat(Food(eq))
        
    # 3️⃣ 吃下分配到的額外食物 (例如: food-pear)，數值會自動疊加上去！
    if additional_food is not None:
        p.eat(Food(additional_food))
        
    return p

def format_team_name(blueprint_list):
    """將藍圖轉換回乾淨的新格式字串"""
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
            
        # 如果是全空，只顯示名字
        if atk is None and hp is None and lvl is None and eq is None and additional_food is None:
            names.append(name)
        else:
            atk_str = "?" if atk is None else atk
            hp_str = "?" if hp is None else hp
            lvl_str = "1" if lvl is None else lvl
            
            # 基礎字串結構
            base_str = f"{name}({atk_str}/{hp_str}/L{lvl_str}"
            
            # 裝備與食物的格式化邏輯
            if additional_food:
                eq_str = eq if eq else "none"
                food_str = additional_food.replace('food-', '') # 去除前綴讓畫面更乾淨
                base_str += f"/{eq_str}/{food_str}"
            elif eq:
                base_str += f"/{eq}"
                
            base_str += ")"
            names.append(base_str)
            
    return "[" + ", ".join(names) + "]"

# ==========================================
# 🌟 商店階段 (EndOfTurn) 鸚鵡變身器 (攻擊力排序版)
# ==========================================
def simulate_end_of_turn(team):
    # 1. 蒐集場上所有動物，並記錄牠們的原始位置 (index)
    pets_with_idx = []
    for i, slot in enumerate(team):
        if not slot.empty and slot.pet.name != "pet-none" and "EMPTY" not in slot.pet.name:
            pets_with_idx.append((slot.pet, i))
            
    # 2. 按照攻擊力 (Attack) 由高到低排序，決定發動順序
    # (SAP 原版機制為攻擊力高者先發動；若攻擊力相同則隨機，這裡我們靠 Python 穩定排序即可)
    pets_with_idx.sort(key=lambda x: x[0].attack, reverse=True)
    
    # 3. 依照攻擊力順序，依序執行 End of Turn 技能
    for original_pet, i in pets_with_idx:
        p = team[i].pet  # 重新從隊伍抓取，確保拿到的還是最新的狀態
        
        if p.name == "pet-parrot":
            # 往前尋找最近的非空位隊友
            for j in range(i - 1, -1, -1):
                front_slot = team[j]
                if not front_slot.empty:
                    front_pet = front_slot.pet
                    if front_pet.name != "pet-none" and "EMPTY" not in front_pet.name:
                        # 記住鸚鵡原本的體質、等級與裝備
                        parrot_atk = p.attack
                        parrot_hp = p.health
                        parrot_lvl = p.level
                        parrot_status = p.status
                        
                        # 複製前方動物的物種
                        cloned_pet = Pet(front_pet.name)
                        
                        # 恢復鸚鵡原本的等級
                        if parrot_lvl == 2:
                            for _ in range(2): cloned_pet.gain_experience()
                        elif parrot_lvl == 3:
                            for _ in range(5): cloned_pet.gain_experience()
                            
                        # 恢復鸚鵡原本的裝備與面板
                        if parrot_status != "none":
                            cloned_pet._status = parrot_status
                        cloned_pet._attack = parrot_atk
                        cloned_pet._health = parrot_hp
                        
                        # 放回隊伍中原本的位置
                        cloned_pet.team = team
                        team[i] = cloned_pet
                        break
        # 🌟 加上 Monkey 的 End of turn 技能邏輯
        elif p.name == "pet-monkey":
            # 尋找最右邊 (index 最小) 的非空位隊友
            for j in range(5):
                front_slot = team[j]
                if not front_slot.empty and front_slot.pet.name != "pet-none" and "EMPTY" not in front_slot.pet.name:
                    # 根據猴子的等級給予 +2/+2, +4/+4, +6/+6 (依據你給的 JSON 設定)
                    buff_amount = p.level * 2
                    front_slot.pet._attack += buff_amount
                    front_slot.pet._health += buff_amount
                    # 找到最右邊的第一隻動物並給完 Buff 後就可以跳出迴圈
                    break

# ==========================================
# ⚙️ 參數區域 (定義你的神仙陣容)
# ==========================================
a = 5   # 己方隊伍總人數
n = 5  # 每一組己方陣容，將對戰【每一個敵人】各 n 次

enemy_file = "turn10_setup.txt" 

# 1. 固定班底 (核心陣容)
fixed_members = [
    ("ant", 7, 7, 2, "meat-bone"),
    ("camel", 9, 9, 2),
    ("spider", 5, 5, 2, "meat-bone"),
    ("rhino", 9, 10, 1),
    ("rooster", 8, 7, 1)
]
# 2. 動物候選池
candidate_pool = [

]

# 3. 🍖 食物分配池   (記得加 food- 前綴)
food_pool = [
    ("pear")
]
# 預設敵方陣容
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
# 🔍 產生並過濾所有排列組合
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
            original_eq = pet_bp[4] if len(pet_bp) == 5 else None
            
            # 🌟 核心修改：不再取代裝備，而是將兩者同時存進藍圖中 (變成長度 6 的 Tuple)
            equipped_team.append((*base_stats, original_eq, new_food))
            
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
total_battles = len(all_permutations) * len(enemy_pool) * n

print(f"🚀 開始暴力破解，預計執行 {total_battles} 場對戰...\n")

start_time = time.time()

for combo_tuple in all_permutations:
    my_wins = 0
    enemy_wins = 0
    draws = 0
    
    # 新增一個列表，用來儲存對上每一組敵人的詳細戰果
    enemy_details = [] 
    
    for enemy_bp in enemy_pool:
        sub_my_wins = 0
        sub_enemy_wins = 0
        sub_draws = 0
        
        # 🌟 除錯雷達：在開打前先印出正在測試的雙方陣容！
        # my_team_str = format_team_name(combo_tuple)
        # enemy_team_str = format_team_name(enemy_bp)
        # print(f"🔍 測試中: 我方 {my_team_str} ⚔️ 敵方 {enemy_team_str}")
        
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
                my_wins += 1
                sub_my_wins += 1
            elif winner == 1:
                enemy_wins += 1
                sub_enemy_wins += 1
            else:
                draws += 1
                sub_draws += 1
        
        # 計算對上這組敵人的子勝率
        sub_win_rate = (sub_my_wins / n) * 100
        enemy_details.append({
            "enemy_str": format_team_name(enemy_bp),  # 假設你的 format_team_name 也可以吃 enemy_bp
            "win_rate": sub_win_rate,
            "wins": sub_my_wins,
            "draws": sub_draws,
            "losses": sub_enemy_wins
        })
                
    total_matches_for_this_combo = len(enemy_pool) * n
    win_rate = (my_wins / total_matches_for_this_combo) * 100
    
    results.append({
        "combo_str": format_team_name(combo_tuple),
        "win_rate": win_rate,
        "wins": my_wins,
        "draws": draws,
        "losses": enemy_wins,
        "enemy_details": enemy_details  # 將詳細戰果加入 result 中
    })

end_time = time.time()

# ==========================================
# 📊 結算與找出最佳解
# ==========================================
results.sort(key=lambda x: (x["win_rate"], x["draws"]), reverse=True)

total_time = end_time - start_time
avg_time_per_combo = total_time / len(all_permutations)
avg_time_per_battle = total_time / total_battles

top_k = 20
actual_display_count = min(top_k, len(results))
top_results = results[:top_k]

# --- 1. 終端機輸出：保持簡潔的總勝率 ---
print(f"🏆 【Top {actual_display_count} 最佳組合揭曉】")
print("=" * 60)

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

# --- 2. 檔案輸出：將詳細的子勝率寫入 txt 檔案 ---
output_file = "subset-winrate.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(f"🏆 【Top {actual_display_count} 最佳組合 - 各組敵人對戰詳細結果】\n")
    f.write("=" * 60 + "\n")
    
    for i, best_combo in enumerate(top_results):
        rank = i + 1
        f.write(f"第 {rank} 名 (排頭在左): {best_combo['combo_str']}\n")
        f.write(f"總勝率: {best_combo['win_rate']:.1f}% ({best_combo['wins']}勝 {best_combo['draws']}平 {best_combo['losses']}敗)\n")
        
        f.write("  ⚔️ 對戰各組敵人詳細結果:\n")
        for j, ed in enumerate(best_combo['enemy_details']):
            f.write(f"      [{j+1}] 敵方: {ed['enemy_str']}\n")
            f.write(f"          ↳ 勝率: {ed['win_rate']:>5.1f}% ({ed['wins']:>2}勝 {ed['draws']:>2}平 {ed['losses']:>2}敗)\n")
        
        f.write("-" * 50 + "\n")

print(f"📁 已將 Top {actual_display_count} 陣容的詳細子勝率報告輸出至: {output_file}")