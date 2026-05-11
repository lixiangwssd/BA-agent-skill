# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

指标异动归因分析 Skill 开发仓库，包含两个平台版本的同一分析技能：

- `.claude/skills/metric-anomaly-analysis/` — Claude Code 平台 Skill（SKILL.md + evals）
- `metric-anomaly-attribution/` — 跨平台版本（OpenAI agents YAML 配置 + 方法论参考文档）

两个版本实现相同的核心能力：判断指标异动、按维度拆解贡献度、归因业务原因，但 Skill 定义格式和输出结构不同。

## 技能评测

评测文件位于 `.claude/skills/metric-anomaly-analysis/evals/evals.json`，包含 3 个测试场景：
1. GMV 渠道拆解分析
2. 注册转化率漏斗分析
3. 预算 vs 实际差异分析（CFO 汇报）

评测工作空间在 `.claude/skills/metric-anomaly-analysis-workspace/`，按 `iteration-N/场景名/with_skill|without_skill/outputs/` 组织。每次评测输出包含 `analysis.py`（分析代码）和 `report.md`（报告）。

运行评测使用 `skill-creator` 技能（通过 `skills-lock.json` 从 `anthropics/skills` 安装）。

## 关键约定

- 所有文档、分析报告使用**中文**
- CSV 数据文件用 UTF-8 BOM 编码，pandas 读取时用 `encoding='utf-8-sig'`
- Skill 输出必须包含两个文件：可执行的 Python 分析代码 + 结构化 Markdown 报告
- 数值计算必须用 Python 脚本，禁止心算
- `metric-anomaly-attribution/references/anomaly-methodology.md` 是方法论参考文档，修改 Skill 逻辑时应同步更新

## 双版本对应关系

| Claude Code 版本 | 跨平台版本 |
|-----------------|-----------|
| `.claude/skills/metric-anomaly-analysis/SKILL.md` | `metric-anomaly-attribution/SKILL.md` |
| evals.json 中的 assertions | 跨平台版本无独立评测 |
| 六步分析框架（理解→接入→框架→假设→可视化→报告） | 四步工作流（验证→拆解→归因→输出） |
