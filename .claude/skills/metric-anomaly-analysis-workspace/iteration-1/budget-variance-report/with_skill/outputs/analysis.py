"""
Q1 收入 vs 预算差异分析
分析框架：框架2（实际 vs 目标差异拆解）+ 框架3（贡献度拆解-加法模型）
报告日期：2026-05-11
"""

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ── 中文字体 ──────────────────────────────────
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# ─────────────────────────────────────────────
# 第一步：数据录入（情况 B：用户粘贴表格数据）
# ─────────────────────────────────────────────
raw = {
    '区域':   ['华东', '华南', '华北', '西部'],
    '预算收入': [800,   600,   500,   300],
    '实际收入': [856,   498,   445,   321],
}
df = pd.DataFrame(raw)

# 已知背景
known_context = {
    '华南': '大客户3月延期签单（偶发性，非市场结构问题）'
}

# ─────────────────────────────────────────────
# 第二步：框架2 — 实际 vs 目标差异拆解
# ─────────────────────────────────────────────
df['差异']  = df['实际收入'] - df['预算收入']    # 绝对差异
df['达成率'] = df['实际收入'] / df['预算收入']   # 达成率
df['差异率'] = df['差异'] / df['预算收入']       # 差异率

# ─────────────────────────────────────────────
# 第三步：框架3 — 贡献度拆解（加法模型）
# ─────────────────────────────────────────────
total_variance = df['差异'].sum()   # -80 万元
df['贡献量'] = df['差异']
df['贡献率'] = df['差异'] / abs(total_variance)

df_sorted = df.sort_values('差异', ascending=True).reset_index(drop=True)

# 汇总行
total_row = pd.DataFrame([{
    '区域': '合计',
    '预算收入': df['预算收入'].sum(),
    '实际收入': df['实际收入'].sum(),
    '差异': total_variance,
    '达成率': df['实际收入'].sum() / df['预算收入'].sum(),
    '差异率': total_variance / df['预算收入'].sum(),
    '贡献量': total_variance,
    '贡献率': 1.0,
}])

# ─────────────────────────────────────────────
# 控制台打印
# ─────────────────────────────────────────────
print("=" * 60)
print("  Q1 收入 vs 预算差异分析")
print("=" * 60)

summary = pd.concat([df, total_row], ignore_index=True)
print(summary[['区域','预算收入','实际收入','差异','达成率','差异率','贡献率']].to_string(
    index=False,
    formatters={
        '预算收入': '{:,.0f}'.format,
        '实际收入': '{:,.0f}'.format,
        '差异':     '{:+,.0f}'.format,
        '达成率':   '{:.1%}'.format,
        '差异率':   '{:+.1%}'.format,
        '贡献率':   '{:+.1%}'.format,
    }
))

print(f"\n总缺口：{total_variance:+.0f} 万元（达成率 {df['实际收入'].sum()/df['预算收入'].sum():.1%}）")
print("\n贡献排名（从大拖累到大拉动）：")
for _, row in df_sorted.iterrows():
    tag = f"  ← {known_context[row['区域']]}" if row['区域'] in known_context else ""
    direction = '▼' if row['差异'] < 0 else '▲'
    print(f"  {direction} {row['区域']}: {row['差异']:+.0f} 万元 | 贡献率 {row['贡献率']:+.1%}{tag}")

# ─────────────────────────────────────────────
# 第五步：可视化
# ─────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('Q1 收入 vs 预算差异分析', fontsize=15, fontweight='bold')

regions  = df['区域'].tolist()
budget   = df['预算收入'].tolist()
actual   = df['实际收入'].tolist()
variance = df['差异'].tolist()
attain   = df['达成率'].tolist()

# ── 图1：预算 vs 实际柱状图 ──────────────────
x = np.arange(len(regions))
w = 0.35
b1 = axes[0].bar(x - w/2, budget, w, label='预算收入', color='#4472C4', alpha=0.85)
b2 = axes[0].bar(x + w/2, actual, w, label='实际收入', color='#ED7D31', alpha=0.85)
axes[0].set_title('预算 vs 实际收入（万元）', fontsize=12, fontweight='bold')
axes[0].set_xticks(x); axes[0].set_xticklabels(regions)
axes[0].set_ylabel('万元'); axes[0].legend()
for bar in list(b1) + list(b2):
    axes[0].annotate(f'{bar.get_height():.0f}',
                     xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                     xytext=(0, 3), textcoords='offset points',
                     ha='center', va='bottom', fontsize=9)

# ── 图2：差异贡献瀑布图 ────────────────────
c2 = ['#C00000' if v < 0 else '#375623' for v in variance]
b3 = axes[1].bar(regions, variance, color=c2, edgecolor='white')
axes[1].set_title('各区域对总缺口的贡献（万元）', fontsize=12, fontweight='bold')
axes[1].set_ylabel('差异（万元）')
axes[1].axhline(0, color='black', linewidth=1, linestyle='--')
axes[1].set_ylim(min(variance) * 1.4, max(variance) * 1.6)
for bar, val in zip(b3, variance):
    offset = 5 if val >= 0 else -14
    axes[1].annotate(f'{val:+.0f}',
                     xy=(bar.get_x() + bar.get_width()/2, val),
                     xytext=(0, offset), textcoords='offset points',
                     ha='center', fontsize=11, fontweight='bold',
                     color='#C00000' if val < 0 else '#375623')

# ── 图3：达成率横向条形图 ──────────────────
c3 = ['#C00000' if a < 1.0 else '#375623' for a in attain]
b4 = axes[2].barh(regions, attain, color=c3, alpha=0.85)
axes[2].axvline(1.0, color='black', linewidth=1.5, linestyle='--', label='预算基准 100%')
axes[2].set_title('各区域预算达成率', fontsize=12, fontweight='bold')
axes[2].set_xlabel('达成率')
axes[2].xaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f'{v:.0%}'))
axes[2].set_xlim(0.78, 1.15); axes[2].legend()
for bar, val in zip(b4, attain):
    axes[2].annotate(f'{val:.1%}',
                     xy=(val, bar.get_y() + bar.get_height()/2),
                     xytext=(5, 0), textcoords='offset points',
                     ha='left', va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
out_img = '/Users/lixiang/Documents/异动分析Agent/.claude/skills/metric-anomaly-analysis-workspace/iteration-1/budget-variance-report/with_skill/outputs/chart.png'
plt.savefig(out_img, dpi=150, bbox_inches='tight')
print(f"\n图表已保存：{out_img}")
plt.show()
