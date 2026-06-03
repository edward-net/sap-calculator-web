import time
import itertools
from sapai import Team
from sapai.pets import Pet
from sapai.battle import Battle
from sapai.foods import Food  # 🌟 記得引入 Food 類別！

# ==========================================
# 🛠️ 輔助工具：動物製造機與格式化工具
# ==========================================
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
                
    # 2. 🍖 吃下裝備 (必須在修改基礎數值前執行)
    if eq is not None:
        p.eat(Food(eq))
                
    # 3. 🚨 暴力覆寫數值
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
# ⚙️ 參數區域 (定義你的神仙陣容)
# ==========================================
a = 5   # 己方隊伍總人數
n = 50  # 每種組合的模擬對戰次數

# 1. 固定班底 (核心陣容)
fixed_members = [
    ("dolphin", 7, 4, None),
    ("deer", None, None, None),
    ("ant", 8, 7, 3), 
    ("peacock", None, None, None),
    ("spider", None, None, None)
]

# 2. 動物候選池 (要爭奪剩下的空位，此處留空啟用食物模式)
candidate_pool = [

]

# 3. 🍖 食物分配池 (測試裝備該給誰)
# ⚠️ 注意：動物候選池與食物分配池不可同時有值！
food_pool = [

]

# 敵方固定陣容
enemy_setup = [
    ("dolphin", 7, 4, None),
    ("deer", None, None, None),
    ("ant", 8, 7, 3), 
    ("peacock", None, None, None),
    ("spider", None, None, None)
]

# ==========================================
# 🔍 產生並過濾所有排列組合 (互斥雙引擎)
# ==========================================
all_permutations = set()

# 安全機制：防止計算量爆炸
if candidate_pool and food_pool:
    print("⚠️ 錯誤：為避免維度爆炸，『動物候選池』與『食物分配池』請擇一使用 (將另一個設為空陣列 [])！")
    exit()

# --------------------------
# 模式 A：動物替補選拔模式
# --------------------------
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

# --------------------------
# 模式 B：食物最高效分配模式
# --------------------------
elif food_pool:
    if len(fixed_members) != a:
        print(f"⚠️ 錯誤：使用食物分配模式時，請先將 fixed_members 填滿 {a} 人！")
        exit()
        
    # 將食物池補齊至隊伍人數 (用 None 填補空缺)
    padded_foods = food_pool + [None] * (a - len(food_pool))
    
    # 計算出食物分配的所有不重複可能性
    unique_food_perms = set(itertools.permutations(padded_foods, a))
    
    for food_perm in unique_food_perms:
        equipped_team = []
        for pet_bp, new_food in zip(fixed_members, food_perm):
            # 擷取動物基礎數值 (前4個參數)
            base_stats = pet_bp[:4]
            # 如果動物原本就有帶裝備，但被分配到 None，則保留原裝備；否則強制換上新裝備
            original_food = pet_bp[4] if len(pet_bp) == 5 else None
            final_food = new_food if new_food is not None else original_food
            
            equipped_team.append((*base_stats, final_food))
            
        # 產生這個食物分配下的所有站位可能性
        for perm in itertools.permutations(equipped_team, a):
            all_permutations.add(perm)

# --------------------------
# 模式 C：純排隊模式 (無替補、無分配食物)
# --------------------------
else:
    for perm in itertools.permutations(fixed_members, a):
        all_permutations.add(perm)

print("=" * 60)
print("🧠 系統初始化中...")
print(f"己方固定成員: {format_team_name(fixed_members)}")
print(f"動物候選池: {format_team_name(candidate_pool) if candidate_pool else '未啟用'}")
print(f"食物分配池: {food_pool if food_pool else '未啟用'}")
print(f"敵方陣容: {format_team_name(enemy_setup)}")
print(f"過濾重複後，共有 {len(all_permutations)} 種不重複的排兵布陣方式！")
print("=" * 60)

# ==========================================
# ⚔️ 執行大規模模擬
# ==========================================
results = []
total_battles = len(all_permutations) * n

print(f"🚀 開始暴力破解，預計執行 {total_battles} 場對戰...\n")

start_time = time.time()

for combo_tuple in all_permutations:
    my_wins = 0
    enemy_wins = 0
    draws = 0
    
    for _ in range(n):
        my_team_pets = [make_pet(blueprint) for blueprint in combo_tuple]
        enemy_team_pets = [make_pet(blueprint) for blueprint in enemy_setup]
        
        my_team = Team(my_team_pets)
        enemy_team = Team(enemy_team_pets)
        
        battle = Battle(my_team, enemy_team)
        winner = battle.battle()
        
        if winner == 0:
            my_wins += 1
        elif winner == 1:
            enemy_wins += 1
        else:
            draws += 1
            
    win_rate = (my_wins / n) * 100
    results.append({
        "combo_str": format_team_name(combo_tuple),
        "win_rate": win_rate,
        "wins": my_wins,
        "draws": draws,
        "losses": enemy_wins
    })

end_time = time.time()

# ==========================================
# 📊 結算與找出最佳解 (Top 10)
# ==========================================
results.sort(key=lambda x: (x["win_rate"], x["draws"]), reverse=True)

total_time = end_time - start_time
avg_time_per_combo = total_time / len(all_permutations)
avg_time_per_battle = total_time / total_battles

print("🏆 【Top 10 最佳組合揭曉】")
print("=" * 60)

top_10_results = results[:10]

for i, best_combo in enumerate(top_10_results):
    rank = i + 1
    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "🏅"
    
    print(f"{medal} 第 {rank} 名 (排頭在左): {best_combo['combo_str']}")
    print(f"   📈 勝率: {best_combo['win_rate']:.1f}% ({best_combo['wins']}勝 {best_combo['draws']}平 {best_combo['losses']}敗)\n")

print("-" * 60)
print("📊 【效能與耗時統計】")
print(f"⏱️ 總耗時: {total_time:.4f} 秒")
print(f"⏱️ 陣容總數: {len(all_permutations)} 種")
print(f"⏱️ 平均耗時 (每種陣容): {avg_time_per_combo:.4f} 秒")
print(f"⏱️ 平均耗時 (每場對戰): {avg_time_per_battle:.6f} 秒")
print("=" * 60)