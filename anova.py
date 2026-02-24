import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scipy import stats
import pingouin as pg
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

cols_1000 = sorted([c for c in df.columns if '(1000Hz)' in c], key=lambda x: int(re.search(r'(\d+)', x).group(1)))
cols_5000 = sorted([c for c in df.columns if '(5000Hz)' in c], key=lambda x: int(re.search(r'(\d+)', x).group(1)))
df['total_1000'] = df[cols_1000].sum(axis=1)
df['total_5000'] = df[cols_5000].sum(axis=1)

# ── ONE-WAY ANOVA ──────────────────────────────────────────
anova_results = []
for col, freq_label in [('total_1000', '1000Hz'), ('total_5000', '5000Hz')]:
    aov     = pg.anova(data=df, dv=col, between='group', detailed=True)
    between = aov[aov['Source'] == 'group'].iloc[0]
    within  = aov[aov['Source'] == 'Within'].iloc[0]
    anova_results.append({
        'Freq':    freq_label,
        'F':       f"{between['F']:.3f}",
        'df1':     int(between['DF']),
        'df2':     int(within['DF']),
        'p-value': f"{between['p-unc']:.3f}",
        'R-squared':     f"{between['np2']:.3f}",
        'p_val':   between['p-unc']
    })
    print(f"{freq_label}: F({int(between['DF'])},{int(within['DF'])}) = {between['F']:.3f}, p = {between['p-unc']:.3f}")

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

ax.text(0.5, 0.95, 'One-Way ANOVA — 1000Hz & 5000Hz',
        ha='center', fontsize=13, fontweight='bold',
        fontfamily=FONT, color='#1a1a2e', transform=ax.transAxes)

headers = ['Frequency', 'F-statistic', 'df1', 'df2', 'R-squared', 'p-value']
cx = [0.05, 0.22, 0.36, 0.48, 0.61, 0.75]
cw = [0.17, 0.14, 0.12, 0.13, 0.14, 0.14]
rh = 0.22

hy = 0.72
for hdr, x, w in zip(headers, cx, cw):
    cell(ax, x, hy, w, rh, hdr, bold=True, facecolor=ALT_COLOR)

for i, row in enumerate(anova_results):
    ry     = hy - (i + 1) * rh
    row_bg = 'white' if i % 2 == 0 else '#fafafa'
    cell(ax, cx[0], ry, cw[0], rh, row['Freq'],    facecolor=row_bg, bold=True)
    cell(ax, cx[1], ry, cw[1], rh, row['F'],       facecolor=row_bg)
    cell(ax, cx[2], ry, cw[2], rh, str(row['df1']),facecolor=row_bg)
    cell(ax, cx[3], ry, cw[3], rh, str(row['df2']),facecolor=row_bg)
    cell(ax, cx[4], ry, cw[4], rh, row['R-squared'],facecolor=row_bg)
    cell(ax, cx[5], ry, cw[5], rh, row['p-value'], facecolor=row_bg)

output_path = 'one_way_anova.png'
plt.savefig(output_path, dpi=180, bbox_inches='tight', facecolor=BG)
print(f"Saved: {output_path}")
plt.show()
