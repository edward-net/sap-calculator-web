import os
import pprint 

# 確保 Graphviz 路徑
graphviz_bin_path = r"C:\Program Files\Graphviz\bin"
os.environ["PATH"] += os.pathsep + graphviz_bin_path

from sapai import Team
from sapai.pets import Pet
from sapai.battle import Battle
from sapai.foods import Food  # 🌟 記得在最上方引入 Food 類別！

# ==========================================
# 🛠️ 輔助函式：根據藍圖製造自訂數值的動物 (🌟 已支援 additional_food)
# ==========================================
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
    
    # 1. 🌟 升級技能
    if lvl is not None:
        if lvl == 2:
            for _ in range(2): p.gain_experience()
        elif lvl == 3:
            for _ in range(5): p.gain_experience()
            
    # 2. 🚨 修改基礎數值 (暴力覆寫)
    if atk is not None:
        p._attack = atk
    if hp is not None:
        p._health = hp
            
    # 3. 🍖 穿上裝備 (例如: food-meat-bone)
    if eq is not None:
        p.eat(Food(eq))

    # 4. 🍎 🌟 吃下分配到的額外食物 (例如: food-bread)，數值會自動疊加上去！
    if additional_food is not None:
        p.eat(Food(additional_food))

    return p

# ==========================================
# 🌟 商店階段 (EndOfTurn) 技能觸發器 (攻擊力排序版)
# ==========================================
def simulate_end_of_turn(team):
    # 1. 蒐集場上所有動物，並記錄牠們的原始位置 (index)
    pets_with_idx = []
    for i, slot in enumerate(team):
        if not slot.empty and slot.pet.name != "pet-none" and "EMPTY" not in slot.pet.name:
            pets_with_idx.append((slot.pet, i))
            
    # 2. 按照攻擊力 (Attack) 由高到低排序，決定發動順序
    pets_with_idx.sort(key=lambda x: x[0].attack, reverse=True)
    
    # 3. 依照攻擊力順序，依序執行 End of Turn 技能
    for original_pet, i in pets_with_idx:
        p = team[i].pet  # 重新從隊伍抓取，確保拿到的還是最新的狀態
        
        # 🦜 鸚鵡能力邏輯
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

        # 🐵 猴子能力邏輯
        elif p.name == "pet-monkey":
            for j in range(5):
                front_slot = team[j]
                if not front_slot.empty and front_slot.pet.name != "pet-none" and "EMPTY" not in front_slot.pet.name:
                    buff_amount = p.level * 2
                    front_slot.pet._attack += buff_amount
                    front_slot.pet._health += buff_amount
                    break

        # 🦬 🌟 新增：野牛 (Bison) 能力邏輯
        elif p.name == "pet-bison":
            has_lvl3_friend = False
            for friend_slot in team:
                if not friend_slot.empty:
                    f_pet = friend_slot.pet
                    if f_pet != p and f_pet.name != "pet-none" and "EMPTY" not in f_pet.name:
                        if f_pet.level == 3:
                            has_lvl3_friend = True
                            break
            
            if has_lvl3_friend:
                buff_amount = p.level * 2
                p._attack += buff_amount
                p._health += buff_amount

# ==========================================
# 1. 建立雙方隊伍 
# ==========================================
my_team_setup = [
    # 🌟 測試 6 參數：給水獺吃一塊麵包 (預設裝備為 None)
    ('otter', None, None, 3, 'chili', 'food-bread'),
    ('bison', None, None, 1),
]

enemy_team_setup = [
    ('elephant', None, None, 1, None),
    ('ant', None, None, 1, None)
]

# 透過製造機實體化動物
my_team_pets = [make_pet(bp) for bp in my_team_setup]
enemy_team_pets = [make_pet(bp) for bp in enemy_team_setup]

my_team = Team(my_team_pets)       
enemy_team = Team(enemy_team_pets) 

print("🐾 戰鬥準備就緒！準備開打...")

# ==========================================
# 2. 建立並執行戰鬥
# ==========================================
# 🚨 關鍵改變：先產生 Battle (讓系統生成複製人)，再對準備上場的軍隊進行變身手術！
battle = Battle(my_team, enemy_team)

print("🐾 執行商店結算階段 (回合結束技能)...")
simulate_end_of_turn(battle.t0)
simulate_end_of_turn(battle.t1)

winner = battle.battle()

if winner == 0:
    print("🏆 結算: 你的隊伍獲勝！")
elif winner == 1:
    print("💀 結算: 敵方隊伍獲勝！")
else:
    print("🤝 結算: 雙方平手！")

print("\n" + "="*50)
print("🎙️ 自走棋文字播報台 (含隊伍狀態)")
print("="*50)

# ==========================================
# 3. 戰況解析器 (升級版)
# ==========================================
def clean_name(obj):
    """統一清理物件字串中的系統雜訊"""
    s = str(obj)
    for noise in ['< Slot ', '< ', ' >', '>']:
        s = s.replace(noise, '')
    return s

def print_team_state(state_list):
    team0_clean = [clean_name(p) for p in state_list[0] if "EMPTY" not in str(p)]
    team1_clean = [clean_name(p) for p in state_list[1] if "EMPTY" not in str(p)]
    print(f"   🔵 我方存活: {', '.join(team0_clean) if team0_clean else '全滅 🪦'}")
    print(f"   🔴 敵方存活: {', '.join(team1_clean) if team1_clean else '全滅 🪦'}")
    print("-" * 50)

for step_name, step_data in battle.battle_history.items():
    
    if step_name == "init":
        print(f"\n🔰 【階段: INIT (初始陣容)】")
        print_team_state(step_data)
        continue
        
    if step_name == "start":
        print(f"\n⚡ 【階段: START (開場技能結算)】")
    elif "attack" in step_name:
        print(f"\n⚔️ 【階段: {step_name.upper()} (交戰回合)】")
    else:
        continue

    for phase_name, events in step_data.items():
        if "move" in phase_name:
            continue
            
        for event in events:
            if isinstance(event, (list, tuple)) and len(event) >= 3:
                action = event[0]
                actor = clean_name(event[2])
                
                # 🌟 強化目標解析：無論是單一物件還是 List，統統轉成乾淨的 List
                raw_targets = event[3] if len(event) >= 4 else []
                if not isinstance(raw_targets, list):
                    raw_targets = [raw_targets]
                targets = [clean_name(t) for t in raw_targets if t]
                target_str = ", ".join(targets) if targets else "無"

                # 🌟 擴充攔截清單，讓播報更詳細
                if action == "DealDamage":
                    print(f"   🩸 {actor} 造成傷害 ➡️ {target_str}")
                elif action == "AllOf":
                    print(f"   🌊 {actor} 發動連續技能 ➡️ 目標: {target_str}")
                elif action == "Fainted":
                    print(f"   💀 {actor} 陣亡了！")
                elif action == "ModifyStats":
                    print(f"   📈 {actor} 獲得數值增益 ➡️ {target_str}")
                elif action == "SummonPet":
                    print(f"   🐣 {actor} 召喚了 ➡️ {target_str}")
                elif action == "Attack":
                    print(f"   💥 {actor} 發起實體衝撞 ➡️ {target_str}")
                elif action == "ApplyStatus":
                    print(f"   🛡️ {actor} 獲得特殊裝備/狀態 ➡️ {target_str}")
                elif action == "Ability":
                    print(f"   ✨ {actor} 發動了專屬技能！")

    if 'phase_move_end' in step_data and len(step_data['phase_move_end']) > 0:
        final_state = step_data['phase_move_end'][-1]
        print_team_state(final_state)

print("\n")