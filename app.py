import streamlit as st
import backend 
from sapai.data import data # 🌟 新增：載入 sapai 官方資料庫

# 頁面基本設定 (使用寬螢幕佈局)
st.set_page_config(page_title="SAP 戰鬥模擬器", layout="wide")

# ==========================================
# 🌟 狀態初始化與自動查表邏輯 (Callback)
# ==========================================
# 預先初始化所有輸入框的 Session State，讓它們一開始是乾淨的空值
if "initialized" not in st.session_state:
    for i in range(10): # 預留給隊伍擴充
        st.session_state[f"my_atk_{i}"] = None
        st.session_state[f"my_hp_{i}"] = None
        st.session_state[f"en_atk_{i}"] = None
        st.session_state[f"en_hp_{i}"] = None
        # 🌟 新增：預留給候選池 (candidate pool) 的狀態
        st.session_state[f"cand_atk_{i}"] = None
        st.session_state[f"cand_hp_{i}"] = None
    st.session_state["initialized"] = True

def auto_fill_stats(prefix, idx):
    """當下拉選單改變時，瞬間查表並填入攻擊力與生命值"""
    pet_name = st.session_state[f"{prefix}_name_{idx}"]
    atk_key = f"{prefix}_atk_{idx}"
    hp_key = f"{prefix}_hp_{idx}"
    
    if pet_name:
        pet_id = f"pet-{pet_name}"
        # 確保資料庫裡有這隻動物
        if pet_id in data["pets"]:
            b_atk = data["pets"][pet_id].get("baseAttack")
            b_hp = data["pets"][pet_id].get("baseHealth")
            
            # 更新 Session State (畫面上的數字會瞬間跟著變！)
            if isinstance(b_atk, int):
                st.session_state[atk_key] = b_atk
            else:
                st.session_state[atk_key] = None
                
            if isinstance(b_hp, int):
                st.session_state[hp_key] = b_hp
            else:
                st.session_state[hp_key] = None
    else:
        # 如果把名稱清空，數值也自動幫你清空
        st.session_state[atk_key] = None
        st.session_state[hp_key] = None

# ==========================================
# 🐾 預設動物清單
# ==========================================
ANIMAL_LIST = [
    "ant", "badger", "bat", "beaver", "bison", "blowfish", "boar", "camel", 
    "cat", "cow", "crab", "cricket", "crocodile", "deer", "dog", "dolphin", "dragon", 
    "dromedary", "duck", "eagle", "elephant", "fish", "flamingo", "fly", "giraffe", 
    "gorilla", "hedgehog", "hippo", "horse", "kangaroo", "leopard", "llama", "mammoth", 
    "microbe", "monkey", "mosquito", "octopus", "otter", "owl", "ox", "parrot", "peacock", 
    "penguin", "pig", "pigeon", "poodle", "rabbit", "rat", "rhino", "rooster", "sauropod", "scorpion", 
    "seal", "shark", "sheep", "shrimp", "skunk", "sloth", "snail", "snake", "spider", 
    "squirrel", "swan", "tabby-cat", "tiger", "tropical-fish", "turkey", "turtle", 
    "tyrannosaurus", "whale", "worm"
]

st.title("🐾 Super Auto Pets 戰鬥模擬器")

# ==========================================
# 1. 頂部通用設定區
# ==========================================
with st.container():
    st.subheader("⚙️ 模擬參數設定")
    col_n, col_a = st.columns(2)
    with col_n:
        n_sim = st.number_input("模擬次數 (n)", min_value=1, max_value=10000, value=5, step=1)
    with col_a:
        team_size = st.number_input("隊伍成員數量 (a)", min_value=1, max_value=5, value=5, step=1)

st.markdown("---")
col_left, col_right = st.columns(2)

# ==========================================
# 2. 左半部：己方陣容 (My Team)
# ==========================================
with col_left:
    st.header("🔵 己方陣容")
    my_mode = st.radio("選擇輸入模式 (己方)", ["手動選取模式", "讀取檔案模式 (setups.txt)"])
    my_team_config = {}
    
    if my_mode == "讀取檔案模式 (setups.txt)":
        my_team_config["mode"] = "file"
        my_team_config["file_path"] = "setups.txt"
        st.info("將讀取同目錄下的 setups.txt 作為測試組合。")
    else:
        my_team_config["mode"] = "manual"
        st.write("設定您的固定陣容 (若有空位，系統會自動填入候選池動物)：")
        
        # --- 1. 固定陣容 (Fixed Members) ---
        h_cols = st.columns([1.5, 3, 2, 2, 2, 2])
        h_cols[1].markdown("**名稱**")
        h_cols[2].markdown("**攻擊力**")
        h_cols[3].markdown("**生命值**")
        h_cols[4].markdown("**等級**")
        h_cols[5].markdown("**裝備**")

        fixed_members = []
        for i in range(team_size):
            cols = st.columns([1.5, 3, 2, 2, 2, 2])
            cols[0].markdown(f"<div style='padding-top: 6px;'><b>🐾 固定 {i+1}</b></div>", unsafe_allow_html=True)
            
            pet_name = cols[1].selectbox(
                "名稱", ANIMAL_LIST, index=None, placeholder="選擇動物", 
                key=f"my_name_{i}", label_visibility="collapsed",
                on_change=auto_fill_stats, args=("my", i)
            )
            
            pet_atk = cols[2].number_input("攻擊力", min_value=1, max_value=50, step=1, key=f"my_atk_{i}", placeholder="攻擊", label_visibility="collapsed")
            pet_hp = cols[3].number_input("生命值", min_value=1, max_value=50, step=1, key=f"my_hp_{i}", placeholder="生命", label_visibility="collapsed")
            pet_lvl = cols[4].selectbox("等級", [1, 2, 3], index=None, placeholder="預設:1", key=f"my_lvl_{i}", label_visibility="collapsed")
            pet_eq = cols[5].text_input("裝備", key=f"my_eq_{i}", placeholder="", label_visibility="collapsed")
            
            if pet_name:
                atk = pet_atk 
                hp = pet_hp   
                lvl = int(pet_lvl) if pet_lvl else 1
                eq = pet_eq if pet_eq else None
                fixed_members.append((pet_name, atk, hp, lvl, eq))
                    
        my_team_config["fixed_members"] = fixed_members
        
        # --- 2. 動物候選池 (Candidate Pool) ---
        st.write("") # 留點白
        with st.expander("➕ 設定動物候選池 (將與上方固定陣容排列組合)"):
            st.info("💡 如果上方固定陣容未滿 5 人，系統會將這裡的動物自動填入空缺並嘗試所有組合！")
            
            # 候選池標題列
            c_cols = st.columns([1.5, 3, 2, 2, 2, 2])
            c_cols[1].markdown("**名稱**")
            c_cols[2].markdown("**攻擊力**")
            c_cols[3].markdown("**生命值**")
            c_cols[4].markdown("**等級**")
            c_cols[5].markdown("**裝備**")
            
            candidate_pool = []
            # 預設給予 5 個候選空位
            for i in range(5):
                cols = st.columns([1.5, 3, 2, 2, 2, 2])
                cols[0].markdown(f"<div style='padding-top: 6px;'><b>🔄 候選 {i+1}</b></div>", unsafe_allow_html=True)
                
                # 🌟 綁定自動查表 (前綴改為 "cand")
                pet_name = cols[1].selectbox(
                    "名稱", ANIMAL_LIST, index=None, placeholder="選擇動物", 
                    key=f"cand_name_{i}", label_visibility="collapsed",
                    on_change=auto_fill_stats, args=("cand", i)
                )
                
                pet_atk = cols[2].number_input("攻擊力", min_value=1, max_value=50, step=1, key=f"cand_atk_{i}", placeholder="攻擊", label_visibility="collapsed")
                pet_hp = cols[3].number_input("生命值", min_value=1, max_value=50, step=1, key=f"cand_hp_{i}", placeholder="生命", label_visibility="collapsed")
                pet_lvl = cols[4].selectbox("等級", [1, 2, 3], index=None, placeholder="預設:1", key=f"cand_lvl_{i}", label_visibility="collapsed")
                pet_eq = cols[5].text_input("裝備", key=f"cand_eq_{i}", placeholder="", label_visibility="collapsed")
                
                if pet_name:
                    atk = pet_atk 
                    hp = pet_hp   
                    lvl = int(pet_lvl) if pet_lvl else 1
                    eq = pet_eq if pet_eq else None
                    candidate_pool.append((pet_name, atk, hp, lvl, eq))
            
            my_team_config["candidate_pool"] = candidate_pool
        
        my_team_config["food_pool"] = []

# ==========================================
# 3. 右半部：敵方陣容 (Enemy Team)
# ==========================================
with col_right:
    st.header("🔴 敵方陣容")
    enemy_mode = st.radio("選擇輸入模式 (敵方)", ["讀取檔案模式 (天梯資料)", "手動選取模式"])
    enemy_team_config = {}
    
    if enemy_mode == "讀取檔案模式 (天梯資料)":
        enemy_team_config["mode"] = "file"
        turn_files = [f"turn{i}_setup.txt" for i in range(1, 14)]
        selected_file = st.selectbox("選擇天梯回合檔案", turn_files, index=10) 
        enemy_team_config["file_path"] = selected_file
    else:
        enemy_team_config["mode"] = "manual"
        st.write("設定敵方固定陣容：")
        
        h_cols = st.columns([1.5, 3, 2, 2, 2, 2])
        h_cols[1].markdown("**名稱**")
        h_cols[2].markdown("**攻擊力**")
        h_cols[3].markdown("**生命值**")
        h_cols[4].markdown("**等級**")
        h_cols[5].markdown("**裝備**")
        
        enemy_fixed = []
        for i in range(team_size):
            cols = st.columns([1.5, 3, 2, 2, 2, 2])
            cols[0].markdown(f"<div style='padding-top: 6px;'><b>🐾 動物 {i+1}</b></div>", unsafe_allow_html=True)
            
            # 🌟 敵方同樣綁定回調函數
            pet_name = cols[1].selectbox(
                "名稱", ANIMAL_LIST, index=None, placeholder="選擇動物", 
                key=f"en_name_{i}", label_visibility="collapsed",
                on_change=auto_fill_stats, args=("en", i)
            )
            
            pet_atk = cols[2].number_input("攻擊力", min_value=1, max_value=50, step=1, key=f"en_atk_{i}", placeholder="攻擊", label_visibility="collapsed")
            pet_hp = cols[3].number_input("生命值", min_value=1, max_value=50, step=1, key=f"en_hp_{i}", placeholder="生命", label_visibility="collapsed")
            
            pet_lvl = cols[4].selectbox("等級", [1, 2, 3], index=None, placeholder="預設:1", key=f"en_lvl_{i}", label_visibility="collapsed")
            pet_eq = cols[5].text_input("裝備", key=f"en_eq_{i}", placeholder="", label_visibility="collapsed")
            
            if pet_name:
                atk = pet_atk
                hp = pet_hp
                lvl = int(pet_lvl) if pet_lvl else 1
                eq = pet_eq if pet_eq else None
                enemy_fixed.append((pet_name, atk, hp, lvl, eq))
                    
        enemy_team_config["fixed_members"] = enemy_fixed

st.markdown("---")

# ==========================================
# 4. 底部：執行模擬與輸出戰報
# ==========================================
st.header("🚀 模擬結果")

config = {
    "settings": {
        "n_simulations": n_sim,
        "team_size": team_size
    },
    "my_team": my_team_config,
    "enemy_team": enemy_team_config
}

if st.button("開始模擬 (Run Simulation)", use_container_width=True, type="primary"):
    with st.spinner('引擎全速運算中... 請稍候...'):
        response = backend.run_simulation(config)
        
        if response["status"] == "error":
            st.error(f"⚠️ 錯誤：{response['message']}")
        else:
            stats = response["stats"]
            top_results = response["top_results"]
            
            st.success(f"✅ 運算完成！總共進行了 {stats['total_battles']} 場戰鬥。")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("己方陣容總數", f"{stats['total_combinations']} 種")
            col2.metric("總耗時", f"{stats['total_time']} 秒")
            col3.metric("單一陣容平均耗時", f"{stats['avg_time_per_combo']} 秒")
            col4.metric("單場戰鬥平均耗時", f"{stats['avg_time_per_battle']} 秒")
            
            st.subheader(f"🏆 Top {len(top_results)} 最佳陣容")
            for i, res in enumerate(top_results):
                rank = i + 1
                medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "🏅"
                
                expander_title = f"{medal} 第 {rank} 名: {res['combo_str']} 👉 勝率 {res['win_rate']:.1f}% ({res['wins']}勝 / {res['draws']}平 / {res['losses']}敗)"
                with st.expander(expander_title):
                    st.write("⚔️ **對戰各組敵人詳細勝率:**")
                    for ed in res['enemy_details']:
                        st.markdown(f"- 🆚 敵方 `{ed['enemy_str']}` ➡️ **{ed['win_rate']:.1f}%** *( {ed['wins']}勝 / {ed['draws']}平 / {ed['losses']}敗 )*")