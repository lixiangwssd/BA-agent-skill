import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# === 第一步：数据构建 ===
data = {
    '区域': ['华东', '华南', '华北', '西部'],
    '预算收入': [800, 600, 500, 300],
    '实际收入': [856, 498, 445, 321]
}
df = pd.DataFrame(data)

# === 第二步：异动验证 ===
df['差异'] = df['实际收入'] - df['预算收入']
df['达成率'] = df['实际收入'] / df['预算收入']
total_budget = df['预算收入'].sum()
total_actual = df['实际收入'].sum()
total_gap = total_actual - total_budget
total_achievement = total_actual / total_budget

print("=" * 60)
print("Q1 收入 vs 预算 异动验证")
print("=" * 60)
print(f"预算总收入：{total_budget} 万元")
print(f"实际总收入：{total_actual} 万元")
print(f"总差异：{total_gap} 万元")
print(f"整体达成率：{total_achievement:.1%}")
print(f"判断：整体达成率 96.4%，差距 80 万，属于轻度未达标")

# === 第三步：贡献度拆解 ===
df['差异贡献'] = df['差异'] / total_gap

print("\n" + "=" * 60)
print("各区域差异贡献度")
print("=" * 60)
print(df[['区域', '预算收入', '实际收入', '差异', '达成率', '差异贡献']].to_string(index=False))

# 区分已知原因和待排查项
print("\n" + "=" * 60)
print("归因分类")
print("=" * 60)
print("已知原因：")
print(f"  华南区：-102 万（大客户 3 月延期签单），贡献 {-102/total_gap:.1%}")
print("\n待排查项：")
print(f"  华北区：-55 万（原因未知），贡献 {-55/total_gap:.1%}")
print("\n正向贡献：")
print(f"  华东区：+56 万，达成率 {856/800:.1%}")
print(f"  西部区：+21 万，达成率 {321/300:.1%}")

# === 第四步：可视化 ===
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 各区域达成率
colors = ['#1a9641' if x >= 1 else '#d73027' for x in df['达成率']]
bars = axes[0].bar(df['区域'], df['达成率'] * 100, color=colors)
axes[0].axhline(100, color='black', linewidth=1, linestyle='--', label='目标线')
axes[0].set_title('各区域 Q1 达成率')
axes[0].set_ylabel('达成率（%）')
axes[0].legend()
for bar, rate in zip(bars, df['达成率']):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{rate:.1%}', ha='center', va='bottom', fontsize=10)

# 差异瀑布图
colors2 = ['#d73027' if v < 0 else '#1a9641' for v in df['差异']]
axes[1].barh(df['区域'], df['差异'], color=colors2)
axes[1].set_title('各区域收入差异（万元）')
axes[1].axvline(0, color='black', linewidth=0.8)
for i, v in enumerate(df['差异']):
    axes[1].text(v + (2 if v >= 0 else -2), i, f"{v:+.0f}",
                va='center', ha='left' if v >= 0 else 'right', fontsize=10)

plt.tight_layout()
plt.savefig('budget_variance.png', dpi=150, bbox_inches='tight')
print("\n图表已保存为 budget_variance.png")
