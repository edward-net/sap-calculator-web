import re

def clean_setups_file(filename="setups.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: {filename} not found in the current directory.")
        return

    # 使用非贪婪匹配，找到最外层的方括号（支持嵌套）
    # 这个正则会找到第一个 '[' 和与之匹配的最后一个 ']'
    pattern = r'\[([^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*)\]'
    
    matches = re.findall(pattern, content)
    
    if not matches:
        print("No bracket content found.")
        return
    
    # 重建每一行，保留原始换行结构
    cleaned_lines = []
    for match in matches:
        cleaned_lines.append(f"[{match}]")
    
    # 移除可能的空行
    cleaned_lines = [line for line in cleaned_lines if line.strip()]
    
    # 直接覆盖原文件
    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(cleaned_lines))
    
    print(f"✓ Successfully overwritten {filename}")
    print(f"✓ Kept {len(cleaned_lines)} lines with bracket content")
    print(f"✓ Example: {cleaned_lines[0] if cleaned_lines else 'None'}")

def clean_setups_file_alternative(filename="setups.txt"):
    """
    备用方案：逐行处理，使用栈来匹配最外层方括号
    更直观，适合复杂嵌套情况
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: {filename} not found in the current directory.")
        return
    
    cleaned_lines = []
    
    for line in lines:
        # 使用栈来查找最外层的方括号内容
        stack = []
        start_index = -1
        
        for i, char in enumerate(line):
            if char == '[':
                if not stack:  # 最外层开始
                    start_index = i
                stack.append(char)
            elif char == ']':
                if stack:
                    stack.pop()
                    if not stack and start_index != -1:  # 最外层结束
                        bracket_content = line[start_index+1:i]
                        cleaned_lines.append(f"[{bracket_content}]")
                        break  # 找到该行的括号后退出循环
    
    # 移除空行
    cleaned_lines = [line for line in cleaned_lines if line.strip()]
    
    # 直接覆盖原文件
    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(cleaned_lines))
    
    print(f"✓ Successfully overwritten {filename}")
    print(f"✓ Kept {len(cleaned_lines)} lines with bracket content")
    print(f"✓ Example: {cleaned_lines[0] if cleaned_lines else 'None'}")

if __name__ == "__main__":
    # 使用备用方案（更可靠）
    clean_setups_file_alternative()