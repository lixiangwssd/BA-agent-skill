# CLAUDE.md

## 项目概述

这是一个策略优化项目的工作目录。使用策略优化 Skill 体系（5 个 Skill）来完成投放/补贴等场景的策略制定与优化。

### 目录结构

```
{项目根目录}/
├── CLAUDE.md               ← 本文件（全局指令）
├── data/                   ← 原始数据文件
├── wiki/                   ← 业务背景对齐产出
│   ├── index.md
│   ├── overview.md
│   ├── metrics.md
│   ├── constraints.md
│   ├── strategic-direction.md
│   └── log.md
├── strategy-library/       ← 策略库
│   ├── framework.md
│   ├── strategies.csv
│   └── mutual-exclusion.md
└── outputs/                ← 策略优化/挖掘输出
```

---

## Skill 链式调用协议

当 Skill A 因缺少前置依赖而调用 Skill B 时，**必须严格遵守以下规则**：

### 规则

1. **记录调用栈**：进入子 Skill 前，明确告知用户当前链路，例如："策略优化 → 需要先完成业务背景对齐"
2. **子 Skill 完成后必须回到父 Skill**：子 Skill 执行完毕后，**必须重新 invoke 父 Skill**（而非自行继续父 Skill 的后续逻辑）。这确保父 Skill 的完整流程被再次加载和遵循
3. **逐层返回**：如果存在多层调用（A → B → C），C 完成后先回到 B，B 完成后再回到 A
4. **不跳过中间环节**：即使你认为中间步骤已满足，仍需重新 invoke 对应 skill 让其自行验证

### 调用链示意

```
用户请求 → Skill(strategy-optimization)
  发现缺 wiki/ → Skill(business-context-alignment)
    完成 → 重新 invoke Skill(strategy-optimization)
      发现缺 strategy-library/ → Skill(strategy-library)
        完成 → 重新 invoke Skill(strategy-optimization)
          前置齐全 → 执行优化求解 → 输出
```

### 禁止行为

- ❌ 子 Skill 完成后直接"裸写"后续逻辑（不经 skill 指导）
- ❌ 跳过 re-invoke 直接进入下一阶段
- ❌ 在一个 Skill 内部直接执行另一个 Skill 的全部逻辑而不通过 Skill tool 调用

---

## 通用铁律

1. **所有 wiki/策略库内容的创建和修改，必须经用户确认**
2. **数值计算必须用 Python 脚本**，禁止心算或估算
3. **CSV 文件使用 UTF-8 BOM 编码**，pandas 读取时用 `encoding='utf-8-sig'`
4. **不硬编码业务细节**：指标名称、维度名称全部从 wiki/ 配置文件读取
5. **信息不足必须追问**：不能跳步或假设

---

## 环境

- Python 3 可用（pandas、matplotlib、pulp 等已安装或可安装）
- 数据文件位于 `data/` 目录
- 所有输出文件写入项目根目录对应子目录，不写到其他位置
