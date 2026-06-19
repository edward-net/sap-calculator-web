import streamlit as st
import backend 
from sapai.data import data
import os
import re

# 頁面基本設定 (使用寬螢幕佈局)
st.set_page_config(page_title="SAP 戰鬥模擬器", layout="wide")

# ==========================================
# 🖼️ SVG 戰隊合照渲染器
# ==========================================
def render_team_images(combo_str):
    """將字串 [ant(2/2/L1), duck] 轉換成五個圖片欄位"""
    clean_str = combo_str.strip("[]")
    if not clean_str:
        return
        
    pet_strs = clean_str.split(", ")
    cols = st.columns(5)
    
    for i, p_str in enumerate(pet_strs):
        if i >= 5: break
        
        # 使用 Regex 切割名稱與數值
        match = re.match(r"([a-zA-Z0-9-]+)(?:\((.*)\))?", p_str)
        if match:
            name = match.group(1)
            stats = match.group(2)
        else:
            name = p_str
            stats = None
            
        with cols[i]:
            # 對應 assets 目錄下的 SVG
            img_path = os.path.join("assets", f"pet-{name}.svg")
            
            if os.path.exists(img_path):
                st.image(img_path, width="stretch") 
            else:
                st.markdown(f"<div style='text-align:center; padding:10px; border:1px dashed #aaa; border-radius:5px;'>無圖片<br>{name}</div>", unsafe_allow_html=True)
            
            # 圖片下方加上排版精美的數值文字
            display_name = name.capitalize()
            html_str = f"<div style='text-align: center; margin-top: 5px;'><b style='font-size:16px;'>{display_name}</b><br>"
            if stats:
                html_str += f"<span style='color: #888; font-size:14px;'>{stats}</span>"
            html_str += "</div>"
            
            st.markdown(html_str, unsafe_allow_html=True)


# ==========================================
# 🌟 狀態初始化與自動查表邏輯 (Callback)
# ==========================================
if "initialized" not in st.session_state:
    for i in range(10): 
        st.session_state[f"my_atk_{i}"] = None
        st.session_state[f"my_hp_{i}"] = None
        st.session_state[f"en_atk_{i}"] = None
        st.session_state[f"en_hp_{i}"] = None
        st.session_state[f"cand_atk_{i}"] = None
        st.session_state[f"cand_hp_{i}"] = None
    st.session_state["initialized"] = True

if "swap_source" not in st.session_state:
    st.session_state["swap_source"] = None

def auto_fill_stats(prefix, idx):
    pet_name = st.session_state[f"{prefix}_name_{idx}"]
    atk_key = f"{prefix}_atk_{idx}"
    hp_key = f"{prefix}_hp_{idx}"
    
    if pet_name:
        pet_id = f"pet-{pet_name}"
        if pet_id in data["pets"]:
            b_atk = data["pets"][pet_id].get("baseAttack")
            b_hp = data["pets"][pet_id].get("baseHealth")
            
            if isinstance(b_atk, int): st.session_state[atk_key] = b_atk
            else: st.session_state[atk_key] = None
                
            if isinstance(b_hp, int): st.session_state[hp_key] = b_hp
            else: st.session_state[hp_key] = None
    else:
        st.session_state[atk_key] = None
        st.session_state[hp_key] = None

def handle_swap(clicked_id):
    if st.session_state["swap_source"] is None:
        st.session_state["swap_source"] = clicked_id
    elif st.session_state["swap_source"] == clicked_id:
        st.session_state["swap_source"] = None
    else:
        src_prefix, src_idx = st.session_state["swap_source"].split("_")
        tgt_prefix, tgt_idx = clicked_id.split("_")
        
        keys = ["name", "atk", "hp", "lvl", "eq"]
        for k in keys:
            key_a = f"{src_prefix}_{k}_{src_idx}"
            key_b = f"{tgt_prefix}_{k}_{tgt_idx}"
            
            val_a = st.session_state.get(key_a, None)
            val_b = st.session_state.get(key_b, None)
            
            st.session_state[key_a] = val_b
            st.session_state[key_b] = val_a
            
        st.session_state["swap_source"] = None
        
# ==========================================
# 🐾 預設動物清單
# ==========================================
ANIMAL_LIST = [
    "ant", "badger", "bat", "beaver", "bison", "blowfish", "boar", "camel", 
    "cat", "cow", "crab", "cricket", "crocodile", "deer", "dodo", "dog", "dolphin", "dragon", 
    "dromedary", "duck", "eagle", "elephant", "fish", "flamingo", "fly", "giraffe", 
    "gorilla", "hedgehog", "hippo", "horse", "kangaroo", "leopard", "llama", "mammoth", 
    "microbe", "monkey", "mosquito", "octopus", "otter", "owl", "ox", "parrot", "peacock", 
    "penguin", "pig", "pigeon", "poodle", "rabbit", "rat", "rhino", "rooster", "sauropod", "scorpion", 
    "seal", "shark", "sheep", "shrimp", "skunk", "sloth", "snail", "snake", "spider", 
    "squirrel", "swan", "tabby-cat", "tiger", "tropical-fish", "turkey", "turtle", 
    "tyrannosaurus", "whale", "worm"
]
# 🌟 新增：預設食物清單
FOOD_LIST = [
    "apple", "bread","honey", "cupcake", "meat-bone", "sleeping-pill", "garlic", "salad-bowl", 
    "canned-food", "pear", "chili", "chocolate", "sushi", "melon", "mushroom", "pizza", "steak", "milk"
]

st.title("🐾 Super Auto Pets 戰鬥模擬器")

with st.container():
    st.subheader("⚙️ 模擬參數設定")
    col_n, col_a = st.columns(2)
    with col_n:
        n_sim = st.number_input("模擬次數 (n)", min_value=1, max_value=10000, value=5, step=1)
    with col_a:
        team_size = st.number_input("隊伍成員數量 (a)", min_value=1, max_value=5, value=5, step=1)

st.markdown("---")
col_left, col_right = st.columns(2)

with col_left:
    st.header("🔵 己方陣容")
    
    # ==========================================
    # 💾 智慧備份與還原系統 (完美修復自動補全)
    # ==========================================
    # 1. 初始化記憶變數
    if "prev_my_mode" not in st.session_state:
        st.session_state["prev_my_mode"] = "手動選取模式"
    if "manual_backup" not in st.session_state:
        st.session_state["manual_backup"] = {}

    my_mode = st.radio("選擇輸入模式 (己方)", ["手動選取模式", "讀取檔案模式 (setups.txt)"])
    
    # 2. 偵測模式切換的「瞬間」來執行存檔或還原
    if st.session_state["prev_my_mode"] == "手動選取模式" and my_mode == "讀取檔案模式 (setups.txt)":
        # 剛剛離開手動模式 ➡️ 拍照存檔
        for i in range(5):
            for k in ["name", "atk", "hp", "lvl", "eq"]:
                for prefix in ["my", "cand"]:
                    key = f"{prefix}_{k}_{i}"
                    if key in st.session_state:
                        st.session_state["manual_backup"][key] = st.session_state[key]
                        
    elif st.session_state["prev_my_mode"] == "讀取檔案模式 (setups.txt)" and my_mode == "手動選取模式":
        # 剛剛切回手動模式 ➡️ 倒回備份
        for key, val in st.session_state["manual_backup"].items():
            st.session_state[key] = val
            
    # 更新目前模式記憶
    st.session_state["prev_my_mode"] = my_mode
    
    # ==========================================
    # 🎨 UI 介面渲染
    # ==========================================
    my_team_config = {}
    
    if my_mode == "讀取檔案模式 (setups.txt)":
        my_team_config["mode"] = "file"
        my_team_config["file_path"] = "setups.txt"
        st.info("將讀取同目錄下的 setups.txt 作為測試組合。")
    else:
        my_team_config["mode"] = "manual"
        
        if st.button("🔄 一鍵交換 (固定陣容 ⇄ 動物候選池)", type="secondary", width="stretch"):
            keys = ["name", "atk", "hp", "lvl", "eq"]
            for i in range(5):
                for k in keys:
                    key_a = f"my_{k}_{i}"
                    key_b = f"cand_{k}_{i}"
                    val_a = st.session_state.get(key_a, None)
                    val_b = st.session_state.get(key_b, None)
                    st.session_state[key_a] = val_b
                    st.session_state[key_b] = val_a
            st.rerun() 
            
        st.markdown("---")
        st.write("設定您的固定陣容 (若有空位，系統會自動填入候選池動物)：")
        
        h_cols = st.columns([1.5, 3, 2, 2, 2, 2])
        h_cols[1].markdown("**名稱**")
        h_cols[2].markdown("**攻擊力**")
        h_cols[3].markdown("**生命值**")
        h_cols[4].markdown("**等級**")
        h_cols[5].markdown("**裝備**")

        fixed_members = []
        for i in range(team_size):
            cols = st.columns([1.5, 3, 2, 2, 2, 2])
            
            my_id = f"my_{i}"
            is_selected = (st.session_state["swap_source"] == my_id)
            btn_type = "primary" if is_selected else "secondary"
            btn_label = f"🎯 選擇替換" if is_selected else f"🐾 固定 {i+1}"
            
            cols[0].button(
                btn_label, key=f"btn_swap_my_{i}", type=btn_type, 
                on_click=handle_swap, args=(my_id,), width="stretch"
            )
            
            pet_name = cols[1].selectbox("名稱", ANIMAL_LIST, index=None, placeholder="選擇動物", key=f"my_name_{i}", label_visibility="collapsed", on_change=auto_fill_stats, args=("my", i))
            pet_atk = cols[2].number_input("攻擊力", min_value=1, max_value=50, step=1, key=f"my_atk_{i}", placeholder="攻擊", label_visibility="collapsed")
            pet_hp = cols[3].number_input("生命值", min_value=1, max_value=50, step=1, key=f"my_hp_{i}", placeholder="生命", label_visibility="collapsed")
            pet_lvl = cols[4].number_input("等級", min_value=1, max_value=3, step=1, key=f"my_lvl_{i}", label_visibility="collapsed")
            pet_eq = cols[5].text_input("裝備", key=f"my_eq_{i}", placeholder="", label_visibility="collapsed")
            
            if pet_name:
                atk, hp = pet_atk, pet_hp   
                lvl = int(pet_lvl) if pet_lvl else 1
                eq = pet_eq if pet_eq else None
                fixed_members.append((pet_name, atk, hp, lvl, eq))
                    
        my_team_config["fixed_members"] = fixed_members
        
        st.write("") 
        with st.expander("➕ 進階排列組合：動物候選 / 食物分配 (互斥)"):
            # 🌟 加入 Radio 按鈕來切換模式 (儲存於 session_state 供備份使用)
            pool_mode = st.radio(
                "選擇進階模式", 
                ["不使用", "動物候選池", "食物分配 (單一食物)"], 
                horizontal=True,
                key="pool_mode_radio"
            )
            
            candidate_pool = []
            food_pool = []
            
            if pool_mode == "動物候選池":
                st.info("💡 若上方固定陣容未滿 5 人，系統會將這裡的動物自動填入空缺並嘗試所有組合！")
                
                c_cols = st.columns([1.5, 3, 2, 2, 2, 2])
                c_cols[1].markdown("**名稱**")
                c_cols[2].markdown("**攻擊力**")
                c_cols[3].markdown("**生命值**")
                c_cols[4].markdown("**等級**")
                c_cols[5].markdown("**裝備**")
                
                for i in range(5):
                    cols = st.columns([1.5, 3, 2, 2, 2, 2])
                    cand_id = f"cand_{i}"
                    is_selected = (st.session_state["swap_source"] == cand_id)
                    btn_type = "primary" if is_selected else "secondary"
                    btn_label = f"🎯 選擇替換" if is_selected else f"🔄 候選 {i+1}"
                    
                    cols[0].button(
                        btn_label, key=f"btn_swap_cand_{i}", type=btn_type, 
                        on_click=handle_swap, args=(cand_id,), width="stretch"
                    )
                    
                    pet_name = cols[1].selectbox("名稱", ANIMAL_LIST, index=None, placeholder="選擇動物", key=f"cand_name_{i}", label_visibility="collapsed", on_change=auto_fill_stats, args=("cand", i))
                    pet_atk = cols[2].number_input("攻擊力", min_value=1, max_value=50, step=1, key=f"cand_atk_{i}", placeholder="攻擊", label_visibility="collapsed")
                    pet_hp = cols[3].number_input("生命值", min_value=1, max_value=50, step=1, key=f"cand_hp_{i}", placeholder="生命", label_visibility="collapsed")
                    pet_lvl = cols[4].number_input("等級", min_value=1, max_value=3, step=1, key=f"cand_lvl_{i}", label_visibility="collapsed")
                    pet_eq = cols[5].text_input("裝備", key=f"cand_eq_{i}", placeholder="", label_visibility="collapsed")
                    
                    if pet_name:
                        atk, hp = pet_atk, pet_hp   
                        lvl = int(pet_lvl) if pet_lvl else 1
                        eq = pet_eq if pet_eq else None
                        candidate_pool.append((pet_name, atk, hp, lvl, eq))
                        
            elif pool_mode == "食物分配 (單一食物)":
                st.info("💡 系統會將您選擇的 1 個食物，輪流分配給固定陣容中的一隻動物 (需先將固定陣容填滿 5 人)。")
                food_name = st.selectbox(
                    "選擇要分配的食物", 
                    FOOD_LIST, 
                    index=None, 
                    placeholder="點擊選擇食物 (例如: garlic)", 
                    key="cand_food_select"
                )
                if food_name:
                    food_pool = [food_name]
            
            my_team_config["candidate_pool"] = candidate_pool
            my_team_config["food_pool"] = food_pool
            
            # ====================
            # 👇 在這裡補上食物與模式的備份
            # ====================
            for i in range(5):
                for k in ["name", "atk", "hp", "lvl", "eq"]:
                    for prefix in ["my", "cand"]:
                        key = f"{prefix}_{k}_{i}"
                        if key in st.session_state:
                            st.session_state["manual_backup"][key] = st.session_state[key]
                        
            # 🌟 額外備份食物模式選項與選中的食物
            for key in ["pool_mode_radio", "cand_food_select"]:
                if key in st.session_state:
                    st.session_state["manual_backup"][key] = st.session_state[key]


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
            
            pet_name = cols[1].selectbox("名稱", ANIMAL_LIST, index=None, placeholder="選擇動物", key=f"en_name_{i}", label_visibility="collapsed", on_change=auto_fill_stats, args=("en", i))
            pet_atk = cols[2].number_input("攻擊力", min_value=1, max_value=50, step=1, key=f"en_atk_{i}", placeholder="攻擊", label_visibility="collapsed")
            pet_hp = cols[3].number_input("生命值", min_value=1, max_value=50, step=1, key=f"en_hp_{i}", placeholder="生命", label_visibility="collapsed")
            pet_lvl = cols[4].number_input("等級", min_value=1, max_value=3, step=1, key=f"en_lvl_{i}", label_visibility="collapsed")
            pet_eq = cols[5].text_input("裝備", key=f"en_eq_{i}", placeholder="", label_visibility="collapsed")
            
            if pet_name:
                atk, hp = pet_atk, pet_hp
                lvl = int(pet_lvl) if pet_lvl else 1
                eq = pet_eq if pet_eq else None
                enemy_fixed.append((pet_name, atk, hp, lvl, eq))
                    
        enemy_team_config["fixed_members"] = enemy_fixed

st.markdown("---")

st.header("🚀 模擬結果")

config = {
    "settings": {
        "n_simulations": n_sim,
        "team_size": team_size
    },
    "my_team": my_team_config,
    "enemy_team": enemy_team_config
}

# 🌟 改變邏輯：點擊模擬後，把結果存進 session_state
if st.button("開始模擬 (Run Simulation)", width="stretch", type="primary"):
    with st.spinner('引擎全速運算中... 請稍候...'):
        st.session_state["sim_response"] = backend.run_simulation(config)

# 🌟 從 session_state 讀取並渲染畫面 (這樣點擊內部按鈕就不會消失了！)
if "sim_response" in st.session_state:
    response = st.session_state["sim_response"]
    
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
        
        # 🌟 新增：將標題與「匯出按鈕」並排顯示
        col_title, col_btn = st.columns([4, 1])
        with col_title:
            st.subheader(f"🏆 Top {len(top_results)} 最佳陣容")
        with col_btn:
            # 點擊後，以覆寫模式 ("w") 寫入 setups.txt
            if st.button("💾 匯出至 setups.txt", width="stretch", type="primary"):
                try:
                    with open("setups.txt", "w", encoding="utf-8") as f:
                        for res in top_results:
                            # 每一行寫入方括號字串，並加上換行符號
                            f.write(res['combo_str'] + "\n")
                            
                    # st.toast 會在右下角彈出短暫的成功提示，不干擾畫面！
                    st.toast("✅ 已成功覆寫並寫入 setups.txt！", icon="💾")
                except Exception as e:
                    st.error(f"寫入失敗: {e}")
        
        for i, res in enumerate(top_results):
            rank = i + 1
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "🏅"
            
            expander_title = f"{medal} 第 {rank} 名: {res['combo_str']} 👉 勝率 {res['win_rate']:.1f}% ({res['wins']}勝 / {res['draws']}平 / {res['losses']}敗)"
            with st.expander(expander_title):
                
                # 依然保留一鍵複製區塊
                st.markdown("📋 **點擊右側按鈕一鍵複製陣容：**")
                st.code(res['combo_str'], language=None)
                
                # 呼叫我們新寫的 SVG 戰隊渲染器！
                render_team_images(res['combo_str'])
                
                st.write("---")
                st.write("⚔️ **對戰各組敵人詳細勝率:**")
                for ed in res['enemy_details']:
                    st.markdown(f"- 🆚 敵方 `{ed['enemy_str']}` ➡️ **{ed['win_rate']:.1f}%** *( {ed['wins']}勝 / {ed['draws']}平 / {ed['losses']}敗 )*")