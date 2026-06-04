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
# 🛠️ 輔助函式：根據藍圖製造自訂數值的動物
# ==========================================
def make_pet(pet_blueprint):
    if len(pet_blueprint) == 5:
        name, atk, hp, lvl, equipment = pet_blueprint
    else:
        name, atk, hp, lvl = pet_blueprint
        equipment = None

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
            
    # 3. 🍖 穿上裝備 (使用官方 API：吃食物！)
    if equipment is not None:
        p.eat(Food(equipment))

    return p

# ==========================================
# 🌟 新增：商店階段 (EndOfTurn) 鸚鵡變身器
# ==========================================
def simulate_end_of_turn(team):
    """手動觸發商店結算，直接將鸚鵡替換成前方的動物！"""
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
                        
                        # 🚨 關鍵修復：幫這隻新誕生的孤兒動物，手動接上隊伍的神經網絡！
                        cloned_pet.team = team
                        
                        # 5. 【偷天換日】直接把這隻新的動物，塞回原本鸚鵡的格子裡！
                        team[i] = cloned_pet
                        
                        print(f"   🦜 [商店階段] 鸚鵡變身了！牠變成了 {front_pet.name} (維持 {parrot_atk}攻 {parrot_hp}血)！")
                        break

# ==========================================
# 1. 建立雙方隊伍 
# ==========================================
my_team_setup = [
    ("dodo", 9, 6, None, "garlic"),
    ("giraffe", 3, 4, None, "pear"),
    ("blowfish", 4, 7, None),
    ("ant", 8, 8, 3),
    ("crocodile", 11, 7, None)
]

enemy_team_setup = [
    ("ant", None, None, None),
    ("spider", None, None, None),
    ("ant", 5, 4, 2),
    ("peacock", None, None, None),
    ("ant", 7, 4, 1)
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

print("🐾 執行商店結算階段 (鸚鵡變身)...")
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
# 3. 戰況解析器
# ==========================================
def print_team_state(state_list):
    team0_clean = [p.replace('< Slot ', '').replace(' >', '') for p in state_list[0] if "EMPTY" not in p]
    team1_clean = [p.replace('< Slot ', '').replace(' >', '') for p in state_list[1] if "EMPTY" not in p]
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
                actor = event[2].replace('< ', '').replace(' >', '')
                
                targets = []
                if len(event) >= 4 and isinstance(event[3], list):
                    targets = [t.replace('< ', '').replace(' >', '') for t in event[3] if t]
                target_str = ", ".join(targets) if targets else "無"

                if action == "DealDamage":
                    print(f"   ✨ {actor} 造成傷害 ➡️ {target_str}")
                elif action == "AllOf":
                    print(f"   🌊 {actor} 發動連續技能 ➡️ 目標: {target_str}")
                elif action == "Fainted":
                    print(f"   💀 {actor} 陣亡了！")
                elif action == "ModifyStats":
                    print(f"   📈 {actor} 觸發增益 ➡️ {target_str}")
                elif action == "SummonPet":
                    print(f"   🐣 {actor} 召喚了 ➡️ {target_str}")
                elif action == "Attack":
                    print(f"   💥 {actor} 衝撞攻擊 ➡️ {target_str}")

    if 'phase_move_end' in step_data and len(step_data['phase_move_end']) > 0:
        final_state = step_data['phase_move_end'][-1]
        print_team_state(final_state)

print("\n")