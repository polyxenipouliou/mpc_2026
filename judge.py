import pandas as pd
import re


def process_survey_scoring_grouped(file_path):
    # ==========================
    # 1. Define Answer Keys
    # ==========================
    # Structure: [Pattern String, Actual Frequency]

    # Part A: Center Frequency 200Hz
    key_part_a = [
        ('FFSS', 192), ('FSFF', 190), ('FSSF', 198), ('FFFF', 191), ('SFSS', 199),
        ('SSFF', 195), ('FFSS', 193), ('FSFS', 194), ('FFSF', 197), ('FSFF', 196)
    ]
    # Part B: Center Frequency 1000Hz
    key_part_b = [
        ('SFSF', 995), ('SFSF', 999), ('SFFF', 993), ('FSFF', 996), ('SFFS', 994),
        ('FFSS', 992), ('FSFS', 990), ('FSFS', 997), ('FSSF', 998), ('FSSS', 991)
    ]
    # Part C: Center Frequency 5000Hz
    key_part_c = [
        ('SSFS', 4940), ('FSFF', 4964), ('FFFF', 4976), ('FFFS', 4952), ('FFFS', 4970),
        ('SFFS', 4946), ('SFSS', 4982), ('SFFF', 4988), ('SSSF', 4958), ('FFFS', 4994)
    ]

    # Combine all keys into a single list.
    # The order must match the sequence of audio files appearing in the CSV.
    # Assumed CSV sequence: Audio 1..10 (Part A) -> Audio 1.1..10.1 (Part B) -> Audio 1.2..10.2 (Part C)
    all_keys = []
    for item in key_part_a: all_keys.append({'p': item[0], 'f': item[1], 'c': 200})
    for item in key_part_b: all_keys.append({'p': item[0], 'f': item[1], 'c': 1000})
    for item in key_part_c: all_keys.append({'p': item[0], 'f': item[1], 'c': 5000})

    # ==========================
    # 2. Read File & Prepare Metadata
    # ==========================
    try:
        df = pd.read_csv(file_path, encoding='gb18030')
    except:
        df = pd.read_csv(file_path, encoding='utf-8-sig')

    # Mapping Chinese column headers to English metadata labels
    metadata_translation = {
        '作答ID': 'Response ID', '用户ID': 'User ID',
        '开始时间': 'Start Time', '结束时间': 'End Time',
        '作答总时长(秒)': 'Total Duration (s)', 'IP': 'IP Address',
        '经度': 'Longitude', '纬度': 'Latitude',
        '省份': 'Province', '城市': 'City',
        '设备类型': 'Device Type', '操作系统类型': 'OS Type',
        '浏览器类型': 'Browser Type', '屏幕分辨率': 'Screen Resolution'
    }

    # Identify demographic information columns based on keywords
    demo_keywords = ["I hereby confirm", "age group", "What is your first language?", "languages",
                     "hobby or profession",
                     "What is it", "How long"]
    found_demo_cols = []
    for k in demo_keywords:
        for c in df.columns:
            if k in str(c):
                found_demo_cols.append(c)
                break

    # Identify audio block columns (excluding "Pair" comparison rows)
    audio_blocks = []
    seen = set()
    for c in df.columns:
        c_str = str(c).strip()
        if c_str.startswith("Audio") and "Pair" not in c_str:
            if c_str not in seen:
                audio_blocks.append(c_str)
                seen.add(c_str)

    # ==========================
    # 3. Process Each Row of Data
    # ==========================
    data_df = df.iloc[1:].copy()  # Skip the header row if necessary
    processed_rows = []

    for idx, row in data_df.iterrows():
        user_record = {}

        # A. Extract Metadata
        for cn in metadata_translation:
            if cn in df.columns:
                user_record[metadata_translation[cn]] = row[cn]
        for cn in found_demo_cols:
            if cn in df.columns:
                user_record[cn] = row[cn]

        # B. Extract User Responses
        user_responses = {}
        current_block = None
        for col in df.columns:
            c_str = str(col).strip()
            # Track which audio block we are currently in
            if c_str.startswith("Audio") and "Pair" not in c_str:
                current_block = c_str
            # Capture the selection for specific pairs
            elif "Please select" in c_str and current_block:
                match = re.search(r'Pair (\d+)-(First|Second|Equal)', c_str)
                if match:
                    p_num = int(match.group(1))
                    opt = match.group(2)
                    # Assuming '1' marks the selected option in the survey export
                    if str(row[col]).strip() == '1':
                        user_responses[(current_block, p_num)] = opt

        # C. Scoring
        for i, block_name in enumerate(audio_blocks):
            if i >= len(all_keys): break

            key_info = all_keys[i]
            correct_pattern = key_info['p']
            delta = abs(key_info['f'] - key_info['c'])  # Calculate frequency difference (Delta)
            center_freq = key_info['c']

            # Column Name Format: "Delta (Center Frequency Hz)"
            col_name = f"{delta} ({center_freq}Hz)"

            if col_name not in user_record:
                user_record[col_name] = 0

            errors = 0
            # Each audio block contains 4 pairs to compare
            for pair_idx in range(1, 5):
                ans = user_responses.get((block_name, pair_idx), "No Answer")
                correct_char = correct_pattern[pair_idx - 1]

                is_correct = False
                # Map 'F' to 'First' and 'S' to 'Second'
                if correct_char == 'F' and ans == 'First':
                    is_correct = True
                elif correct_char == 'S' and ans == 'Second':
                    is_correct = True

                if not is_correct:
                    errors += 1

            # Accumulate error count for this frequency delta
            user_record[col_name] += errors

        processed_rows.append(user_record)

    result_df = pd.DataFrame(processed_rows)

    # ==========================
    # 4. Column Sorting (Grouped by Center Frequency)
    # ==========================
    all_cols = result_df.columns.tolist()

    # Filter columns into groups
    cols_200 = [c for c in all_cols if "(200Hz)" in c]
    cols_1000 = [c for c in all_cols if "(1000Hz)" in c]
    cols_5000 = [c for c in all_cols if "(5000Hz)" in c]

    # Helper function: Extract the Delta value for numeric sorting
    def get_delta_num(col_name):
        m = re.search(r'^(\d+)', col_name)
        return int(m.group(1)) if m else 9999

    # Sort within each group (Descending order of Delta)
    cols_200.sort(key=get_delta_num, reverse=True)
    cols_1000.sort(key=get_delta_num, reverse=True)
    cols_5000.sort(key=get_delta_num, reverse=True)

    # Isolate metadata columns (keeping their original relative order)
    score_cols_set = set(cols_200 + cols_1000 + cols_5000)
    meta_cols = [c for c in all_cols if c not in score_cols_set]

    # Concatenate final column order
    final_cols = meta_cols + cols_200 + cols_1000 + cols_5000

    final_df = result_df[final_cols]
    return final_df


# === Execution and Saving ===
file_path = '59a388032ed94d8db10f69c217cea8da.csv'
df_final = process_survey_scoring_grouped(file_path)
df_final.to_csv('final_scored_grouped.csv', index=False, encoding='utf-8-sig')
print("Processing complete.")