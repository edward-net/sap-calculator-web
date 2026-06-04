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
    ("beaver", None, None, None),
    ("ant", None, None, None),
    ("ant", 3, 3, None),        # 自訂 3 攻 3 血的螞蟻
    ("beaver", None, None, None),
    ("ant", None, None, None)
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
# 3. 戰況解析器與輔助函式
# ==========================================
def print_team_state(state_list):
    # state_list 是包含兩個陣列的列表：[我方陣容, 敵方陣容]
    
    # 1. 濾掉空的格子 (EMPTY)
    team0 = [pet for pet in state_list[0] if "EMPTY" not in pet]
    team1 = [pet for pet in state_list[1] if "EMPTY" not in pet]
    
    # 2. 清理字串，把 '< Slot ' 和 ' >' 拔掉，讓畫面更簡潔
    team0_clean = [p.replace('< Slot ', '').replace(' >', '') for p in team0]
    team1_clean = [p.replace('< Slot ', '').replace(' >', '') for p in team1]
    
    print(f"   🔵 我方存活: {', '.join(team0_clean) if team0_clean else '全滅 🪦'}")
    print(f"   🔴 敵方存活: {', '.join(team1_clean) if team1_clean else '全滅 🪦'}")
    print("-" * 50)


for step_name, step_data in battle.battle_history.items():
    
    # 🟢 處理 INIT 階段 (剛進入戰鬥，還沒發動任何開場技能)
    if step_name == "init":
        print(f"\n🔰 【階段: INIT (初始陣容)】")
        print_team_state(step_data)
        
    # 🟡 處理 START 階段 (開場技能觸發，例如蚊子、海豚吐口水)
    elif step_name == "start" and isinstance(step_data, dict):
        print(f"\n⚡ 【階段: START (開場技能結算)】")
        
        # 額外抓取開場技能造成的傷害
        skills = step_data.get('phase_start', [])
        for skill in skills:
            if skill[0] == 'DealDamage':
                attacker = skill[2].replace('< ', '').replace(' >', '')
                defender = skill[3][0].replace('< ', '').replace(' >', '') if len(skill[3]) > 0 else "無"
                print(f"   ✨ {attacker} 發動開場技能 ➡️ 擊中 {defender}")
        
        # 尋找這回合結束後的隊伍狀態
        if 'phase_move_end' in step_data and len(step_data['phase_move_end']) > 0:
            final_state = step_data['phase_move_end'][-1]
            print_team_state(final_state)
            
    # 🔴 處理 ATTACK 階段 (正式交戰回合)
    elif "attack" in step_name and isinstance(step_data, dict):
        print(f"\n⚔️ 【階段: {step_name.upper()} (交戰回合)】")
        
        # 抓取攻擊事件
        attacks = step_data.get('phase_attack', [])
        for atk in attacks:
            attacker = atk[2].replace('< ', '').replace(' >', '')
            defender = atk[3][0].replace('< ', '').replace(' >', '') if len(atk[3]) > 0 else "無"
            print(f"   💥 {attacker} 發動攻擊 ➡️ {defender}")
            
        # 抓取陣亡事件
        faints = step_data.get('phase_hurt_and_faint_aa', [])
        for faint in faints:
            if faint[0] == 'Fainted':
                fainted_pet = faint[2].replace('< ', '').replace(' >', '')
                print(f"   💀 {fainted_pet} 陣亡了！")

        # 尋找交戰結束後的隊伍狀態
        if 'phase_move_end' in step_data and len(step_data['phase_move_end']) > 0:
            final_state = step_data['phase_move_end'][-1]
            print_team_state(final_state)

print("\n")