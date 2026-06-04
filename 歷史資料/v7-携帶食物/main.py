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
            
    # 2. 🍖 穿上裝備 (使用官方 API：吃食物！)
    # 🚨 關鍵：必須在「修改基礎數值」之前吃！
    # 因為有些食物 (如蘋果) 吃了會加基礎數值，我們等牠吃完後，再把數值強制壓回我們想要的設定。
    if equipment is not None:
        p.eat(Food(equipment))
        
    # 3. 🚨 修改基礎數值 (暴力覆寫)
    if atk is not None:
        p._attack = atk
    if hp is not None:
        p._health = hp
            
    return p

# ==========================================
# 1. 建立雙方隊伍 
# ==========================================
my_team_setup = [
    ("dolphin", None, 7, 1) 
]

enemy_team_setup = [
    # 🚨 藍圖的第 5 個參數，請改填「食物名稱 (meat-bone)」，而不是「狀態名稱」
    ("ant", 2, 5, None, "meat-bone"),
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
battle = Battle(my_team, enemy_team)
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