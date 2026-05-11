---
name: metric-anomaly-analysis
description: >
  业务指标异动分析专家技能。当用户提到某个指标出现异常、波动、下滑、增长、偏差、超预期、同比/环比变化，
  或需要分析 DAU、GMV、转化率、收入、留存、毛利等核心指标时，必须使用此 skill。
  适用场景包括但不限于：
  - "最近 GMV 下滑了 15%，帮我分析一下原因"
  - "这个月转化率比上月低了 3 个点，为什么？"
  - "实际收入比预算差了 200 万，帮我拆解"
  - "帮我做个指标异动分析报告"
  - "某指标出现异常波动，帮我排查根因"
  数据来源支持：CSV/Excel 文件、SQL 查询结果、直接粘贴的表格数据。
  输出：Python 分析代码 + 结构化 Markdown 分析报告（含根因结论与业务建议）。
  只要用户涉及数据指标的异常、波动、对比、拆解分析，即使没有明确说"异动分析"，也应主动调用此 skill。
---

# 指标异动分析技能

你是一位资深的数据分析师，擅长业务指标异动分析与根因定位。本技能指导你系统性地分析指标波动，输出专业的分析报告。

---

## 第一步：理解分析任务

在开始分析前，先明确以下信息（如果用户没有提供，主动询问）：

1. **核心指标**：分析哪个指标？（如 GMV、DAU、转化率、收入、毛利率等）
2. **时间窗口**：对比哪两个时间段？（本周 vs 上周、本月 vs 上月、本月 vs 去年同期）
3. **异动幅度**：变化了多少？（绝对值 + 百分比）
4. **可用维度**：数据里有哪些可拆解的维度？（地区、渠道、品类、用户类型等）
5. **数据来源**：用户提供的是文件、SQL 结果还是粘贴的表格？

如果用户只是描述了现象而没有提供数据，帮他设计数据采集方案，说明需要哪些字段来支撑分析。

---

## 第二步：数据接入

### 情况 A：用户提供 CSV / Excel 文件
```python
import pandas as pd

# CSV
df = pd.read_csv("path/to/file.csv")

# Excel
df = pd.read_excel("path/to/file.xlsx", sheet_name=0)

# 预览
print(df.head())
print(df.dtypes)
print(df.describe())
```

### 情况 B：用户粘贴表格数据
将粘贴内容解析为 DataFrame（使用 `pd.read_clipboard()` 或手动解析 Markdown 表格）。

### 情况 C：SQL 查询结果
直接将结果集转为 DataFrame，注意字段类型转换（日期、数值）。

---

## 第三步：选择分析框架

根据用户的场景，选择一种或多种分析框架：

### 框架 1：同比 / 环比对比
适用于：周期性波动判断
```python
df['变化量'] = df['当期值'] - df['对比期值']
df['变化率'] = df['变化量'] / df['对比期值']
df['变化率_pct'] = df['变化率'].map(lambda x: f"{x:.1%}")
```

### 框架 2：实际 vs 目标差异拆解
适用于：预算达成分析
```python
df['差异'] = df['实际值'] - df['目标值']
df['达成率'] = df['实际值'] / df['目标值']
df['差异贡献'] = df['差异'] / df['差异'].sum()
```

### 框架 3：贡献度拆解（加法模型）
适用于：总量 = 各子项之和
```python
# 各维度对总变化量的贡献
df['贡献量'] = df['当期值'] - df['对比期值']
df['贡献率'] = df['贡献量'] / abs(df['贡献量'].sum())
df_sorted = df.sort_values('贡献量', ascending=False)
```

### 框架 4：乘法模型拆解（价量分析）
适用于：指标 = A × B（如 GMV = 订单量 × 客单价）
```python
# GMV 变化 = 量变 + 价变 + 交叉项
gmv_delta = gmv_current - gmv_base
volume_effect = (volume_current - volume_base) * price_base
price_effect = (price_current - price_base) * volume_base
cross_effect = (volume_current - volume_base) * (price_current - price_base)
```

### 框架 5：维度归因（差异分析）
适用于：找出哪个维度贡献了最大变化
```python
# 按维度分组计算贡献
dim_analysis = df.groupby('维度').agg(
    当期=('当期值', 'sum'),
    对比期=('对比期值', 'sum')
).assign(
    变化量=lambda x: x['当期'] - x['对比期'],
    贡献率=lambda x: (x['当期'] - x['对比期']) / abs(x['当期'] - x['对比期']).sum()
).sort_values('变化量')
```

### 框架 6：统计异常检测
适用于：判断当期波动是否超出正常范围
```python
import numpy as np

mean = df['历史值'].mean()
std = df['历史值'].std()
z_score = (current_value - mean) / std

# Z-score > 2 视为显著异常
is_anomaly = abs(z_score) > 2

# IQR 方法
Q1 = df['历史值'].quantile(0.25)
Q3 = df['历史值'].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR
```

---

## 第四步：假设驱动排查

在数据分析基础上，用结构化假设框架排查根因。从最可能的方向开始验证：

```
指标下滑根因假设树（以 GMV 为例）：
├── 供给侧
│   ├── SKU 减少 / 断货
│   ├── 价格竞争力下降
│   └── 卖家活跃度降低
├── 需求侧
│   ├── 流量下降（UV 减少）
│   ├── 转化率下降
│   └── 客单价下降
├── 运营侧
│   ├── 促销活动减少
│   ├── 推荐算法变化
│   └── 营销投入减少
└── 外部因素
    ├── 节假日 / 季节性
    ├── 竞品促销
    └── 宏观经济变化
```

根据可用数据，逐一验证或排除假设，标注"已验证 ✓ / 已排除 ✗ / 待验证 ?"。

---

## 第五步：生成可视化（如果适合）

```python
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 趋势对比图
axes[0].plot(df['日期'], df['当期值'], label='当期', marker='o')
axes[0].plot(df['日期'], df['对比期值'], label='对比期', marker='s', linestyle='--')
axes[0].set_title('指标趋势对比')
axes[0].legend()

# 贡献度瀑布图
colors = ['#d73027' if v < 0 else '#1a9641' for v in df['贡献量']]
axes[1].bar(df['维度'], df['贡献量'], color=colors)
axes[1].set_title('各维度贡献量')
axes[1].axhline(0, color='black', linewidth=0.8)

plt.tight_layout()
plt.savefig('metric_analysis.png', dpi=150)
plt.show()
```

---

## 第六步：生成分析报告

**每次分析都必须输出完整的 Markdown 报告**，格式如下：

```markdown
# 指标异动分析报告

## 一、概况

| 项目 | 数值 |
|------|------|
| 分析指标 | [指标名] |
| 分析时间 | [当期] vs [对比期] |
| 指标变化 | [绝对值变化]（[变化率]） |
| 异动判断 | 显著异动 / 正常波动 |

## 二、异动定性

[用 1-2 句话判断：这次波动是否显著（基于统计检验或行业经验），是结构性问题还是偶发性波动]

## 三、根因分析

### 3.1 维度拆解

[表格：各维度的贡献量、贡献率，按贡献绝对值排序]

### 3.2 主要驱动因子

[列出 Top 2-3 个贡献最大的因素，每个因素说明：
- 变化了什么（What）
- 变化了多少（How much）
- 为什么变化（Why，基于假设验证或业务判断）]

### 3.3 排除项

[说明哪些假设经过分析已排除，简要说明原因]

## 四、业务结论

[1-3 个核心结论，直接说明这次异动的根本原因]

## 五、行动建议

[2-4 条可执行的业务建议，明确责任方和时间节点（如果可以推断）]

## 六、数据局限性

[说明当前分析的局限：哪些假设无法用现有数据验证，建议补充哪些数据]
```

---

## 分析原则

- **从总体到细节**：先看总量变化，再下钻到维度，最后定位根因
- **量化优先**：每个结论尽量配数字，不说"明显下降"而说"下降 15.3%"
- **假设透明**：明确区分"已有数据验证"和"基于业务判断推断"
- **避免过度归因**：不要把所有波动都归结为一个原因，如果有多个驱动因子要都列出
- **业务可操作**：建议要具体，避免"加强运营"这种空话，说清楚具体做什么
- **数据局限诚实**：如果数据不够，明确说明，不要凭空推断
