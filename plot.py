import pandas as pd
import re
import matplotlib.pyplot as plt


def generate_plots_with_id_names(file_path):
    # ==========================
    # 1. Data Processing and Scoring
    # ==========================

    # Standard answer configuration
    # (Sequence pattern, target frequency)
    key_part_a = [('FFSS', 192), ('FSFF', 190), ('FSSF', 198), ('FFFF', 191), ('SFSS', 199),
                  ('SSFF', 195), ('FFSS', 193), ('FSFS', 194), ('FFSF', 197), ('FSFF', 196)]
    key_part_b = [('SFSF', 995), ('SFSF', 999), ('SFFF', 993), ('FSFF', 996), ('SFFS', 994),
                  ('FFSS', 992), ('FSFS', 990), ('FSFS', 997), ('FSSF', 998), ('FSSS', 991)]
    key_part_c = [('SSFS', 4940), ('FSFF', 4964), ('FFFF', 4976), ('FFFS', 4952), ('FFFS', 4970),
                  ('SFFS', 4946), ('SFSS', 4982), ('SFFF', 4988), ('SSSF', 4958), ('FFFS', 4994)]

    # Flatten the keys into a list of dictionaries with center frequencies (c)
    all_keys = []
    for item in key_part_a: all_keys.append({'p': item[0], 'f': item[1], 'c': 200})
    for item in key_part_b: all_keys.append({'p': item[0], 'f': item[1], 'c': 1000})
    for item in key_part_c: all_keys.append({'p': item[0], 'f': item[1], 'c': 5000})

    # Read the file with encoding fallback
    try:
        df = pd.read_csv(file_path, encoding='gb18030')
    except:
        df = pd.read_csv(file_path, encoding='utf-8-sig')

    # Identify the specific Audio columns for processing
    audio_blocks = []
    seen = set()
    for c in df.columns:
        c_str = str(c).strip()
        if c_str.startswith("Audio") and "Pair" not in c_str:
            if c_str not in seen:
                audio_blocks.append(c_str)
                seen.add(c_str)

    # Process scores from the data (excluding the header row if necessary)
    data_df = df.iloc[1:].copy()
    processed_data = []

    for idx, row in data_df.iterrows():
        user_record = {}
        user_responses = {}
        current_block = None

        # Extract user responses from columns
        for col in df.columns:
            c_str = str(col).strip()
            if c_str.startswith("Audio") and "Pair" not in c_str:
                current_block = c_str
            elif "Please select" in c_str and current_block:
                match = re.search(r'Pair (\d+)-(First|Second|Equal)', c_str)
                if match:
                    p_num = int(match.group(1))
                    opt = match.group(2)
                    # Checking if the option was selected (marked as '1')
                    if str(row[col]).strip() == '1':
                        user_responses[(current_block, p_num)] = opt

        # Compare responses against the answer key to calculate error counts
        for i, block_name in enumerate(audio_blocks):
            if i >= len(all_keys): break
            key = all_keys[i]
            delta = abs(key['f'] - key['c'])
            col_name = f"{delta} ({key['c']}Hz)"

            if col_name not in user_record: user_record[col_name] = 0
            err = 0
            for p in range(1, 5):
                ans = user_responses.get((block_name, p), "No Answer")
                corr = key['p'][p - 1]
                # 'F' stands for First, 'S' stands for Second
                if not ((corr == 'F' and ans == 'First') or (corr == 'S' and ans == 'Second')):
                    err += 1
            user_record[col_name] += err
        processed_data.append(user_record)

    df_scores = pd.DataFrame(processed_data)

    # ==========================
    # 2. Plotting Section (Auto-naming)
    # ==========================
    plt.style.use('ggplot')
    # Set fonts for Unicode support (Chinese/Special chars)
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False

    # Helper function to sort columns by the frequency delta
    def get_cols_sorted(all_cols, freq_tag):
        cols = [c for c in all_cols if freq_tag in c]
        cols.sort(key=lambda x: int(re.search(r'^(\d+)', x).group(1)))
        return cols

    all_cols = df_scores.columns.tolist()
    cols_200 = get_cols_sorted(all_cols, "(200Hz)")
    cols_1000 = get_cols_sorted(all_cols, "(1000Hz)")
    cols_5000 = get_cols_sorted(all_cols, "(5000Hz)")

    # Use enumerate to generate an auto-incrementing ID for filenames (starting at 1)
    for i, (idx, row) in enumerate(df_scores.iterrows(), start=1):
        fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)

        def plot_subplot(ax, cols, title_freq):
            deltas = [str(int(re.search(r'^(\d+)', c).group(1))) for c in cols]
            values = [row[c] for c in cols]
            bars = ax.bar(deltas, values, color='#5DADE2', edgecolor='black', alpha=0.8)
            ax.set_title(f"{title_freq} (Center Freq)", fontsize=14, fontweight='bold')
            ax.set_xlabel("Frequency Difference (Hz)", fontsize=12)
            if ax == axes[0]: ax.set_ylabel("Error Count", fontsize=12)
            ax.set_ylim(0, 4.5)

            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2., height + 0.05,
                        '%d' % int(height), ha='center', va='bottom', fontsize=11)

        plot_subplot(axes[0], cols_200, "200Hz")
        plot_subplot(axes[1], cols_1000, "1000Hz")
        plot_subplot(axes[2], cols_5000, "5000Hz")

        plt.tight_layout()

        # --- Modification: Using the auto-increment ID as the filename ---
        filename = f"{i}.png"
        plt.savefig(filename, bbox_inches='tight', dpi=150)
        plt.close()
        print(f"Saved plot: {filename}")


# === Execution ===
file_path = '2.csv'
generate_plots_with_id_names(file_path)