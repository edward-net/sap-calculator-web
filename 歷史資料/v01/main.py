from sapai import Team
from sapai.battle import Battle

# 1. 建立雙方隊伍 (從左到右，排頭在最後面)
# 這裡我們用最基礎的 Tier 1 動物來測試
my_team = Team(["ant", "fish"])       # 你的隊伍：一隻螞蟻、一隻魚
enemy_team = Team(["mosquito", "cricket"]) # 敵方隊伍：一隻蚊子、一隻蟋蟀

print("🐾 戰鬥準備就緒！")
print(f"你的隊伍: {my_team}")
print(f"敵方隊伍: {enemy_team}")
print("-" * 30)

# 2. 建立戰鬥引擎
battle = Battle(my_team, enemy_team)

# 3. 執行戰鬥，會回傳獲勝者的編號 (0 代表左方 my_team，1 代表右方 enemy_team，2 代表平手)
winner = battle.battle()

# 4. 顯示結算結果
if winner == 0:
    print("🏆 結算: 你的隊伍獲勝！")
elif winner == 1:
    print("💀 結算: 敵方隊伍獲勝！")
else:
    print("🤝 結算: 雙方平手！")
