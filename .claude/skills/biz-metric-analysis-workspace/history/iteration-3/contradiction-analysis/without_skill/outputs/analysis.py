"""
DAU下降但留存上升的矛盾现象分析
===================================
数据：
  - DAU: 下降 10%
  - 新增用户: 下降 15%
  - 活跃用户: 下降 8%
  - 流失用户: 增加 12%
  - 留存率: 上升 5%
背景：上周做了版本更新

分析目标：解释矛盾现象，给出假设验证方案
"""

import pandas as pd
import numpy as np

# ============================================================
# 第一部分：构建数据模型验证矛盾现象
# ============================================================

print("=" * 60)
print("DAU下降但留存上升 - 矛盾现象分析")
print("=" * 60)

# 设定基准数据（用于推导）
# 设上周数据为基准
base = {
    'new_users': 1000,      # 新增用户
    'active_users': 5000,   # 活跃用户
    'churned_users': 800,   # 流失用户
    'dau': 5800,            # DAU = 新增 + 活跃（简化模型）
}

# 本周变化后的数据
current = {
    'new_users': base['new_users'] * 0.85,      # 下降15%
    'active_users': base['active_users'] * 0.92, # 下降8%
    'churned_users': base['churned_users'] * 1.12, # 增加12%
}

# 重新计算 DAU
current['dau'] = current['new_users'] + current['active_users']

# 计算留存率
# 留存率 = 活跃用户 / (新增用户 + 活跃用户) - 简化模型
# 实际留存率定义更复杂，这里用简化模型说明

base_retention_rate = base['active_users'] / (base['new_users'] + base['active_users'])
current_retention_rate = current['active_users'] / (current['new_users'] + current['active_users'])

print("\n【数据重建验证】")
print(f"基准 DAU: {base['dau']:.0f}")
print(f"当前 DAU: {current['dau']:.0f}")
print(f"DAU 变化: {(current['dau']/base['dau']-1)*100:.1f}%")

print(f"\n基准留存率: {base_retention_rate:.2%}")
print(f"当前留存率: {current_retention_rate:.2%}")
print(f"留存率变化: {(current_retention_rate/base_retention_rate-1)*100:.1f}%")

# ============================================================
# 第二部分：数学拆解 - 理解矛盾根源
# ============================================================

print("\n" + "=" * 60)
print("矛盾现象数学拆解")
print("=" * 60)

# DAU 下降但留存上升的数学关系
# DAU = 新用户 + 老用户（活跃）
# 留存率 = 活跃用户 / (新用户 + 活跃用户)

# 关键洞察：分母（总用户池）下降更快时，留存率上升
# 当 new_users 下降幅度 > active_users 下降幅度 时

change_rates = {
    'new_users': (current['new_users']/base['new_users'] - 1) * 100,
    'active_users': (current['active_users']/base['active_users'] - 1) * 100,
    'dau': (current['dau']/base['dau'] - 1) * 100,
}

print("\n变化率汇总:")
for k, v in change_rates.items():
    print(f"  {k}: {v:+.1f}%")

# 留存率变化的精确分解
# 留存率 = 活跃用户 / (活跃用户 + 新增用户)
# 留存率变化取决于: 活跃用户变化 vs 新增用户变化

print("\n【关键发现】")
print(f"新增用户下降 {-change_rates['new_users']:.1f}% > 活跃用户下降 {-change_rates['active_users']:.1f}%")
print("→ 分母（新增用户）下降更快，导致留存率被动抬升")
print("→ 这是'幸存者偏差'效应的数学体现")

# ============================================================
# 第三部分：列出可能的共同原因假设
# ============================================================

print("\n" + "=" * 60)
print("DAU下降但留存上升的共同原因假设")
print("=" * 60)

hypotheses = [
    {
        'id': 'H1',
        'name': '版本更新筛选了低价值用户',
        'mechanism': '新版本对低活跃/低留存用户产生排斥，导致其流失',
        'prediction': '流失用户中低留存特征用户占比高',
        'verification': '对比流失用户在版本更新前后的行为特征差异'
    },
    {
        'id': 'H2',
        'name': '版本更新提升了核心用户体验',
        'mechanism': '功能优化使活跃用户使用深度增加，留存率上升',
        'prediction': '人均使用时长/核心功能使用率上升',
        'verification': '对比版本更新前后用户行为埋点数据'
    },
    {
        'id': 'H3',
        'name': '新增渠道质量下降',
        'mechanism': '新增用户来源变化，新用户质量（留存潜力）下降',
        'prediction': '新增用户的次日留存率下降',
        'verification': '按渠道拆分新增用户的留存率'
    },
    {
        'id': 'H4',
        'name': '产品周期效应',
        'mechanism': '版本更新在周中，低活跃老用户自然流失',
        'prediction': '流失集中在特定用户群（最后活跃在更新前）',
        'verification': '分析流失用户的最后活跃时间分布'
    },
    {
        'id': 'H5',
        'name': '推送/触达策略变化',
        'mechanism': '沉默用户被重新激活的触达减少，误判为流失',
        'prediction': '部分"流失用户"实际是沉默用户',
        'verification': '检查推送打开率和沉默用户召回率'
    }
]

for h in hypotheses:
    print(f"\n假设 {h['id']}: {h['name']}")
    print(f"  机制: {h['mechanism']}")
    print(f"  预测: {h['prediction']}")
    print(f"  验证: {h['verification']}")

# ============================================================
# 第四部分：假设验证方案
# ============================================================

print("\n" + "=" * 60)
print("假设验证方案")
print("=" * 60)

verification_plan = [
    {
        'step': 1,
        'action': '用户分群留存分析',
        'method': '按用户最后活跃时间/历史留存率分层，对比各层在版本更新前后的变化',
        'expected': '低历史留存用户流失更多'
    },
    {
        'step': 2,
        'action': '版本前后行为对比',
        'method': '对比更新前后活跃用户的人均时长、核心功能点击数',
        'expected': '若H2成立，核心用户使用深度上升'
    },
    {
        'step': 3,
        'action': '新增用户质量追踪',
        'method': '按新增日期追踪新增用户的次日/7日留存',
        'expected': '若H3成立，新增用户留存率下降'
    },
    {
        'step': 4,
        'action': '流失用户特征分析',
        'method': '画像分析：设备、渠道、首次活跃日期、历史LTV',
        'expected': '识别流失用户群体特征'
    },
    {
        'step': 5,
        'action': 'A/B测试验证（如有）',
        'method': '对比升级vs未升级用户群的关键指标',
        'expected': '因果验证"
    }
]

for v in verification_plan:
    print(f"\n步骤 {v['step']}: {v['action']}")
    print(f"  方法: {v['method']}")
    print(f"  预期: {v['expected']}")

# ============================================================
# 第五部分：结论与建议
# ============================================================

print("\n" + "=" * 60)
print("结论与建议")
print("=" * 60)

conclusions = """
【现象解释】
DAU下降10%但留存率上升5%并不矛盾，核心原因是：
- 新增用户下降15%，分母缩小
- 留存率被动抬升（数学效应）
- 实际是"幸存老用户"撑高了留存率分子

【最可能原因】（需数据验证）
1. 版本更新导致低价值用户流失（净 positive）
2. 核心用户体验改善，留存率真实提升
3. 两者叠加

【建议行动】
1. 立即：拆分新增/老用户的留存率，避免混合均值陷阱
2. 本周：完成假设验证，确定是净化效应还是真实提升
3. 下周：基于结论决策是否加强版本更新策略

【风险提示】
若不验证直接解读，可能误判为"产品变好"，忽略用户流失风险。
"""

print(conclusions)

# ============================================================
# 第六部分：输出结构化结论（供报告使用）
# ============================================================

summary = {
    'phenomenon': 'DAU下降但留存率上升',
    'root_cause': '新增用户下降 > 活跃用户下降，分母效应 + 可能的净化效应',
    'hypotheses': [h['id'] for h in hypotheses],
    'verification_priority': ['H1', 'H2', 'H3'],
    'recommendation': '拆分用户群验证，确认是正向净化还是负向流失'
}

print("\n【结构化摘要】")
print(summary)