"""
注册转化率漏斗分析
分析目标：定位注册转化率从 3.2% 下降至 2.1% 的根因步骤
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
    '上月转化率': [None, 0.25, 0.50, 0.256],
    '本月转化率': [None, 0.21, 0.45, 0.222],
}
df = pd.DataFrame(data)

# 计算漏斗各步骤的转化率（基于UV计算）
df['上月转化率_calc'] = df['上月UV'] / df['上月UV'].shift(1)
df['本月转化率_calc'] = df['本月UV'] / df['本月UV'].shift(1)

# ============================================================
# 第一步：验证异动真实性
# ============================================================
print("=" * 60)
print("一、异动验证")
print("=" * 60)

overall_conversion_last = df['上月UV'].iloc[-1] / df['上月UV'].iloc[0]
overall_conversion_current = df['本月UV'].iloc[-1] / df['本月UV'].iloc[0]

print(f"上月整体注册转化率: {overall_conversion_last:.2%}")
print(f"本月整体注册转化率: {overall_conversion_current:.2%}")
print(f"变化幅度: {(overall_conversion_current - overall_conversion_last):.2%} ({(overall_conversion_current - overall_conversion_last) * 100:.1f}个百分点)")

# 用户提供的数字验证
print(f"\n用户反馈：整体下降 1.1 个百分点 ({(overall_conversion_current - overall_conversion_last) * 100:.1f}个百分点) ✓")
print(f"损失注册用户数：{df['本月UV'].iloc[-1] - df['上月UV'].iloc[-1]:,} (实际差值)")

# ============================================================
# 第二步：漏斗贡献度拆解
# ============================================================
print("\n" + "=" * 60)
print("二、漏斗各步骤贡献度拆解")
print("=" * 60)

# 计算各步骤转化率
step_conversion = df.copy()
step_conversion['上月转化率'] = step_conversion['上月UV'] / step_conversion['上月UV'].shift(1)
step_conversion['本月转化率'] = step_conversion['本月UV'] / step_conversion['本月UV'].shift(1)
step_conversion = step_conversion.iloc[1:]  # 去掉第一行（无上一步）

# 计算流失量
step_conversion['上月流失量'] = step_conversion['上月UV'] - step_conversion['上月UV'].shift(-1)
step_conversion['本月流失量'] = step_conversion['本月UV'] - step_conversion['本月UV'].shift(-1)

# 计算新增流失（本月流失 - 上月流失，正值表示流失加剧）
step_conversion['新增流失'] = step_conversion['本月流失量'] - step_conversion['上月流失量']
step_conversion['转化率变化'] = step_conversion['本月转化率'] - step_conversion['上月转化率']

# 计算各步骤对整体转化率下降的贡献
# 贡献度 = 各步骤新增流失 / 总流失增量（绝对值）
total_incremental_loss = step_conversion['新增流失'].sum()
step_conversion['贡献度'] = step_conversion['新增流失'] / abs(total_incremental_loss)

print("\n漏斗各步骤详细数据：")
print(step_conversion[['漏斗步骤', '上月UV', '本月UV', '上月转化率', '本月转化率', '转化率变化', '新增流失', '贡献度']].to_string(index=False))

# ============================================================
# 第三步：量化各步骤对总体转化率下降的贡献
# ============================================================
print("\n" + "=" * 60)
print("三、各步骤对总体转化率下降的贡献分解")
print("=" * 60)

# 方法：计算各步骤转化率下降对整体转化率的偏导效应
# 整体转化率 = 各步骤转化率的乘积
# 整体变化 ≈ Σ(偏导效应) = Σ(各步骤转化率变化 × 其他步骤转化率之积)

last_month_overall = overall_conversion_last
this_month_overall = overall_conversion_current

step_effects = []
for i in range(1, len(df)):
    # 其他步骤的转化率（使用上月数据作为基准）
    other_conversions = []
    for j in range(1, i):
        other_conversions.append(df['本月UV'].iloc[j] / df['本月UV'].iloc[j-1])
    for j in range(i+1, len(df)):
        other_conversions.append(df['上月UV'].iloc[j] / df['上月UV'].iloc[j-1])

    baseline_other = np.prod(other_conversions) if other_conversions else 1
    rate_change = (df['本月UV'].iloc[i] / df['本月UV'].iloc[i-1]) - (df['上月UV'].iloc[i] / df['上月UV'].iloc[i-1])
    effect = abs(rate_change) * baseline_other
    step_effects.append(effect)

total_effect = sum(step_effects)
step_names = df['漏斗步骤'].iloc[1:].tolist()

print("\n各步骤转化率变化对整体的贡献（绝对影响量）：")
for name, effect in zip(step_names, step_effects):
    pct = effect / total_effect if total_effect > 0 else 0
    print(f"  {name}: {effect:.4%} (贡献 {pct:.1%})")

# ============================================================
# 第四步：根因分析与假设
# ============================================================
print("\n" + "=" * 60)
print("四、根因分析与优先级排序")
print("=" * 60)

# 按新增流失排序
step_ranked = step_conversion.sort_values('新增流失', ascending=False, key=abs)
print("\n按流失恶化程度排序（绝对值）：")
for idx, row in step_ranked.iterrows():
    direction = "恶化" if row['新增流失'] > 0 else "改善"
    print(f"  {row['漏斗步骤']}: {direction} {abs(row['新增流失']):,.0f}人 (转化率变化 {row['转化率变化']*100:+.1f}个百分点)")

# ============================================================
# 第五步：输出分析结论
# ============================================================
print("\n" + "=" * 60)
print("五、核心结论")
print("=" * 60)

# 问题最大的步骤
worst_step = step_conversion.loc[step_conversion['新增流失'].idxmax()]
second_worst = step_conversion.nlargest(2, '新增流失').iloc[1]

print(f"""
【核心发现】

1. 问题最严重的步骤：{worst_step['漏斗步骤']}
   - 转化率从 {worst_step['上月转化率']:.1%} 下降至 {worst_step['本月转化率']:.1%}
   - 转化率变化：{worst_step['转化率变化']*100:+.1f} 个百分点
   - 新增流失：{worst_step['新增流失']:,.0f} 人
   - 贡献度：{worst_step['贡献度']:.1%}

2. 第二问题步骤：{second_worst['漏斗步骤']}
   - 转化率从 {second_worst['上月转化率']:.1%} 下降至 {second_worst['本月转化率']:.1%}
   - 转化率变化：{second_worst['转化率变化']*100:+.1f} 个百分点
   - 新增流失：{second_worst['新增流失']:,.0f} 人
   - 贡献度：{second_worst['贡献度']:.1%}

3. 两个步骤合计贡献了整体流失的 {worst_step['贡献度'] + second_worst['贡献度']:.1%}

【优先级排序】
1. {worst_step['漏斗步骤']}（最高优先级）- 流失最严重，需首先排查
2. {second_worst['漏斗步骤']}（次优先级）
3. 提交成功（第三优先级）
""")

# ============================================================
# 生成报告数据供可视化
# ============================================================
report_data = {
    'steps': step_names,
    '上月转化率': step_conversion['上月转化率'].tolist(),
    '本月转化率': step_conversion['本月转化率'].tolist(),
    '转化率变化': step_conversion['转化率变化'].tolist(),
    '新增流失': step_conversion['新增流失'].tolist(),
    '贡献度': step_conversion['贡献度'].tolist(),
    'worst_step': worst_step['漏斗步骤'],
    'second_worst_step': second_worst['漏斗步骤'],
}

print("\n分析完成，结果已输出。")