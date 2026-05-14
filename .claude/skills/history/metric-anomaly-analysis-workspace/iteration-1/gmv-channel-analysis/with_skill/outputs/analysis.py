"""
GMV 渠道异动分析
分析时间：上周 vs 前周
核心指标：GMV（万元）
拆解维度：渠道（自然搜索、付费推广、直播带货、社群裂变）
"""

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── 字体配置（支持中文） ──────────────────────────────────────────────────────
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'PingFang SC', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# ─────────────────────────────────────────────────────────────────────────────
# 第一步：数据构建（情况 B：用户粘贴的 Markdown 表格）
# ─────────────────────────────────────────────────────────────────────────────
data = {
    '渠道': ['自然搜索', '付费推广', '直播带货', '社群裂变'],
    '前周GMV': [420, 310, 180, 90],
    '上周GMV': [380, 195, 210, 55],
}

df = pd.DataFrame(data)

# ─────────────────────────────────────────────────────────────────────────────
# 第二步：基础指标计算（框架 1 + 框架 3：环比对比 + 贡献度拆解）
# ─────────────────────────────────────────────────────────────────────────────
df['变化量'] = df['上周GMV'] - df['前周GMV']
df['变化率'] = df['变化量'] / df['前周GMV']
df['变化率_pct'] = df['变化率'].map(lambda x: f"{x:+.1%}")

total_prev = df['前周GMV'].sum()       # 1000 万元
total_curr = df['上周GMV'].sum()       # 840  万元
total_delta = total_curr - total_prev  # -160 万元
total_chg_rate = total_delta / total_prev  # -16%（实际 -16%，题目给 -18% 为近似值）

# 贡献率 = 该渠道变化量 / 总变化量绝对值（用于判断各渠道拖累程度）
df['贡献量（万元）'] = df['变化量']
df['贡献率'] = df['变化量'] / abs(total_delta)
df['贡献率_pct'] = df['贡献率'].map(lambda x: f"{x:+.1%}")

# 各渠道在前周的GMV占比（结构占比）
df['前周占比'] = df['前周GMV'] / total_prev
df['前周占比_pct'] = df['前周占比'].map(lambda x: f"{x:.1%}")
df['上周占比'] = df['上周GMV'] / total_curr
df['上周占比_pct'] = df['上周占比'].map(lambda x: f"{x:.1%}")

# 排序：按贡献量升序（最拖累在最上方）
df_sorted = df.sort_values('变化量', ascending=True).reset_index(drop=True)

# ─────────────────────────────────────────────────────────────────────────────
# 第三步：打印核心结论
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 60)
print("GMV 渠道异动分析报告（数据层）")
print("=" * 60)
print(f"\n【总量】前周：{total_prev} 万元 → 上周：{total_curr} 万元")
print(f"        变化：{total_delta:+} 万元  ({total_chg_rate:+.1%})\n")

print("【各渠道明细】")
print(df_sorted[['渠道', '前周GMV', '上周GMV', '变化量', '变化率_pct',
                  '贡献量（万元）', '贡献率_pct']].to_string(index=False))

print("\n【各渠道结构占比变化】")
print(df[['渠道', '前周占比_pct', '上周占比_pct']].to_string(index=False))

# ─────────────────────────────────────────────────────────────────────────────
# 第四步：可视化
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('GMV 渠道异动分析  |  上周 vs 前周', fontsize=15, fontweight='bold', y=1.01)

# --- 子图 1：GMV 对比柱状图 ---
ax1 = axes[0]
channels = df['渠道'].tolist()
x = np.arange(len(channels))
width = 0.35

bars1 = ax1.bar(x - width/2, df['前周GMV'], width, label='前周', color='#4C72B0', alpha=0.85)
bars2 = ax1.bar(x + width/2, df['上周GMV'], width, label='上周', color='#DD8452', alpha=0.85)

ax1.set_title('各渠道 GMV 对比（万元）', fontsize=12, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(channels, fontsize=10)
ax1.set_ylabel('GMV（万元）')
ax1.legend()
ax1.set_ylim(0, 480)

for bar in bars1:
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
             f'{bar.get_height():.0f}', ha='center', va='bottom', fontsize=9)
for bar in bars2:
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
             f'{bar.get_height():.0f}', ha='center', va='bottom', fontsize=9)

# --- 子图 2：贡献量瀑布图 ---
ax2 = axes[1]
colors_bar = ['#d73027' if v < 0 else '#1a9641' for v in df_sorted['变化量']]
bars3 = ax2.barh(df_sorted['渠道'], df_sorted['变化量'], color=colors_bar, alpha=0.85)
ax2.axvline(0, color='black', linewidth=0.8)
ax2.set_title('各渠道 GMV 变化量贡献（万元）', fontsize=12, fontweight='bold')
ax2.set_xlabel('变化量（万元）')

for bar, val in zip(bars3, df_sorted['变化量']):
    offset = 1 if val >= 0 else -1
    ha = 'left' if val >= 0 else 'right'
    ax2.text(val + offset, bar.get_y() + bar.get_height()/2,
             f'{val:+.0f}', va='center', ha=ha, fontsize=10, fontweight='bold')

# --- 子图 3：变化率对比 ---
ax3 = axes[2]
chg_rates = df['变化率'].tolist()
colors_rate = ['#d73027' if v < 0 else '#1a9641' for v in chg_rates]
bars4 = ax3.bar(channels, [v * 100 for v in chg_rates], color=colors_rate, alpha=0.85)
ax3.axhline(total_chg_rate * 100, color='black', linewidth=1.2, linestyle='--',
            label=f'总体变化率 {total_chg_rate:.1%}')
ax3.set_title('各渠道 GMV 变化率（%）', fontsize=12, fontweight='bold')
ax3.set_ylabel('变化率（%）')
ax3.legend(fontsize=9)

for bar, val in zip(bars4, chg_rates):
    offset = 0.5 if val >= 0 else -0.5
    va = 'bottom' if val >= 0 else 'top'
    ax3.text(bar.get_x() + bar.get_width()/2, val * 100 + offset,
             f'{val:+.1%}', ha='center', va=va, fontsize=10, fontweight='bold')

plt.tight_layout()

output_path = '/Users/lixiang/Documents/异动分析Agent/.claude/skills/metric-anomaly-analysis-workspace/iteration-1/gmv-channel-analysis/with_skill/outputs/chart.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"\n图表已保存至：{output_path}")
plt.show()
