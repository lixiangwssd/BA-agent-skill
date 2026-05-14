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

收集或推断以下信息（**信息不足时必须主动追问**，不能跳步）：

1. **核心指标**：指标名称和公式（如 GMV = 订单量 × 客单价）
2. **对比方式**：环比/同比/vs 目标/vs 实验对照组
3. **异动幅度**：绝对值 + 百分比
4. **可用维度**：渠道、地区、品类、用户类型、商家等
5. **数据来源**：文件路径 / SQL 结果 / 粘贴表格
6. **已知背景**：活动上下线、策略调整、系统变更、外部事件

**追问原则**：
- 指标不明确 → 询问："请问是哪个指标？"
- 时间段不明确 → 询问："对比哪个时间段？"
- 数据未提供 → 询问："有数据文件或表格可以提供吗？"
- 用户只说"波动" → 先确认指标和周期再分析

---

## 第二步：验证异动真实性

判断变化是否属于真实异动，防止在正常波动或数据问题上浪费精力。

```python
import pandas as pd
import numpy as np

# 计算变化量和变化率
absolute_change = current_value - baseline_value
relative_change = absolute_change / baseline_value

# 有历史数据时检查是否超出正常波动范围
historical_values = df['metric'].values
mean, std = historical_values.mean(), historical_values.std()
z_score = (current_value - mean) / std  # |z| > 2 为显著异动

# IQR 法作为补充
Q1, Q3 = np.percentile(historical_values, [25, 75])
IQR = Q3 - Q1
is_outlier = (current_value < Q1 - 1.5 * IQR) or (current_value > Q3 + 1.5 * IQR)
```

结论归类：**真实异动** / **正常波动** / **数据质量问题** / **暂无法判断**

数据质量检查项：分母变化、延迟到达/缺失分区、指标定义变更（去重/归因/筛选）

---

## 第三步：数据接入与预处理

```python
import pandas as pd

df = pd.read_csv("path/to/file.csv", encoding='utf-8-sig')  # CSV 中文编码
df = pd.read_excel("path/to/file.xlsx", sheet_name=0)       # Excel

print(f"数据量：{len(df)} 行")
print(df.describe())
print(df.isnull().sum())
```

---

## 第四步：贡献度拆解

按贡献度排序，而非只看分段自身增长率。

### 4.1 加总型（GMV、收入、订单量、用户数）

```python
df['变化量'] = df['当期值'] - df['对比期值']
total_change = df['变化量'].sum()
df['贡献度'] = df['变化量'] / total_change
df_sorted = df.sort_values('贡献度', ascending=False)
```

### 4.2 乘法模型（价量拆解）

指标 = A × B 时（GMV = 订单量 × 客单价）：

```python
# GMV 变化 = 量变效应 + 价变效应 + 交叉效应
volume_effect = (volume_current - volume_base) * price_base
price_effect = (price_current - price_base) * volume_base
cross_effect = (volume_current - volume_base) * (price_current - price_base)
total_effect = volume_effect + price_effect + cross_effect

print(f"量变效应：{volume_effect:,.0f}（{volume_effect/total_effect:.1%}）")
print(f"价变效应：{price_effect:,.0f}（{price_effect/total_effect:.1%}）")
print(f"交叉效应：{cross_effect:,.0f}（{cross_effect/total_effect:.1%}）")
```

### 4.3 比率型（转化率、ROI、留存率）

拆分为分子效应、分母效应、结构效应。检测 Simpson 悖论：整体上升但各分段下降时，检查是否为结构变化。

### 4.4 漏斗型（注册转化、下单转化）

```python
df['当期流失量'] = df['当期UV'] - df['当期UV'].shift(-1)
df['对比期流失量'] = df['对比期UV'] - df['对比期UV'].shift(-1)
df['新增流失'] = df['当期流失量'] - df['对比期流失量']
df['转化率变化'] = df['当期转化率'] - df['对比期转化率']
df_sorted = df.sort_values('新增流失', ascending=False)
```

### 4.5 实际 vs 目标差异

```python
df['差异'] = df['实际值'] - df['目标值']
df['达成率'] = df['实际值'] / df['目标值']
total_gap = df['差异'].sum()
df['差异贡献'] = df['差异'] / total_gap
```

### 4.6 多维并行拆解 + 交叉下钻

当数据包含多个维度（渠道、品类、地区等）时，按以下路径分析：

```python
# Step 1: 并行计算所有维度的贡献度
dimensions = ['渠道', '品类', '地区']
contributions = {}
for dim in dimensions:
    contributions[dim] = calculate_contribution(df, dim)

# Step 2: 找出贡献度最大的维度
top_dim = max(contributions, key=contributions.get)

# Step 3: 对贡献最大的维度做交叉分析
# 例如：渠道 × 地区
cross_analysis = df.groupby(['渠道', '地区'])['变化量'].sum().reset_index()
cross_analysis['贡献度'] = cross_analysis['变化量'] / total_change
cross_sorted = cross_analysis.sort_values('贡献度', ascending=False)

# Step 4: 定位最大拖累组合
top_combo = cross_sorted.iloc[0]
```

**多维下钻原则**：
1. 先并行拆解所有维度，找出贡献最大的维度
2. 对贡献最大的维度做交叉验证（维度1 × 维度2）
3. 找到贡献最大的组合后，结合已知背景归因
4. 每层下钻都量化贡献度

---

## 第五步：根因假设与验证

对贡献最大的 2-3 个因素逐一建立假设并验证：

```
根因假设树：
├── 产品侧：功能上线/改版、体验问题/bug、推荐策略变化
├── 增长/投放侧：投放量/预算变化、素材疲劳、渠道结构、归因调整
├── 运营侧：活动上下线、供给变化、定价/佣金策略、审核收紧
├── 用户侧：cohort 结构变化、竞品分流
└── 外部因素：节假日/天气、宏观/政策、数据链路变更
```

每假设标注：支持证据 / 反向证据 / 待验证数据 / 置信度（高/中/低）

### 5.1 矛盾现象处理

当出现矛盾指标时（如 DAU↓ 但留存↑），处理方式：

1. **识别矛盾**：列出所有矛盾指标对
2. **提出假设**：建立能解释矛盾的假设（如：新版本留住老用户但排斥新用户）
3. **设计验证方案**：明确需要什么数据来验证假设

```python
# 矛盾分析示例：DAU 下降但留存上升
contradictions = [
    ("DAU 下降 10%", "留存上升 5%")
]

hypotheses = [
    "假设：版本更新导致体验好的老用户留下，体验差的新用户流失",
]

verification_plan = """
验证步骤：
1. 分群对比：新用户 vs 老用户的 DAU 变化
2. 版本对比：更新前 vs 更新后的各指标趋势
3. 渠道对比：各渠道的新增用户转化率差异
"""
```

---

## 第六步：可视化

```python
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

colors = ['#d73027' if v < 0 else '#1a9641' for v in df_sorted['变化量']]
axes[0].barh(df_sorted['维度'], df_sorted['变化量'], color=colors)
axes[0].set_title('各维度贡献量')
axes[0].axvline(0, color='black', linewidth=0.8)

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

[历史波动范围、季节性检查、数据质量检查结果]

## 三、贡献度拆解

### 3.1 各维度并行拆解
| 维度 | 总变化量 | 贡献度 |
|------|---------|--------|
| 渠道 | -120 万 | 50% |
| 品类 | -80 万 | 33% |
| 地区 | -120 万 | 50% |

### 3.2 交叉维度下钻（贡献最大维度）
| 维度组合 | 变化量 | 贡献度 |
|----------|--------|--------|
| 付费推广 × 华南 | -80 万 | 33% |

## 四、根因分析

### 4.1 主要驱动因素
[Top 2-3 贡献最大因素，说明 What / How much / Why]

### 4.2 假设验证
| 假设 | 支持证据 | 反向证据 | 置信度 |
|------|---------|---------|--------|
| ... | ... | ... | ... |

### 4.3 已排除项
[排除的假设及原因]

## 五、结论

[1-3 句话：异动性质 + 主驱动因素 + 最可能原因]

## 六、行动建议

[2-4 条具体可执行建议，明确责任方/优先级]

## 七、数据局限

[分析局限、无法验证的假设、建议补充的数据]
```

---

## 分析原则

- **从总体到细节**：先看总量，再下钻维度，最后定位根因
- **量化优先**：每个结论配数字，不用"明显下降"而用"下降 15.3%"
- **区分贡献度和增长率**：小分段大幅增长但对总量贡献可能很小
- **注意抵消项**：正向负向贡献可能互相抵消，不只看净变化
- **假设透明**：区分"数据验证"和"业务推断"
- **避免过度归因**：多驱动因子都列出，不强行归结单一原因
- **建议可操作**：具体到做什么、谁做、优先级
- **诚实面对不确定性**：数据不够就说明，不凭空推断
- **多维下钻**：先并行拆解所有维度，再对最大贡献维度做交叉验证

---

## 方法论参考

如需更详细的公式推导、输出模板和常见误区，读取 `references/methodology.md`。