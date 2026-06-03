import time
import itertools
from sapai import Team
from sapai.pets import Pet
from sapai.battle import Battle

# ==========================================
# 🛠️ 輔助工具：動物製造機與格式化工具
# ==========================================
def make_pet(pet_blueprint):
    name, atk, hp, lvl = pet_blueprint
    p = Pet(name)
    
    if lvl is not None:
        if lvl == 2:
            for _ in range(2):
                p.gain_experience()
        elif lvl == 3:
            for _ in range(5):
                p.gain_experience()
                
    if atk is not None:
        p._attack = atk
    if hp is not None:
        p._health = hp
        
    return p

def format_team_name(blueprint_list):
    names = []
    for name, atk, hp, lvl in blueprint_list:
        if atk is None and hp is None and lvl is None:
            names.append(name)
        else:
            atk_str = "?" if atk is None else atk
            hp_str = "?" if hp is None else hp
            lvl_str = "1" if lvl is None else lvl
            names.append(f"{name}({atk_str}/{hp_str}/L{lvl_str})")
    return "[" + ", ".join(names) + "]"

# ==========================================
# ⚙️ 參數區域 (定義你的神仙陣容)
# ==========================================
a = 5   # 己方隊伍總人數
n = 100  # 每種組合的模擬對戰次數

# 1. 固定班底 (核心陣容)
fixed_members = [
    ("ant", 5, 4, 2),
    ("dolphin", 7, 4, None),
    ("ant", None, None, None),
    ("spider", None, None, None),
    ("peacock", None, None, None)
]

# 2. 替補候選池 (要爭奪剩下的空位)
candidate_pool = [
]

# 敵方固定陣容
enemy_setup = [
    ("ant", 5, 4, 2),
    ("dolphin", 7, 4, None),
    ("ant", None, None, None),
    ("spider", None, None, None),
    ("peacock", None, None, None)
]

# ==========================================
# 🔍 產生並過濾所有排列組合 (全新兩階段邏輯)
# ==========================================
all_permutations = set()

# 計算需要從候選池中挑選幾隻動物
slots_to_fill = a - len(fixed_members)

if slots_to_fill > 0:
    # 階段一：從候選池中抽出 (combinations) 足夠的動物來補滿空位
    for chosen_candidates in itertools.combinations(candidate_pool, slots_to_fill):
        # 將固定成員與挑出的候選成員合併，組成 5 人陣容
        full_team = fixed_members + list(chosen_candidates)
        
        # 階段二：針對這 5 名成員，進行所有可能的站位排列 (permutations)
        for perm in itertools.permutations(full_team, a):
            all_permutations.add(perm)
elif slots_to_fill == 0:
    # 如果固定成員已經滿 5 人，直接針對固定成員進行站位排列
    for perm in itertools.permutations(fixed_members, a):
        all_permutations.add(perm)
else:
    print("⚠️ 錯誤：固定成員的數量超過了隊伍總人數！")
    exit()

print("=" * 60)
print("🧠 系統初始化中...")
print(f"己方固定成員: {format_team_name(fixed_members)}")
print(f"己方候選池: {format_team_name(candidate_pool)}")
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
    
    # 將標籤修正為 (排頭在左) 以對應陣列的第一個元素
    print(f"{medal} 第 {rank} 名 (排頭在左): {best_combo['combo_str']}")
    print(f"   📈 勝率: {best_combo['win_rate']:.1f}% ({best_combo['wins']}勝 {best_combo['draws']}平 {best_combo['losses']}敗)\n")

print("-" * 60)
print("📊 【效能與耗時統計】")
print(f"⏱️ 總耗時: {total_time:.4f} 秒")
print(f"⏱️ 陣容總數: {len(all_permutations)} 種")
print(f"⏱️ 平均耗時 (每種陣容): {avg_time_per_combo:.4f} 秒")
print(f"⏱️ 平均耗時 (每場對戰): {avg_time_per_battle:.6f} 秒")
print("=" * 60)