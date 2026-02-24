import pandas as pd
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

# ── COMPUTE STATS ──────────────────────────────────────────
group_order = ['Tonal | Musician', 'Tonal | Non-Musician',
               'Non-Tonal | Musician', 'Non-Tonal | Non-Musician']
freq_cols   = [('200Hz', 'total_200'), ('1000Hz', 'total_1000'), ('5000Hz', 'total_5000')]

rows = []
for freq_label, col in freq_cols:
    for group in group_order:
        data = df[df['group'] == group][col].dropna()
        if len(data) >= 3:
            ks_stat, ks_p = stats.kstest(data, 'norm', args=(data.mean(), data.std()))
            sw_stat, sw_p = stats.shapiro(data)
            rows.append({
                'freq':    freq_label,
                'group':   group.replace(' | ', '\n'),
                'n':       len(data),
                'ks_stat': f'{ks_stat:.3f}',
                'ks_df':   len(data),
                'ks_sig':  f'{ks_p:.3f}*' if ks_p > 0.05 else f'{ks_p:.3f}',
                'sw_stat': f'{sw_stat:.3f}',
                'sw_df':   len(data),
                'sw_sig':  f'{sw_p:.3f}',
                'sw_p':    sw_p,
            })

# ── DRAW TABLE ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 6))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

FONT       = 'DejaVu Serif'
LINE_COLOR = '#333333'
ALT_COLOR  = '#f7f7f7'
RED_COLOR  = '#ffcccc'
RED_TEXT   = '#cc0000'

def cell(ax, x, y, w, h, text, bold=False, fontsize=9, ha='center',
         facecolor='white', textcolor='black', italic=False):
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
            fontstyle='italic' if italic else 'normal',
            color=textcolor, fontfamily=FONT, zorder=3)

# Column x positions & widths
cx = [0.01, 0.13, 0.22, 0.27, 0.36, 0.44, 0.54, 0.63, 0.72]
cw = [0.12, 0.09, 0.05, 0.09, 0.08, 0.10, 0.09, 0.09, 0.10]
rh  = 0.058
top = 0.94

# Title
ax.text(0.5, 0.975, 'Tests of Normality', transform=ax.transAxes,
        ha='center', va='center', fontsize=14, fontweight='bold',
        fontfamily=FONT, color='#1a1a2e')

# Header row 1 — merged KS and SW
h1y = top - rh
for i in range(3):
    cell(ax, cx[i], h1y, cw[i], rh, '', facecolor=ALT_COLOR)
cell(ax, cx[3], h1y, sum(cw[3:6]), rh, 'Kolmogorov-Smirnov',
     bold=True, fontsize=10, facecolor=ALT_COLOR)
cell(ax, cx[6], h1y, sum(cw[6:]), rh, 'Shapiro-Wilk',
     bold=True, fontsize=10, facecolor=ALT_COLOR)

# Header row 2
h2y = h1y - rh
for hdr, x, w in zip(['Frequency','Group','n','Statistic','df','Sig.',
                       'Statistic','df','Sig.'], cx, cw):
    cell(ax, x, h2y, w, rh, hdr, bold=True, fontsize=9.5, facecolor=ALT_COLOR)

# Data rows
prev_freq = None
for ri, row in enumerate(rows):
    ry     = h2y - (ri + 1) * rh
    row_bg = 'white' if ri % 2 == 0 else '#fafafa'

    freq_text = row['freq'] if row['freq'] != prev_freq else ''
    prev_freq = row['freq']

    cell(ax, cx[0], ry, cw[0], rh, freq_text, bold=(freq_text!=''),
         fontsize=10, ha='left', facecolor=row_bg)
    cell(ax, cx[1], ry, cw[1], rh, row['group'],
         fontsize=8, ha='left', facecolor=row_bg)
    cell(ax, cx[2], ry, cw[2], rh, str(row['n']),   facecolor=row_bg)
    cell(ax, cx[3], ry, cw[3], rh, row['ks_stat'],  facecolor=row_bg)
    cell(ax, cx[4], ry, cw[4], rh, str(row['ks_df']),facecolor=row_bg)
    cell(ax, cx[5], ry, cw[5], rh, row['ks_sig'],   facecolor=row_bg, fontsize=8.5)
    cell(ax, cx[6], ry, cw[6], rh, row['sw_stat'],  facecolor=row_bg)
    cell(ax, cx[7], ry, cw[7], rh, str(row['sw_df']),facecolor=row_bg)

    # SW Sig. — red if non-normal
    sig_bg = RED_COLOR if row['sw_p'] < 0.05 else row_bg
    sig_tc = RED_TEXT  if row['sw_p'] < 0.05 else 'black'
    cell(ax, cx[8], ry, cw[8], rh, row['sw_sig'],
         facecolor=sig_bg, textcolor=sig_tc, bold=(row['sw_p'] < 0.05))

# Footnotes
fn_y = h2y - (len(rows) + 1.3) * rh
ax.text(0.01, fn_y, '* p > .05 (lower bound of true significance)',
        transform=ax.transAxes, fontsize=8.5, fontfamily=FONT, style='italic', color='#444')
ax.text(0.01, fn_y - 0.04,
        'Red shading indicates violation of normality assumption (SW p < .05)',
        transform=ax.transAxes, fontsize=8.5, fontfamily=FONT, color=RED_TEXT)

plt.tight_layout()
output_path = 'normality_table_final.png'
plt.savefig(output_path, dpi=180, bbox_inches='tight', facecolor='white')
print(f"Saved: {output_path}")
