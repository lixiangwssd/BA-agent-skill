"""
注册转化率漏斗异动分析
分析时间：本月 vs 上月
核心指标：注册转化率（落地页访问 -> 提交成功）
"""

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# 中文字体配置
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# ============================================================
# 第一步：数据录入
# ============================================================

# 漏斗各步骤数据
funnel_data = {
    '步骤': ['落地页访问', '点击注册按钮', '填写表单', '提交成功'],
    '上月UV': [500000, 125000, 62500, 16000],
    '本月UV': [520000, 109200, 49140, 10920],
}

df = pd.DataFrame(funnel_data)

# 步骤间转化率（本步骤UV / 上一步骤UV）
# 上月各步骤对上一步骤的转化率
df['上月步骤转化率'] = [None, 125000/500000, 62500/125000, 16000/62500]
# 本月各步骤对上一步骤的转化率
df['本月步骤转化率'] = [None, 109200/520000, 49140/109200, 10920/49140]

# 整体注册转化率 = 提交成功UV / 落地页访问UV
overall_last_month = 16000 / 500000  # 3.2%
overall_this_month = 10920 / 520000  # 2.1%
overall_delta_abs = overall_this_month - overall_last_month
overall_delta_pct = overall_delta_abs / overall_last_month

print("=" * 60)
print("整体注册转化率对比")
print("=" * 60)
print(f"上月整体转化率: {overall_last_month:.2%}")
print(f"本月整体转化率: {overall_this_month:.2%}")
print(f"变化量 (pp):    {overall_delta_abs*100:.2f} pp")
print(f"变化率:         {overall_delta_pct:.2%}")
print(f"损失注册用户（基于本月流量）: {int(520000 * abs(overall_delta_abs)):,} 人")

# ============================================================
# 第二步：各步骤 UV 变化分析
# ============================================================

print("\n" + "=" * 60)
print("各步骤 UV 变化")
print("=" * 60)

df['UV变化量'] = df['本月UV'] - df['上月UV']
df['UV变化率'] = df['UV变化量'] / df['上月UV']

print(df[['步骤', '上月UV', '本月UV', 'UV变化量', 'UV变化率']].to_string(index=False))

# ============================================================
# 第三步：各步骤转化率变化分析（核心）
# ============================================================

print("\n" + "=" * 60)
print("各步骤转化率变化（步骤间转化率）")
print("=" * 60)

step_names = ['点击注册按钮', '填写表单', '提交成功']
last_cr = [125000/500000, 62500/125000, 16000/62500]
this_cr = [109200/520000, 49140/109200, 10920/49140]
cr_delta = [t - l for t, l in zip(this_cr, last_cr)]
cr_delta_pct = [(t - l) / l for t, l in zip(this_cr, last_cr)]

cr_df = pd.DataFrame({
    '步骤': step_names,
    '上月步骤转化率': last_cr,
    '本月步骤转化率': this_cr,
    '变化量(pp)': [d * 100 for d in cr_delta],
    '变化率': cr_delta_pct,
})

print(cr_df.to_string(index=False))

# ============================================================
# 第四步：损失用户归因拆解（乘法模型拆解）
# ============================================================
# 整体转化率 = CR1 × CR2 × CR3
# 本月 = 21.0% × 45.0% × 22.2% = 2.10%
# 上月 = 25.0% × 50.0% × 25.6% = 3.20%
#
# 采用逐步替换法（Shapley近似），依次固定其他步骤转化率，单独计算每步变化的贡献

cr1_last, cr2_last, cr3_last = 125000/500000, 62500/125000, 16000/62500
cr1_this, cr2_this, cr3_this = 109200/520000, 49140/109200, 10920/49140

base_rate = cr1_last * cr2_last * cr3_last  # 上月整体转化率

# 各步骤单独变化时整体转化率
rate_only_cr1_changed = cr1_this * cr2_last * cr3_last
rate_only_cr2_changed = cr1_last * cr2_this * cr3_last
rate_only_cr3_changed = cr1_last * cr2_last * cr3_this

effect_cr1 = rate_only_cr1_changed - base_rate
effect_cr2 = rate_only_cr2_changed - base_rate
effect_cr3 = rate_only_cr3_changed - base_rate

# 交叉效应（残差）
total_delta = overall_this_month - overall_last_month
cross_effect = total_delta - effect_cr1 - effect_cr2 - effect_cr3

# 基于上月流量折算为损失用户数（用本月流量 520000 作为基准）
base_uv = 520000

print("\n" + "=" * 60)
print("各步骤转化率下降对整体转化率的独立贡献（逐步替换法）")
print("=" * 60)

attribution = pd.DataFrame({
    '步骤': ['落地页->点击注册（CR1）', '点击->填写表单（CR2）', '填写->提交成功（CR3）', '交叉项'],
    '整体转化率贡献(pp)': [effect_cr1*100, effect_cr2*100, effect_cr3*100, cross_effect*100],
    '损失注册用户数': [
        int(effect_cr1 * base_uv),
        int(effect_cr2 * base_uv),
        int(effect_cr3 * base_uv),
        int(cross_effect * base_uv),
    ],
    '贡献率': [
        effect_cr1 / total_delta,
        effect_cr2 / total_delta,
        effect_cr3 / total_delta,
        cross_effect / total_delta,
    ]
})

print(attribution.to_string(index=False))

print(f"\n合计损失整体转化率: {total_delta*100:.2f} pp")
print(f"合计损失注册用户（本月流量基准）: {int(total_delta * base_uv):,} 人")

# ============================================================
# 第五步：优先级排序
# ============================================================

print("\n" + "=" * 60)
print("问题步骤优先级排序（按损失用户绝对值）")
print("=" * 60)

priority = attribution[attribution['步骤'] != '交叉项'].copy()
priority['损失用户绝对值'] = priority['损失注册用户数'].abs()
priority = priority.sort_values('损失用户绝对值', ascending=False)
priority['优先级'] = range(1, len(priority) + 1)

print(priority[['优先级', '步骤', '整体转化率贡献(pp)', '损失注册用户数', '贡献率']].to_string(index=False))

# ============================================================
# 第六步：可视化
# ============================================================

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('注册转化率漏斗异动分析', fontsize=16, fontweight='bold')

# 图1：漏斗UV对比
steps = df['步骤'].tolist()
x = np.arange(len(steps))
width = 0.35

bars1 = axes[0].bar(x - width/2, df['上月UV'], width, label='上月', color='#4472C4', alpha=0.85)
bars2 = axes[0].bar(x + width/2, df['本月UV'], width, label='本月', color='#ED7D31', alpha=0.85)
axes[0].set_title('各步骤UV对比', fontsize=13)
axes[0].set_xticks(x)
axes[0].set_xticklabels(steps, rotation=15, ha='right', fontsize=9)
axes[0].set_ylabel('UV')
axes[0].legend()
axes[0].yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f'{int(v):,}'))

# 图2：步骤间转化率对比
step_labels = ['CR1\n落地页->点击', 'CR2\n点击->填写', 'CR3\n填写->提交']
x2 = np.arange(len(step_labels))
axes[1].bar(x2 - width/2, [r * 100 for r in last_cr], width, label='上月', color='#4472C4', alpha=0.85)
axes[1].bar(x2 + width/2, [r * 100 for r in this_cr], width, label='本月', color='#ED7D31', alpha=0.85)
axes[1].set_title('各步骤间转化率对比 (%)', fontsize=13)
axes[1].set_xticks(x2)
axes[1].set_xticklabels(step_labels, fontsize=9)
axes[1].set_ylabel('转化率 (%)')
axes[1].legend()
for i, (l, t) in enumerate(zip(last_cr, this_cr)):
    axes[1].text(i - width/2, l * 100 + 0.3, f'{l:.1%}', ha='center', va='bottom', fontsize=8)
    axes[1].text(i + width/2, t * 100 + 0.3, f'{t:.1%}', ha='center', va='bottom', fontsize=8)

# 图3：各步骤贡献的损失用户数
contrib_steps = ['CR1\n落地页->点击', 'CR2\n点击->填写', 'CR3\n填写->提交']
contrib_values = [int(effect_cr1 * base_uv), int(effect_cr2 * base_uv), int(effect_cr3 * base_uv)]
colors_bar = ['#d73027' if v < 0 else '#1a9641' for v in contrib_values]
bars3 = axes[2].bar(contrib_steps, contrib_values, color=colors_bar, alpha=0.85)
axes[2].set_title('各步骤贡献的注册用户损失数', fontsize=13)
axes[2].set_ylabel('损失用户数')
axes[2].axhline(0, color='black', linewidth=0.8)
for bar, val in zip(bars3, contrib_values):
    axes[2].text(bar.get_x() + bar.get_width()/2, val - 80, f'{val:,}', ha='center', va='top', fontsize=9, color='white', fontweight='bold')

plt.tight_layout()
output_dir = "/Users/lixiang/Documents/异动分析Agent/.claude/skills/metric-anomaly-analysis-workspace/iteration-1/conversion-funnel-analysis/with_skill/outputs"
plt.savefig(f'{output_dir}/funnel_analysis.png', dpi=150, bbox_inches='tight')
print(f"\n可视化图表已保存至: {output_dir}/funnel_analysis.png")
plt.show()

print("\n分析完成。")
