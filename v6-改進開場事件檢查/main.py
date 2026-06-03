import os
import pprint # 引入 Python 內建的漂亮列印模組

# 確保 Graphviz 路徑
graphviz_bin_path = r"C:\Program Files\Graphviz\bin"
os.environ["PATH"] += os.pathsep + graphviz_bin_path

from sapai import Team
from sapai.pets import Pet
from sapai.battle import Battle

# ==========================================
# 🛠️ 輔助函式：根據藍圖製造自訂數值的動物 (官方優雅版)
# ==========================================
def make_pet(pet_blueprint):
    name, atk, hp, lvl = pet_blueprint
    p = Pet(name)
    
    # 1. 🌟 使用官方 API 增加經驗值，系統會自動升級技能！
    if lvl is not None:
        if lvl == 2:
            # 升到 2 星需要 2 點經驗
            for _ in range(2):
                p.gain_experience()
        elif lvl == 3:
            # 升到 3 星總共需要 5 點經驗
            for _ in range(5):
                p.gain_experience()
                
    # 2. 修改數值 (照官方文件，直接修改底層的 _attack 和 _health)
    if atk is not None:
        p._attack = atk
    if hp is not None:
        p._health = hp
        
    return p

# ==========================================
# 1. 建立雙方隊伍 (支援自訂數值藍圖)
# 藍圖格式: ("動物名稱", 攻擊, 血量, 星級)
# ==========================================
# 測試我們魔改後的 3 星海豚
my_team_setup = [
    ("dolphin", None, None, 3) 
]

# 敵方為你指定的複雜陣容
enemy_team_setup = [
    ("ant", 4, 13, None),
]

# 透過製造機實體化動物
my_team_pets = [make_pet(bp) for bp in my_team_setup]
enemy_team_pets = [make_pet(bp) for bp in enemy_team_setup]

# 建立真正的隊伍
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
# 3. 戰況解析器與輔助函式 (萬能事件捕捉版)
# ==========================================
def print_team_state(state_list):
    # 濾掉空格子並清理字串
    team0_clean = [p.replace('< Slot ', '').replace(' >', '') for p in state_list[0] if "EMPTY" not in p]
    team1_clean = [p.replace('< Slot ', '').replace(' >', '') for p in state_list[1] if "EMPTY" not in p]
    print(f"   🔵 我方存活: {', '.join(team0_clean) if team0_clean else '全滅 🪦'}")
    print(f"   🔴 敵方存活: {', '.join(team1_clean) if team1_clean else '全滅 🪦'}")
    print("-" * 50)


for step_name, step_data in battle.battle_history.items():
    
    # 🟢 處理 INIT 階段
    if step_name == "init":
        print(f"\n🔰 【階段: INIT (初始陣容)】")
        print_team_state(step_data)
        continue
        
    # 印出階段標題
    if step_name == "start":
        print(f"\n⚡ 【階段: START (開場技能結算)】")
    elif "attack" in step_name:
        print(f"\n⚔️ 【階段: {step_name.upper()} (交戰回合)】")
    else:
        continue

    # 🌟 萬用事件捕捉器：遍歷該階段內的所有微小動作
    for phase_name, events in step_data.items():
        # 略過單純的移動補位事件，保持版面乾淨
        if "move" in phase_name:
            continue
            
        for event in events:
            # 確保這是一個標準的事件格式 (Tuple 或 List)
            if isinstance(event, (list, tuple)) and len(event) >= 3:
                action = event[0]
                actor = event[2].replace('< ', '').replace(' >', '')
                
                # 處理受擊者/目標字串
                targets = []
                if len(event) >= 4 and isinstance(event[3], list):
                    targets = [t.replace('< ', '').replace(' >', '') for t in event[3] if t]
                target_str = ", ".join(targets) if targets else "無"

                # 根據不同動作進行播報
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

    # 印出該階段結束後的最終隊伍狀態
    if 'phase_move_end' in step_data and len(step_data['phase_move_end']) > 0:
        final_state = step_data['phase_move_end'][-1]
        print_team_state(final_state)

print("\n")