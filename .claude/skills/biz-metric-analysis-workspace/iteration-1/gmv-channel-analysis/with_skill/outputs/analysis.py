import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# === 第一步：数据构建 ===
data = {
    '渠道': ['自然搜索', '付费推广', '直播带货', '社群裂变'],
    '前周GMV': [420, 310, 180, 90],
    '上周GMV': [380, 195, 210, 55]
}
df = pd.DataFrame(data)

# === 第二步：异动验证 ===
total_prev = df['前周GMV'].sum()
total_curr = df['上周GMV'].sum()
total_change = total_curr - total_prev
total_change_rate = total_change / total_prev

print("=" * 50)
print("异动验证")
print("=" * 50)
print(f"前周 GMV 合计：{total_prev} 万元")
print(f"上周 GMV 合计：{total_curr} 万元")
print(f"变化量：{total_change} 万元")
print(f"变化率：{total_change_rate:.1%}")
print(f"判断：变化率 {abs(total_change_rate):.1%} > 10%，属于显著异动")

# === 第三步：贡献度拆解 ===
df['变化量'] = df['上周GMV'] - df['前周GMV']
df['变化率'] = df['变化量'] / df['前周GMV']
df['贡献度'] = df['变化量'] / total_change
df['贡献度_pct'] = df['贡献度'].map(lambda x: f"{x:.1%}")

print("\n" + "=" * 50)
print("各渠道贡献度拆解")
print("=" * 50)
print(df[['渠道', '前周GMV', '上周GMV', '变化量', '变化率', '贡献度']].to_string(index=False))

# 排序：按贡献度绝对值降序
df_sorted = df.reindex(df['变化量'].abs().sort_values(ascending=False).index)

print("\n" + "=" * 50)
print("按贡献绝对值排序")
print("=" * 50)
for _, row in df_sorted.iterrows():
    direction = "↓" if row['变化量'] < 0 else "↑"
    print(f"  {row['渠道']}: {direction} {abs(row['变化量'])} 万元 (贡献度 {row['贡献度']:.1%})")

# === 第四步：可视化 ===
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 贡献度瀑布图
colors = ['#d73027' if v < 0 else '#1a9641' for v in df_sorted['变化量']]
axes[0].barh(df_sorted['渠道'], df_sorted['变化量'], color=colors)
axes[0].set_title('各渠道 GMV 变化量（万元）')
axes[0].axvline(0, color='black', linewidth=0.8)
for i, (v, name) in enumerate(zip(df_sorted['变化量'], df_sorted['渠道'])):
    axes[0].text(v + (2 if v >= 0 else -2), i, f"{v:+.0f}", va='center',
                ha='left' if v >= 0 else 'right', fontsize=10)

# 前后对比柱状图
x = range(len(df))
width = 0.35
axes[1].bar([i - width/2 for i in x], df['前周GMV'], width, label='前周', color='#4393c3')
axes[1].bar([i + width/2 for i in x], df['上周GMV'], width, label='上周', color='#d6604d')
axes[1].set_xticks(x)
axes[1].set_xticklabels(df['渠道'])
axes[1].set_title('各渠道 GMV 前后对比（万元）')
axes[1].legend()
axes[1].set_ylabel('GMV（万元）')

plt.tight_layout()
plt.savefig('metric_analysis.png', dpi=150, bbox_inches='tight')
print("\n图表已保存为 metric_analysis.png")
