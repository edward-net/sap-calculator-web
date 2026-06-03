import time
import itertools
from sapai import Team
from sapai.pets import Pet
from sapai.battle import Battle

# ==========================================
# 🛠️ 輔助工具：動物製造機與格式化工具
# ==========================================
def make_pet(pet_blueprint):
    """
    根據藍圖製造一隻全新的動物。
    藍圖格式為 Tuple: (名稱, 攻擊力, 生命值, 星級)
    若數值填寫 None，則使用原廠預設值。
    """
    name, atk, hp, lvl = pet_blueprint
    p = Pet(name)
    
    # 🚨 破解唯讀限制：加上底線直接修改底層變數
    if atk is not None:
        p._attack = atk
    if hp is not None:
        p._health = hp
    if lvl is not None:
        p._level = lvl
        
    return p

def format_team_name(blueprint_list):
    """將藍圖轉換成方便閱讀的字串，例如: ant(5/5/L2)"""
    names = []
    for name, atk, hp, lvl in blueprint_list:
        # 如果都是 None，代表是預設的白板動物
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
# 藍圖格式: ("動物名稱", 攻擊力, 生命值, 星級)
# 若想使用原廠設定，請填入 None

# 己方候選池
candidate_pool = [
    ("ant", 3, 3, None),   
    ("ant", None, None, None),    
    ("ant", None, None, None),
    ("beaver", None, None, None),
    ("beaver", None, None, None)
]

a = 5   # 己方隊伍人數 (上陣人數)
n = 100  # 每種組合的模擬對戰次數

# 敵方固定陣容
enemy_setup = [
    ("beaver", None, None, None),
    ("ant", None, None, None),
    ("ant", 3, 3, None),
    ("beaver", None, None, None),
    ("ant", None, None, None)
]

# ==========================================
# 🔍 產生並過濾所有排列組合
# ==========================================
# 使用 set() 來自動去除相同數值的動物 (例如互換兩隻標準海狸) 造成的重複組合
all_permutations = set(itertools.permutations(candidate_pool, a))

print("=" * 60)
print("🧠 系統初始化中...")
print(f"己方上陣: {a} 隻 | 敵方陣容: {format_team_name(enemy_setup)}")
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
    
    # 針對這個特定的陣容，進行 n 次對戰
    for _ in range(n):
        # 🚨 關鍵：每一場對戰前，都依照「藍圖」重新製造一批全新、滿血的動物
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
            
    # 儲存此陣容的戰績
    win_rate = (my_wins / n) * 100
    results.append({
        "combo_str": format_team_name(combo_tuple), # 轉成漂亮字串方便顯示
        "win_rate": win_rate,
        "wins": my_wins,
        "draws": draws,
        "losses": enemy_wins
    })

end_time = time.time()

# ==========================================
# 📊 結算與找出最佳解 (Top 10)
# ==========================================
# 排序邏輯：優先比勝率 (由高到低) -> 再比平手次數 (平手總比輸好)
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
    
    print(f"{medal} 第 {rank} 名 (排頭在右): {best_combo['combo_str']}")
    print(f"   📈 勝率: {best_combo['win_rate']:.1f}% ({best_combo['wins']}勝 {best_combo['draws']}平 {best_combo['losses']}敗)\n")

print("-" * 60)
print("📊 【效能與耗時統計】")
print(f"⏱️ 總耗時: {total_time:.4f} 秒")
print(f"⏱️ 陣容總數: {len(all_permutations)} 種")
print(f"⏱️ 平均耗時 (每種陣容): {avg_time_per_combo:.4f} 秒")
print(f"⏱️ 平均耗時 (每場對戰): {avg_time_per_battle:.6f} 秒")
print("=" * 60)