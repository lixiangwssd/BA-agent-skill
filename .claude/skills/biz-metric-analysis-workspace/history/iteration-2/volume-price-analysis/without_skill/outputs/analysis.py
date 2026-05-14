# -*- coding: utf-8 -*-
"""
GMV 异动归因分析：量价拆解 + 交互效应量化

背景数据：
  整体：GMV 下降（-15%），订单量 +8%，客单价 -21%
  渠道拆分：
    渠道A：对比期 5000×200，当期 5600×164
    渠道B：对比期 8000×250，当期 7600×257.5
"""

import pandas as pd
import numpy as np

# ═══════════════════════════════════════════════════════════
# 1. 基础数据
# ═══════════════════════════════════════════════════════════
data = {
    '渠道':       ['渠道A', '渠道B'],
    'Q0':         [5000,   8000  ],   # 对比期订单量
    'Q1':         [5600,   7600  ],   # 当期订单量
    'P0':         [200.0,  250.0 ],   # 对比期客单价
    'P1':         [164.0,  257.5 ],   # 当期客单价
}
df = pd.DataFrame(data)

# ═══════════════════════════════════════════════════════════
# 2. 各期 GMV
# ═══════════════════════════════════════════════════════════
df['GMV0'] = df['Q0'] * df['P0']
df['GMV1'] = df['Q1'] * df['P1']

GMV0 = df['GMV0'].sum()   # 对比期总 GMV
GMV1 = df['GMV1'].sum()   # 当期总 GMV
dGMV = GMV1 - GMV0        # GMV 变动额

print("=" * 65)
print("【整体概览】")
print(f"  对比期总 GMV ：{GMV0:,.0f} 元  (= {GMV0/10000:.1f} 万元)")
print(f"  当期总 GMV   ：{GMV1:,.0f} 元  (= {GMV1/10000:.1f} 万元)")
print(f"  GMV 变动额   ：{dGMV:,.0f} 元  (= {dGMV/10000:.1f} 万元)")
print(f"  GMV 变动率   ：{dGMV/GMV0*100:.2f}%")
print("=" * 65)

# ═══════════════════════════════════════════════════════════
# 3. 各渠道 GMV 贡献（绝对值）
# ═══════════════════════════════════════════════════════════
df['dGMV']        = df['GMV1'] - df['GMV0']
df['贡献占比_绝对'] = df['dGMV'].abs() / abs(dGMV) * 100

print("\n【各渠道 GMV 变动详情】")
for _, r in df.iterrows():
    sign = '+' if r['dGMV'] >= 0 else ''
    pct  = r['dGMV']/r['GMV0']*100
    print(f"  {r['渠道']}：{r['GMV0']:,.0f} → {r['GMV1']:,.0f} 元，"
          f" 变动 {sign}{r['dGMV']:,.0f}（{sign}{pct:.2f}%），"
          f" 贡献占比 {r['贡献占比_绝对']:.2f}%")

# ═══════════════════════════════════════════════════════════
# 4. 量价拆解：加法模型（Young-Smith 分解）
#    dGMV = ΔQ·P1 + ΔP·Q0 + ΔQ·ΔP
#    第三项为量价交互效应（hybrid term）
# ═══════════════════════════════════════════════════════════
rows = []
for _, r in df.iterrows():
    Q0, Q1 = r['Q0'], r['Q1']
    P0, P1 = r['P0'], r['P1']

    vol_contrib  = (Q1 - Q0) * P1    # 数量变动（按当期价格计量）
    price_contrib= (P1 - P0) * Q0    # 价格变动（按对比期数量计量）
    interaction  = (Q1 - Q0) * (P1 - P0)  # 量价交叉项

    rows.append({
        '渠道':        r['渠道'],
        '数量贡献':    vol_contrib,
        '价格贡献':    price_contrib,
        '交互效应':    interaction,
        '渠道总变动':  vol_contrib + price_contrib + interaction,
    })

res = pd.DataFrame(rows)
vol_tot   = res['数量贡献'].sum()
price_tot = res['价格贡献'].sum()
inter_tot = res['交互效应'].sum()
total_chg = res['渠道总变动'].sum()

print("\n【量价拆解 - 加法模型（Young-Smith 分解）】")
print(f"  {'渠道':<6}  {'数量贡献':>12}  {'价格贡献':>12}  {'交互效应':>10}  {'渠道总变动':>12}")
print("  " + "-" * 56)
for _, r in res.iterrows():
    print(f"  {r['渠道']:<6}  {r['数量贡献']:>+12,.0f}  {r['价格贡献']:>+12,.0f}  "
          f"{r['交互效应']:>+10,.0f}  {r['渠道总变动']:>+12,.0f}")
print("  " + "-" * 56)
print(f"  {'合计':<6}  {vol_tot:>+12,.0f}  {price_tot:>+12,.0f}  "
      f"{inter_tot:>+10,.0f}  {total_chg:>+12,.0f}")

# ═══════════════════════════════════════════════════════════
# 5. 各因子对整体 GMV 下降的贡献占比
# ═══════════════════════════════════════════════════════════
print("\n【各因子对整体 GMV 下降的贡献占比】")
factor_total = vol_tot + price_tot + inter_tot
print(f"  整体 GMV 变动：{dGMV:,.0f} 元（{dGMV/GMV0*100:.2f}%）")
print(f"  数量因素贡献：{vol_tot:,.0f} 元（{vol_tot/abs(factor_total)*100:.2f}%）")
print(f"  价格因素贡献：{price_tot:,.0f} 元（{price_tot/abs(factor_total)*100:.2f}%）")
print(f"  交互效应    ：{inter_tot:,.0f} 元（{inter_tot/abs(factor_total)*100:.2f}%）")
print(f"  （验证：{vol_tot:,.0f}+{price_tot:,.0f}+{inter_tot:,.0f}={total_chg:,.0f} ≈ {dGMV:,.0f}）")

# ═══════════════════════════════════════════════════════════
# 6. 各渠道贡献率（相对于整体 GMV 变动）
# ═══════════════════════════════════════════════════════════
print("\n【各渠道对整体 GMV 变动的贡献率】")
for _, r in res.iterrows():
    pct = r['渠道总变动'] / dGMV * 100
    sign = '+' if pct >= 0 else ''
    print(f"  {r['渠道']}：{sign}{pct:.2f}%（贡献 {r['渠道总变动']:+,g} 元）")

# ═══════════════════════════════════════════════════════════
# 7. 乘法模型验证（变动率视角）
# ═══════════════════════════════════════════════════════════
print("\n【乘法模型 - 变动率拆解】")
for _, r in df.iterrows():
    q_chg_rate = (r['Q1'] - r['Q0']) / r['Q0'] * 100
    p_chg_rate = (r['P1'] - r['P0']) / r['P0'] * 100
    gmv_chg_rate = r['dGMV'] / r['GMV0'] * 100
    # 乘法交叉项
    cross = q_chg_rate * p_chg_rate / 100
    print(f"  {r['渠道']}：订单量{q_chg_rate:+.2f}%，客单价{p_chg_rate:+.2f}%，"
          f"交叉{cross:+.2f}%，GMV{gmv_chg_rate:+.2f}%")

# ═══════════════════════════════════════════════════════════
# 8. 结论摘要
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("【结论摘要】")
print("=" * 65)
print(f"  整体 GMV 下降 {-dGMV:,.0f} 元（{-dGMV/GMV0*100:.2f}%），分解为：")
print(f"  · 客单价下降拖累：{price_tot:,.0f} 元（{price_tot/abs(factor_total)*100:.1f}%）——主因")
print(f"  · 量价交互效应  ：{inter_tot:,.0f} 元（{inter_tot/abs(factor_total)*100:.1f}%）")
print(f"  · 订单量上升贡献：{vol_tot:,.0f} 元（{vol_tot/abs(factor_total)*100:.1f}%）——正向缓冲")
print()
print(f"  渠道视角：")
for _, r in res.iterrows():
    pct = r['渠道总变动'] / dGMV * 100
    sign = '+' if pct >= 0 else ''
    print(f"  · {r['渠道']} 贡献整体 {-dGMV/abs(dGMV)*100:.1f}% 中的 {abs(pct):.1f}%（{r['渠道总变动']:+,g} 元）")
print("=" * 65)