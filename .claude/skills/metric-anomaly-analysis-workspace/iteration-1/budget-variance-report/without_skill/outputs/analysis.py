"""
Q1 Revenue vs Budget Variance Analysis
Financial Analysis for CFO Reporting
Date: 2026-05-11
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib import rcParams

# --- Configure Chinese font support ---
rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti SC', 'Arial Unicode MS', 'SimHei', 'sans-serif']
rcParams['axes.unicode_minus'] = False

# ============================================================
# 1. Data Preparation
# ============================================================

data = {
    'Region':         ['华东', '华南', '华北', '西部'],
    'Budget':         [800,    600,    500,    300],
    'Actual':         [856,    498,    445,    321],
}

df = pd.DataFrame(data)
df['Variance']        = df['Actual'] - df['Budget']
df['Variance_Pct']    = (df['Variance'] / df['Budget'] * 100).round(2)
df['Variance_Label']  = df['Variance'].apply(lambda x: f"+{x}" if x > 0 else str(x))
df['Status']          = df['Variance'].apply(lambda x: 'Favorable' if x >= 0 else 'Unfavorable')

# Total row
total_budget  = df['Budget'].sum()
total_actual  = df['Actual'].sum()
total_variance = total_actual - total_budget
total_pct     = round(total_variance / total_budget * 100, 2)

print("=" * 60)
print("Q1 Revenue vs Budget Variance Summary (Unit: 万元)")
print("=" * 60)
print(df[['Region', 'Budget', 'Actual', 'Variance', 'Variance_Pct', 'Status']].to_string(index=False))
print("-" * 60)
print(f"{'Total':<10} {total_budget:<10} {total_actual:<10} {total_variance:<10} {total_pct}%")
print("=" * 60)

# ============================================================
# 2. Contribution Analysis — which regions drove the shortfall
# ============================================================

df['Contribution_to_Total_Variance'] = (df['Variance'] / abs(total_variance) * 100).round(1)

print("\nContribution to Total Variance (-80 万元):")
print(df[['Region', 'Variance', 'Contribution_to_Total_Variance']].to_string(index=False))

# ============================================================
# 3. Visualization
# ============================================================

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('Q1 2026  Revenue vs Budget Analysis', fontsize=16, fontweight='bold', y=1.02)

colors_bar  = ['#4CAF50' if v >= 0 else '#F44336' for v in df['Variance']]
colors_bgt  = '#90CAF9'
colors_act  = '#1565C0'

# --- Chart 1: Budget vs Actual by Region ---
ax1 = axes[0]
x = np.arange(len(df['Region']))
width = 0.35
bars1 = ax1.bar(x - width/2, df['Budget'], width, label='预算', color=colors_bgt, edgecolor='white')
bars2 = ax1.bar(x + width/2, df['Actual'], width, label='实际', color=colors_act, edgecolor='white')
ax1.set_xlabel('区域')
ax1.set_ylabel('收入（万元）')
ax1.set_title('预算 vs 实际收入（分区域）')
ax1.set_xticks(x)
ax1.set_xticklabels(df['Region'])
ax1.legend()
ax1.set_ylim(0, 950)
for bar in bars1:
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
             f'{int(bar.get_height())}', ha='center', va='bottom', fontsize=9, color='#555')
for bar in bars2:
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
             f'{int(bar.get_height())}', ha='center', va='bottom', fontsize=9, color='#1565C0', fontweight='bold')

# --- Chart 2: Variance Waterfall ---
ax2 = axes[1]
variances = df['Variance'].tolist()
bars = ax2.bar(df['Region'], variances, color=colors_bar, edgecolor='white', width=0.5)
ax2.axhline(0, color='black', linewidth=0.8, linestyle='--')
ax2.set_xlabel('区域')
ax2.set_ylabel('差异（万元）')
ax2.set_title('各区域收入差异（实际 - 预算）')
for bar, val in zip(bars, variances):
    label = f'+{val}' if val > 0 else str(val)
    ypos = val + 2 if val >= 0 else val - 4
    ax2.text(bar.get_x() + bar.get_width()/2, ypos, label,
             ha='center', va='bottom' if val >= 0 else 'top', fontsize=11, fontweight='bold')
fav_patch   = mpatches.Patch(color='#4CAF50', label='有利差异')
unfav_patch = mpatches.Patch(color='#F44336', label='不利差异')
ax2.legend(handles=[fav_patch, unfav_patch])

# --- Chart 3: Contribution to Total Shortfall ---
ax3 = axes[2]
contribs = df['Contribution_to_Total_Variance'].tolist()
colors_contrib = ['#4CAF50' if v > 0 else '#F44336' for v in df['Variance']]
bars3 = ax3.barh(df['Region'], contribs, color=colors_contrib, edgecolor='white')
ax3.axvline(0, color='black', linewidth=0.8, linestyle='--')
ax3.set_xlabel('对总差异的贡献度（%）')
ax3.set_title('各区域对总差异的贡献（总差异 = -80 万元）')
for bar, val in zip(bars3, contribs):
    xpos = val + 1 if val >= 0 else val - 1
    ha   = 'left' if val >= 0 else 'right'
    ax3.text(xpos, bar.get_y() + bar.get_height()/2,
             f'{val:+.1f}%', ha=ha, va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(
    '/Users/lixiang/Documents/异动分析Agent/.claude/skills/metric-anomaly-analysis-workspace/'
    'iteration-1/budget-variance-report/without_skill/outputs/variance_charts.png',
    dpi=150, bbox_inches='tight'
)
print("\nChart saved to variance_charts.png")

# ============================================================
# 4. Key Metrics Summary
# ============================================================

print("\n--- Key Metrics ---")
print(f"Total Budget Achievement Rate : {total_actual/total_budget*100:.1f}%")
print(f"Total Variance                : {total_variance:+d} 万元 ({total_pct:+.1f}%)")
print(f"Largest Favorable Region      : 华东 (+56 万元, +7.0%)")
print(f"Largest Unfavorable Region    : 华南 (-102 万元, -17.0%)  [Known: large client delayed signing]")
print(f"Second Unfavorable Region     : 华北 (-55 万元, -11.0%)")
print(f"\nExcluding 华南 one-off impact:")

adj_variance = total_variance - (-102)
adj_actual   = total_actual   - 498
adj_budget   = total_budget   - 600
print(f"  Adjusted Variance           : {adj_variance:+d} 万元 ({adj_variance/adj_budget*100:+.1f}%)")
print(f"  => Underlying business is slightly ahead of budget once the one-off is stripped out.")

# ============================================================
# 5. Write Markdown Report
# ============================================================

import os

report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report.md')

report_content = """# Q1 2026 收入差异分析报告

**报告日期：** 2026年5月11日
**报告对象：** CFO
**准备人：** 财务分析部门
**数据口径：** 2026年第一季度（1月－3月）合并口径，单位：万元

---

## 一、执行摘要

Q1 公司合并收入实现 **2,120 万元**，较预算 **2,200 万元** 低 **80 万元**，完成率 **96.4%**，整体轻微低于预算。

核心结论：

- **华南区** 是最大拖累项，缺口达 **-102 万元**（-17.0%），主因已明确：一家大客户合同于3月延期签署，属**一次性影响**，客户资产安全、合同大概率于Q2落地。
- **排除华南一次性影响后**，其余三大区域合计差异为 **+22 万元**，即基础业务整体**略优于预算**，经营质量健康。
- **华东区** 超额完成预算 **+56 万元**（+7.0%），表现突出，可作为优秀实践在集团内推广。
- **华北区** 存在结构性缺口 **-55 万元**（-11.0%），需重点跟进，建议列入Q2专项改善计划。

---

## 二、数据明细

### 2.1 区域收入差异总览

| 区域 | 预算收入 | 实际收入 | 差异 | 差异率 | 状态 |
|:----:|:-------:|:-------:|:----:|:------:|:----:|
| 华东 | 800 | 856 | **+56** | +7.0% | 有利 |
| 华南 | 600 | 498 | **-102** | -17.0% | 不利（一次性） |
| 华北 | 500 | 445 | **-55** | -11.0% | 不利 |
| 西部 | 300 | 321 | **+21** | +7.0% | 有利 |
| **合计** | **2,200** | **2,120** | **-80** | **-3.6%** | 轻微低于预算 |

### 2.2 各区域对总差异的贡献度

| 区域 | 差异（万元） | 对总缺口贡献度 | 性质 |
|:----:|:-----------:|:-------------:|:----:|
| 华南 | -102 | **127.5%** | 一次性延期 |
| 华北 | -55 | **68.8%** | 需关注 |
| 华东 | +56 | -70.0% | 对冲正贡献 |
| 西部 | +21 | -26.3% | 对冲正贡献 |
| **合计** | **-80** | **100%** | — |

> 注：贡献度超过100%意味着华南和华北的缺口已超过总缺口，但被华东、西部的正超额部分部分抵消。

---

## 三、根因分析

### 3.1 华南区（-102 万元，-17.0%）— 一次性事件，可控

**已知背景（CFO已掌握）：** 华南区某大客户原计划在3月完成合同签署，因客户内部审批流程延误，合同顺延至Q2。

**影响评估：**

- 该缺口属**时间性差异（Timing Difference）**，非客户流失或竞争失利。
- 合同尚在谈判推进中，风险可控，Q2有望确认收入。
- 建议在Q2报告中追踪该笔合同的最终签约情况，并对CFO保持透明披露。

**管理建议：** 无需对Q1绩效评估做重大调整，但应在Q2收入预测中纳入该笔合同的落地概率进行敏感性分析。

---

### 3.2 华北区（-55 万元，-11.0%）— 需深度排查

华北区差异为 **-55 万元**，缺口率 -11.0%，在排除华南一次性因素后，是最值得关注的区域。

**可能原因（建议核查）：**

| 排查维度 | 核查问题 |
|:--------:|:--------|
| 客户结构 | 是否存在大客户流失或续约率下降？ |
| 销售执行 | Q1 pipeline 转化率相比去年同期是否恶化？ |
| 市场竞争 | 北方市场是否存在竞争加剧或价格压力？ |
| 季节性 | Q1 华北是否存在历史性季节性低谷模式？ |
| 预算准确性 | 华北预算是否设置偏高，需要重新校准基线？ |

**管理建议：** 要求华北区域负责人提交Q1根因说明及Q2改善计划，不晚于5月底前上报。

---

### 3.3 华东区（+56 万元，+7.0%）— 超额亮点，值得复盘

华东区超额完成预算 **+56 万元**，超额率 7.0%，是本季度最佳表现区域。

**建议行动：**

- 组织华东区管理层进行经验分享，识别可在全国复制的销售方法论或客户运营策略。
- 评估华东区Q2预算是否需要上调，避免低估天花板。

---

### 3.4 西部区（+21 万元，+7.0%）— 稳健超额

西部区以较低的预算基础实现 +7.0% 的超额，表现稳健，增长质量良好。

---

## 四、调整后视角：剔除一次性因素

为真实反映基础业务健康度，剔除华南区一次性延期影响后：

| 指标 | 金额 |
|:----:|:----:|
| 调整后预算（不含华南） | 1,600 万元 |
| 调整后实际（不含华南） | 1,622 万元 |
| **调整后差异** | **+22 万元（+1.4%）** |

**结论：基础业务整体轻微超额，公司核心经营盘保持健康。**

---

## 五、风险提示

| 风险项 | 级别 | 说明 |
|:------:|:----:|:-----|
| 华南客户合同Q2仍未签署 | 中 | 若延续至Q2仍未落地，需重新评估全年收入预测 |
| 华北区持续承压 | 中高 | 若Q2继续低于预算，需启动专项干预机制 |
| 预算准确性偏差 | 低 | 部分区域预算设置可能存在基线偏差，建议年中滚动校准 |

---

## 六、结论与行动建议

### 核心结论

> Q1 整体收入低于预算 **-80 万元（-3.6%）**，表面上存在缺口，但实质上由**华南区单一客户延期签单**这一一次性因素所主导。剔除该一次性影响后，基础业务保持健康，多个区域实现超额完成。公司整体收入质量可控，无需过度担忧。

### 行动建议清单

| 优先级 | 行动项 | 责任方 | 时限 |
|:------:|:------|:------:|:----:|
| 高 | 持续跟踪华南大客户合同进展，建立周报机制 | 华南区总 + 销售VP | 即刻启动 |
| 高 | 要求华北区提交Q1根因说明及Q2改善计划 | 华北区总 | 5月底前 |
| 中 | 复盘华东超额经验，提炼可推广的销售方法 | 销售运营部 | 6月中 |
| 中 | 对华南合同Q2落地概率进行敏感性分析，纳入Q2预测模型 | FP&A团队 | 5月底前 |
| 低 | 评估各区域预算基线准确性，启动年中预算滚动修订 | FP&A团队 | Q2末 |

---

## 附录：数据说明

- 数据来源：各区域Q1财务结算数据
- 预算口径：2026年年度预算Q1分解数
- 差异计算公式：差异 = 实际收入 - 预算收入；差异率 = 差异 / 预算收入
- 华南一次性说明：该客户合同金额及延期原因已由华南区总确认，背景信息由CFO掌握

---

*本报告由财务分析部门编制，如有疑问请联系财务分析团队。*
"""

with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report_content)

print(f"\nMarkdown report saved to: {report_path}")
