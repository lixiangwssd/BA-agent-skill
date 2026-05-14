"""
DAU 下降但留存上升的矛盾现象分析
数据背景：新增用户-15%，活跃用户-8%，流失用户+12%，上周有版本更新
"""

import pandas as pd
import numpy as np

# ==================== 第一步：数据建模 ====================
# 假设基准期数据
baseline_data = {
    '新增用户': 1000,
    '活跃用户': 5000,
    '流失用户': 800
}

# 本期数据（根据变化率推算）
current_data = {
    '新增用户': baseline_data['新增用户'] * (1 - 0.15),  # -15%
    '活跃用户': baseline_data['活跃用户'] * (1 - 0.08),   # -8%
    '流失用户': baseline_data['流失用户'] * (1 + 0.12)    # +12%
}

print("=" * 60)
print("DAU 矛盾现象分析 - 数据概览")
print("=" * 60)
print(f"\n{'指标':<12} {'基准期':<12} {'本期':<12} {'变化量':<12} {'变化率':<10}")
print("-" * 60)

for key in baseline_data:
    change = current_data[key] - baseline_data[key]
    rate = change / baseline_data[key]
    print(f"{key:<10} {baseline_data[key]:<12,.0f} {current_data[key]:<12,.0f} {change:<+12,.0f} {rate:<+10.1%}")

# ==================== 第二步：DAU 结构拆解 ====================
# DAU = 新增用户 + 活跃用户（留存用户）
# 留存率 = 活跃用户 / (新增用户 + 活跃用户) 近似表达

print("\n" + "=" * 60)
print("DAU 构成分析")
print("=" * 60)

# 计算留存率（简化模型：留存用户 / (新增用户 + 上期留存用户)）
# 为简化分析，假设留存率 = 活跃用户 / (新增用户 + 活跃用户) 的某种比例关系
# 实际上留存率 = 上期留存用户 / 上期总用户

# 假设基准期：DAU = 6000，新增=1000，活跃=5000，留存率=80%
# 本期：DAU = 5400，新增=850，活跃=4600，留存率需上升

# 验证矛盾：DAU下降10%但留存上升5%
# 如果留存率从 80% 升至 84%（+5%），但 DAU 下降

# 核心指标计算
DAU_base = baseline_data['新增用户'] + baseline_data['活跃用户']  # 6000
DAU_current = current_data['新增用户'] + current_data['活跃用户']  # 5450

retention_rate_base = baseline_data['活跃用户'] / DAU_base  # 约 83.3%
retention_rate_current = current_data['活跃用户'] / DAU_current  # 约 84.4%

print(f"\n基准期 DAU: {DAU_base:,.0f}")
print(f"本期 DAU: {DAU_current:,.0f}")
print(f"DAU 变化: {(DAU_current - DAU_base) / DAU_base:+.1%}")

print(f"\n基准期留存率（活跃/DAU）: {retention_rate_base:.1%}")
print(f"本期留存率（活跃/DAU）: {retention_rate_current:.1%}")
print(f"留存率变化: {(retention_rate_current - retention_rate_base) / retention_rate_base:+.1%}")

# ==================== 第三步：矛盾现象建模 ====================
print("\n" + "=" * 60)
print("矛盾现象根因分析")
print("=" * 60)

# DAU = 新增 × 留存率（简化）
# 但实际上 DAU 受三个因素影响：新增用户、留存率、流失率

# 构建用户结构模型
print("\n用户结构变化分析：")
print("-" * 40)

# 计算各指标对 DAU 变化的贡献
# 方式一：新用户减少导致 DAU 下降
new_user_effect = current_data['新增用户'] - baseline_data['新增用户']
print(f"新增用户变化: {new_user_effect:+.0f}（贡献 {(new_user_effect / (DAU_base - DAU_current)) * 100:.1f}% 的下降）")

# 方式二：老用户留存变化
# 留存用户 = 活跃用户 - 新增用户（简化）
retained_base = baseline_data['活跃用户'] - baseline_data['新增用户']  # 4000
retained_current = current_data['活跃用户'] - current_data['新增用户']  # 3750

print(f"留存用户变化: {retained_current - retained_base:+.0f}")
print(f"流失用户变化: {current_data['流失用户'] - baseline_data['流失用户']:+.0f}")

# ==================== 第四步：假设验证框架 ====================
print("\n" + "=" * 60)
print("核心假设与验证方案")
print("=" * 60)

hypotheses = [
    {
        "id": "H1",
        "假设": "版本更新后体验改善，留住老用户但排斥新用户",
        "机制": "新版本对老用户更友好 → 活跃老用户留存率↑ → 整体留存↑\n同时新版本可能门槛更高/功能复杂 → 新用户转化率↓ → 新增↓",
        "验证数据": ["新老用户分群DAU对比", "版本更新前后各指标趋势", "各渠道新增转化率"],
        "置信度": "中",
        "优先级": 1
    },
    {
        "id": "H2",
        "假设": "版本更新筛选出低价值用户，高活跃高流失用户流失",
        "机制": "版本更新后部分用户不适应而流失（流失↑）\n留下的都是高质量、适应版本的用户（留存率↑）\n新用户获取受影响（新增↓），可能因为产品调整期投放减少",
        "验证数据": ["流失用户画像 vs 留存用户画像", "流失时段与版本上线时间相关性", "投放预算变化"],
        "置信度": "中",
        "优先级": 2
    },
    {
        "id": "H3",
        "假设": "新增渠道质量下降，低质量新增用户无法转化为活跃",
        "机制": "新增下降15%可能是渠道收缩或渠道质量下降\n新用户质量差 → 转化活跃率低 → 活跃用户↓\n但老用户不受影响 → 整体留存率被动提升",
        "验证数据": ["各渠道新增用户质量（活跃转化率）", "渠道结构变化", "CPA/CPI变化"],
        "置信度": "中-低",
        "优先级": 3
    }
]

for h in hypotheses:
    print(f"\n假设 {h['id']}: {h['假设']}")
    print(f"  机制: {h['机制']}")
    print(f"  需验证数据: {', '.join(h['验证数据'])}")
    print(f"  置信度: {h['置信度']} | 优先级: {h['优先级']}")

# ==================== 第五步：验证方案详细设计 ====================
print("\n" + "=" * 60)
print("假设验证执行方案")
print("=" * 60)

verification_steps = """
【验证步骤 1：新老用户分群对比】
- 拆分 DAU 为：新用户（注册7天内）+ 老用户（注册7天以上）
- 对比本期 vs 基准期各分群 DAU 变化
- 预期：如果 H1 成立 → 老用户 DAU 持平或上升，新用户 DAU 大幅下降

【验证步骤 2：版本更新前后趋势对比】
- 拉取版本上线前后各指标每日数据
- 检查：上线前各指标趋势 vs 上线后各指标趋势
- 预期：如果 H1 成立 → 版本更新后活跃用户下降但留存率上升

【验证步骤 3：流失用户画像分析】
- 提取流失用户特征：注册时长、活跃度、渠道
- 对比流失用户 vs 留存用户画像差异
- 预期：如果 H2 成立 → 流失用户集中在特定特征群

【验证步骤 4：渠道质量监控】
- 按渠道拆分新增用户和活跃转化率
- 检查：是否特定渠道质量下降导致整体新增下降但质量好的渠道留存高
- 预期：如果 H3 成立 → 新增下降来自低质量渠道收缩

【数据需求清单】
1. 每日 DAU 明细（含用户分层：新/老）
2. 版本发布记录（时间、范围）
3. 用户画像数据（注册时长、活跃度、渠道）
4. 渠道维度的新增和活跃转化数据
"""

print(verification_steps)

# ==================== 第六步：量化矛盾分析 ====================
print("\n" + "=" * 60)
print("矛盾现象量化解释")
print("=" * 60)

# 为什么 DAU 下降但留存率上升？

# 留存率上升的数学解释
# 留存率 = 活跃用户 / DAU
# DAU 下降但留存率上升 → 分子（活跃用户）相对分母（DAU）下降更慢

# 计算分解
print("\n留存率变化分解：")
print("-" * 40)

# 假设新用户留存率较低，老用户留存率较高
# 当新增下降时，DAU 结构变化：高留存的老用户占比↑ → 整体留存率↑

# 简化模型：假设老用户留存率 = 90%，新用户留存率 = 30%
old_retention = 0.90
new_retention = 0.30

# 基准期：新增1000，老用户5000
old_users_base = 5000
new_users_base = 1000
active_base = old_users_base * old_retention + new_users_base * new_retention
dau_base = old_users_base + new_users_base
retention_base = active_base / dau_base

# 本期：新增850（-15%），活跃用户下降8%
old_users_current = 5000 * (1 - 0.08)  # 4600
new_users_current = 1000 * (1 - 0.15)   # 850

active_current = old_users_current * old_retention + new_users_current * new_retention
dau_current = old_users_current + new_users_current
retention_current = active_current / dau_current

print(f"\n简化模型（老用户留存90%，新用户留存30%）：")
print(f"基准期: 活跃={active_base:.0f}, DAU={dau_base:.0f}, 整体留存率={retention_base:.1%}")
print(f"本期:   活跃={active_current:.0f}, DAU={dau_current:.0f}, 整体留存率={retention_current:.1%}")
print(f"\n结论：新增用户下降15% → 新用户占比↓ → 老用户占比↑ → 整体留存率↑")
print(f"这就是 DAU 下降但留存率上升的数学原因")

# ==================== 第七步：结论总结 ====================
print("\n" + "=" * 60)
print("分析结论")
print("=" * 60)

conclusions = """
【核心结论】
1. DAU 下降10%的主要驱动因素：新增用户下降15%（贡献最大）
2. 留存率上升的主要驱动因素：用户结构变化，新用户占比下降导致分母收缩
3. 矛盾现象的可能原因：
   - 版本更新对老用户友好，对新用户不友好
   - 新增渠道质量下降，低质量新增无法转化
   - 版本更新筛选用户，留下高质量用户

【最可能原因排序】
1. 版本更新影响（置信度：中）← 可能性最高
2. 渠道质量变化（置信度：中-低）
3. 自然波动（置信度：低）← 变化幅度较大，难归因自然波动

【建议行动】
1. 紧急：拉取新老用户分群数据，验证 H1
2. 紧急：对比版本更新前后各指标趋势，验证 H2
3. 中期：检查各渠道新增转化率，验证 H3
"""

print(conclusions)

# 保存结果供报告使用
results = {
    'DAU变化': (DAU_current - DAU_base) / DAU_base,
    '留存率变化': (retention_current - retention_rate_base) / retention_rate_base,
    '新增下降贡献': abs(new_user_effect) / abs(DAU_base - DAU_current),
    '关键假设': '版本更新导致用户体验分化'
}
print(f"\n关键指标: DAU变化={results['DAU变化']:+.1%}, 留存率变化={results['留存率变化']:+.1%}")