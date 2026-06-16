import backend

# 模擬前端 UI 蒐集到的資料
sample_config = {
    "settings": {
        "n_simulations": 5,
        "team_size": 5
    },
    "my_team": {
        "mode": "manual",
        "fixed_members": [
            ("mosquito", None, None, None, None),
            ("fish", None, None, None, "honey"),
            ("duck", None, None, None, None),
            ("ant", None, None, None, None),
            ("beaver", None, None, None, None),
            # (如果使用者在 UI 留空，前端就不傳，後端就知道要組合)
        ],
        "candidate_pool": [("sheep", 4, 4, 2, None)],
        "food_pool": []
    },
    "enemy_team": {
        "mode": "file",
        "file_path": "turn2_setup.txt"
    }
}

# 把「訂單」交給廚房，瞬間拿到結構化的戰報結果！
response = backend.run_simulation(sample_config)

if response["status"] == "success":
    print(f"✅ 模擬成功！總共跑了 {response['stats']['total_battles']} 場。")
    print(f"🥇 第一名陣容：{response['top_results'][0]['combo_str']}")
else:
    print(f"❌ 錯誤：{response['message']}")