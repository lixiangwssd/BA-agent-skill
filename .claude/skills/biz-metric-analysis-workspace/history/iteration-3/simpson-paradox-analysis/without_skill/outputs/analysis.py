"""
整体注册转化率上升但各渠道转化率下降的辛普森悖论分析
"""

import pandas as pd

# ========== 1. 构建数据 ==========
data = {
    '渠道': ['渠道A', '渠道B', '汇总'],
    '对比期UV': [200000, 800000, 1000000],
    '当期UV': [600000, 400000, 1000000],
    '对比期注册数': [10000, 24000, 34000],
    '当期注册数': [27000, 11200, 38200],
}
df = pd.DataFrame(data)

# 计算转化率
df['对比期转化率'] = df['对比期注册数'] / df['对比期UV'] * 100
df['当期转化率'] = df['当期注册数'] / df['当期UV'] * 100

# 计算转化率变化
df['转化率变化'] = df['当期转化率'] - df['对比期转化率']

# ========== 2. 辛普森悖论分析 ==========
print("=" * 60)
print("辛普森悖论诊断")
print("=" * 60)
print(df.to_string(index=False))
print()

# 整体转化率变化
overall_old = 34000 / 1000000 * 100
overall_new = 38200 / 1000000 * 100
overall_change = overall_new - overall_old
print(f"整体转化率变化: {overall_old:.2f}% → {overall_new:.2f}% ({(overall_change):+.2f}%)")
print()

# 各渠道加权贡献度拆解
print("=" * 60)
print("各渠道UV权重与转化率贡献拆解")
print("=" * 60)

channels = df[df['渠道'] != '汇总'].copy()

# 对比期加权
channels['对比期UV权重'] = channels['对比期UV'] / channels['对比期UV'].sum()
channels['当期UV权重'] = channels['当期UV'] / channels['当期UV'].sum()

print(f"\n【对比期】")
for _, row in channels.iterrows():
    print(f"  {row['渠道']}: UV={row['对比期UV']:,}, 权重={row['对比期UV权重']:.1%}, 转化率={row['对比期转化率']:.2f}%")

print(f"\n【当期】")
for _, row in channels.iterrows():
    print(f"  {row['渠道']}: UV={row['当期UV']:,}, 权重={row['当期UV权重']:.1%}, 转化率={row['当期转化率']:.2f}%")

# 加权转化率验证
weighted_old = (channels['对比期UV权重'] * channels['对比期转化率']).sum()
weighted_new = (channels['当期UV权重'] * channels['当期转化率']).sum()
print(f"\n加权验证: 对比期={weighted_old:.2f}%, 当期={weighted_new:.2f}%")

# ========== 3. 贡献度拆解 ==========
print()
print("=" * 60)
print("贡献度拆解: 为什么整体转化率上升?")
print("=" * 60)

total_old = 34000 / 1000000 * 100
total_new = 38200 / 1000000 * 100

# 各渠道对整体变化的贡献
for _, row in channels.iterrows():
    old_weight = row['对比期UV'] / 1000000
    new_weight = row['当期UV'] / 1000000
    old_rate = row['对比期转化率']
    new_rate = row['当期转化率']

    # 固定权重法: 假设对比期和当期的权重差由渠道结构变化贡献
    structure_effect = (new_weight - old_weight) * old_rate  # 渠道结构变化的贡献
    rate_effect = new_weight * (new_rate - old_rate)          # 转化率变化的贡献

    print(f"\n{row['渠道']}:")
    print(f"  对比期: 权重={old_weight:.2%}, 转化率={old_rate:.2f}%")
    print(f"  当期:   权重={new_weight:.2%}, 转化率={new_rate:.2f}%")
    print(f"  渠道结构变化贡献: {structure_effect:+.4f}% (权重从{old_weight:.2%}变为{new_weight:.2%})")
    print(f"  转化率变化贡献:   {rate_effect:+.4f}% (转化率从{old_rate:.2f}%变为{new_rate:.2f}%)")

# 汇总验证
structure_total = 0
rate_total = 0
for _, row in channels.iterrows():
    old_weight = row['对比期UV'] / 1000000
    new_weight = row['当期UV'] / 1000000
    old_rate = row['对比期转化率']
    new_rate = row['当期转化率']
    structure_total += (new_weight - old_weight) * old_rate
    rate_total += new_weight * (new_rate - old_rate)

print(f"\n汇总验证:")
print(f"  渠道结构变化贡献: {structure_total:+.4f}%")
print(f"  转化率下降贡献:   {rate_total:+.4f}%")
print(f"  合计: {structure_total + rate_total:+.4f}%")
print(f"  实际变化: {overall_change:+.4f}%")

# ========== 4. 根因结论 ==========
print()
print("=" * 60)
print("根因结论")
print("=" * 60)

print("""
【辛普森悖论】整体转化率从 3.4% 上升到 3.82%，但渠道A和渠道B的转化率都在下降。

【真实原因】渠道结构性变化（渠道权重再分配）

渠道A（高转化率渠道）:
  - 权重从 20% → 60%（+40%）
  - 转化率从 5.0% → 4.5%（-0.5%）
  - 贡献: +40% × 5.0% = +2.0%

渠道B（低转化率渠道）:
  - 权重从 80% → 40%（-40%）
  - 转化率从 3.0% → 2.8%（-0.2%）
  - 贡献: -40% × 3.0% = -1.2%

【净效果】
  渠道结构贡献: +0.8%
  各渠道转化率下降贡献: -0.38%
  整体变化: +0.42%

【结论】
整体转化率上升是因为高转化率的渠道A获取了更多UV权重（60% vs 20%），
弥补并超过了各渠道转化率下降带来的负面影响。
这是典型的辛普森悖论: 整体指标上升掩盖了各组分都在恶化的真相。
""")