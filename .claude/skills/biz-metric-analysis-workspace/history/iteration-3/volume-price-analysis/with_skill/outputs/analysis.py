"""
GMV 异动分析：量价拆解 + 渠道贡献度分析
数据：渠道A、渠道B 的对比期/当期订单量与客单价
"""

import pandas as pd
import numpy as np

# ==================== 第一步：数据接入 ====================
data = {
    '渠道': ['渠道A', '渠道B'],
    '对比期订单量': [5000, 8000],
    '当期订单量': [5600, 7600],
    '对比期客单价': [200, 250],
    '当期客单价': [164, 257.5]
}
df = pd.DataFrame(data)

# 计算 GMV（单位：万元）
df['对比期GMV'] = df['对比期订单量'] * df['对比期客单价']
df['当期GMV'] = df['当期订单量'] * df['当期客单价']
df['GMV变化量'] = df['当期GMV'] - df['对比期GMV']
df['GMV变化率'] = df['GMV变化量'] / df['对比期GMV']

print("=" * 60)
print("一、数据概览")
print("=" * 60)
print(df.to_string(index=False))

# ==================== 第二步：整体指标验证 ====================
total_base_gmv = df['对比期GMV'].sum()
total_current_gmv = df['当期GMV'].sum()
total_gmv_change = total_current_gmv - total_base_gmv
total_gmv_change_pct = total_gmv_change / total_base_gmv

total_base_volume = df['对比期订单量'].sum()
total_current_volume = df['当期订单量'].sum()
total_volume_change = total_current_volume - total_base_volume
total_volume_change_pct = total_volume_change / total_base_volume

# 加权平均客单价
avg_base_price = total_base_gmv / total_base_volume
avg_current_price = total_current_gmv / total_current_volume
price_change_pct = (avg_current_price - avg_base_price) / avg_base_price

print("\n" + "=" * 60)
print("二、整体指标验证")
print("=" * 60)
print(f"对比期总 GMV：{total_base_gmv:,.0f} 万元")
print(f"当期总 GMV：{total_current_gmv:,.0f} 万元")
print(f"GMV 变化量：{total_gmv_change:,.0f} 万元")
print(f"GMV 变化率：{total_gmv_change_pct:.2%}")
print(f"\n对比期总订单量：{total_base_volume:,}")
print(f"当期总订单量：{total_current_volume:,}")
print(f"订单量变化率：{total_volume_change_pct:.2%}")
print(f"\n对比期平均客单价：{avg_base_price:.2f} 元")
print(f"当期平均客单价：{avg_current_price:.2f} 元")
print(f"客单价变化率：{price_change_pct:.2%}")

# ==================== 第三步：渠道贡献度拆解 ====================
print("\n" + "=" * 60)
print("三、渠道贡献度拆解（加总型）")
print("=" * 60)

total_change = df['GMV变化量'].sum()
df['贡献度'] = df['GMV变化量'] / total_change
df_sorted = df.sort_values('GMV变化量', ascending=True)

print(f"\n总 GMV 变化量：{total_change:,.0f} 万元")
print("\n各渠道 GMV 变化：")
for _, row in df_sorted.iterrows():
    direction = "下降" if row['GMV变化量'] < 0 else "上涨"
    print(f"  {row['渠道']}：{row['GMV变化量']:+,.0f} 万元（{direction} {abs(row['GMV变化量']/row['对比期GMV']):.2%}），贡献度 {row['贡献度']:.1%}")

# ==================== 第四步：量价交互效应拆解 ====================
print("\n" + "=" * 60)
print("四、量价交互效应拆解（乘法模型）")
print("=" * 60)

def calculate_volume_price_effects(channel_name, v_base, v_curr, p_base, p_curr):
    """计算单个渠道的量效应、价效应、交叉效应"""
    volume_effect = (v_curr - v_base) * p_base
    price_effect = (p_curr - p_base) * v_base
    cross_effect = (v_curr - v_base) * (p_curr - p_base)
    total_effect = volume_effect + price_effect + cross_effect
    return volume_effect, price_effect, cross_effect, total_effect

results = []
for _, row in df.iterrows():
    ch = row['渠道']
    v_base = row['对比期订单量']
    v_curr = row['当期订单量']
    p_base = row['对比期客单价']
    p_curr = row['当期客单价']

    vol_eff, price_eff, cross_eff, total_eff = calculate_volume_price_effects(ch, v_base, v_curr, p_base, p_curr)
    results.append({
        '渠道': ch,
        '量变效应': vol_eff,
        '价变效应': price_eff,
        '交叉效应': cross_eff,
        '总效应': total_eff
    })

effect_df = pd.DataFrame(results)

print("\n各渠道效应分解（单位：万元）")
print("-" * 60)
for _, row in effect_df.iterrows():
    print(f"\n{row['渠道']}：")
    print(f"  量变效应：{row['量变效应']:+,.0f} 万元（{(row['量变效应']/abs(total_change)):.1%}）")
    print(f"  价变效应：{row['价变效应']:+,.0f} 万元（{(row['价变效应']/abs(total_change)):.1%}）")
    print(f"  交叉效应：{row['交叉效应']:+,.0f} 万元（{(row['交叉效应']/abs(total_change)):.1%}）")
    print(f"  合计：{row['总效应']:+,.0f} 万元")

# 汇总各效应
total_vol_effect = effect_df['量变效应'].sum()
total_price_effect = effect_df['价变效应'].sum()
total_cross_effect = effect_df['交叉效应'].sum()
total_effect_sum = effect_df['总效应'].sum()

print("\n" + "-" * 60)
print("汇总效应：")
print(f"  量变效应合计：{total_vol_effect:+,.0f} 万元（{total_vol_effect/abs(total_change):.1%}）")
print(f"  价变效应合计：{total_price_effect:+,.0f} 万元（{total_price_effect/abs(total_change):.1%}）")
print(f"  交叉效应合计：{total_cross_effect:+,.0f} 万元（{total_cross_effect/abs(total_change):.1%}）")
print(f"  总效应：{total_effect_sum:+,.0f} 万元（验证：{abs(total_effect_sum - abs(total_change))/abs(total_change)*100:.2f}% 误差）")

# ==================== 第五步： Simpson 悖论检测 ====================
print("\n" + "=" * 60)
print("五、Simpson 悖论检测")
print("=" * 60)

# 检查整体与分层变化方向
print(f"\n整体订单量变化率：{total_volume_change_pct:.2%}（上涨）")
print(f"整体客单价变化率：{price_change_pct:.2%}（下降）")
print(f"渠道A 订单量变化率：{(5600-5000)/5000:.2%}（上涨 {(5600-5000)/5000:.2%}）")
print(f"渠道A 客单价变化率：{(164-200)/200:.2%}（下降 {(164-200)/200:.2%}）")
print(f"渠道B 订单量变化率：{(7600-8000)/8000:.2%}（下降 {(7600-8000)/8000:.2%}）")
print(f"渠道B 客单价变化率：{(257.5-250)/250:.2%}（上涨 {(257.5-250)/250:.2%}）")

# 结构效应：渠道占比变化
base_share_a = 5000 / total_base_volume
curr_share_a = 5600 / total_current_volume
print(f"\n渠道A 订单量占比：对比期 {base_share_a:.1%} → 当期 {curr_share_a:.1%}（{'+' if curr_share_a > base_share_a else ''}{(curr_share_a - base_share_a)*100:.1f} ppt）")
print(f"渠道B 订单量占比：对比期 {1-base_share_a:.1%} → 当期 {1-curr_share_a:.1%}（{'+' if (1-curr_share_a) > (1-base_share_a) else ''}{(base_share_a - curr_share_a)*100:.1f} ppt）")

print("\n结论：整体订单量上涨但渠道B订单量下降，存在结构变化（渠道A占比提升）")

# ==================== 第六步：关键发现 ====================
print("\n" + "=" * 60)
print("六、关键发现汇总")
print("=" * 60)

findings = f"""
1. GMV 下降主要是客单价下跌驱动（{abs(total_price_effect)/abs(total_change)*100:.0f}% 贡献）
2. 渠道A 客单价暴跌 18%，是最大负向因素
3. 渠道B 客单价微涨 3%，但订单量下滑 5%，量价基本持平
4. 渠道A 订单量增长 12%，部分抵消了价跌影响
5. 交叉效应为 {(total_cross_effect):+,.0f} 万元，说明量价变动存在交互作用
"""
print(findings)

# ==================== 保存结果 ====================
effect_df.to_csv('/Users/lixiang/Documents/异动分析Agent/.claude/skills/biz-metric-analysis-workspace/iteration-3/volume-price-analysis/with_skill/outputs/effects.csv', index=False, encoding='utf-8-sig')
print("\n效应分解数据已保存")