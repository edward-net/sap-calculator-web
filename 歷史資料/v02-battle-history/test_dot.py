import shutil
import os

print("當前 Python 看到的環境變數 PATH:")
print(os.environ.get("PATH")[:200] + "...") # 印出前200個字元看看
print("\n尋找 dot.exe 的結果:")
print(shutil.which("dot"))