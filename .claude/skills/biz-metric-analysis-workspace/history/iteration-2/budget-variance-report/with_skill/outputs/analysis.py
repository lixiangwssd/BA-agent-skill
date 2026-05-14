#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q1 收入 vs 预算差异分析
用于 CFO 汇报
"""

import pandas as pd
import numpy as np

# ============================================================
# 第一步：数据接入
# ============================================================

data = {
    '区域': ['华东', '华南', '华北', '西部'],
    '预算收入': [800, 600, 500, 300],
    '实际收入': [856, 498, 445, 321]
}
df = pd.DataFrame(data)

# 计算差异
df['差异'] = df['实际收入'] - df['预算收入']
df['达成率'] = df['实际收入'] / df['预算收入']
df['差异率'] = (df['实际收入'] - df['预算收入']) / df['预算收入']

print("=" * 60)
print("Q1 收入 vs 预算差异分析")
print("=" * 60)
print(f"\n数据概览：")
print(df.to_string(index=False))

# ============================================================
# 第二步：验证异动真实性
# ============================================================

total_budget = df['预算收入'].sum()
total_actual = df['实际收入'].sum()
total_gap = total_actual - total_budget
total_gap_rate = total_gap / total_budget

print(f"\n总体情况：")
print(f"  预算收入合计：{total_budget:,} 万元")
print(f"  实际收入合计：{total_actual:,} 万元")
print(f"  总差异：{total_gap:,} 万元（{total_gap_rate:.2%}）")

# 差异分解
df['差异贡献'] = df['差异'] / total_gap

print(f"\n各区域差异贡献度：")
for _, row in df.sort_values('差异', ascending=True).iterrows():
    direction = "正向" if row['差异'] > 0 else "负向"
    print(f"  {row['区域']}：{row['差异']:+,} 万元（{row['差异贡献']:.1%}贡献，{direction}）")

# ============================================================
# 第三步：贡献度拆解
# ============================================================

print(f"\n贡献度排序（从最大负向贡献到最大正向贡献）：")
df_sorted = df.sort_values('差异', ascending=True)
print(df_sorted[['区域', '预算收入', '实际收入', '差异', '达成率', '差异贡献']].to_string(index=False))

# 计算各区域对总目标的贡献
df['预算贡献'] = df['预算收入'] / total_budget
df['实际贡献'] = df['实际收入'] / total_actual

print(f"\n各区域占比：")
print(f"  {'区域':<6} {'预算占比':>8} {'实际占比':>8} {'占比变化':>8}")
print(f"  {'-'*6} {'-'*8} {'-'*8} {'-'*8}")
for _, row in df.sort_values('预算收入', ascending=False).iterrows():
    change = row['实际贡献'] - row['预算贡献']
    print(f"  {row['区域']:<6} {row['预算贡献']:>7.1%} {row['实际贡献']:>7.1%} {change:>+7.1%}")

# ============================================================
# 第四步：根因分析
# ============================================================

print(f"\n" + "=" * 60)
print("根因分析")
print("=" * 60)

# 华南分析
south_gap = df[df['区域'] == '华南']['差异'].values[0]
south_gap_rate = df[df['区域'] == '华南']['差异率'].values[0]
print(f"\n1. 华南区（最大负向贡献）：")
print(f"   差异：{south_gap:,} 万元（{south_gap_rate:.1%}）")
print(f"   根因：CFO 已确认，一个大客户 3 月份延期签单")
print(f"   影响程度：占总体差异的 {abs(df[df['区域'] == '华南']['差异贡献'].values[0]):.1%}")

# 华北分析
north_gap = df[df['区域'] == '华北']['差异'].values[0]
north_gap_rate = df[df['区域'] == '华北']['差异率'].values[0]
print(f"\n2. 华北区（第二负向贡献）：")
print(f"   差异：{north_gap:,} 万元（{north_gap_rate:.1%}）")
print(f"   可能原因：需进一步排查（建议补充客户结构/签单数据）")

# 华东分析
east_gap = df[df['区域'] == '华东']['差异'].values[0]
east_gap_rate = df[df['区域'] == '华东']['差异率'].values[0]
print(f"\n3. 华东区（最大正向贡献）：")
print(f"   差异：{east_gap:,} 万元（{east_gap_rate:.1%}）")
print(f"   超额完成原因：需进一步了解业务背景")

# 西部分析
west_gap = df[df['区域'] == '西部']['差异'].values[0]
west_gap_rate = df[df['区域'] == '西部']['差异率'].values[0]
print(f"\n4. 西部区（正向贡献）：")
print(f"   差异：{west_gap:,} 万元（{west_gap_rate:.1%}）")

# ============================================================
# 第五步：结论与建议
# ============================================================

print(f"\n" + "=" * 60)
print("结论与建议")
print("=" * 60)

print(f"\n【结论】")
print(f"  Q1 实际收入 {total_actual:,} 万元 vs 预算 {total_budget:,} 万元，差异 {total_gap:,} 万元（{total_gap_rate:.2%}）。")
print(f"  三大负向区域（华南、华北）拉低 {abs(south_gap + north_gap):,} 万元，")
print(f"  被华东、西部的正向贡献 {east_gap + west_gap:,} 万元部分弥补。")
print(f"  其中华南区差异已确认原因（大客户延期签单），其余区域需进一步排查。")

print(f"\n【建议】")
print(f"  1. 【高优先级】华南区：与销售团队确认该客户延期签单的最新状态，")
print(f"     评估是否能在 Q2 补签或转介到其他客户，预计可挽回损失约 100 万元。")
print(f"  2. 【高优先级】华北区：排查 3 月份销售线索分配、客户跟进情况，")
print(f"     识别是市场问题（线索量减少）还是转化问题（转化率下降）。")
print(f"  3. 【中优先级】华东区：复盘超额完成原因，识别可复制的成功经验。")
print(f"  4. 【低优先级】西部区：关注增长势能是否可持续。")

# ============================================================
# 输出结果汇总
# ============================================================

summary = {
    '指标': ['总收入', '总预算', '总差异', '差异率'],
    '数值': [f'{total_actual:,}万', f'{total_budget:,}万', f'{total_gap:,}万', f'{total_gap_rate:.2%}']
}
print(f"\n【Q1 收入 vs 预算汇总】")
print(pd.DataFrame(summary).to_string(index=False))

# 保存详细数据
output_data = df.copy()
output_data['差异率'] = output_data['差异率'].apply(lambda x: f'{x:.1%}')
output_data['达成率'] = output_data['达成率'].apply(lambda x: f'{x:.1%}')
output_data['差异贡献'] = output_data['差异贡献'].apply(lambda x: f'{x:.1%}')
output_data['预算贡献'] = output_data['预算贡献'].apply(lambda x: f'{x:.1%}')
output_data['实际贡献'] = output_data['实际贡献'].apply(lambda x: f'{x:.1%}')
output_data.to_csv('/Users/lixiang/Documents/异动分析Agent/.claude/skills/biz-metric-analysis-workspace/iteration-2/budget-variance-report/with_skill/outputs/budget_variance_summary.csv', index=False, encoding='utf-8-sig')
print(f"\n详细数据已保存至 budget_variance_summary.csv")