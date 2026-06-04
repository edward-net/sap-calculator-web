import re

def convert_sap_team_format(team_str):
    # 移除字串首尾的空白與中括號 []
    team_str = team_str.strip("[] ")
    
    # 以逗號分割每隻寵物的字串
    pet_strings = team_str.split(",")
    
    result = []
    
    # 正規表達式解析規則
    # Group 1: 寵物名稱
    # Group 2: 食物/裝備 (在 -[...] 之中)
    # Group 3, 4, 5: 攻擊力、血量、等級
    pattern = re.compile(r"([a-zA-Z]+)(?:-\[([a-zA-Z]+)\])?(?:\((\d+)/(\d+)/L(\d+)\))?")
    
    for pet in pet_strings:
        pet = pet.strip()
        if not pet:
            continue
            
        match = pattern.match(pet)
        if match:
            # 提取名稱與數值
            name = match.group(1).lower()
            item = match.group(2)  # 🎯 提取食物/裝備名稱 (例如 "garlic")，若無則為 None
            atk = int(match.group(3)) if match.group(3) else None
            hp = int(match.group(4)) if match.group(4) else None
            lvl = int(match.group(5)) if match.group(5) else None
            
            # 🎯 依據需求，將 item 放到第五個位置：(name, atk, hp, lvl, item)
            result.append((name, atk, hp, lvl, item))
            
    return result

# ==========================================
# 🎮 主程式：互動式輸入迴圈
# ==========================================
if __name__ == "__main__":
    print("🐾 歡迎使用 SAP 隊伍格式轉換器 (含食物/裝備版)！")
    print("格式範例: [ant-[garlic](9/8/L3), spider, dolphin(7/4/L1)]")
    print("輸入 'q' 或 'exit' 即可離開程式。\n")
    print("-" * 50)

    while True:
        # 等待使用者輸入
        user_input = input("👉 請貼上隊伍字串: ")
        
        # 檢查是否要離開程式
        if user_input.strip().lower() in ['q', 'exit', 'quit']:
            print("掰掰！祝你爬分順利 👋")
            break
            
        # 避免空輸入報錯
        if not user_input.strip():
            continue
            
        # 進行轉換
        formatted_team = convert_sap_team_format(user_input)
        
        # 印出排版好的結果
        print("\n✅ 轉換結果：\n[")
        for pet in formatted_team:
            print(f"    {pet},")
        print("]")
        print("-" * 50 + "\n")