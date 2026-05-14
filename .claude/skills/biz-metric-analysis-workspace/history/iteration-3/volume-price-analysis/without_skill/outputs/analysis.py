import pandas as pd
import numpy as np

# 构建数据（单位：万元）
data = {
    'channel': ['渠道A', '渠道B'],
    'vol_base': [5000, 8000],      # 对比期订单量
    'vol_curr': [5600, 7600],      # 当期订单量
    'price_base': [200, 250],      # 对比期客单价
    'price_curr': [164, 257.5]     # 当期客单价
}
df = pd.DataFrame(data)

# 计算各渠道GMV
df['gmv_base'] = df['vol_base'] * df['price_base']
df['gmv_curr'] = df['vol_curr'] * df['price_curr']
df['gmv_change'] = df['gmv_curr'] - df['gmv_base']

# 加法模型拆解：ΔGMV = ΔVolume×Price₀ + ΔPrice×Vol₀ + ΔVolume×ΔPrice
df['volume_effect'] = (df['vol_curr'] - df['vol_base']) * df['price_base']
df['price_effect'] = (df['price_curr'] - df['price_base']) * df['vol_curr']
df['interaction'] = (df['vol_curr'] - df['vol_base']) * (df['price_curr'] - df['price_base'])

# 验证
df['verification'] = df['volume_effect'] + df['price_effect'] + df['interaction']

print("=" * 60)
print("GMV异动分析 - 量价交互效应拆解")
print("=" * 60)
print("\n【原始数据】")
print(df.to_string(index=False))

# 整体GMV
total_gmv_base = df['gmv_base'].sum()
total_gmv_curr = df['gmv_curr'].sum()
total_gmv_change = total_gmv_curr - total_gmv_base

print("\n【整体GMV变化】")
print(f"对比期GMV: {total_gmv_base:.1f}万元")
print(f"当期GMV: {total_gmv_curr:.1f}万元")
print(f"GMV变化: {total_gmv_change:.1f}万元")

# 各效应汇总
total_vol = df['volume_effect'].sum()
total_price = df['price_effect'].sum()
total_inter = df['interaction'].sum()

print("\n【效应拆解汇总】")
print(f"订单量效应 (Volume Effect): {total_vol:.1f}万元")
print(f"客单价效应 (Price Effect): {total_price:.1f}万元")
print(f"交互效应 (Interaction): {total_inter:.1f}万元")
print(f"合计: {total_vol + total_price + total_inter:.1f}万元")

print("\n【各渠道贡献度】")
for _, row in df.iterrows():
    pct = row['gmv_change'] / total_gmv_change * 100 if total_gmv_change != 0 else 0
    print(f"{row['channel']}: {row['gmv_change']:.1f}万元 (贡献 {pct:.1f}%)")

print("\n【效应贡献占比】")
for effect, name in [(total_vol, '订单量效应'), (total_price, '客单价效应'), (total_inter, '交互效应')]:
    pct = effect / abs(total_gmv_change) * 100 if total_gmv_change != 0 else 0
    print(f"{name}: {pct:.1f}%")

# 保存结果
result = {
    'total_gmv_base': total_gmv_base,
    'total_gmv_curr': total_gmv_curr,
    'total_gmv_change': total_gmv_change,
    'volume_effect': total_vol,
    'price_effect': total_price,
    'interaction': total_inter
}