#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GMV 渠道异动分析
分析日期：2026-05-13
"""

import pandas as pd
import numpy as np

# ==================== 第一步：数据定义 ====================
data = {
    '渠道': ['自然搜索', '付费推广', '直播带货', '社群裂变'],
    '前周GMV': [420, 310, 180, 90],
    '上周GMV': [380, 195, 210, 55]
}
df = pd.DataFrame(data)

# ==================== 第二步：异动验证 ====================
total_current = df['上周GMV'].sum()
total_baseline = df['前周GMV'].sum()
total_change = total_current - total_baseline
total_change_pct = total_change / total_baseline

print("=" * 60)
print("GMV 渠道异动分析")
print("=" * 60)
print(f"\n【异动概况】")
print(f"前周 GMV：{total_baseline} 万元")
print(f"上周 GMV：{total_current} 万元")
print(f"变化量：{total_change} 万元")
print(f"变化率：{total_change_pct:.1%}")
print(f"异动判定：真实异动（下降 {abs(total_change_pct):.1%}，超过正常波动范围）")

# ==================== 第三步：贡献度拆解 ====================
df['变化量'] = df['上周GMV'] - df['前周GMV']
df['变化率'] = df['变化量'] / df['前周GMV']
df['贡献度'] = df['变化量'] / total_change
df['贡献度_pct'] = df['贡献度'] * 100

# 按贡献度排序（负向贡献最大的在最前）
df_sorted = df.sort_values('贡献度', ascending=True)

print(f"\n【各渠道贡献度分析】")
print("-" * 60)
for _, row in df_sorted.iterrows():
    direction = "↓" if row['变化量'] < 0 else "↑"
    print(f"{row['渠道']}：{row['前周GMV']} → {row['上周GMV']}（{direction}{abs(row['变化量'])}万，{row['变化率']:.1%}），贡献度 {row['贡献度_pct']:.1f}%")

# ==================== 第四步：量化主要拖累 ====================
print(f"\n【主要拖累分析】")
print("-" * 60)

# 负向贡献排序
negative_df = df_sorted[df_sorted['变化量'] < 0].copy()
print(f"拖累最大的渠道：")
for i, row in negative_df.iterrows():
    print(f"  • {row['渠道']}：拖累 {abs(row['变化量'])} 万，占总下降的 {abs(row['贡献度_pct']):.1f}%")

# 正向贡献
positive_df = df_sorted[df_sorted['变化量'] > 0]
if len(positive_df) > 0:
    print(f"\n正向贡献（部分抵消下滑）：")
    for i, row in positive_df.iterrows():
        print(f"  • {row['渠道']}：贡献 {row['变化量']} 万，占总下降的 {row['贡献度_pct']:.1f}%")

# ==================== 第五步：根因假设 ====================
print(f"\n【根因假设】")
print("-" * 60)

# 付费推广分析
paid_before = 310
paid_current = 195
paid_change = paid_current - paid_before
paid_change_pct = paid_change / paid_before

print(f"\n1. 付费推广（最大拖累源）")
print(f"   变化：{paid_before} → {paid_current}（{paid_change}万，{paid_change_pct:.1%}）")
print(f"   贡献度：{abs(paid_change / total_change * 100):.1f}% 的下降由它造成")
print(f"   可能原因：")
print(f"   • 投放预算缩减或暂停")
print(f"   • 投放渠道归因窗口调整")
print(f"   • 素材疲劳导致 CTR/CVR 下降")
print(f"   • 竞争对手加投导致 CPM/CPC 上涨")
print(f"   建议排查：")
print(f"   → 投放后台检查上周预算/出价变化")
print(f"   → 对比点击率和转化率趋势")
print(f"   → 检查是否有渠道政策变化")

# 社群裂变分析
community_before = 90
community_current = 55
community_change = community_current - community_before
community_change_pct = community_change / community_before

print(f"\n2. 社群裂变（第二大拖累）")
print(f"   变化：{community_before} → {community_current}（{community_change}万，{community_change_pct:.1%}）")
print(f"   贡献度：{abs(community_change / total_change * 100):.1f}% 的下降由它造成")
print(f"   可能原因：")
print(f"   • 裂变活动结束或力度减弱")
print(f"   • 社群活跃度下降")
print(f"   • 分享诱导话术被限制")
print(f"   建议排查：")
print(f"   → 检查上周是否有裂变活动上线/下线")
print(f"   → 对比新用户来源中社群占比变化")

# 自然搜索分析
organic_before = 420
organic_current = 380
organic_change = organic_current - organic_before
organic_change_pct = organic_change / organic_before

print(f"\n3. 自然搜索（小幅下滑）")
print(f"   变化：{organic_before} → {organic_current}（{organic_change}万，{organic_change_pct:.1%}）")
print(f"   可能原因：")
print(f"   • SEO 排名波动")
print(f"   • 搜索需求季节性变化")
print(f"   • 竞品自然流量增加")
print(f"   建议排查：")
print(f"   → 检查搜索指数和 SEO 排名变化")

# 直播带货分析（唯一正向）
live_before = 180
live_current = 210
live_change = live_current - live_before
live_change_pct = live_change / live_before

print(f"\n4. 直播带货（逆势增长）")
print(f"   变化：{live_before} → {live_current}（+{live_change}万，+{live_change_pct:.1%}）")
print(f"   贡献度：抵消了 {live_change / abs(total_change) * 100:.1f}% 的下降")
print(f"   启示：")
print(f"   → 如有关键主播/活动在这块加码，说明策略有效")
print(f"   → 可考虑将更多资源向直播渠道倾斜")

# ==================== 第六步：总结 ====================
print(f"\n{'=' * 60}")
print(f"【结论与建议】")
print(f"{'=' * 60}")
print(f"\n1. 主要拖累：付费推广贡献了 {abs(paid_change / total_change * 100):.1f}% 的下降，")
print(f"   社群裂变贡献了 {abs(community_change / total_change * 100):.1f}% 的下降。")
print(f"\n2. 结构特征：直播带货是唯一正增长渠道（+{live_change}万），")
print(f"   但无法完全抵消付费推广（-{abs(paid_change)}万）的大幅下滑。")
print(f"\n3. 重点排查方向：")
print(f"   优先级 P0：付费推广 - 检查投放预算、渠道归因、转化率")
print(f"   优先级 P1：社群裂变 - 检查裂变活动状态、分享率")
print(f"\n4. 次要关注：自然搜索虽下滑幅度小（-{abs(organic_change)}万），")
print(f"   但基数大也应关注 SEO 和搜索需求变化。")
print(f"\n{'=' * 60}")