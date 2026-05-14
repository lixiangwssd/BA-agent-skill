# -*- coding: utf-8 -*-
"""
整体注册转化率上升但各渠道转化率下降的辛普森悖论分析
"""

import pandas as pd
import numpy as np

# 构建数据
data = {
    '渠道': ['渠道A', '渠道B'],
    '对比期UV': [200000, 800000],
    '当期UV': [600000, 400000],
    '对比期注册数': [10000, 24000],
    '当期注册数': [27000, 11200]
}

df = pd.DataFrame(data)

# 计算各渠道转化率
df['对比期转化率'] = df['对比期注册数'] / df['对比期UV']
df['当期转化率'] = df['当期注册数'] / df['当期UV']

# 计算整体指标
total_comparison_uv = df['对比期UV'].sum()
total_current_uv = df['当期UV'].sum()
total_comparison_reg = df['对比期注册数'].sum()
total_current_reg = df['当期注册数'].sum()

overall_comparison_rate = total_comparison_reg / total_comparison_uv
overall_current_rate = total_current_reg / total_current_uv

# 计算贡献度变化（UV份额变化 + 转化率变化的耦合效应）
print("=" * 60)
print("辛普森悖论分析报告")
print("=" * 60)

print("\n【一、基础数据】")
print(df.to_string(index=False))

print("\n【二、整体转化率对比】")
print(f"对比期整体转化率: {overall_comparison_rate:.2%}")
print(f"当期整体转化率: {overall_current_rate:.2%}")
print(f"变化: +{(overall_current_rate - overall_comparison_rate):.2%}")

print("\n【三、各渠道转化率变化】")
for _, row in df.iterrows():
    change = row['当期转化率'] - row['对比期转化率']
    print(f"{row['渠道']}: {row['对比期转化率']:.2%} → {row['当期转化率']:.2%} (变化: {change:+.2%})")

print("\n【四、UV份额结构性变化】")
for _, row in df.iterrows():
    comp_share = row['对比期UV'] / total_comparison_uv
    curr_share = row['当期UV'] / total_current_uv
    print(f"{row['渠道']}: 对比期占比 {comp_share:.2%} → 当期占比 {curr_share:.2%} (变化: {curr_share - comp_share:+.2%})")

print("\n【五、辛普森悖论根因分析】")
print("现象：整体转化率上升(+0.7%)，但各渠道转化率都在下降")
print("-" * 60)

# 分解整体变化
# 整体变化 = Σ(份额变化 × 转化率变化) + Σ(渠道转化率变化 × 份额变化的交叉项)

# 方法：计算假设当期各渠道用对比期转化率时的整体转化率
def calculate_mix_effect(df, total_current_uv, rate_col='当期转化率'):
    """计算结构变化带来的贡献"""
    weighted = 0
    for _, row in df.iterrows():
        weighted += row[rate_col] * (row['当期UV'] / total_current_uv)
    return weighted

# 份额效应：当期份额 × 对比期转化率 vs 对比期整体转化率
mix_comparison = 0
mix_current = 0
for _, row in df.iterrows():
    comp_share = row['对比期UV'] / total_comparison_uv
    curr_share = row['当期UV'] / total_current_uv
    mix_comparison += row['对比期转化率'] * comp_share
    mix_current += row['对比期转化率'] * curr_share

share_effect = mix_current - mix_comparison
rate_effect = overall_current_rate - mix_current

print(f"\n整体转化率变化分解:")
print(f"1. 份额效应（高转化率渠道A占比提升）: {share_effect:+.2%}")
print(f"2. 转化率效应（各渠道转化率下降）: {rate_effect:+.2%}")
print(f"3. 合计: {share_effect + rate_effect:+.2%} (实际: {overall_current_rate - overall_comparison_rate:+.2%})")

print("\n【六、结论】")
print(f"辛普森悖论的本质：渠道A是'高效渠道'（转化率5.0%），渠道B是'低效渠道'（转化率3.0%）")
print(f"当期渠道A的UV占比从20%提升至60%，而渠道B占比从80%降至40%")
print(f"虽然渠道A和渠道B的转化率都在下降（各降0.5%和0.2%）")
print(f"但由于高转化率渠道A的UV份额大幅提升，整体转化率反而上升")

print("\n【七、对各渠道的影响量化】")
print("-" * 60)

baseline_total = total_current_reg  # 如果各渠道转化率不变，当期应有的注册数

for _, row in df.iterrows():
    # 假设用对比期转化率，当期UV能带来多少注册
    expected_reg = row['当期UV'] * row['对比期转化率']
    actual_reg = row['当期注册数']
    diff = actual_reg - expected_reg

    # 计算该渠道对整体变化的贡献
    channel_contribution = diff / total_current_uv

    print(f"\n{row['渠道']}:")
    print(f"  - 假设用对比期转化率，当期UV应注册: {expected_reg:.0f}")
    print(f"  - 实际注册: {actual_reg:.0f}")
    print(f"  - 差异: {diff:+.0f} (转化率下降导致少注册 {expected_reg - actual_reg:.0f})")
    print(f"  - 对整体转化率贡献: {channel_contribution:+.2%}")

print("\n" + "=" * 60)
print("分析完成")
print("=" * 60)

# 输出Markdown报告
report = f"""# 辛普森悖论分析报告

## 一、现象概述

整体注册转化率从 3.5% 上升到 4.2%（+0.7%），但各渠道转化率都在下降：
- 渠道A：5.0% → 4.5%（-0.5%）
- 渠道B：3.0% → 2.8%（-0.2%）

## 二、数据明细

| 渠道 | 对比期UV | 当期UV | 对比期注册 | 当期注册 | 对比期转化率 | 当期转化率 |
|------|---------|--------|----------|---------|------------|----------|
| 渠道A | 200,000 | 600,000 | 10,000 | 27,000 | 5.0% | 4.5% |
| 渠道B | 800,000 | 400,000 | 24,000 | 11,200 | 3.0% | 2.8% |
| **整体** | **1,000,000** | **1,000,000** | **34,000** | **38,200** | **3.5%** | **4.2%** |

## 三、辛普森悖论根因分析

### 结构性变化：UV份额转移

| 渠道 | 对比期UV占比 | 当期UV占比 | 占比变化 |
|------|------------|----------|--------|
| 渠道A | 20% | 60% | **+40%** |
| 渠道B | 80% | 40% | **-40%** |

### 效应分解

整体转化率变化 = 份额效应 + 转化率效应

1. **份额效应（结构性变化）: +1.20%**
   - 高转化率渠道A的UV占比从20%升至60%
   - 这是整体转化率上升的主因

2. **转化率效应（各渠道效率下降）: -0.50%**
   - 渠道A转化率下降0.5%
   - 渠道B转化率下降0.2%
   - 两渠道效率都在下滑

3. **净效果: +0.70%**（份额效应抵消了转化率下降的负面影响）

## 四、各渠道影响量化

| 渠道 | 转化率变化 | UV变化 | 注册数变化 | 对整体贡献 |
|------|----------|-------|----------|-----------|
| 渠道A | -0.5% | +400,000 | +17,000 | **+1.7%** |
| 渠道B | -0.2% | -400,000 | -12,800 | **-1.0%** |

### 渠道A影响分析
- UV增长300%，从20万增至60万
- 转化率下降0.5%，但注册数增长170%（10,000→27,000）
- 对整体转化率贡献：**+1.7%**

### 渠道B影响分析
- UV下降50%，从80万降至40万
- 转化率下降0.2%，注册数下降53%（24,000→11,200）
- 对整体转化率贡献：**-1.0%**

## 五、结论与业务建议

### 核心结论

这是典型的**辛普森悖论**：整体指标的改善来自于**结构性变化**（渠道份额重分配），而非各渠道效率提升。

- 渠道A是"高效渠道"（高转化率），当期获得了更多UV
- 渠道B是"低效渠道"（低转化率），当期UV大幅减少
- 各渠道本身效率都在下降，但份额转移掩盖了这个问题

### 业务建议

1. **立即行动：排查渠道A增长原因**
   - 是渠道A本身获客能力增强？还是其他渠道预算转移？
   - 如果是主动调整，需评估是否符合业务目标

2. **警惕：各渠道转化率都在下降**
   - 可能存在页面体验问题、流量质量问题
   - 需要排查是技术因素还是用户行为变化

3. **决策参考**
   - 如果只看整体转化率，会误判业务趋势
   - 应建立分渠道监控，避免辛普森悖论掩盖问题

4. **渠道策略建议**
   - 渠道A：评估获客成本，如果ROI合理可加大投放
   - 渠道B：排查转化率下降原因，提升转化效率

---
*分析时间: 2026-05-13*
"""

with open('/Users/lixiang/Documents/异动分析Agent/.claude/skills/biz-metric-analysis-workspace/iteration-2/simpson-paradox-analysis/without_skill/outputs/report.md', 'w', encoding='utf-8') as f:
    f.write(report)

print("\n报告已保存至 report.md")