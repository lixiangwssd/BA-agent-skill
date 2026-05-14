#!/usr/bin/env python3
"""
注册转化率漏斗分析
分析转化率从 3.2% 下降到 2.1% 的原因
"""

import pandas as pd

# ========== 1. 原始数据 ==========
data = {
    'step': ['落地页访问', '点击注册按钮', '填写表单', '提交成功'],
    'last_month_uv': [500000, 125000, 62500, 16000],
    'this_month_uv': [520000, 109200, 49140, 10920],
    'last_month_rate': [None, 0.25, 0.50, 0.256],
    'this_month_rate': [None, 0.21, 0.45, 0.222]
}
df = pd.DataFrame(data)

# ========== 2. 计算各步骤转化率 ==========
df['last_month_conv'] = df['last_month_uv'] / df.loc[0, 'last_month_uv']
df['this_month_conv'] = df['this_month_uv'] / df.loc[0, 'this_month_uv']

print("=" * 60)
print("漏斗各步骤数据")
print("=" * 60)
for idx, row in df.iterrows():
    if idx == 0:
        print(f"{row['step']}: 上月UV={row['last_month_uv']:,}, 本月UV={row['this_month_uv']:,}")
    else:
        last_rate = row['last_month_conv'] * 100
        this_rate = row['this_month_conv'] * 100
        diff = this_rate - last_rate
        print(f"{row['step']}: 上月={last_rate:.1f}%, 本月={this_rate:.1f}%, 差异={diff:+.1f}个点")

# ========== 3. 计算各步骤对整体转化的贡献度 ==========
print("\n" + "=" * 60)
print("贡献度拆解（乘法模型）")
print("=" * 60)

# 整体转化率
last_overall = df.loc[3, 'last_month_conv']  # 16000/500000 = 3.2%
this_overall = df.loc[3, 'this_month_conv']   # 10920/520000 = 2.1%

print(f"上月整体转化率: {last_overall*100:.2f}%")
print(f"本月整体转化率: {this_overall*100:.2f}%")
print(f"整体变化: {(this_overall-last_overall)*100:+.2f}个点")
print(f"绝对损失: {df.loc[3, 'last_month_uv'] - df.loc[3, 'this_month_uv']:,} 注册用户")

# ========== 4. 各步骤贡献度计算 ==========
# 使用乘法模型的偏导数来分解各步骤贡献度
contributions = []
for idx in range(1, 4):
    step_name = df.loc[idx, 'step']
    step_last = df.loc[idx, 'last_month_conv']
    step_this = df.loc[idx, 'this_month_conv']

    # 固定其他步骤，计算该步骤变化对整体的贡献
    # 贡献 = 其他步骤不变 * 该步骤变化
    other_steps_product = 1.0
    for j in range(1, 4):
        if j != idx:
            other_steps_product *= df.loc[j, 'this_month_conv']

    contribution = (step_this - step_last) * other_steps_product

    # 也计算如果只有该步骤恶化，其他不变的模拟
    sim_last = 1.0
    sim_this = 1.0
    for j in range(1, 4):
        if j == idx:
            sim_last *= df.loc[j, 'last_month_conv']
            sim_this *= df.loc[j, 'this_month_conv']
        else:
            sim_last *= df.loc[j, 'last_month_conv']
            sim_this *= df.loc[j, 'this_month_conv']

    actual_contribution = this_overall - last_overall

    contributions.append({
        'step': step_name,
        'last_rate': step_last,
        'this_rate': step_this,
        'diff_pp': (step_this - step_last) * 100,
        'contribution': contribution,
        'contribution_pp': contribution * 100
    })

contrib_df = pd.DataFrame(contributions)

# 排序（按贡献度绝对值）
contrib_df['abs_contribution'] = contrib_df['contribution'].abs()
contrib_df = contrib_df.sort_values('abs_contribution', ascending=False)

print("\n各步骤贡献度（对整体转化率下降的贡献）:")
total_change = this_overall - last_overall
for _, row in contrib_df.iterrows():
    pct_of_total = (row['contribution'] / total_change) * 100 if total_change != 0 else 0
    print(f"  {row['step']}: {row['contribution_pp']:+.4f}个点 ({pct_of_total:+.1f}% of total)")

# ========== 5. 计算各步骤流失加剧程度 ==========
print("\n" + "=" * 60)
print("各步骤流失分析")
print("=" * 60)

for idx in range(1, 4):
    step = df.loc[idx, 'step']
    prev_last = df.loc[idx-1, 'last_month_uv']
    prev_this = df.loc[idx-1, 'this_month_uv']
    curr_last = df.loc[idx, 'last_month_uv']
    curr_this = df.loc[idx, 'this_month_uv']

    # 流失用户数
    lost_last = prev_last - curr_last
    lost_this = prev_this - curr_this

    # 流失率
    churn_last = lost_last / prev_last * 100
    churn_this = lost_this / prev_this * 100

    # 额外流失
    extra_churn = lost_this - lost_last

    print(f"\n{step}:")
    print(f"  上月流失: {lost_last:,} (流失率{churn_last:.1f}%)")
    print(f"  本月流失: {lost_this:,} (流失率{churn_this:.1f}%)")
    print(f"  额外流失: {extra_churn:+,}")

# ========== 6. 模拟：如果只修复某一个步骤 ==========
print("\n" + "=" * 60)
print("单步修复模拟（假设其他步骤不变）")
print("=" * 60)

baseline = this_overall
steps_impact = []

for idx in range(1, 4):
    step_name = df.loc[idx, 'step']
    step_rate = df.loc[idx, 'this_month_conv']

    # 模拟：如果该步骤恢复到上月水平，其他不变
    simulated = 1.0
    for j in range(1, 4):
        if j == idx:
            simulated *= df.loc[j, 'last_month_conv']  # 恢复该步骤
        else:
            simulated *= df.loc[j, 'this_month_conv']   # 保持本月

    improvement = (simulated - baseline) * 100
    steps_impact.append({
        'step': step_name,
        'improvement_pp': improvement,
        'recovered_loss_pct': (simulated - baseline) / (last_overall - this_overall) * 100 if last_overall != this_overall else 0
    })

impact_df = pd.DataFrame(steps_impact).sort_values('improvement_pp', ascending=False)
for _, row in impact_df.iterrows():
    print(f"  {row['step']}: 提升 {row['improvement_pp']:+.3f}个点 (恢复 {row['recovered_loss_pct']:.1f}% 损失)")

# ========== 7. 保存结果 ==========
# 保存详细数据到 CSV
result_df = pd.DataFrame({
    '漏斗步骤': contrib_df['step'].tolist(),
    '上月转化率': [f"{x*100:.1f}%" for x in contrib_df['last_rate'].tolist()],
    '本月转化率': [f"{x*100:.1f}%" for x in contrib_df['this_rate'].tolist()],
    '变化(个点)': [f"{x:+.1f}" for x in contrib_df['diff_pp'].tolist()],
    '贡献度(个点)': [f"{x*100:+.4f}" for x in contrib_df['contribution'].tolist()],
    '贡献占比': [f"{(x/contrib_df['contribution'].sum())*100:.1f}%" if contrib_df['contribution'].sum() != 0 else "N/A" for x in contrib_df['contribution'].tolist()]
})

result_df.to_csv('/Users/lixiang/Documents/异动分析Agent/.claude/skills/biz-metric-analysis-workspace/iteration-3/conversion-funnel-analysis/without_skill/outputs/funnel_analysis.csv', index=False, encoding='utf-8-sig')
print("\n详细数据已保存到 funnel_analysis.csv")