"""
CPA 异动归因分析
数据来源：用户提供的分渠道投放数据
"""

import pandas as pd
from io import StringIO

# ========== 1. 数据定义 ==========
data = """渠道,上周消耗_万,上周新客数,上上周消耗_万,上上周新客数
信息流,65,9028,50,11111
搜索,18,4500,20,5000
短视频,22,4400,15,4286"""

df = pd.read_csv(StringIO(data))
df['上上周CPA'] = (df['上上周消耗_万'] * 10000 / df['上上周新客数']).round(2)
df['上周CPA'] = (df['上周消耗_万'] * 10000 / df['上周新客数']).round(2)
df['CPA涨幅'] = ((df['上周CPA'] - df['上上周CPA']) / df['上上周CPA'] * 100).round(1)

# ========== 2. 总体计算 ==========
total_prev_cost = 85  # 万
total_curr_cost = 105  # 万
total_prev_customers = 20397
total_curr_customers = 17928

prev_overall_cpa = total_prev_cost * 10000 / total_prev_customers
curr_overall_cpa = total_curr_cost * 10000 / total_curr_customers
overall_cpa_increase = (curr_overall_cpa - prev_overall_cpa) / prev_overall_cpa * 100

print("=" * 50)
print("CPA 异动归因分析报告")
print("=" * 50)
print(f"\n【总体情况】")
print(f"上上周整体 CPA: {prev_overall_cpa:.2f} 元")
print(f"上周整体 CPA: {curr_overall_cpa:.2f} 元")
print(f"CPA 涨幅: {overall_cpa_increase:.1f}%")

# ========== 3. 贡献度拆解 ==========
print(f"\n【各渠道贡献度拆解】")

# 计算各渠道的成本贡献
prev_costs = df['上上周消耗_万'].values
curr_costs = df['上周消耗_万'].values
prev_cpas = df['上上周CPA'].values
curr_cpas = df['上周CPA'].values

# 新客数贡献
prev_new_customers = df['上上周新客数'].values
curr_new_customers = df['上周新客数'].values

# CPA 变化贡献拆解
print(f"\n{'渠道':<8} {'上上周CPA':>10} {'上周CPA':>10} {'涨幅':>8} {'消耗变化贡献':>14} {'CPA变化贡献':>14}")
print("-" * 70)

for i, row in df.iterrows():
    cost_change = (row['上周消耗_万'] - row['上上周消耗_万']) / (total_curr_cost - total_prev_cost) * 100 if (total_curr_cost - total_prev_cost) != 0 else 0
    cpa_change_ratio = (row['上周CPA'] - row['上上周CPA']) / row['上上周CPA'] * 100
    print(f"{row['渠道']:<8} {row['上上周CPA']:>10.1f} {row['上周CPA']:>10.1f} {row['CPA涨幅']:>7.1f}% {cost_change:>13.1f}% {cpa_change_ratio:>13.1f}%")

# ========== 4. 关键发现 ==========
print(f"\n【关键发现】")
print(f"1. 信息流渠道 CPA 从 45 涨到 72，涨幅 60%，是 CPA 上涨的主因")
print(f"2. 信息流渠道消耗占比从 58.8% 提升到 61.9%，增加了成本负担")
print(f"3. 信息流渠道新客数下降了 18.7%（11111→9028），转化效率大幅下降")
print(f"4. 短视频渠道 CPA 从 35 涨到 50，涨幅 42.9%，也有较大影响")
print(f"5. 搜索渠道 CPA 维持 40 元不变，表现稳定")

# ========== 5. 归因分析 ==========
print(f"\n【归因分析】")
print(f"根据背景信息（上周信息流渠道换了一批新素材，同时竞品在做大促）：")
print(f"1. 新素材效果不佳是主因：信息流渠道 CPA 暴涨 60%，大概率与素材更新有关")
print(f"2. 竞品大促加剧竞争：信息流和短视频渠道 CPA 同时上涨，符合竞争加剧特征")
print(f"3. 成本结构恶化：高 CPA 的信息流渠道消耗占比提升，拉高了整体 CPA")

# ========== 6. 应对建议 ==========
print(f"\n【应对建议】")
print(f"1. 立即检查新素材质量：对比新旧素材的 CTR 和转化率，暂停低效素材")
print(f"2. 优化渠道预算分配：减少信息流消耗，转移到 CPA 更稳定的搜索渠道")
print(f"3. 关注短视频渠道：该渠道 CPA 涨幅 42.9%，需评估是否继续投放")
print(f"4. 搜索渠道加投：搜索渠道 CPA 稳定在 40 元，可适度增加预算")
print(f"5. 监控竞品动态：竞品大促期间避免正面竞争，可调整投放时段或受众定向")

# ========== 7. 计算详细数据 ==========
print(f"\n【详细数据表】")
print(df.to_string(index=False))

# 保存分析结果
df.to_csv('/Users/lixiang/Documents/异动分析Agent/.claude/skills/biz-metric-analysis-workspace/iteration-3/cpa-attribution-analysis/without_skill/outputs/cpa_data.csv', index=False, encoding='utf-8-sig')
print(f"\n数据已保存到 cpa_data.csv")