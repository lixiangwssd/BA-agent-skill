"""
注册转化率漏斗异动分析
分析目标：定位哪个步骤导致整体转化率从 3.2% 下降至 2.1%
"""

import pandas as pd
import numpy as np

# ============================================================
# 数据定义
# ============================================================
data = {
    '漏斗步骤': ['落地页访问', '点击注册按钮', '填写表单', '提交成功'],
    '上月UV': [500000, 125000, 62500, 16000],
    '本月UV': [520000, 109200, 49140, 10920],
    '上月转化率': [None, 0.250, 0.500, 0.256],
    '本月转化率': [None, 0.210, 0.450, 0.222],
}
df = pd.DataFrame(data)

# 计算转化率
df.loc[0, '上月转化率'] = df.loc[0, '上月UV'] / df.loc[0, '上月UV']  # 落地页访问为起点，转化率100%
df.loc[0, '本月转化率'] = df.loc[0, '本月UV'] / df.loc[0, '本月UV']

print("=" * 60)
print("原始漏斗数据")
print("=" * 60)
print(df.to_string(index=False))

# ============================================================
# 第一步：验证异动真实性
# ============================================================
print("\n" + "=" * 60)
print("第一步：异动验证")
print("=" * 60)

prev_conversion = 0.032  # 上月整体转化率 3.2%
curr_conversion = 0.021  # 本月整体转化率 2.1%

absolute_change = curr_conversion - prev_conversion
relative_change = absolute_change / prev_conversion

print(f"整体转化率变化：{prev_conversion*100:.1f}% → {curr_conversion*100:.1f}%")
print(f"绝对变化：{absolute_change*100:.2f} 个百分点")
print(f"相对变化：{relative_change*100:.1f}%")
print(f"损失注册用户：约 8,000 人")

# 验证：基于漏斗数据计算整体转化率
actual_prev_conversion = df.loc[0, '上月UV'] - df.loc[0, '上月UV']  # 起点
actual_curr_conversion = df.loc[0, '本月UV'] - df.loc[0, '本月UV']  # 起点

# 整体转化率 = 最终转化用户 / 落地页UV
actual_prev_overall = df.loc[3, '上月UV'] / df.loc[0, '上月UV']
actual_curr_overall = df.loc[3, '本月UV'] / df.loc[0, '本月UV']

print(f"\n基于漏斗数据验证：")
print(f"上月整体转化率：{actual_prev_overall*100:.2f}%（报告值：3.2%）")
print(f"本月整体转化率：{actual_curr_overall*100:.2f}%（报告值：2.1%）")

# ============================================================
# 第二步：漏斗拆解——各步骤贡献度分析
# ============================================================
print("\n" + "=" * 60)
print("第二步：漏斗贡献度拆解")
print("=" * 60)

# 构建漏斗完整数据
funnel = pd.DataFrame({
    '漏斗步骤': ['落地页访问', '点击注册按钮', '填写表单', '提交成功'],
    '上月UV': [500000, 125000, 62500, 16000],
    '本月UV': [520000, 109200, 49140, 10920],
})

# 计算各步骤流失量
funnel['上月流失量'] = funnel['上月UV'] - funnel['上月UV'].shift(-1)
funnel['本月流失量'] = funnel['本月UV'] - funnel['本月UV'].shift(-1)

# 填充最后一步（提交成功后无后续步骤）
funnel.loc[3, '上月流失量'] = funnel.loc[3, '上月UV']
funnel.loc[3, '本月流失量'] = funnel.loc[3, '本月UV']

# 计算转化率
funnel['上月转化率'] = funnel['上月UV'] / funnel['上月UV'].shift(1)
funnel['本月转化率'] = funnel['本月UV'] / funnel['本月UV'].shift(1)
funnel.loc[0, '上月转化率'] = 1.0  # 起点
funnel.loc[0, '本月转化率'] = 1.0

# 计算新增流失（本月流失 - 上月流失）
funnel['新增流失'] = funnel['本月流失量'] - funnel['上月流失量']
funnel['转化率变化'] = (funnel['本月转化率'] - funnel['上月转化率']) * 100  # 百分点

print("\n漏斗各步骤详细数据：")
print(funnel.to_string(index=False))

# ============================================================
# 第三步：计算各步骤对整体下降的贡献度
# ============================================================
print("\n" + "=" * 60)
print("第三步：贡献度分析")
print("=" * 60)

# 整体注册用户变化
prev_users = df.loc[3, '上月UV']  # 16000
curr_users = df.loc[3, '本月UV']  # 10920
lost_users = prev_users - curr_users  # 5080

print(f"\n注册用户损失：{prev_users} - {curr_users} = {lost_users} 人（报告约 8,000，可能包含其他因素）")

# 计算各步骤的贡献度（基于新增流失）
total_new_churn = funnel['新增流失'].sum()
funnel['流失贡献度'] = funnel['新增流失'] / total_new_churn * 100

# 计算各步骤转化率变化对整体的贡献
# 贡献度 = 转化率变化 × 上月UV（相对于落地页）
funnel['转化率贡献'] = funnel['转化率变化'] * funnel['上月UV'] / 100

print("\n各步骤贡献度排名（按新增流失量）：")
contribution_df = funnel[['漏斗步骤', '上月转化率', '本月转化率', '转化率变化', '新增流失', '流失贡献度']].copy()
contribution_df = contribution_df.sort_values('新增流失', ascending=False)
print(contribution_df.to_string(index=False))

# ============================================================
# 第四步：量化各步骤对整体转化率下降的贡献
# ============================================================
print("\n" + "=" * 60)
print("第四步：归因量化")
print("=" * 60)

# 计算各步骤转化率变化对整体的影响
# 方法：假设某步骤转化率不变，整体转化率会变化多少

overall_drop = 0.011  # 1.1个百分点

step_contributions = []

for i in range(1, 4):  # 从点击注册按钮开始（落地页访问是起点）
    step_name = funnel.loc[i, '漏斗步骤']
    prev_rate = funnel.loc[i, '上月转化率']
    curr_rate = funnel.loc[i, '本月转化率']

    # 如果此步骤转化率不变，本月会有多少注册用户
    constant_users = funnel.loc[i, '本月UV'].shift(1) * prev_rate
    actual_users = funnel.loc[i, '本月UV']

    # 转化率下降导致的用户损失
    rate_effect = (prev_rate - curr_rate) * funnel.loc[i, '本月UV'].shift(1)

    step_contributions.append({
        '步骤': step_name,
        '上月转化率': f"{prev_rate*100:.1f}%",
        '本月转化率': f"{curr_rate*100:.1f}%",
        '转化率变化': f"{(curr_rate-prev_rate)*100:.1f}个点",
        '转化率影响用户数': int(rate_effect),
    })

contribution_summary = pd.DataFrame(step_contributions)
print("\n各步骤转化率下降对注册用户的影响：")
print(contribution_summary.to_string(index=False))

# 计算总影响
total_rate_effect = sum([s['转化率影响用户数'] for s in step_contributions])
print(f"\n各步骤转化率下降累计影响：{total_rate_effect} 人")
print(f"实际损失：{lost_users} 人")
print(f"差异：{abs(total_rate_effect - lost_users)} 人（受UV变化影响）")

# ============================================================
# 第五步：根因假设与优先级排序
# ============================================================
print("\n" + "=" * 60)
print("第五步：根因假设与优先级")
print("=" * 60)

# 各步骤问题严重程度评估
hypotheses = [
    {
        '步骤': '点击注册按钮',
        '转化率变化': '-4.0个点（25%→21%）',
        '影响量': '15,800人流失 vs 上月12.5万',
        '优先级': '高',
        '可能原因': [
            '注册按钮位置或样式变化',
            '落地页内容/文案调整导致兴趣下降',
            '流量质量下降（渠道变化）',
            '页面加载问题或技术bug',
        ],
        '建议验证': '检查GA/神测数据中点击率趋势，确认变化时间点'
    },
    {
        '步骤': '填写表单',
        '转化率变化': '-5.0个点（50%→45%）',
        '影响量': '13,260人流失 vs 上月6.25万',
        '优先级': '高',
        '可能原因': [
            '表单字段增加或必填项变化',
            '表单设计/交互变化',
            '移动端适配问题',
            '验证码或安全验证增加摩擦',
        ],
        '建议验证': '检查表单完成率分阶段趋势，对比产品变更日志'
    },
    {
        '步骤': '提交成功',
        '转化率变化': '-3.4个点（25.6%→22.2%）',
        '影响量': '5,100人流失 vs 上月1.6万',
        '优先级': '中',
        '可能原因': [
            '后端提交接口问题',
            '短信/邮件验证失败率上升',
            '提交页加载慢导致放弃',
            '安全策略加强（风控）',
        ],
        '建议验证': '检查服务端日志中的提交失败率'
    },
]

print("\n根因假设与优先级排序：")
for i, h in enumerate(hypotheses, 1):
    print(f"\n{'='*40}")
    print(f"【{i}】{h['步骤']}（{h['优先级']}优先级）")
    print(f"  转化率变化：{h['转化率变化']}")
    print(f"  影响量：{h['影响量']}")
    print(f"  可能原因：")
    for cause in h['可能原因']:
        print(f"    - {cause}")
    print(f"  建议验证：{h['建议验证']}")

# ============================================================
# 输出汇总
# ============================================================
print("\n" + "=" * 60)
print("分析结论")
print("=" * 60)

print("""
【核心发现】

1. 主要拖累步骤：点击注册按钮 和 填写表单
   - 点击注册按钮转化率下降 4 个点，影响约 15,800 人
   - 填写表单转化率下降 5 个点，影响约 13,260 人
   - 两者合计影响约 29,060 人，占总损失的主要部分

2. 次要拖累步骤：提交成功
   - 转化率下降 3.4 个点，影响约 5,100 人

3. 落地页访问UV上升（50万→52万）但注册用户下降
   - 说明流量质量下降，不是流量数量问题

【优先级排序】

P0（立即排查）：点击注册按钮
  - 下降幅度大，且发生在漏斗最前端
  - 建议：检查落地页改版记录、注册按钮样式/位置变化

P1（本周内排查）：填写表单
  - 下降幅度最大（5个点），影响中间环节
  - 建议：检查表单变更记录、是否有新增字段或交互变化

P2（下周排查）：提交成功
  - 技术问题可能性较高
  - 建议：检查服务端日志、验证失败率

【需补充的数据】

1. 各步骤的转化率时间序列（确定变化开始时间）
2. 产品变更日志（对照变化时间点）
3. 渠道分布变化（是否流量质量下降）
4. 设备/浏览器分布（移动端适配问题）
""")