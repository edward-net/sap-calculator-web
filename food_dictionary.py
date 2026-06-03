import sapai

print("\n🍏 探索小動物自走棋底層圖鑑 (食物/裝備篇)...")

# 直接存取 sapai 內建的 data 字典，這次抓取 'foods'
foods_pool = sapai.data.get('foods', {})

print(f"\n🍔 系統中總共收錄了 {len(foods_pool) - 1} 種食物與裝備！") # 減去 1 是因為作者塞了一個 'food-none' 當作空殼

# 讓使用者輸入想要查詢的 Tier
target_tier = input("\n請輸入你想查詢的商店星級 (1-6): ")

print(f"\n🔍 查詢結果: Tier {target_tier} 的食物與裝備")
print("=" * 40)

count = 0
for food_id, food_info in foods_pool.items():
    # 略過空殼資料
    if food_id == "food-none":
        continue
        
    # 將輸入轉換成整數 (如果是數字的話)
    try:
        tier_to_check = int(target_tier)
    except ValueError:
        tier_to_check = target_tier
        
    # 如果符合我們想找的 Tier，就印出資料
    if food_info.get('tier') == tier_to_check:
        count += 1
        name = food_info.get('name')
        
        # 食物沒有分星級，所以直接抓取 'ability'
        ability = "無特殊效果"
        if 'ability' in food_info:
            ability = food_info['ability'].get('description', ability)
            
        print(f"【{name}】")
        print(f"   💡 效果: {ability}")
        print("-" * 40)

print(f"✅ 總共找到 {count} 種符合條件的食物/裝備。")