"""
GMV 异动归因分析 - 渠道维度拆解
分析日期：2026/05/13
"""

import pandas as pd

# 数据
data = {
    '渠道': ['自然搜索', '付费推广', '直播带货', '社群裂变'],
    '前周GMV': [420, 310, 180, 90],
    '上周GMV': [380, 195, 210, 55]
}
df = pd.DataFrame(data)

# 计算变化
df['GMV变化'] = df['上周GMV'] - df['前周GMV']
df['变化率'] = df['GMV变化'] / df['前周GMV']
df['贡献度'] = df['GMV变化'] / df['前周GMV'].sum()  # 占总变化的比例
df['占比前周'] = df['前周GMV'] / df['前周GMV'].sum()

# 总变化
total_change = df['GMV变化'].sum()
total_change_pct = total_change / df['前周GMV'].sum()

print("=" * 60)
print("GMV 异动分析报告")
print("=" * 60)
print(f"\n总体情况：上周 GMV {df['上周GMV'].sum()} 万，前周 {df['前周GMV'].sum()} 万")
print(f"总变化：{total_change} 万，变化率 {total_change_pct:.1%}")
print("\n" + "-" * 60)
print("各渠道贡献度拆解：")
print("-" * 60)
print(df.to_string(index=False))

# 贡献度排序（只看拖后腿的）
print("\n" + "=" * 60)
print("拖累分析（按 GMV 变化量排序）：")
print("=" * 60)
drag = df[df['GMV变化'] < 0].sort_values('GMV变化')
for _, row in drag.iterrows():
    channel = row['渠道']
    change = row['GMV变化']
    pct = row['变化率']
    contribution = change / total_change * 100
    print(f"\n{channel}：下降 {abs(change)} 万（{pct:.1%}），贡献了总下降的 {abs(contribution):.1f}%")

# 计算如果剔除拖累渠道后的模拟
print("\n" + "=" * 60)
print("模拟分析：剔除付费推广后的 GMV")
print("=" * 60)
simulated_total = df[df['渠道'] != '付费推广']['上周GMV'].sum()
simulated_base = df[df['渠道'] != '付费推广']['前周GMV'].sum()
print(f"剔除付费推广后：上周 {simulated_total} 万 vs 前周 {simulated_base} 万")
print(f"变化率：{(simulated_total - simulated_base) / simulated_base:.1%}")

print("\n" + "=" * 60)
print("核心结论")
print("=" * 60)
print(f"1. 主要拖累：付费推广下降 115 万，占总下降的 {115/160*100:.0f}%，是最大拖累")
print(f"2. 次要拖累：社群裂变下降 35 万，自然搜索下降 40 万")
print(f"3. 正向对冲：直播带货增长 30 万，部分抵消了下滑")
print(f"4. 重点关注：付费推广（-37.1%）和社群裂变（-38.9%）降幅最大")