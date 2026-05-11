import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# === 第一步：数据构建 ===
data = {
    '渠道': ['信息流', '搜索', '短视频'],
    '上上周消耗_万': [50, 20, 15],
    '上周消耗_万': [65, 18, 22],
    '上上周新客数': [11111, 5000, 4286],
    '上周新客数': [9028, 4500, 4400],
    '上上周CPA': [45, 40, 35],
    '上周CPA': [72, 40, 50]
}
df = pd.DataFrame(data)

# === 第二步：异动验证 ===
total_cost_prev = df['上上周消耗_万'].sum()
total_cost_curr = df['上周消耗_万'].sum()
total_users_prev = df['上上周新客数'].sum()
total_users_curr = df['上周新客数'].sum()
cpa_prev = total_cost_prev * 10000 / total_users_prev  # 转为元
cpa_curr = total_cost_curr * 10000 / total_users_curr
cpa_change = cpa_curr - cpa_prev
cpa_change_rate = cpa_change / cpa_prev

print("=" * 60)
print("CPA 异动验证")
print("=" * 60)
print(f"上上周整体 CPA：{cpa_prev:.0f} 元")
print(f"上周整体 CPA：{cpa_curr:.0f} 元")
print(f"变化：+{cpa_change:.0f} 元（+{cpa_change_rate:.1%}）")
print(f"判断：CPA 上涨 {cpa_change_rate:.0%}，属于显著异动")

# === 第三步：乘法模型拆解（CPA = 消耗 / 新客数） ===
print("\n" + "=" * 60)
print("CPA 价量拆解（CPA = 消耗 / 新客数）")
print("=" * 60)

# 整体拆解
cost_effect = (total_cost_curr - total_cost_prev) / total_users_prev * 10000
volume_effect = total_cost_prev * 10000 * (1/total_users_curr - 1/total_users_prev)
cross_effect = cpa_change * 10000 - cost_effect - volume_effect

# 简化分析：消耗变化 vs 新客数变化
cost_change_rate = (total_cost_curr - total_cost_prev) / total_cost_prev
users_change_rate = (total_users_curr - total_users_prev) / total_users_prev

print(f"消耗变化：{total_cost_prev} → {total_cost_curr} 万（+{cost_change_rate:.1%}）")
print(f"新客数变化：{total_users_prev} → {total_users_curr}（{users_change_rate:.1%}）")
print(f"\nCPA 上涨分解：")
print(f"  消耗增长效应（+{cost_change_rate:.1%}）：推高 CPA")
print(f"  新客下降效应（{users_change_rate:.1%}）：推高 CPA")
print(f"  结论：消耗涨 + 新客降 双重推高 CPA")

# === 第四步：渠道贡献度拆解 ===
print("\n" + "=" * 60)
print("各渠道 CPA 变化与贡献")
print("=" * 60)

df['消耗变化_万'] = df['上周消耗_万'] - df['上上周消耗_万']
df['新客变化'] = df['上周新客数'] - df['上上周新客数']
df['CPA变化'] = df['上周CPA'] - df['上上周CPA']
df['消耗变化率'] = df['消耗变化_万'] / df['上上周消耗_万']
df['新客变化率'] = df['新客变化'] / df['上上周新客数']

# 各渠道对总CPA变化的贡献（基于消耗权重加权）
df['上周消耗占比'] = df['上周消耗_万'] / df['上周消耗_万'].sum()
df['加权CPA贡献'] = df['CPA变化'] * df['上周消耗占比']

print(df[['渠道', '上上周CPA', '上周CPA', 'CPA变化', '消耗变化率', '新客变化率']].to_string(index=False))

print("\n各渠道问题诊断：")
for _, row in df.iterrows():
    print(f"\n  {row['渠道']}：CPA {row['上上周CPA']} → {row['上周CPA']}（+{row['CPA变化']} 元）")
    print(f"    消耗变化：{row['消耗变化率']:+.1%}")
    print(f"    新客变化：{row['新客变化率']:+.1%}")
    if row['消耗变化率'] > 0 and row['新客变化率'] < 0:
        print(f"    诊断：消耗↑ + 新客↓ = 效率严重恶化")
    elif row['消耗变化率'] > 0 and row['新客变化率'] > 0:
        print(f"    诊断：消耗↑ + 新客↑，但消耗增速 > 新客增速")
    elif row['CPA变化'] == 0:
        print(f"    诊断：CPA 稳定")

# === 第五步：可视化 ===
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# CPA 对比
x = range(len(df))
width = 0.35
axes[0].bar([i - width/2 for i in x], df['上上周CPA'], width, label='上上周', color='#4393c3')
axes[0].bar([i + width/2 for i in x], df['上周CPA'], width, label='上周', color='#d6604d')
axes[0].set_xticks(x)
axes[0].set_xticklabels(df['渠道'])
axes[0].set_title('各渠道 CPA 对比（元）')
axes[0].set_ylabel('CPA（元）')
axes[0].legend()

# 消耗 vs 新客变化率对比
x_pos = range(len(df))
axes[1].bar([i - width/2 for i in x_pos], df['消耗变化率'] * 100, width, label='消耗变化率', color='#fc8d59')
axes[1].bar([i + width/2 for i in x_pos], df['新客变化率'] * 100, width, label='新客变化率', color='#91bfdb')
axes[1].set_xticks(x_pos)
axes[1].set_xticklabels(df['渠道'])
axes[1].set_title('消耗 vs 新客 变化率对比（%）')
axes[1].set_ylabel('变化率（%）')
axes[1].axhline(0, color='black', linewidth=0.8)
axes[1].legend()

plt.tight_layout()
plt.savefig('cpa_analysis.png', dpi=150, bbox_inches='tight')
print("\n图表已保存为 cpa_analysis.png")
