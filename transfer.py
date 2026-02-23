import pandas as pd
import re


def process_and_translate_survey_data(file_path):
    # 1. Read CSV file (handle Chinese encoding)
    try:
        # gb18030 is a Chinese character set that covers gbk and most rare characters
        df = pd.read_csv(file_path, encoding='gb18030')
    except UnicodeDecodeError:
        # If failed, try utf-8-sig
        df = pd.read_csv(file_path, encoding='utf-8-sig')

    # 2. Define column name translation dictionary (Chinese -> English)
    metadata_translation = {
        '作答 ID': 'Response ID',
        '用户 ID': 'User ID',
        '开始时间': 'Start Time',
        '结束时间': 'End Time',
        '作答总时长 (秒)': 'Total Duration (s)',
        'IP': 'IP Address',
        '经度': 'Longitude',
        '纬度': 'Latitude',
        '省份': 'Province',
        '城市': 'City',
        '设备类型': 'Device Type',
        '操作系统类型': 'OS Type',
        '浏览器类型': 'Browser Type',
        '屏幕分辨率': 'Screen Resolution'
    }

    # Get all metadata column names to be processed (original Chinese names)
    metadata_cols_cn = list(metadata_translation.keys())

    # Define search keywords for demographic questions (keep original question text)
    demographic_keywords = [
        "I hereby confirm that",
        "Please select your age group",
        "What is your first language?",
        "What other languages are you fluent in",
        "Have you ever had, or do you still have",
        "What is it/was it",
        "How long did you do it"
    ]

    # Find actual existing demographic columns in the DataFrame
    found_demo_cols = []
    for keyword in demographic_keywords:
        for col in df.columns:
            if keyword in str(col):
                found_demo_cols.append(col)
                break

    # 3. Process data rows
    # Skip row 0 (metadata/question instructions), keep only user data from row 1 onwards
    data_df = df.iloc[1:].copy()
    processed_rows = []

    for idx, row in data_df.iterrows():
        row_data = {}

        # A: Process metadata (and rename simultaneously)
        for col_cn in metadata_cols_cn:
            if col_cn in df.columns:
                english_name = metadata_translation[col_cn]
                row_data[english_name] = row[col_cn]

        # B: Process demographic information (keep original column names)
        for col in found_demo_cols:
            if col in df.columns:
                row_data[col] = row[col]

        # C: Process audio experiment data (merge First/Second/Equal options)
        current_audio_block = None
        for col_name in df.columns:
            col_str = str(col_name).strip()

            # Identify Audio block (e.g., "Audio 1", "Audio 2.1")
            if col_str.startswith("Audio") and "Pair" not in col_str:
                current_audio_block = col_str

            # Identify specific option columns
            elif "Please select the one you think is higher in each pair" in col_str:
                if current_audio_block:
                    # Extract Pair number and option (First/Second/Equal)
                    match = re.search(r'Pair (\d+)-(First|Second|Equal)', col_str)
                    if match:
                        pair_num = match.group(1)
                        option_type = match.group(2)

                        # If the user selected this item (value is '1')
                        cell_value = str(row[col_name]).strip()
                        if cell_value == '1':
                            new_col_name = f"{current_audio_block} - Pair {pair_num}"
                            row_data[new_col_name] = option_type

        processed_rows.append(row_data)

    # 4. Generate result DataFrame
    result_df = pd.DataFrame(processed_rows)
    return result_df


# === Usage Example ===
# Please replace with your actual local file path
file_path = '59a388032ed94d8db10f69c217cea8da.csv'
df_final = process_and_translate_survey_data(file_path)

# Print result preview
# print(df_final.head().T)

# Save as CSV
df_final.to_csv('processed_data_english.csv', index=False, encoding='utf-8-sig')