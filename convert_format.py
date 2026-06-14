import os
import glob

def convert_pet_string(ps):
    """將單一舊版動物字串轉換為新版格式"""
    ps = ps.strip()
    if not ps or ps == "pet-none":
        return ps
        
    stats = None
    food = None
    eq = None
    
    # 1. 提取面板數值 (例如: (9/8/L3) )
    if ps.endswith(')'):
        last_open = ps.rfind('(')
        content = ps[last_open+1:-1]
        if '/' in content:  # 確認括號內是面板數值
            stats = content
            ps = ps[:last_open]  # 剝離數值部分
            
    # 2. 提取食物 (例如: (+apple) )
    if ps.endswith(')'):
        last_open = ps.rfind('(')
        content = ps[last_open+1:-1]
        if content.startswith('+'):
            food = content[1:]  # 剝離 '+' 號
            ps = ps[:last_open]  # 剝離食物部分
            
    # 3. 提取裝備 (例如: -[garlic] )
    if ps.endswith(']'):
        last_open = ps.rfind('-[')
        if last_open != -1:
            eq = ps[last_open+2:-1]
            ps = ps[:last_open]  # 剝離裝備部分
            
    name = ps
    
    # 4. 重構為新格式
    if not stats:
        # 如果完全沒有數值，代表是白板動物 (如 spider)
        return name
        
    res = f"{name}({stats}"
    if food:
        # 如果有食物，必須檢查是否有裝備 (沒有的話用 none 佔位)
        res += f"/{eq if eq else 'none'}/{food}"
    elif eq:
        # 如果只有裝備
        res += f"/{eq}"
        
    res += ")"
    return res

def process_line(line):
    """處理單行陣容"""
    line = line.strip()
    # 略過空行或非陣容格式的行
    if not line.startswith('[') or not line.endswith(']'):
        return line + '\n'
        
    inner = line[1:-1]
    if not inner:
        return '[]\n'
        
    # 切割每隻動物並轉換
    pet_strs = inner.split(', ')
    new_pet_strs = [convert_pet_string(p) for p in pet_strs]
    
    return '[' + ', '.join(new_pet_strs) + ']\n'

def main():
    # 尋找目錄下所有符合 turn*_setup.txt 的檔案
    target_files = glob.glob("turn*_setup.txt")
    
    if not target_files:
        print("⚠️ 找不到任何 turn*_setup.txt 檔案！請確認腳本是否與 txt 檔在同一個目錄。")
        return
        
    for filepath in target_files:
        print(f"🔄 正在轉換: {filepath} ...")
        
        # 讀取舊檔案內容
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # 轉換內容
        new_lines = [process_line(line) for line in lines]
        
        # 覆寫回原檔案 (如果你想保留備份，可以改為 filepath + ".new")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
            
    print(f"\n✅ 轉換完成！共更新了 {len(target_files)} 個檔案。")

if __name__ == "__main__":
    main()