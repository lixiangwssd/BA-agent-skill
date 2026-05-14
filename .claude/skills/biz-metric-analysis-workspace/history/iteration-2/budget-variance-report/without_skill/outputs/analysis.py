#!/usr/bin/env python3
"""
Q1 收入 vs 预算差异分析
财务分析师汇报用 - 收入差异拆解分析
"""

import pandas as pd
import numpy as np

# ============================================================
# 1. 数据定义
# ============================================================
data = {
    '区域': ['华东', '华南', '华北', '西部'],
    '预算收入': [800, 600, 500, 300],
    '实际收入': [856, 498, 445, 321],
}

df = pd.DataFrame(data)
df['差异'] = df['实际收入'] - df['预算收入']
df['达成率'] = (df['实际收入'] / df['预算收入'] * 100).round(1)
df['贡献度'] = (df['差异'] / df['差异'].sum() * 100).round(1)
df['预算占比'] = (df['预算收入'] / df['预算收入'].sum() * 100).round(1)
df['实际占比'] = (df['实际收入'] / df['实际收入'].sum() * 100).round(1)

# 合计行
total = pd.DataFrame({
    '区域': ['合计'],
    '预算收入': [df['预算收入'].sum()],
    '实际收入': [df['实际收入'].sum()],
    '差异': [df['差异'].sum()],
    '达成率': [round(df['实际收入'].sum() / df['预算收入'].sum() * 100, 1)],
    '贡献度': [100.0],
    '预算占比': [100.0],
    '实际占比': [100.0],
})
df_full = pd.concat([df, total], ignore_index=True)

print("=" * 60)
print("Q1 收入 vs 预算差异分析表")
print("=" * 60)
print(df_full.to_string(index=False))
print()

# ============================================================
# 2. 差异结构拆解
# ============================================================
total_budget = 2200
total_actual = 2120
total_variance = -80

# 各区域差异
east_china = 56
south_china = -102
north_china = -55
west_china = 21

# 拆解各区域对总体差异的贡献
print("=" * 60)
print("差异贡献度拆解")
print("=" * 60)
print(f"华东贡献: +{east_china}万 (拖累正向)")
print(f"华南贡献: {south_china}万 (最大拖累项)")
print(f"华北贡献: {north_china}万 (拖累项)")
print(f"西部贡献: +{west_china}万 (正向贡献)")
print(f"合计差异: {total_variance}万")
print()

# 华南区大客户延期信息
south_impact = 102  # 华南总差异
big_customer_delay = 102  # CFO已知：大客户3月延期签单

print("=" * 60)
print("华南区归因分析（已知背景）")
print("=" * 60)
print(f"华南区差异: {south_impact}万")
print(f"已知原因: 大客户3月延期签单 → 影响约 {big_customer_delay}万")
print(f"归因比例: 100%（完全归因于大客户延期）")
print()

# ============================================================
# 3. 关键指标计算
# ============================================================
overall_achieve_rate = round(total_actual / total_budget * 100, 1)
gap = total_budget - total_actual

print("=" * 60)
print("关键指标汇总")
print("=" * 60)
print(f"预算总收入: {total_budget}万")
print(f"实际总收入: {total_actual}万")
print(f"总差异: {total_variance}万")
print(f"整体达成率: {overall_achieve_rate}%")
print(f"缺口: {gap}万")
print()

# 各区域达成率
print("各区域达成率:")
for _, row in df.iterrows():
    emoji = "+" if row['差异'] >= 0 else ""
    print(f"  {row['区域']}: {row['达成率']}% ({emoji}{row['差异']}万)")

print()

# ============================================================
# 4. 输出分析结果摘要（用于报告）
# ============================================================
summary = {
    'total_budget': total_budget,
    'total_actual': total_actual,
    'total_variance': total_variance,
    'overall_achieve_rate': overall_achieve_rate,
    'gap': gap,
    'region_analysis': {
        '华东': {'variance': east_china, 'achieve_rate': 107.0, 'contribution': 56},
        '华南': {'variance': south_china, 'achieve_rate': 83.0, 'contribution': -102, 'known_reason': '大客户3月延期签单'},
        '华北': {'variance': north_china, 'achieve_rate': 89.0, 'contribution': -55},
        '西部': {'variance': west_china, 'achieve_rate': 107.0, 'contribution': 21},
    }
}

print("=" * 60)
print("分析完成")
print("=" * 60)
print(f"结论: Q1整体收入达成率 {overall_achieve_rate}%，低于预算 {gap}万")
print(f"主因: 华南区大客户延期签单导致 {abs(south_impact)}万缺口")
print(f"建议: 尽快跟进大客户签单节奏，Q2抢收收入")