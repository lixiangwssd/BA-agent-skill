import pandas as pd

# 数据
data = {
    '区域': ['华东', '华南', '华北', '西部'],
    '预算收入': [800, 600, 500, 300],
    '实际收入': [856, 498, 445, 321]
}
df = pd.DataFrame(data)

# 计算
df['差异'] = df['实际收入'] - df['预算收入']
df['达成率'] = (df['实际收入'] / df['预算收入'] * 100).round(1)

total_budget = df['预算收入'].sum()
total_actual = df['实际收入'].sum()

print("Q1 收入预算差异分析")
print("=" * 50)
print(f"预算合计：{total_budget} 万")
print(f"实际合计：{total_actual} 万")
print(f"差异：{total_actual - total_budget} 万")
print(f"达成率：{total_actual/total_budget*100:.1f}%")
print()
print(df.to_string(index=False))
