---
name: strategy-library
description: >
  Use when needing to establish, populate, or update a strategy library for a project.
  Triggers: user wants to define strategy framework (what dimensions/elements compose a strategy),
  cold-start the library from historical data, add new strategy records, update strategy effectiveness,
  perform strategy interpolation for untested strategies, or replace interpolated values with real results.
  Also triggers when strategy optimization or strategy mining skills need strategy data but the library
  is empty or incomplete.
---

# 策略库

管理策略的结构化知识库。包含策略框架定义（策略由哪些要素构成）和策略效果记录（历史策略的实际表现）。

核心原则：**所有内容必须经用户确认，绝不自行编造或擅自修改。**

---

## 触发条件

- 新项目需要建立策略框架
- 需要从历史数据冷启动策略库
- 新策略执行后需要沉淀效果数据
- 下游 skill 需要策略数据但库为空或不完整
- 需要对未覆盖策略进行效果拟合
- 拟合策略获得真实数据后需要验证替换

---

## 前置依赖

运行本 skill 前，检查以下文件是否存在：

- `{项目名}/wiki/metrics.md` — 指标体系定义
- `{项目名}/wiki/constraints.md` — 能力约束定义

**如不存在，不要生硬提示"请先运行XX skill"。** 应自然地向用户收集所需信息：
- 询问业务目标是什么、关注哪些指标、约束条件有哪些
- 询问是否有现成的项目文档或背景材料可以提供
- 收集到足够信息后，内部自动生成前置文件（经用户确认）
- 让用户体验到连贯的对话流程，而非被系统挡在门外

---

## 策略库的两层结构

### 第一层：策略框架

定义"一个策略由哪些要素组成"以及每个要素的可选值。

存储位置：`{项目名}/strategy-library/framework.md`

格式：

```markdown
## 策略要素维度

| 要素维度 | 可选值 | 说明 |
|---------|--------|------|
| {维度1} | {值1, 值2, 值3...} | {说明} |
| {维度2} | {值1, 值2, 值3...} | {说明} |
| ... | ... | ... |
```

**要素维度和可选值必须与用户沟通对齐确认。** 从 `constraints.md` 中的能力约束（差异化颗粒度、可选动作集）获取初始信息，再与用户确认完善。

### 第二层：策略效果

记录每个策略的执行效果数据。

存储位置：`{项目名}/strategy-library/strategies.csv`

CSV 列结构（根据项目指标体系动态生成）：

```
策略ID, {要素维度1}, {要素维度2}, ..., {要素维度N}, 执行开始时间, 执行结束时间, {目标指标}, {围栏指标1}, ..., {过程指标1}, ..., {环境指标1}, ..., 数据来源, 置信度
```

- **策略ID**：唯一标识
- **要素维度列**：该策略在每个维度上的具体值
- **指标列**：从 `metrics.md` 中读取所有指标，每个指标一列
- **执行时间**：策略实际执行的时间段
- **数据来源**：实测 / 拟合
- **置信度**：高（实测）/ 中（拟合-数据充分）/ 低（拟合-数据不足）

---

## 策略互斥关系

存储位置：`{项目名}/strategy-library/mutual-exclusion.md`

格式：

```markdown
## 互斥规则

| 规则ID | 互斥策略描述 | 互斥原因 | 约束表达 |
|--------|------------|---------|---------|
| 1 | {描述哪些策略不能同时选} | {原因} | {形式化表达，如 x_a + x_b <= 1} |
```

互斥关系必须在策略框架对齐阶段与用户确认。

---

## 工作流程

### 流程一：建立策略框架

```dot
digraph framework {
    "读取 constraints.md" [shape=box];
    "提取差异化维度和动作集" [shape=box];
    "与用户对齐策略要素" [shape=box];
    "用户确认?" [shape=diamond];
    "调整" [shape=box];
    "确认互斥关系" [shape=box];
    "写入 framework.md 和 mutual-exclusion.md" [shape=box];

    "读取 constraints.md" -> "提取差异化维度和动作集";
    "提取差异化维度和动作集" -> "与用户对齐策略要素";
    "与用户对齐策略要素" -> "用户确认?";
    "用户确认?" -> "调整" [label="否"];
    "调整" -> "用户确认?";
    "用户确认?" -> "确认互斥关系" [label="是"];
    "确认互斥关系" -> "写入 framework.md 和 mutual-exclusion.md";
}
```

### 流程二：冷启动填充

```dot
digraph coldstart {
    "用户提供历史数据" [shape=box];
    "读取 framework.md 和 metrics.md" [shape=box];
    "按策略框架结构解析数据" [shape=box];
    "提取策略条目" [shape=box];
    "展示给用户确认" [shape=box];
    "写入 strategies.csv" [shape=box];

    "用户提供历史数据" -> "读取 framework.md 和 metrics.md";
    "读取 framework.md 和 metrics.md" -> "按策略框架结构解析数据";
    "按策略框架结构解析数据" -> "提取策略条目";
    "提取策略条目" -> "展示给用户确认";
    "展示给用户确认" -> "写入 strategies.csv";
}
```

关键原则：
- 数据不全没关系，有多少填多少
- 尽量从数据中提取，避免口述
- 即使用户口述，也必须落成策略框架的结构化格式

### 流程三：增量沉淀

被触发时（用户要求或定期执行），将新策略及效果写入 strategies.csv：

1. 接收新策略执行数据
2. 按 framework.md 结构解析
3. 按 metrics.md 指标体系计算效果值（或调用效果评估 skill）
4. 展示给用户确认
5. 追加写入 strategies.csv

### 流程四：策略拟合

对策略框架中存在但 strategies.csv 中无记录的策略组合，进行效果预估：

1. 识别未覆盖的策略空间（框架中的可能组合 - 已有记录）
2. 找到相邻已知策略（要素值接近的策略）
3. 基于相邻策略效果进行插值/外推
4. 输出拟合效果值 + 置信度 + 拟合依据
5. 写入 strategies.csv，数据来源标记为"拟合"

相邻策略定义：在某个要素维度上值接近的策略。例如已知 20-25 岁和 30-35 岁效果，可拟合 25-30 岁效果。

### 流程五：验证替换

当拟合策略被实际执行后：

1. 用真实效果数据替换拟合预估值
2. 数据来源从"拟合"改为"实测"
3. 置信度更新为"高"
4. 记录拟合值与实测值的偏差（用于优化后续拟合精度）

---

## 数据格式约定

- 存储格式：CSV（UTF-8 BOM 编码，pandas 读取用 `encoding='utf-8-sig'`）
- 模型消费方式：Python 按需读取筛选后，转为 markdown 表格供 LLM 推理
- 人可用 Excel 打开查看和编辑

---

## 铁律

1. **策略框架必须与用户对齐确认**后才能进入数据收集阶段
2. **互斥关系必须与用户明确**
3. **所有写入操作需用户确认**
4. **不硬编码业务细节**：要素维度名称、指标名称全部从配置文件读取
