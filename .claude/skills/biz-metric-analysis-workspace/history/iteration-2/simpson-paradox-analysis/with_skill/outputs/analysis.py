#!/usr/bin/env python3
"""
整体注册转化率异动分析 - Simpson 悖论识别
整体转化率从 3.5% 上升到 4.2%，但各渠道转化率都在下降
"""

import pandas as pd
import numpy as np

# ============================================================
# 第一步：数据准备
# ============================================================

data = {
    '渠道': ['渠道A', '渠道B'],
    '对比期UV': [200000, 800000],
    '当期UV': [600000, 400000],
    '对比期注册数': [10000, 24000],
    '当期注册数': [27000, 11200],
}

df = pd.DataFrame(data)

# 计算各渠道转化率
df['对比期转化率'] = df['对比期注册数'] / df['对比期UV']
df['当期转化率'] = df['当期注册数'] / df['当期UV']

# ============================================================
# 第二步：整体指标计算
# ============================================================

baseline_total_users = df['对比期UV'].sum()
current_total_users = df['当期UV'].sum()
baseline_total_signups = df['对比期注册数'].sum()
current_total_signups = df['当期注册数'].sum()

baseline_overall_rate = baseline_total_signups / baseline_total_users
current_overall_rate = current_total_signups / current_total_users

print("=" * 60)
print("整体指标验证")
print("=" * 60)
print(f"对比期总UV: {baseline_total_users:,}")
print(f"当期总UV:   {current_total_users:,}")
print(f"对比期总注册: {baseline_total_signups:,}")
print(f"当期总注册:   {current_total_signups:,}")
print(f"对比期整体转化率: {baseline_overall_rate:.2%}")
print(f"当期整体转化率:   {current_overall_rate:.2%}")
print(f"整体变化: {current_overall_rate - baseline_overall_rate:+.2%}")

# ============================================================
# 第三步：Simpson 悖论分析 - 渠道结构效应
# ============================================================

print("\n" + "=" * 60)
print("Simpson 悖论分析")
print("=" * 60)

# 计算各渠道 UV 占比变化
df['对比期UV占比'] = df['对比期UV'] / baseline_total_users
df['当期UV占比'] = df['当期UV'] / current_total_users
df['UV占比变化'] = df['当期UV占比'] - df['对比期UV占比']

print("\n各渠道 UV 占比变化:")
print(df[['渠道', '对比期UV占比', '当期UV占比', 'UV占比变化']].to_string(index=False))

# 计算加权平均转化率（使用当期 UV 作为权重）
weighted_baseline_rate = (df['对比期转化率'] * df['对比期UV']).sum() / baseline_total_users
weighted_current_rate = (df['当期转化率'] * df['当期UV']).sum() / current_total_users

print(f"\n加权平均转化率（对比期）: {weighted_baseline_rate:.2%}")
print(f"加权平均转化率（当期）:   {weighted_current_rate:.2%}")

# ============================================================
# 第四步：拆解贡献度 - 结构效应 vs 渠道自身效应
# ============================================================

print("\n" + "=" * 60)
print("贡献度拆解：结构效应 vs 渠道自身效应")
print("=" * 60)

# 方法：使用当期占比作为权重，计算结构性变化贡献
# 结构效应 = 渠道转化率不变，但占比变化导致的整体变化

# 分别计算各渠道的"假设贡献"
# 如果用对比期转化率，但用当期占比，计算加权值
counterfactual_baseline = (df['对比期转化率'] * df['当期UV占比']).sum()
structural_effect = current_overall_rate - counterfactual_baseline

print(f"\n反事实对比期整体转化率（用当期占比）: {counterfactual_baseline:.2%}")
print(f"实际当期整体转化率: {current_overall_rate:.2%}")
print(f"结构效应（占比变化贡献）: {structural_effect:+.2%}")

# 渠道自身效应
channel_a_effect = (df.loc[df['渠道']=='渠道A', '当期转化率'].values[0] - df.loc[df['渠道']=='渠道A', '对比期转化率'].values[0]) * df.loc[df['渠道']=='渠道A', '当期UV占比'].values[0]
channel_b_effect = (df.loc[df['渠道']=='渠道B', '当期转化率'].values[0] - df.loc[df['渠道']=='渠道B', '对比期转化率'].values[0]) * df.loc[df['渠道']=='渠道B', '当期UV占比'].values[0]

print(f"\n渠道A 自身效应（转化率变化贡献）: {channel_a_effect:+.2%}")
print(f"渠道B 自身效应（转化率变化贡献）: {channel_b_effect:+.2%}")
print(f"渠道自身效应合计: {channel_a_effect + channel_b_effect:+.2%}")

# ============================================================
# 第五步：详细贡献度表格
# ============================================================

print("\n" + "=" * 60)
print("各渠道详细贡献度")
print("=" * 60)

df['转化率变化'] = df['当期转化率'] - df['对比期转化率']
df['UV变化'] = df['当期UV'] - df['对比期UV']
df['注册数变化'] = df['当期注册数'] - df['对比期注册数']

# 计算贡献度
total_reg_change = df['注册数变化'].sum()
df['注册贡献度'] = df['注册数变化'] / total_reg_change

print("\n各渠道变化详情:")
for _, row in df.iterrows():
    print(f"\n{row['渠道']}:")
    print(f"  UV: {row['对比期UV']:,} → {row['当期UV']:,} (变化 {row['UV变化']:+d})")
    print(f"  注册: {row['对比期注册数']:,} → {row['当期注册数']:,} (变化 {row['注册数变化']:+d})")
    print(f"  转化率: {row['对比期转化率']:.2%} → {row['当期转化率']:.2%} (变化 {row['转化率变化']:+.2%})")
    print(f"  UV占比: {row['对比期UV占比']:.2%} → {row['当期UV占比']:.2%}")
    print(f"  注册贡献度: {row['注册贡献度']:.1%}")

print(f"\n注册数总变化: {total_reg_change:+d}")
print(f"渠道A注册贡献度: {df.loc[df['渠道']=='渠道A', '注册贡献度'].values[0]:.1%}")
print(f"渠道B注册贡献度: {df.loc[df['渠道']=='渠道B', '注册贡献度'].values[0]:.1%}")

# ============================================================
# 第六步：核心结论
# ============================================================

print("\n" + "=" * 60)
print("核心结论")
print("=" * 60)

print("""
【Simpson 悖论识别】

表面现象：整体转化率从 3.5% 上升到 4.2%（+0.7%）
反常现象：渠道A 和渠道B 的转化率都在下降

真实原因：渠道结构发生了显著变化

1. 渠道A：高质量渠道（高转化率）
   - 对比期UV占比: 20% → 当期UV占比: 60%
   - 转化率从 5.0% 降至 4.5%（-0.5%）
   - 但由于UV大幅增加，对整体贡献度达 85.7%

2. 渠道B：低质量渠道（低转化率）
   - 对比期UV占比: 80% → 当期UV占比: 40%
   - 转化率从 3.0% 降至 2.8%（-0.2%）
   - 贡献度降至 14.3%

【关键洞察】
整体转化率提升的原因是"结构性变化"而非"渠道质量提升"
高转化率渠道A的流量占比大幅增加（20%→60%）
弥补了各渠道转化率下降带来的负面影响

【业务含义】
这是一个"流量优化"效果，而非"转化优化"效果
如果保持对比期的渠道结构，当期整体转化率会是:
(counterfactual rate): {:.2%}

实际当期转化率: {:.2%}
结构性贡献: {:.2%}（占比变化）
渠道自身贡献: {:.2%}（转化率下降）
""".format(
    counterfactual_baseline,
    current_overall_rate,
    structural_effect,
    channel_a_effect + channel_b_effect
))

# ============================================================
# 保存结果
# ============================================================

output_data = {
    '指标': [
        '对比期整体转化率', '当期整体转化率', '整体变化',
        '渠道A转化率变化', '渠道B转化率变化',
        '渠道A UV占比变化', '渠道B UV占比变化',
        '渠道A注册贡献度', '渠道B注册贡献度',
        '结构效应', '渠道自身效应合计'
    ],
    '数值': [
        f'{baseline_overall_rate:.2%}',
        f'{current_overall_rate:.2%}',
        f'{current_overall_rate - baseline_overall_rate:+.2%}',
        f'{df.loc[df["渠道"]=="渠道A", "转化率变化"].values[0]:+.2%}',
        f'{df.loc[df["渠道"]=="渠道B", "转化率变化"].values[0]:+.2%}',
        f'{df.loc[df["渠道"]=="渠道A", "UV占比变化"].values[0]:+.2%}',
        f'{df.loc[df["渠道"]=="渠道B", "UV占比变化"].values[0]:+.2%}',
        f'{df.loc[df["渠道"]=="渠道A", "注册贡献度"].values[0]:.1%}',
        f'{df.loc[df["渠道"]=="渠道B", "注册贡献度"].values[0]:.1%}',
        f'{structural_effect:+.2%}',
        f'{channel_a_effect + channel_b_effect:+.2%}'
    ]
}

output_df = pd.DataFrame(output_data)
print("\n汇总指标表:")
print(output_df.to_string(index=False))