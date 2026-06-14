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
# 1. 建立雙方隊伍 
# ==========================================
my_team_setup = [
    ('blowfish', 4, 3, 1, None),
    ('otter', 2, 2, 1, None),
    ('hedgehog', 4, 2, 1, None),
    ('otter', 2, 30, 1, None),
    ('wolverine', None, 30, 1, None),
]

enemy_team_setup = [
    ('otter', 2, 6, 1, None),
    ('peacock', 2, 10, 1, None),
    ('fish', None, None, None, None),
    ('fish', None, None, None, None),
    ('elephant', 2, 45, 1, None),
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