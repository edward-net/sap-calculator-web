import sapai

print("\n📚 探索小動物自走棋底層圖鑑...")

# 直接存取 sapai 內建的 data 字典
pets_pool = sapai.data.get('pets', {})

print(f"\n🐾 系統中總共收錄了 {len(pets_pool) - 1} 隻小動物！") # 減去 1 是因為作者塞了一個 'pet-none' 當作空殼

# 讓使用者輸入想要查詢的 Tier
target_tier = input("\n請輸入你想查詢的星級 (1-6)，或輸入 'Summoned' 查詢召喚物: ")

print(f"\n🔍 查詢結果: Tier {target_tier} 的動物")
print("=" * 40)

count = 0
for pet_id, pet_info in pets_pool.items():
    # 略過空殼資料
    if pet_id == "pet-none":
        continue
        
    # 將輸入轉換成整數 (如果是數字的話)
    try:
        tier_to_check = int(target_tier)
    except ValueError:
        tier_to_check = target_tier
        
    # 如果符合我們想找的 Tier，就印出資料
    if pet_info.get('tier') == tier_to_check:
        count += 1
        name = pet_info.get('name')
        atk = pet_info.get('baseAttack', '未知')
        hp = pet_info.get('baseHealth', '未知')
        
        # 嘗試抓取技能描述 (如果有第一星級的技能)
        ability = "無特殊技能"
        if 'level1Ability' in pet_info:
            ability = pet_info['level1Ability'].get('description', ability)
            
        print(f"【{name}】 ⚔️攻擊: {atk} | 💖血量: {hp}")
        print(f"   💡 技能: {ability}")
        print("-" * 40)

print(f"✅ 總共找到 {count} 隻符合條件的動物。")