#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GMV 异动分析 - 渠道维度拆分 + 华南区域假设验证
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# =====================
# 第一步：数据接入
# =====================
data = {
    '渠道': ['自然流量', '付费推广', '自然搜索', '私域流量'],
    '上周GMV': [12000000, 8000000, 5000000, 3000000],
    '本周GMV': [11500000, 6000000, 4800000, 3200000]
}
df = pd.DataFrame(data)

print("=" * 60)
print("GMV 异动分析报告")
print("=" * 60)

# =====================
# 第二步：异动验证
# =====================
df['变化量'] = df['本周GMV'] - df['上周GMV']
df['变化率'] = df['变化量'] / df['上周GMV']

total_current = df['本周GMV'].sum()
total_base = df['上周GMV'].sum()
total_change = total_current - total_base
total_change_rate = total_change / total_base

print("\n【一、概况】")
print(f"  上周 GMV：{total_base/10000:.0f} 万")
print(f"  本周 GMV：{total_current/10000:.0f} 万")
print(f"  变化量：{total_change/10000:.0f} 万")
print(f"  变化率：{total_change_rate:.1%}")
print(f"  异动判定：真实异动（|变化率| > 5% 为显著异动）")

# =====================
# 第三步：贡献度拆解
# =====================
df['贡献度'] = df['变化量'] / total_change
df['贡献度百分比'] = df['贡献度'].apply(lambda x: f"{x:.1%}")

# 按贡献度排序
df_sorted = df.sort_values('变化量', ascending=True)

print("\n【二、渠道贡献度拆解】")
print("-" * 60)
print(f"{'渠道':<10} {'上周(万)':<12} {'本周(万)':<12} {'变化量(万)':<12} {'变化率':<10} {'贡献度'}")
print("-" * 60)
for _, row in df.iterrows():
    print(f"{row['渠道']:<10} {row['上周GMV']/10000:<12.0f} {row['本周GMV']/10000:<12.0f} {row['变化量']/10000:<12.0f} {row['变化率']:<10.1%} {row['贡献度百分比']}")
print("-" * 60)
print(f"{'总计':<10} {total_base/10000:<12.0f} {total_current/10000:<12.0f} {total_change/10000:<12.0f} {total_change_rate:<10.1%} {'100.0%'}")

# 主要拖累项
top_negative = df[df['变化量'] < 0].sort_values('变化量')
print("\n【三、主要拖累项】")
print(f"  1. 付费推广：下降 200 万，贡献了 {abs(df[df['渠道']=='付费推广']['贡献度'].values[0]):.1%} 的负向变化")
print(f"  2. 自然流量：下降 50 万，贡献了 {abs(df[df['渠道']=='自然流量']['贡献度'].values[0]):.1%} 的负向变化")
print(f"  3. 自然搜索：下降 20 万，贡献了 {abs(df[df['渠道']=='自然搜索']['贡献度'].values[0]):.1%} 的负向变化")

# 唯一正增长
positive = df[df['变化量'] > 0]
if len(positive) > 0:
    print(f"\n  亮点：私域流量 增长 20 万，贡献了 {positive['贡献度'].values[0]:.1%} 的正向变化")

# =====================
# 第四步：根因分析
# =====================
print("\n【四、根因分析】")
print("""
  付费推广大幅下降 25%（-200万）是最主要的拖累因素。

  可能的根因假设：
  1. 投放预算降低或渠道出价策略调整
  2. 投放素材效果下降，导致 CTR/CVR 下降
  3. 渠道竞争加剧，CPC 上涨导致流量减少
  4. 归因窗口调整，部分转化被归因到其他渠道

  华南区域假设：
  - 用户提到"华南可能有点问题"，但当前数据只有渠道维度
  - 建议补充华南分渠道数据做交叉验证
""")

# =====================
# 第五步：可视化
# =====================
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 图1：各渠道变化量
colors = ['#d73027' if v < 0 else '#1a9641' for v in df_sorted['变化量']]
axes[0].barh(df_sorted['渠道'], df_sorted['变化量']/10000, color=colors)
axes[0].set_title('各渠道 GMV 变化量（万元）', fontsize=12)
axes[0].axvline(0, color='black', linewidth=0.8)
axes[0].set_xlabel('变化量（万元）')

# 添加数值标签
for i, (v, ch) in enumerate(zip(df_sorted['变化量'], df_sorted['渠道'])):
    axes[0].text(v/10000 - 30 if v < 0 else v/10000 + 5, i, f'{v/10000:.0f}万',
                 va='center', ha='left' if v >= 0 else 'right', fontsize=10)

# 图2：贡献度饼图
contrib_df = df.set_index('渠道')['贡献度']
contrib_df = contrib_df.sort_values()
colors_pie = ['#d73027' if v < 0 else '#1a9641' for v in contrib_df]
axes[1].pie(contrib_df.abs(), labels=contrib_df.index, autopct='%1.1f%%',
            colors=colors_pie, startangle=90)
axes[1].set_title('各渠道贡献度占比', fontsize=12)

plt.tight_layout()
plt.savefig('/Users/lixiang/Documents/异动分析Agent/.claude/skills/biz-metric-analysis-workspace/iteration-3/conversation-clarification/with_skill/outputs/gmv_analysis.png', dpi=150, bbox_inches='tight')
plt.close()

print("\n【五、可视化】")
print("  图表已保存：gmv_analysis.png")

# =====================
# 第六步：结论与建议
# =====================
print("\n【六、结论】")
print(f"  本周 GMV 环比下降 250 万（-8.9%），为显著真实异动。")
print(f"  付费推广是最大拖累项，下降 200 万，贡献了 80% 的负向变化。")
print(f"  自然流量和自然搜索也有小幅下降。")
print(f"  私域流量逆势增长 20 万，部分抵消了下滑。")

print("\n【七、行动建议】")
print("  1. 【高优先级】排查付费推广异动：")
print("     - 检查是否在近期调整了投放预算或出价策略")
print("     - 对比同类素材的历史表现，排查是否素材疲劳")
print("     - 分析 CPC 变化趋势，评估渠道竞争环境")
print("  ")
print("  2. 【中优先级】验证华南区域影响：")
print("     - 补充华南分渠道 GMV 数据进行交叉分析")
print("     - 如华南问题确认，需联动投放侧调整区域策略")
print("  ")
print("  3. 【亮点】私域流量正增长：")
print("     - 分析私域增长原因（活动？运营策略？）")
print("     - 考虑将私域运营策略复制到其他渠道")

print("\n【八、数据局限】")
print("  - 当前只有渠道维度数据，无法直接验证华南假设")
print("  - 建议补充：华南 × 渠道 交叉数据、投放关键指标（ CPC/CTR/CVR）")
print("=" * 60)