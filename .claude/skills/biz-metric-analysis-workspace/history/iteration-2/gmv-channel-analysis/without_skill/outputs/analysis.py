# -*- coding: utf-8 -*-
"""GMV异动分析：按渠道拆解贡献度"""

import pandas as pd
import numpy as np

# ===== 1. 数据定义 =====
data = {
    '渠道': ['自然搜索', '付费推广', '直播带货', '社群裂变'],
    '前周GMV': [420, 310, 180, 90],
    '上周GMV': [380, 195, 210, 55]
}
df = pd.DataFrame(data)

# ===== 2. 计算异动情况 =====
df['GMV变化'] = df['上周GMV'] - df['前周GMV']
df['环比变化率'] = (df['GMV变化'] / df['前周GMV'] * 100).round(2)
df['贡献度占比'] = (df['GMV变化'] / df['GMV变化'].sum() * 100).round(2)

total_last = df['前周GMV'].sum()
total_this = df['上周GMV'].sum()
total_change = total_this - total_last
total_change_pct = total_change / total_last * 100

print("=" * 60)
print("GMV异动分析报告")
print("=" * 60)
print(f"\n总体情况：前周 {total_last} 万元 → 上周 {total_this} 万元")
print(f"总下降：{total_change} 万元（{total_change_pct:.1f}%）")

# ===== 3. 各渠道分析 =====
print("\n【各渠道异动明细】")
print("-" * 60)
print(f"{'渠道':<10} {'前周':>10} {'上周':>10} {'变化':>10} {'变化率':>10} {'贡献度':>10}")
print("-" * 60)
for _, row in df.iterrows():
    print(f"{row['渠道']:<10} {row['前周GMV']:>10} {row['上周GMV']:>10} {row['GMV变化']:>10} {row['环比变化率']:>10.2f}% {row['贡献度占比']:>10.2f}%")
print("-" * 60)

# ===== 4. 拖累最大的渠道 =====
df_sorted = df.sort_values('GMV变化')
worst = df_sorted.iloc[0]
second_worst = df_sorted.iloc[1]

print(f"\n【核心结论】")
print(f"1. 最大拖累渠道：{worst['渠道']}（下降 {abs(worst['GMV变化'])} 万，贡献了 {abs(worst['贡献度占比']):.1f}% 的总降幅）")
print(f"2. 次大拖累渠道：{second_worst['渠道']}（下降 {abs(second_worst['GMV变化'])} 万，贡献了 {abs(second_worst['贡献度占比']):.1f}% 的总降幅）")
print(f"3. 唯一增长渠道：{df[df['GMV变化'] > 0]['渠道'].values[0]}（增长 {df[df['GMV变化'] > 0]['GMV变化'].values[0]} 万）")

# ===== 5. 重点排查方向 =====
print(f"\n【重点排查方向】")
print(f"\n▶ {worst['渠道']} 异动排查清单：")
if worst['渠道'] == '付费推广':
    print("  - 投放平台：检查百度/抖音/腾讯广告后台消费是否有异常")
    print("  - 关键词：核对高花费关键词的 CPM/CPC 是否突然上涨")
    print("  - 账户健康：是否存在违规被限流、创意疲劳")
    print("  - 时段/地域：对照上周是否有预算削减或暂停")
    print("  - 落地页：检查页面加载速度、转化组件是否正常")

print(f"\n▶ {second_worst['渠道']} 异动排查清单：")
print("  - 近期是否有运营动作变化（推送频次、内容形式）")
print("  - 是否有外部竞对在做补贴活动")

print(f"\n▶ 增长渠道（{df[df['GMV变化'] > 0]['渠道'].values[0]}）为何增长：")
print("  - 是自然增长还是上周有特殊运营动作（如专场直播）")
print("  - 如果是运营带动的，是否可以复制放大")

# ===== 6. 输出结果到文件 =====
results = {
    '总体下降': f"{abs(total_change)} 万元（{total_change_pct:.1f}%）",
    '最大拖累渠道': worst['渠道'],
    '拖累金额': f"{abs(worst['GMV变化'])} 万元",
    '贡献度': f"{abs(worst['贡献度占比']):.1f}%",
    '次大拖累渠道': second_worst['渠道'],
    '增长渠道': df[df['GMV变化'] > 0]['渠道'].values[0]
}

import json
with open('/Users/lixiang/Documents/异动分析Agent/.claude/skills/biz-metric-analysis-workspace/iteration-2/gmv-channel-analysis/without_skill/outputs/analysis_result.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n分析结果已保存到 outputs/ 目录")