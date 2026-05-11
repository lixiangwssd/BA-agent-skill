import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# === 第一步：数据构建 ===
data = {
    '漏斗步骤': ['落地页访问', '点击注册按钮', '填写表单', '提交成功'],
    '上月UV': [500000, 125000, 62500, 16000],
    '本月UV': [520000, 109200, 49140, 10920],
    '上月转化率': [None, 0.250, 0.500, 0.256],
    '本月转化率': [None, 0.210, 0.450, 0.222]
}
df = pd.DataFrame(data)

# === 第二步：异动验证 ===
overall_prev = 16000 / 500000  # 3.2%
overall_curr = 10920 / 520000  # 2.1%
overall_change = overall_curr - overall_prev
lost_users = 16000 - 10920  # 实际损失注册用户

print("=" * 60)
print("异动验证")
print("=" * 60)
print(f"上月整体注册转化率：{overall_prev:.1%}")
print(f"本月整体注册转化率：{overall_curr:.1%}")
print(f"变化：{overall_change:.1%}（下降 {abs(overall_change)*100:.1f} 个百分点）")
print(f"损失注册用户：约 {lost_users} 人")
print(f"判断：下降超过 1 个百分点，且绝对损失 > 5000 人，属于显著异动")

# === 第三步：各步骤流失分析 ===
print("\n" + "=" * 60)
print("各步骤转化率变化与流失分析")
print("=" * 60)

# 计算各步骤的新增流失
df['上月流失量'] = df['上月UV'] - df['上月UV'].shift(-1)
df['本月流失量'] = df['本月UV'] - df['本月UV'].shift(-1)
df['新增流失'] = df['本月流失量'] - df['上月流失量']
df['转化率变化'] = df['本月转化率'] - df['上月转化率']

# 各步骤贡献度分析
steps = ['点击注册按钮', '填写表单', '提交成功']
contributions = []

for step in steps:
    row = df[df['漏斗步骤'] == step].iloc[0]
    rate_change = row['转化率变化']
    # 用上一步的本月UV作为基数，计算该步骤转化率下降带来的绝对损失
    step_idx = df[df['漏斗步骤'] == step].index[0]
    prev_step_uv = df.loc[step_idx - 1, '本月UV']
    absolute_loss = rate_change * prev_step_uv
    contributions.append({
        '步骤': step,
        '转化率变化': rate_change,
        '上游UV': prev_step_uv,
        '该步骤绝对损失': absolute_loss
    })

contrib_df = pd.DataFrame(contributions)
contrib_df['贡献权重'] = contrib_df['该步骤绝对损失'].abs() / contrib_df['该步骤绝对损失'].abs().sum()

print(contrib_df.to_string(index=False))

# === 第四步：优先级排序 ===
print("\n" + "=" * 60)
print("优先级排序（按绝对损失）")
print("=" * 60)
contrib_sorted = contrib_df.sort_values('该步骤绝对损失')
for i, row in enumerate(contrib_sorted.itertuples(), 1):
    print(f"  P{i}: {row.步骤}")
    print(f"      转化率变化：{row.转化率变化:.1%}")
    print(f"      绝对损失：{row.该步骤绝对损失:,.0f} UV")
    print(f"      贡献权重：{row.贡献权重:.1%}")
    print()

# === 第五步：可视化 ===
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 漏斗对比图
steps_all = df['漏斗步骤'].tolist()
axes[0].plot(steps_all, df['上月UV'], 'o-', label='上月', linewidth=2, markersize=8)
axes[0].plot(steps_all, df['本月UV'], 's--', label='本月', linewidth=2, markersize=8)
axes[0].set_title('注册漏斗各步骤 UV 对比')
axes[0].set_ylabel('UV')
axes[0].legend()
axes[0].tick_params(axis='x', rotation=15)

# 转化率变化柱状图
step_names = contrib_df['步骤'].tolist()
rate_changes = [x * 100 for x in contrib_df['转化率变化'].tolist()]
colors = ['#d73027' if v < 0 else '#1a9641' for v in rate_changes]
axes[1].bar(step_names, rate_changes, color=colors)
axes[1].set_title('各步骤转化率变化（百分点）')
axes[1].set_ylabel('变化（百分点）')
axes[1].axhline(0, color='black', linewidth=0.8)

plt.tight_layout()
plt.savefig('funnel_analysis.png', dpi=150, bbox_inches='tight')
print("\n图表已保存为 funnel_analysis.png")
