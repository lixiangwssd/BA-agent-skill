# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

指标异动归因分析 Skill 开发仓库。包含三个 Skill 版本实现相同的核心能力：判断指标异动、按维度拆解贡献度、归因业务原因。

| 版本 | 路径 | 平台 | 分析框架 |
|------|------|------|---------|
| metric-anomaly-analysis | `.claude/skills/metric-anomaly-analysis/` | Claude Code | 六步（理解→接入→框架→假设→可视化→报告） |
| biz-metric-analysis | `.claude/skills/biz-metric-analysis/` | Claude Code | 七步（明确→验证→接入→拆解→归因→可视化→报告） |
| metric-anomaly-attribution | `metric-anomaly-attribution/` | OpenAI agents（YAML） | 四步（验证→拆解→归因→输出） |

`biz-metric-analysis` 是 `metric-anomaly-analysis` 的迭代升级版，增加了异动验证环节、更完整的触发/不触发条件定义，以及 trigger-eval。

## 技能评测

运行评测使用 `skill-creator` 技能（通过 `skills-lock.json` 从 `anthropics/skills` 安装，缓存在 `.agents/skills/skill-creator/`）。

### metric-anomaly-analysis

- 评测定义：`.claude/skills/metric-anomaly-analysis/evals/evals.json`（3 个场景）
- 评测工作空间：`.claude/skills/metric-anomaly-analysis-workspace/`

### biz-metric-analysis

- 评测定义：`.claude/skills/biz-metric-analysis/evals/evals.json`（4 个场景，含 CPA 归因）
- 触发评测：`.claude/skills/biz-metric-analysis-workspace/trigger-eval.json`（19 条触发/不触发用例）
- 评测工作空间：`.claude/skills/biz-metric-analysis-workspace/`

### 评测输出结构

```
workspace/iteration-N/场景名/{with_skill,without_skill}/
├── outputs/
│   ├── analysis.py    # 可执行的 Python 分析代码
│   └── report.md      # 结构化 Markdown 分析报告
├── grading.json       # 各 assertion 评分结果
└── timing.json        # 执行耗时
```

`iteration-N/benchmark.json` 汇总该轮各场景评分，`eval-review.html` 是可视化评审页面。

## 关键约定

- 所有文档、分析报告使用**中文**
- CSV 数据文件用 UTF-8 BOM 编码，pandas 读取时用 `encoding='utf-8-sig'`
- Skill 输出必须包含两个文件：可执行的 Python 分析代码（`analysis.py`）+ 结构化 Markdown 报告（`report.md`）
- 数值计算必须用 Python 脚本，禁止心算
- 修改 Skill 分析逻辑时应同步更新对应的方法论参考文档：
  - `biz-metric-analysis` → `.claude/skills/biz-metric-analysis/references/methodology.md`
  - `metric-anomaly-attribution` → `metric-anomaly-attribution/references/anomaly-methodology.md`

## 方法论参考文档

两份方法论文档内容一致，覆盖：异动验证（Z-score/IQR）、贡献度拆解公式（加总型/乘法模型/比率型/漏斗型）、业务归因框架、常见误区、输出模板。修改分析方法时以这两份文档为规范来源。

## 常用命令

### 运行技能评测
```bash
# 使用 skill-creator 技能运行评测
# 在 Claude Code 中调用 /skill-creator 并选择 "Run evals"
```

### 评测输出结构
每次评测产生 `iteration-N` 目录，结构如下：
```
workspace/iteration-N/场景名/{with_skill,without_skill}/
├── outputs/
│   ├── analysis.py    # 可执行的 Python 分析代码
│   └── report.md      # 结构化 Markdown 分析报告
├── grading.json       # 各 assertion 评分结果
└── timing.json        # 执行耗时
```

### 数据文件编码
- CSV 文件使用 UTF-8 BOM 编码
- pandas 读取：`pd.read_csv(path, encoding='utf-8-sig')`
