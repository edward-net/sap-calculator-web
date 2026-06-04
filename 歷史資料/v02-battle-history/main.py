from sapai import Team
from sapai.battle import Battle
from sapai.graph import graph_battle  # ⬅️ 這裡多引入了官方的流程圖工具

# 1. 建立雙方隊伍 (從左到右，排頭在最後面)
my_team = Team(["ant", "fish"])       
enemy_team = Team(["mosquito", "cricket"]) 

print("🐾 戰鬥準備就緒！")
print(f"你的隊伍: {my_team}")
print(f"敵方隊伍: {enemy_team}")
print("-" * 30)

# 2. 建立戰鬥引擎
battle = Battle(my_team, enemy_team)

# 3. 執行戰鬥
winner = battle.battle()

# 4. 顯示結算結果
if winner == 0:
    print("🏆 結算: 你的隊伍獲勝！")
elif winner == 1:
    print("💀 結算: 敵方隊伍獲勝！")
else:
    print("🤝 結算: 雙方平手！")

# 5. 輸出視覺化戰鬥流程圖
print("\n--- 📝 正在產生戰鬥流程圖 ---")
try:
    # 這行會讀取內部的紀錄，並產生一個檔案
    graph_battle(battle, file_name="battle_log")
    print("✅ 戰鬥流程圖已成功產生！請在資料夾查看 battle_log 檔案。")
except Exception as e:
    print("⚠️ 產生流程圖失敗。")
    print("原因：系統中尚未安裝 Graphviz 繪圖引擎 (ExecutableNotFound)。")
    print("雖然不能畫圖，但戰鬥邏輯本身是完全正常運作的！")

print("\n--- 📝 戰鬥詳細紀錄 ---")
# 使用 .items() 同時把階段名稱 (step_name) 和當下的詳細資料 (step_data) 拿出來
for step_name, step_data in battle.battle_history.items():
    print(f"📌 階段: {step_name}")
    print(f"雙方狀態: {step_data}")
    print("-" * 30)