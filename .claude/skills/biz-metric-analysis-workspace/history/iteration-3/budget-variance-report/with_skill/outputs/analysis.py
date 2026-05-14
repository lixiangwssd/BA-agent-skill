#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q1 收入 vs 预算差异分析
财务分析师给 CFO 汇报用
"""

import pandas as pd
import numpy as np

# ============================================
# 第一步：数据准备
# ============================================
data = {
    '区域': ['华东', '华南', '华北', '西部'],
    '预算收入': [800, 600, 500, 300],
    '实际收入': [856, 498, 445, 321]
}
df = pd.DataFrame(data)

# 计算差异
df['差异'] = df['实际收入'] - df['预算收入']
df['达成率'] = df['实际收入'] / df['预算收入']
df['差异率'] = df['差异'] / df['预算收入']

# 汇总行
total_budget = df['预算收入'].sum()
total_actual = df['实际收入'].sum()
total_diff = total_actual - total_budget
total_achieve = total_actual / total_budget

print("=" * 60)
print("Q1 收入 vs 预算差异分析")
print("=" * 60)

# ============================================
# 第二步：差异验证
# ============================================
print("\n【一、概况】")
print(f"预算收入合计：{total_budget:,} 万元")
print(f"实际收入合计：{total_actual:,} 万元")
print(f"差异：{total_diff:,} 万元（{total_diff/total_budget:.2%}）")

# ============================================
# 第三步：贡献度拆解
# ============================================
print("\n【二、各区域贡献度拆解】")

# 计算各区域贡献度（差异贡献）
total_change = total_diff
df['贡献度'] = df['差异'] / total_change
df['贡献度_pct'] = df['贡献度'].apply(lambda x: f"{x:.1%}")

# 按贡献度排序
df_sorted = df.sort_values('差异', ascending=True)

print("\n各区域表现明细：")
print("-" * 70)
print(f"{'区域':<6} {'预算':>10} {'实际':>10} {'差异':>10} {'达成率':>10} {'贡献度':>10}")
print("-" * 70)
for _, row in df.iterrows():
    print(f"{row['区域']:<6} {row['预算收入']:>10,} {row['实际收入']:>10,} {row['差异']:>+10,} {row['达成率']:>9.1%} {row['贡献度']:>+10.1%}")
print("-" * 70)
print(f"{'合计':<6} {total_budget:>10,} {total_actual:>10,} {total_diff:>+10,} {total_achieve:>9.1%} {'100.0%':>10}")
print("-" * 70)

# ============================================
# 第四步：归因分析
# ============================================
print("\n【三、根因分析】")

# 已知背景：华南区大客户3月延期签单
huanan_impact = -102  # 华南贡献的负差异
huanan_total_budget = 600
huanan_impact_pct = abs(huanan_impact) / abs(total_diff) if total_diff != 0 else 0

print(f"\n1. 华南区差异：{huanan_impact:,} 万元（达成率 83.0%）")
print(f"   已确认原因：大客户 3 月延期签单")
print(f"   对总差异的贡献：{huanan_impact_pct:.1%}")

# 计算剔除华南后的表现
other_total = total_actual - 498
other_budget = total_budget - 600
other_diff = other_total - other_budget
other_achieve = other_total / other_budget

print(f"\n2. 剔除华南后的整体表现：")
print(f"   预算：{other_budget:,} 万元，实际：{other_total:,} 万元")
print(f"   差异：{other_diff:+,} 万元，达成率：{other_achieve:.1%}")

# 华北区域分析
huabei_impact = -55
huabei_impact_pct = abs(huabei_impact) / abs(total_diff) if total_diff != 0 else 0
print(f"\n3. 华北区差异：{huabei_impact:,} 万元（达成率 89.0%）")

# 正向贡献区域
huadong_impact = 56
huadong_impact_pct = huadong_impact / total_diff if total_diff != 0 else 0
xibu_impact = 21
xibu_impact_pct = xibu_impact / total_diff if total_diff != 0 else 0

print(f"\n4. 华东区差异：+{huadong_impact} 万元（达成率 107.0%）")
print(f"   贡献度：{huadong_impact_pct:.1%}")
print(f"\n5. 西部区差异：+{xibu_impact} 万元（达成率 107.0%）")
print(f"   贡献度：{xibu_impact_pct:.1%}")

# ============================================
# 第五步：结论与建议
# ============================================
print("\n【四、结论】")
print(f"1. Q1 实际收入 {total_actual:,} 万元 vs 预算 {total_budget:,} 万元，差距 {abs(total_diff):,} 万元")
print(f"2. 华南区是最大拖累项，贡献了 {huanan_impact_pct:.1%} 的负差异，主因是大客户 3 月延期签单")
print(f"3. 剔除华南后，实际收入达成预算的 {other_achieve:.1%}，整体表现尚可")
print(f"4. 华东、西部超预期完成，合计贡献 +{huadong_impact + xibu_impact} 万元正向差异")

print("\n【五、建议】")
print("1. 【高优先级】华南区：紧密跟进大客户签约进度，确认合同金额及入账时间")
print("2. 【高优先级】华南区：评估是否能在 Q2 把延误的订单补回来")
print("3. 【中优先级】华北区域：分析华北 {abs(huabei_impact):,} 万缺口原因（需进一步下钻）")
print("4. 【中优先级】华东、西部：总结超预期完成的经验，看是否可以复制")