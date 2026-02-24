import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scipy import stats
import re
import warnings
warnings.filterwarnings('ignore')

# ── LOAD & CLASSIFY ────────────────────────────────────────
df = pd.read_csv('final_scored_grouped_2.csv', encoding='utf-8-sig')
df.columns = [c.replace('\xa0', ' ').strip() for c in df.columns]

lang_col  = [c for c in df.columns if 'first language' in c.lower()][0]
music_col = [c for c in df.columns if 'what is it' in c.lower()][0]
years_col = [c for c in df.columns if 'how long' in c.lower()][0]

tonal_languages   = ['chinese', 'mandarin', 'cantonese', 'thai', 'vietnamese']
musician_keywords = ['musician', 'piano', 'guitar', 'violin', 'drums', 'flute',
                     'singing', 'playing', 'composing', 'composition', 'mixing',
                     'producing', 'jazz', 'recording', 'performing', 'ukulele',
                     'vocalist', 'teacher', 'academic', 'writing', 'song']

def classify_tonal(row):
    return any(t in str(row[lang_col]).lower() for t in tonal_languages)

def classify_musician(row):
    music = str(row[music_col]).lower()
    if music == 'nan': return False
    if not any(k in music for k in musician_keywords): return False
    years_raw = str(row[years_col]).lower()
    if years_raw == 'nan': return False
    if 'month' in years_raw and 'year' not in years_raw: return False
    elif any(w in years_raw for w in ['many', 'several', 'more than', '10+', '15+']): return True
    elif 'since' in years_raw or 'ago' in years_raw:
        nums = re.findall(r'\d+', years_raw); return int(nums[-1]) >= 3 if nums else False
    elif 'age' in years_raw:
        nums = re.findall(r'\d+', years_raw); return (26 - int(nums[0])) >= 3 if nums else False
    elif 'year' in years_raw or 'yr' in years_raw:
        nums = re.findall(r'\d+', years_raw); return int(nums[0]) >= 3 if nums else False
    else:
        nums = re.findall(r'\d+', years_raw); return int(nums[0]) >= 3 if nums else False

df['is_tonal']    = df.apply(classify_tonal, axis=1)
df['is_musician'] = df.apply(classify_musician, axis=1)
df['group']       = df.apply(lambda r:
    ('Tonal' if r['is_tonal'] else 'Non-Tonal') + ' | ' +
    ('Musician' if r['is_musician'] else 'Non-Musician'), axis=1)

cols_200  = sorted([c for c in df.columns if '(200Hz)'  in c], key=lambda x: int(re.search(r'(\d+)', x).group(1)))
cols_1000 = sorted([c for c in df.columns if '(1000Hz)' in c], key=lambda x: int(re.search(r'(\d+)', x).group(1)))
cols_5000 = sorted([c for c in df.columns if '(5000Hz)' in c], key=lambda x: int(re.search(r'(\d+)', x).group(1)))
df['total_200']  = df[cols_200].sum(axis=1)
df['total_1000'] = df[cols_1000].sum(axis=1)
df['total_5000'] = df[cols_5000].sum(axis=1)

# ── LEVENE'S TEST ──────────────────────────────────────────
group_order = ['Tonal | Musician', 'Tonal | Non-Musician',
               'Non-Tonal | Musician', 'Non-Tonal | Non-Musician']
freq_cols   = [('200Hz', 'total_200'), ('1000Hz', 'total_1000'), ('5000Hz', 'total_5000')]

rows = []
for freq_label, col in freq_cols:
    groups_data = [df[df['group'] == g][col].dropna() for g in group_order]
    lev_stat, lev_p = stats.levene(*groups_data)
    rows.append({
        'freq':      freq_label,
        'F':         f'{lev_stat:.3f}',
        'df1':       3,
        'df2':       len(df) - 4,
        'p':         f'{lev_p:.3f}',
        'p_val':     lev_p,
        'result':    'Equal' if lev_p > 0.05 else 'Unequal',
        'next_step': 'ANOVA / Kruskal-Wallis' if lev_p > 0.05 else "Welch's ANOVA / Kruskal-Wallis"
    })

# ── DRAW SPSS-STYLE TABLE ──────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 4))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

FONT      = 'DejaVu Serif'
ALT_COLOR = '#f7f7f7'
RED_COLOR = '#ffcccc'
RED_TEXT  = '#cc0000'
LINE_COLOR= '#333333'

def cell(ax, x, y, w, h, text, bold=False, fontsize=9, ha='center',
         facecolor='white', textcolor='black'):
    if facecolor != 'white':
        ax.add_patch(patches.Rectangle((x, y), w, h, linewidth=0,
                     facecolor=facecolor, transform=ax.transAxes, zorder=1))
    ax.add_patch(patches.Rectangle((x, y), w, h, linewidth=0.4,
                 edgecolor=LINE_COLOR, facecolor='none',
                 transform=ax.transAxes, zorder=2))
    tx = x + w/2 if ha == 'center' else x + 0.012
    ax.text(tx, y + h/2, text, transform=ax.transAxes,
            ha=ha, va='center', fontsize=fontsize,
            fontweight='bold' if bold else 'normal',
            color=textcolor, fontfamily=FONT, zorder=3)

cx = [0.05, 0.23, 0.38, 0.51, 0.64]
cw = [0.18, 0.15, 0.13, 0.13, 0.25]
rh  = 0.16
top = 0.82

# Title
ax.text(0.5, 0.93, "Levene's Test of Equality of Variances",
        transform=ax.transAxes, ha='center', va='center',
        fontsize=13, fontweight='bold', fontfamily=FONT, color='#1a1a2e')

# Headers
headers = ['Frequency', 'F-statistic', 'df1', 'df2', 'Sig.']
hy = top - rh
for hdr, x, w in zip(headers, cx, cw):
    cell(ax, x, hy, w, rh, hdr, bold=True, fontsize=9.5, facecolor=ALT_COLOR)

# Data rows
for ri, row in enumerate(rows):
    ry     = hy - (ri + 1) * rh
    row_bg = 'white' if ri % 2 == 0 else '#fafafa'
    p_bg   = RED_COLOR if row['p_val'] < 0.05 else row_bg
    p_tc   = RED_TEXT  if row['p_val'] < 0.05 else 'black'

    cell(ax, cx[0], ry, cw[0], rh, row['freq'],     bold=True, facecolor=row_bg)
    cell(ax, cx[1], ry, cw[1], rh, row['F'],         facecolor=row_bg)
    cell(ax, cx[2], ry, cw[2], rh, str(row['df1']),  facecolor=row_bg)
    cell(ax, cx[3], ry, cw[3], rh, str(row['df2']),  facecolor=row_bg)
    cell(ax, cx[4], ry, cw[4], rh, row['p'],         facecolor=p_bg, textcolor=p_tc, bold=(row['p_val']<0.05))

plt.tight_layout()
output_path = 'levene_table.png'
plt.savefig(output_path, dpi=180, bbox_inches='tight', facecolor='white')
print(f"Saved: {output_path}")
plt.show()
