import time
import itertools
from sapai import Team
from sapai.battle import Battle

# ==========================================
# ⚙️ 參數區域
# ==========================================
# 候選池：將可用的動物列出，要幾隻就寫幾次 (例如 beaver 有兩隻)
candidate_pool = ["beaver", "beaver", "ant", "duck", "horse"]

a = 3   # 己方隊伍人數 (上陣人數)
n = 10  # 每種組合的模擬對戰次數

# 敵方固定組合 (這裡隨意挑了 3 隻來測試)
enemy_pets = ["ant", "beaver", "duck"]

# ==========================================
# 🔍 產生並過濾所有排列組合
# ==========================================
# 1. itertools.permutations 會將所有元素進行排列
# 2. 我們用 set() 將結果包起來，這樣能自動去除同名動物(如兩隻 beaver 互換)造成的重複組合
all_permutations = set(itertools.permutations(candidate_pool, a))

print("=" * 50)
print("🧠 系統初始化中...")
print(f"候選卡池: {candidate_pool}")
print(f"己方上陣: {a} 隻 | 敵方陣容: {enemy_pets}")
print(f"過濾重複後，共有 {len(all_permutations)} 種不重複的排兵布陣方式！")
print("=" * 50)

# ==========================================
# ⚔️ 執行大規模模擬
# ==========================================
results = []  # 用來儲存每種組合的戰績
total_battles = len(all_permutations) * n

print(f"🚀 開始暴力破解，預計執行 {total_battles} 場對戰...\n")

# 啟動計時器
start_time = time.time()

# 遍歷每一種排兵布陣
for combo_tuple in all_permutations:
    combo_list = list(combo_tuple) # 將 tuple 轉回 list 讓 sapai 可以讀取
    my_wins = 0
    enemy_wins = 0
    draws = 0
    
    # 針對這個特定的陣容，進行 n 次對戰
    for _ in range(n):
        # 🚨 必須在迴圈內部重新產生全新滿血的隊伍
        my_team = Team(combo_list)
        enemy_team = Team(enemy_pets)
        
        battle = Battle(my_team, enemy_team)
        winner = battle.battle()
        
        if winner == 0:
            my_wins += 1
        elif winner == 1:
            enemy_wins += 1
        else:
            draws += 1
            
    # 計算勝率並存入成績單
    win_rate = (my_wins / n) * 100
    results.append({
        "combo": combo_list,
        "win_rate": win_rate,
        "wins": my_wins,
        "draws": draws,
        "losses": enemy_wins
    })

# 停止計時
end_time = time.time()

# ==========================================
# 📊 結算與找出最佳解 (Top 10)
# ==========================================
# 排序邏輯：優先比勝率 (由高到低)，如果勝率一樣，則比平手次數 (平手總比輸好)
results.sort(key=lambda x: (x["win_rate"], x["draws"]), reverse=True)

# 計算耗時
total_time = end_time - start_time
avg_time_per_combo = total_time / len(all_permutations)
avg_time_per_battle = total_time / total_battles

print("\n" + "=" * 50)
print("🏆 【Top 10 最佳組合揭曉】")
print("=" * 50)

# 取出前 10 名 (如果總組合數不到 10 種，Python 也會自動處理，不會報錯)
top_10_results = results[:10]

for i, best_combo in enumerate(top_10_results):
    # 排行榜名次 (i 從 0 開始，所以要 +1)
    rank = i + 1
    
    # 幫前三名加上特別的皇冠符號
    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "🏅"
    
    print(f"{medal} 第 {rank} 名 (排頭在右): {best_combo['combo']}")
    print(f"   📈 勝率: {best_combo['win_rate']:.1f}% ({best_combo['wins']}勝 {best_combo['draws']}平 {best_combo['losses']}敗)")

print("-" * 50)
print("📊 【效能與耗時統計】")
print(f"⏱️ 總耗時: {total_time:.4f} 秒")
print(f"⏱️ 陣容總數: {len(all_permutations)} 種")
print(f"⏱️ 平均耗時 (每種陣容): {avg_time_per_combo:.4f} 秒")
print(f"⏱️ 平均耗時 (每場對戰): {avg_time_per_battle:.6f} 秒")
print("=" * 50)