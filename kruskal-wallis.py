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

cols_200 = sorted([c for c in df.columns if '(200Hz)' in c],
                   key=lambda x: int(re.search(r'(\d+)', x).group(1)))
df['total_200'] = df[cols_200].sum(axis=1)

group_order = ['Tonal | Musician', 'Tonal | Non-Musician',
               'Non-Tonal | Musician', 'Non-Tonal | Non-Musician']

# ── KRUSKAL-WALLIS ─────────────────────────────────────────
groups_data = [df[df['group'] == g]['total_200'].dropna() for g in group_order]
kw_stat, kw_p = stats.kruskal(*groups_data)
n, k = len(df), 4
eta2 = max((kw_stat - k + 1) / (n - k), 0)
print(f"H={kw_stat:.3f}, df={k-1}, p={kw_p:.3f}, η²={eta2:.3f}")

# ── PLOT ───────────────────────────────────────────────────
FONT       = 'DejaVu Serif'
LINE_COLOR = '#333333'
ALT_COLOR  = '#f7f7f7'
BG         = 'white'

def cell(ax, x, y, w, h, text, bold=False, fontsize=9.5, ha='center',
         facecolor='white', textcolor='black', italic=False):
    if facecolor != 'white':
        ax.add_patch(patches.Rectangle((x, y), w, h, linewidth=0,
                     facecolor=facecolor, transform=ax.transAxes, zorder=1))
    ax.add_patch(patches.Rectangle((x, y), w, h, linewidth=0.4,
                 edgecolor=LINE_COLOR, facecolor='none',
                 transform=ax.transAxes, zorder=2))
    tx = x + w/2 if ha == 'center' else x + 0.01
    ax.text(tx, y + h/2, text, transform=ax.transAxes,
            ha=ha, va='center', fontsize=fontsize,
            fontweight='bold' if bold else 'normal',
            fontstyle='italic' if italic else 'normal',
            color=textcolor, fontfamily=FONT, zorder=3)

fig, ax = plt.subplots(figsize=(12, 4))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')

ax.text(0.5, 0.95, 'Kruskal-Wallis Test — 200Hz',
        ha='center', fontsize=13, fontweight='bold',
        fontfamily=FONT, color='#1a1a2e', transform=ax.transAxes)

headers = ['Frequency', 'H-statistic', 'df', 'R-squared', 'p-value']
values  = [f'200Hz', f'{kw_stat:.3f}', str(k-1), f'{eta2:.3f}', f'{kw_p:.3f}']
cx = [0.05, 0.22, 0.38, 0.54, 0.70]
cw = [0.17, 0.16, 0.16, 0.16, 0.16]
rh = 0.22

hy = 0.72
for hdr, x, w in zip(headers, cx, cw):
    cell(ax, x, hy, w, rh, hdr, bold=True, facecolor=ALT_COLOR)

for i, (val, x, w) in enumerate(zip(values, cx, cw)):
    bold = True if i == 0 else False
    cell(ax, x, hy - rh, w, rh, val, facecolor='#fafafa', textcolor='black', bold=bold)
    
output_path = 'kruskal_wallis_200hz.png'
plt.savefig(output_path, dpi=180, bbox_inches='tight', facecolor=BG)
print(f"Saved: {output_path}")
plt.show()