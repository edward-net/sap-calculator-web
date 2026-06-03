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
# 🌟 新增：商店階段 (EndOfTurn) 鸚鵡變身器 (靜音版)
# ==========================================
def simulate_end_of_turn(team):
    """手動觸發商店結算，直接將鸚鵡替換成前方的動物！(為追求效能已移除 print)"""
    for i, slot in enumerate(team):
        if slot.empty:
            continue
            
        p = slot.pet
        if p.name == "pet-parrot":
            # 往前方 (靠近排頭 0 的方向) 尋找隊友
            for j in range(i - 1, -1, -1):
                front_slot = team[j]
                if not front_slot.empty:
                    front_pet = front_slot.pet
                    if front_pet.name != "pet-none" and "EMPTY" not in front_pet.name:
                        
                        # 1. 記錄鸚鵡原本的狀態
                        parrot_atk = p.attack
                        parrot_hp = p.health
                        parrot_lvl = p.level
                        parrot_status = p.status
                        
                        # 2. 製造一隻全新的「前方隊友」
                        cloned_pet = Pet(front_pet.name)
                        
                        # 3. 讓複製出來的動物達到鸚鵡的星級
                        if parrot_lvl == 2:
                            for _ in range(2): cloned_pet.gain_experience()
                        elif parrot_lvl == 3:
                            for _ in range(5): cloned_pet.gain_experience()
                            
                        # 4. 把裝備、攻擊力與血量，強制設定成鸚鵡原本的數值
                        if parrot_status != "none":
                            cloned_pet._status = parrot_status
                        cloned_pet._attack = parrot_atk
                        cloned_pet._health = parrot_hp
                        
                        # 5. 接上神經網絡並偷天換日
                        cloned_pet.team = team
                        team[i] = cloned_pet
                        break

# ==========================================
# ⚙️ 參數區域 (定義你的神仙陣容)
# ==========================================
a = 5   # 己方隊伍總人數
n = 100  # 每種組合的模擬對戰次數

# 1. 固定班底 (核心陣容)
fixed_members = [
    ("turtle", 7, 10, 2),
    ("ant", 8, 10, 3),
    ("hippo", 8, 10, 2),
    ("peacock", 10, 13, 2),
    ("gorilla", 8, 11, None)
]

# 2. 動物候選池 (要爭奪剩下的空位，此處留空啟用食物模式)
candidate_pool = [

]

# 3. 🍖 食物分配池 (測試裝備該給誰)
food_pool = [
    ("chili")
]

# 敵方固定陣容
enemy_setup = [
    ("mammoth", 4, 12, None),
    ("dolphin", 14, 16, None, "garlic"),
    ("ant", 10, 10, 3, "garlic"),
    ("crocodile", 9, 14, None),
    ("deer", 8, 11, 2),
]

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
        
        # 🚨 關鍵攔截點：先建立 Battle 物件，再對複製人軍團施加魔法！
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
# 📊 結算與找出最佳解
# ==========================================
results.sort(key=lambda x: (x["win_rate"], x["draws"]), reverse=True)

total_time = end_time - start_time
avg_time_per_combo = total_time / len(all_permutations)
avg_time_per_battle = total_time / total_battles

# 🌟 在這裡設定你想看前幾名！(例如改為 20, 50, 或 100)
top_k = 20

# 如果總組合數比你想看的還少，就以實際數量為準
actual_display_count = min(top_k, len(results))

print(f"🏆 【Top {actual_display_count} 最佳組合揭曉】")
print("=" * 60)

# 使用切片 (slice) 語法取出前 top_k 名
top_results = results[:top_k]

for i, best_combo in enumerate(top_results):
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