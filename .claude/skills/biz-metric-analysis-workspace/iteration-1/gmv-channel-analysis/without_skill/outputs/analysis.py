import pandas as pd
import matplotlib.pyplot as plt

# 数据
data = {
    '渠道': ['自然搜索', '付费推广', '直播带货', '社群裂变'],
    '前周GMV': [420, 310, 180, 90],
    '上周GMV': [380, 195, 210, 55]
}
df = pd.DataFrame(data)

# 计算变化
df['变化量'] = df['上周GMV'] - df['前周GMV']
df['变化率'] = df['变化量'] / df['前周GMV']
total_change = df['变化量'].sum()
df['贡献占比'] = df['变化量'] / total_change

print("GMV 渠道分析")
print("=" * 60)
print(f"总变化：{total_change} 万元 ({total_change/df['前周GMV'].sum():.1%})")
print()
print(df.to_string(index=False))

# 可视化
fig, ax = plt.subplots(figsize=(10, 5))
colors = ['red' if x < 0 else 'green' for x in df['变化量']]
ax.bar(df['渠道'], df['变化量'], color=colors)
ax.set_title('各渠道GMV变化量')
ax.set_ylabel('变化量（万元）')
ax.axhline(0, color='black', linewidth=0.5)
plt.tight_layout()
plt.savefig('gmv_analysis.png', dpi=150)
