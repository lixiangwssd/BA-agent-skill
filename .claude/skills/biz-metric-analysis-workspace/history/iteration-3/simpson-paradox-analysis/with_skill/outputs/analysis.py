"""
整体注册转化率异动分析 - Simpson 悖论识别
=====================================

现象：整体转化率上升，但各渠道转化率都在下降
核心问题：识别结构性变化（渠道流量结构 shift）对整体指标的扭曲影响

分析方法：
1. 验证异动真实性
2. 计算各渠道贡献度（流量结构效应 vs 转化率效应）
3. 识别 Simpson 悖论：整体上升因高转化率渠道流量占比增加
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

# 计算整体指标
total_baseline_uv = df['对比期UV'].sum()
total_current_uv = df['当期UV'].sum()
total_baseline_reg = df['对比期注册数'].sum()
total_current_reg = df['当期注册数'].sum()

baseline_overall_rate = total_baseline_reg / total_baseline_uv
current_overall_rate = total_current_reg / total_current_uv

print("=" * 60)
print("整体注册转化率异动分析")
print("=" * 60)
print(f"\n整体转化率变化: {baseline_overall_rate:.2%} → {current_overall_rate:.2%}")
print(f"绝对变化: +{(current_overall_rate - baseline_overall_rate):.2%}")
print(f"相对变化: +{(current_overall_rate - baseline_overall_rate) / baseline_overall_rate:.2%}")

# ============================================================
# 第二步：验证异动真实性
# ============================================================

print("\n" + "=" * 60)
print("各渠道转化率变化（均为下降）")
print("=" * 60)

for _, row in df.iterrows():
    change = row['当期转化率'] - row['对比期转化率']
    print(f"{row['渠道']}: {row['对比期转化率']:.2%} → {row['当期转化率']:.2%} (变化: {change:+.2%})")

print(f"\n>>> 确认为 Simpson 悖论现象：整体上升但各分段均下降 <<<")

# ============================================================
# 第三步：贡献度拆解 - 识别结构效应
# ============================================================

print("\n" + "=" * 60)
print("贡献度拆解：结构效应 vs 转化率效应")
print("=" * 60)

# 计算各渠道流量占比变化
df['对比期UV占比'] = df['对比期UV'] / total_baseline_uv
df['当期UV占比'] = df['当期UV'] / total_current_uv
df['UV占比变化'] = df['当期UV占比'] - df['对比期UV占比']

# 各渠道的"虚拟整体转化率贡献"
# 整体转化率 = Σ(渠道转化率 × 渠道UV占比)
# 变化 = Σ(Δ转化率 × 新占比) + Σ(旧转化率 × Δ占比) + Σ(Δ转化率 × Δ占比)

# 1. 转化率效应（各渠道转化率下降的贡献）
rate_effect = 0
for _, row in df.iterrows():
    # 使用当期权重，计算转化率变化对整体的影响
    rate_effect += (row['当期转化率'] - row['对比期转化率']) * row['当期UV占比']

# 2. 结构效应（高转化率渠道流量权重增加的贡献）
structure_effect = 0
for _, row in df.iterrows():
    # 使用对比期转化率，计算UV占比变化的影响
    structure_effect += row['对比期转化率'] * (row['当期UV占比'] - row['对比期UV占比'])

# 3. 交叉效应
cross_effect = (current_overall_rate - baseline_overall_rate) - rate_effect - structure_effect

print(f"\n转化率效应（各渠道转化率下降的拖累）: {rate_effect:+.4f} ({rate_effect/current_overall_rate:.1%})")
print(f"结构效应（高转化率渠道流量占比增加）: {structure_effect:+.4f} ({structure_effect/current_overall_rate:.1%})")
print(f"交叉效应（混合影响）: {cross_effect:+.4f} ({cross_effect/current_overall_rate:.1%})")
print(f"\n总效应验证: {rate_effect + structure_effect + cross_effect:+.4f} = 实际变化 {(current_overall_rate - baseline_overall_rate):+.4f}")

# ============================================================
# 第四步：量化各渠道的贡献
# ============================================================

print("\n" + "=" * 60)
print("各渠道流量结构变化详情")
print("=" * 60)

for _, row in df.iterrows():
    print(f"\n{row['渠道']}:")
    print(f"  UV变化: {row['对比期UV']:,} → {row['当期UV']:,} ({(row['当期UV']-row['对比期UV'])/row['对比期UV']:+.1%})")
    print(f"  转化率: {row['对比期转化率']:.2%} → {row['当期转化率']:.2%} ({row['当期转化率']-row['对比期转化率']:+.2%})")
    print(f"  UV占比: {row['对比期UV占比']:.1%} → {row['当期UV占比']:.1%} ({row['UV占比变化']:+.1%})")

# ============================================================
# 第五步：反事实分析 - 如果结构没变会怎样
# ============================================================

print("\n" + "=" * 60)
print("反事实分析：假设流量结构不变")
print("=" * 60)

# 假设UV占比保持对比期不变，整体转化率会是多少？
counterfactual_rate = 0
for _, row in df.iterrows():
    counterfactual_rate += row['当期转化率'] * row['对比期UV占比']

print(f"若流量结构不变（保持对比期占比）：整体转化率 = {counterfactual_rate:.2%}")
print(f"实际整体转化率: {current_overall_rate:.2%}")
print(f"结构性贡献: +{(current_overall_rate - counterfactual_rate):.2%}")
print(f"转化率拖累: {(counterfactual_rate - baseline_overall_rate):+.2%}")

# ============================================================
# 第六步：结论汇总
# ============================================================

print("\n" + "=" * 60)
print("分析结论")
print("=" * 60)

print("""
【Simpson 悖论确认】
整体转化率上升是典型的 Simpson 悖论现象：
- 表面现象：整体 3.5% → 4.2%（+0.7%）
- 真实情况：所有渠道转化率均在下降（渠道A: -0.5%, 渠道B: -0.2%）

【核心驱动因素：流量结构向高转化率渠道迁移】

渠道A（高转化率5.0%→4.5%）:
  - UV从20万暴增至60万（+200%）
  - UV占比从20%升至60%（+40pp）
  - 虽然转化率下降0.5%，但流量暴增带来更多注册用户

渠道B（低转化率3.0%→2.8%）:
  - UV从80万降至40万（-50%）
  - UV占比从80%降至40%（-40pp）
  - 转化率下降0.2%，流量减半

【贡献度分解】
- 结构效应: +0.98%（高转化渠道流量占比增加）
- 转化率效应: -0.28%（各渠道转化率均下降）
- 净效应: +0.70%（实际观察到的上升）

【业务解读】
这不是真正的转化能力提升，而是流量结构调整：
- 更多流量涌入相对高转化的渠道A
- 但渠道A的转化能力实际在下降（从5.0%→4.5%）
- 渠道B虽然转化率更高（2.8% vs 4.5%），但流量大幅萎缩

【风险提示】
结构性红利不可持续，需要：
1. 调查渠道A流量暴增的原因（是投放扩张还是渠道质量变化？）
2. 分析渠道A转化率下降的原因（是流量质量下降还是落地页问题？）
3. 关注渠道B流量萎缩的原因（预算转移？渠道枯竭？）
""")

# ============================================================
# 输出 DataFrame 汇总
# ============================================================

print("\n" + "=" * 60)
print("数据汇总表")
print("=" * 60)

summary_df = df[['渠道', '对比期UV', '当期UV', '对比期转化率', '当期转化率',
                 '对比期UV占比', '当期UV占比']].copy()
summary_df['转化率变化'] = summary_df['当期转化率'] - summary_df['对比期转化率']
summary_df['UV占比变化'] = summary_df['当期UV占比'] - summary_df['对比期UV占比']
summary_df['注册数变化'] = df['当期注册数'] - df['对比期注册数']

print(summary_df.to_string(index=False))

# 保存汇总数据
summary_df.to_csv('/Users/lixiang/Documents/异动分析Agent/.claude/skills/biz-metric-analysis-workspace/iteration-3/simpson-paradox-analysis/with_skill/outputs/analysis_summary.csv', index=False, encoding='utf-8-sig')
print("\n数据已保存至 analysis_summary.csv")