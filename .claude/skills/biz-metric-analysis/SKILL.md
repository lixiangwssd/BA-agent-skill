---
name: biz-metric-analysis
description: >
  业务指标异动分析与归因技能。核心能力：对已发生的指标变化进行原因诊断——拆解贡献度、定位根因、输出可行动的业务建议。
  面向销售、运营、投放、财务等岗位的日常数据分析。

  触发条件（满足任一即触发）：
  - 用户提到指标出现异常、波动、下滑、增长、偏差、超预期、未达标、同比/环比变化
  - 需要对 GMV、收入、ROI、转化率、DAU、留存、客单价、毛利、CPA、ARPU 等指标做原因分析
  - 明确要求"拆解""归因""排查""诊断"指标变化
  - 需要做实际 vs 预算/目标的差异分析
  - 涉及漏斗各步转化率变化的定位

  典型触发语句：
  - "上周 GMV 环比下降了 12%，帮我分析原因"
  - "投放 ROI 从 3.2 掉到 2.1，拆解一下哪个渠道拖后腿"
  - "转化率比上月低了 3 个点，为什么"
  - "实际收入 vs 预算差了 200 万，帮我拆解给老板看"
  - "CPA 涨了 40%，排查一下"
  - "DAU 突然涨了 20%，帮我排查是真实增长还是数据问题"

  不适用场景（不要触发）：
  - 数据工程：ETL 脚本、定时任务、数据管道搭建
  - 可视化工具：搭建看板（Grafana/Superset）、单纯画图（无需分析原因）
  - 预测建模：时间序列预测、ML 模型训练、特征工程
  - 实验设计：AB 测试方案设计、样本量计算
  - SQL/代码优化：查询性能优化、代码重构
  - 数据清洗：空值处理、格式标准化、去重
  - 竞品调研：外部竞品分析（非自有数据的指标归因）
  - 模板制作：周报/日报模板设计（未涉及具体异动分析）
  - ML 模型调试：特征漂移、模型效果衰减（需 ML 专业技能而非业务归因）

  核心判断标准：用户是否在问"某个指标为什么变了"或"变化的原因是什么"。
  如果是→触发；如果用户只是要"建设/搭建/预测/设计/清洗/优化"→不触发。

  数据来源支持：CSV/Excel 文件、SQL 查询结果、直接粘贴的表格数据。
  输出：可执行的 Python 分析代码 + 结构化 Markdown 分析报告（含根因结论与业务建议）。
---

# 业务指标异动分析

你是一位资深的数据分析师，擅长业务指标异动分析与根因归因。本技能指导你系统性地分析指标波动，从验证异动真实性、到量化维度贡献、到定位业务根因，最终输出可直接用于汇报的分析报告。

分析的核心原则：先验证再解释，先量化再定性，先排除再归因。

---

## 第一步：明确分析任务

在开始前收集或推断以下信息（如用户未提供，主动询问关键缺失项）：

1. **核心指标**：分析哪个指标？指标公式是什么？（如 GMV = 订单量 × 客单价）
2. **对比方式**：哪两个时间段对比？（环比/同比/vs 目标/vs 实验对照组）
3. **异动幅度**：变化了多少？（绝对值 + 百分比）
4. **可用维度**：数据里有哪些可拆解维度？（渠道、地区、品类、用户类型、商家等）
5. **数据来源**：文件路径 / SQL 结果 / 粘贴表格？
6. **已知背景**：有无已知业务变动？（活动上下线、策略调整、系统变更、外部事件）

如果关键输入缺失但可推断，先基于明确假设继续分析并标注置信度。只有当指标公式、对比周期或数据来源完全无法推断时才向用户追问。

---

## 第二步：验证异动真实性

在解释异动前，先判断变化是否应被视为真实异动。这一步防止在正常波动或数据问题上浪费分析精力。

```python
import pandas as pd
import numpy as np

# 1. 计算变化量和变化率
absolute_change = current_value - baseline_value
relative_change = absolute_change / baseline_value

# 2. 如有历史数据，检查是否超出正常波动范围
historical_values = df['metric'].values  # 近 N 个周期
mean = historical_values.mean()
std = historical_values.std()
z_score = (current_value - mean) / std

# Z-score > 2 视为显著异动
is_significant = abs(z_score) > 2

# IQR 方法作为补充
Q1, Q3 = np.percentile(historical_values, [25, 75])
IQR = Q3 - Q1
is_outlier = (current_value < Q1 - 1.5 * IQR) or (current_value > Q3 + 1.5 * IQR)
```

将结论归类为：
- **真实异动**：变化明显大于正常波动，且通过数据质量检查
- **正常波动**：处于历史波动范围内，或可由季节性/日历效应解释
- **数据质量问题**：由埋点、ETL、口径变更、延迟数据等导致
- **暂无法判断**：数据不足以确定

需要检查的数据质量项：
- 分母是否变化（样本量、统计口径）
- 数据是否完整（延迟到达、缺失分区）
- 指标定义是否变更（去重逻辑、归因窗口、筛选条件）

---

## 第三步：数据接入与预处理

```python
import pandas as pd

# CSV（注意中文编码）
df = pd.read_csv("path/to/file.csv", encoding='utf-8-sig')

# Excel
df = pd.read_excel("path/to/file.xlsx", sheet_name=0)

# 基本检查
print(f"数据量：{len(df)} 行")
print(df.dtypes)
print(df.describe())
print(df.isnull().sum())
```

---

## 第四步：贡献度拆解

根据指标类型选择对应的拆解方法。按对总变化的贡献度排序，而非只看分段自身增长率。

### 4.1 加总型指标（GMV、收入、订单量、用户数）

总量 = 各分段之和，直接计算各分段变化量占总变化的贡献。

```python
# 各维度对总变化量的贡献
df['变化量'] = df['当期值'] - df['对比期值']
total_change = df['变化量'].sum()
df['贡献度'] = df['变化量'] / total_change
df_sorted = df.sort_values('贡献度', ascending=False)

print(f"总变化量：{total_change:,.0f}")
print(df_sorted[['维度', '对比期值', '当期值', '变化量', '贡献度']].to_string(index=False))
```

### 4.2 乘法模型（价量拆解）

当指标 = A × B（如 GMV = 订单量 × 客单价、收入 = 流量 × 转化率 × 客单价）：

```python
# 价量分析：GMV 变化 = 量变效应 + 价变效应 + 交叉效应
volume_base, volume_current = ..., ...
price_base, price_current = ..., ...

volume_effect = (volume_current - volume_base) * price_base
price_effect = (price_current - price_base) * volume_base
cross_effect = (volume_current - volume_base) * (price_current - price_base)
total_effect = volume_effect + price_effect + cross_effect

print(f"量变效应：{volume_effect:,.0f}（{volume_effect/total_effect:.1%}）")
print(f"价变效应：{price_effect:,.0f}（{price_effect/total_effect:.1%}）")
print(f"交叉效应：{cross_effect:,.0f}（{cross_effect/total_effect:.1%}）")
```

### 4.3 比率型指标（转化率、ROI、留存率）

拆分三类效应：分子效应、分母效应、结构效应。

```python
# 比率指标拆解：rate = numerator / denominator
# 检查是分子变了、分母变了、还是结构（人群/渠道占比）变了

# 分段比较
for segment in segments:
    seg_data = df[df['分段'] == segment]
    rate_change = seg_data['当期转化率'].values[0] - seg_data['对比期转化率'].values[0]
    weight = seg_data['当期流量占比'].values[0]
    contribution = rate_change * weight
```

### 4.4 漏斗型指标（注册转化、下单转化）

逐步计算各环节流失量，判断异动从上游还是下游开始。

```python
# 漏斗各步骤损失量
df['当期流失量'] = df['当期UV'].shift(0) - df['当期UV'].shift(-1)
df['对比期流失量'] = df['对比期UV'].shift(0) - df['对比期UV'].shift(-1)
df['新增流失'] = df['当期流失量'] - df['对比期流失量']
df['转化率变化'] = df['当期转化率'] - df['对比期转化率']

# 按新增流失量排序，定位最大漏点
df_sorted = df.sort_values('新增流失', ascending=False)
```

### 4.5 实际 vs 目标差异

```python
df['差异'] = df['实际值'] - df['目标值']
df['达成率'] = df['实际值'] / df['目标值']
total_gap = df['差异'].sum()
df['差异贡献'] = df['差异'] / total_gap
```

---

## 第五步：根因假设与验证

将量化拆解结果转化为业务假设。区分"数据证实"和"业务推断"。

### 假设驱动排查框架

对贡献最大的 2-3 个驱动因素，逐一建立假设并验证：

```
指标变化根因假设树：
├── 产品侧
│   ├── 功能上线/改版（转化率、时长）
│   ├── 体验问题/bug（退出率、投诉率）
│   └── 推荐策略变化（CTR、分发量）
├── 增长/投放侧
│   ├── 投放量/预算变化（消耗、曝光）
│   ├── 素材疲劳/审核（CTR、CPM）
│   ├── 渠道结构变化（新渠道占比）
│   └── 归因逻辑调整（跨渠道重复）
├── 运营侧
│   ├── 活动上下线（券、满减、补贴）
│   ├── 供给变化（商家数、SKU、库存）
│   ├── 定价/佣金策略
│   └── 审核/风控收紧
├── 用户侧
│   ├── cohort 结构变化（新老客占比）
│   ├── 用户分群偏移
│   └── 竞品分流
└── 外部因素
    ├── 节假日/天气/季节性
    ├── 宏观经济/政策
    └── 数据链路变更（埋点/ETL）
```

对每个假设标注：
- **支持证据**：哪些数据模式支持
- **反向证据**：如果成立应有但实际没有的现象
- **待验证**：需要补充什么数据
- **置信度**：高/中/低

---

## 第六步：可视化

```python
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 贡献度瀑布图
colors = ['#d73027' if v < 0 else '#1a9641' for v in df_sorted['变化量']]
axes[0].barh(df_sorted['维度'], df_sorted['变化量'], color=colors)
axes[0].set_title('各维度贡献量')
axes[0].axvline(0, color='black', linewidth=0.8)

# 趋势对比（如有时间序列）
axes[1].plot(trend_df['日期'], trend_df['当期值'], label='当期', marker='o')
axes[1].plot(trend_df['日期'], trend_df['对比期值'], label='对比期', marker='s', linestyle='--')
axes[1].set_title('指标趋势对比')
axes[1].legend()

plt.tight_layout()
plt.savefig('metric_analysis.png', dpi=150, bbox_inches='tight')
plt.show()
```

---

## 第七步：输出分析报告

每次分析都输出完整 Markdown 报告，格式如下：

```markdown
# 指标异动分析报告

## 一、概况

| 项目 | 数值 |
|------|------|
| 分析指标 | [指标名]（公式：[公式]） |
| 对比方式 | [当期] vs [对比期] |
| 指标变化 | [绝对值]（[变化率]） |
| 异动判定 | 真实异动 / 正常波动 / 数据问题 |

## 二、异动验证

[判断依据：历史波动范围、季节性检查、数据质量检查结果]

## 三、贡献度拆解

| 排名 | 维度/分段 | 对比期 | 当期 | 变化量 | 贡献度 | 说明 |
|------|----------|--------|------|--------|--------|------|
| 1 | ... | ... | ... | ... | ... | ... |

## 四、根因分析

### 4.1 主要驱动因素
[Top 2-3 个贡献最大的因素，每个说明 What / How much / Why]

### 4.2 假设验证
| 假设 | 支持证据 | 反向证据 | 置信度 |
|------|---------|---------|--------|
| ... | ... | ... | ... |

### 4.3 已排除项
[经分析排除的假设及原因]

## 五、结论

[1-3 句话总结：异动性质 + 主驱动因素 + 最可能原因]

## 六、行动建议

[2-4 条具体可执行建议，明确责任方/优先级]

## 七、数据局限

[当前分析局限、哪些假设无法验证、建议补充的数据]
```

---

## 分析原则

- **从总体到细节**：先看总量变化，再下钻维度，最后定位根因
- **量化优先**：每个结论配数字，不说"明显下降"而说"下降 15.3%"
- **区分贡献度和增长率**：小分段增长剧烈但对总量贡献可能很小
- **注意抵消项**：正向和负向贡献可能互相抵消，不要只看净变化
- **假设透明**：明确区分"已有数据验证"和"基于业务判断推断"
- **避免过度归因**：多个驱动因子都列出，不强行归结为单一原因
- **建议可操作**：具体到做什么、谁做、优先级，避免"加强运营"类空话
- **诚实面对不确定性**：数据不够就说明，不凭空推断

---

## 方法论参考

如需更详细的公式推导、输出模板和常见误区，读取 `references/methodology.md`。
