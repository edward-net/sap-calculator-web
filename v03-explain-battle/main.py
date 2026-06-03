import os
import pprint # 引入 Python 內建的漂亮列印模組

# 確保 Graphviz 路徑 (雖然畫圖模組壞了，但保留著也無妨)
graphviz_bin_path = r"C:\Program Files\Graphviz\bin"
os.environ["PATH"] += os.pathsep + graphviz_bin_path

from sapai import Team
from sapai.battle import Battle

# 1. 建立雙方隊伍
my_team = Team(["ant", "fish"])       
enemy_team = Team(["mosquito", "cricket"]) 

print("🐾 戰鬥準備就緒！準備開打...")

# 2. 建立並執行戰鬥
battle = Battle(my_team, enemy_team)
winner = battle.battle()

if winner == 0:
    print("🏆 結算: 你的隊伍獲勝！")
elif winner == 1:
    print("💀 結算: 敵方隊伍獲勝！")
else:
    print("🤝 結算: 雙方平手！")

print("\n" + "="*40)
print("🎙️ 自走棋文字播報台 (重點戰況)")
print("="*40)

# 3. 自己寫的戰況解析器
for step_name, step_data in battle.battle_history.items():
    # 只挑選戰鬥交鋒的回合來印出，過濾掉繁雜的移動過程
    if "attack" in step_name and isinstance(step_data, dict):
        print(f"\n⚔️ 【交戰回合: {step_name.upper()}】")
        
        # 抓取攻擊事件
        attacks = step_data.get('phase_attack', [])
        for atk in attacks:
            # atk 陣列的結構大約是: ['Attack', 座標, 攻擊者, [受擊者]]
            attacker = atk[2]
            defender = atk[3][0] if len(atk[3]) > 0 else "無"
            print(f"   💥 {attacker} 發動攻擊 ➡️ {defender}")
            
        # 抓取陣亡事件
        faints = step_data.get('phase_hurt_and_faint_aa', [])
        for faint in faints:
            # faint 陣列的結構大約是: ('Fainted', 座標, 陣亡者, [])
            if faint[0] == 'Fainted':
                fainted_pet = faint[2]
                print(f"   💀 {fainted_pet} 陣亡了！")

print("\n" + "="*40)
print("📊 完整底層資料 (如需除錯可看此處):")
# 用 pprint 可以把原本擠成一團的 JSON 結構排版得非常整齊易讀
# pprint.pprint(battle.battle_history) # 如果你想看完整資料，可以把這行開頭的 # 拿掉

# 4. 輸出戰鬥流程
print("\n--- 📝 戰鬥詳細紀錄 ---")
# 使用 .items() 同時把階段名稱 (step_name) 和當下的詳細資料 (step_data) 拿出來
for step_name, step_data in battle.battle_history.items():
    print(f"📌 階段: {step_name}")
    print(f"雙方狀態: {step_data}")
    print("-" * 30)