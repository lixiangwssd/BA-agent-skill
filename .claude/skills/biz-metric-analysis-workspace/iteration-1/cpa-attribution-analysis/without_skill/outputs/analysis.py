import pandas as pd

# 数据
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

# 计算变化
df['CPA变化'] = df['上周CPA'] - df['上上周CPA']
df['消耗变化%'] = (df['上周消耗_万'] - df['上上周消耗_万']) / df['上上周消耗_万'] * 100
df['新客变化%'] = (df['上周新客数'] - df['上上周新客数']) / df['上上周新客数'] * 100

# 整体
total_cost_prev = df['上上周消耗_万'].sum()
total_cost_curr = df['上周消耗_万'].sum()
total_users_prev = df['上上周新客数'].sum()
total_users_curr = df['上周新客数'].sum()

print("CPA 分析")
print("=" * 50)
print(f"整体 CPA：{total_cost_prev*10000/total_users_prev:.0f} → {total_cost_curr*10000/total_users_curr:.0f} 元")
print(f"总消耗：{total_cost_prev} → {total_cost_curr} 万（+{(total_cost_curr-total_cost_prev)/total_cost_prev*100:.1f}%）")
print(f"总新客：{total_users_prev} → {total_users_curr}（{(total_users_curr-total_users_prev)/total_users_prev*100:.1f}%）")
print()
print("各渠道：")
print(df[['渠道', '上上周CPA', '上周CPA', 'CPA变化', '消耗变化%', '新客变化%']].to_string(index=False))
