"""
GMV 渠道异动分析脚本
分析周期：前周 vs 上周
目标指标：GMV（万元）
"""

import pandas as pd
import numpy as np

# ─────────────────────────────────────────────
# 1. 数据录入
# ─────────────────────────────────────────────
data = {
    "渠道":    ["自然搜索", "付费推广", "直播带货", "社群裂变"],
    "前周GMV": [420,       310,       180,       90],
    "上周GMV": [380,       195,       210,       55],
}

df = pd.DataFrame(data)

# ─────────────────────────────────────────────
# 2. 基础计算
# ─────────────────────────────────────────────
df["GMV变化额"]   = df["上周GMV"] - df["前周GMV"]
df["GMV变化率%"]  = (df["GMV变化额"] / df["前周GMV"] * 100).round(2)

total_prev = df["前周GMV"].sum()   # 1000
total_curr = df["上周GMV"].sum()   # 840
total_delta = total_curr - total_prev  # -160

# 贡献度 = 该渠道变化额 / 总变化额（负值说明是拖累）
df["拖累贡献度%"] = (df["GMV变化额"] / total_delta * 100).round(2)

# 结构占比
df["前周占比%"]   = (df["前周GMV"] / total_prev * 100).round(2)
df["上周占比%"]   = (df["上周GMV"] / total_curr * 100).round(2)
df["占比变化pct"] = (df["上周占比%"] - df["前周占比%"]).round(2)

# ─────────────────────────────────────────────
# 3. 汇总行
# ─────────────────────────────────────────────
total_row = pd.DataFrame({
    "渠道":       ["合计"],
    "前周GMV":    [total_prev],
    "上周GMV":    [total_curr],
    "GMV变化额":  [total_delta],
    "GMV变化率%": [(total_delta / total_prev * 100).round(2)],
    "拖累贡献度%":["100.00"],
    "前周占比%":  [100.00],
    "上周占比%":  [100.00],
    "占比变化pct":[0.00],
})

result = pd.concat([df, total_row], ignore_index=True)

# ─────────────────────────────────────────────
# 4. 打印分析结果
# ─────────────────────────────────────────────
print("=" * 65)
print("GMV 渠道异动分析报告（前周 vs 上周）")
print("=" * 65)
print(f"\n总GMV：前周 {total_prev} 万元 → 上周 {total_curr} 万元")
print(f"绝对变化：{total_delta} 万元  |  变化率：{total_delta/total_prev*100:.1f}%\n")

cols_display = ["渠道", "前周GMV", "上周GMV", "GMV变化额", "GMV变化率%", "拖累贡献度%"]
print(result[cols_display].to_string(index=False))

# ─────────────────────────────────────────────
# 5. 主要拖累渠道识别
# ─────────────────────────────────────────────
drag_channels = df[df["GMV变化额"] < 0].sort_values("GMV变化额")

print("\n─── 负向贡献渠道（拖累项）排序 ───")
for _, row in drag_channels.iterrows():
    print(
        f"  {row['渠道']:6s}  变化额: {row['GMV变化额']:>6.0f} 万元  "
        f"变化率: {row['GMV变化率%']:>6.1f}%  "
        f"拖累贡献度: {row['拖累贡献度%']:>6.1f}%"
    )

# ─────────────────────────────────────────────
# 6. 结构变化分析
# ─────────────────────────────────────────────
print("\n─── 渠道结构占比变化 ───")
cols_struct = ["渠道", "前周占比%", "上周占比%", "占比变化pct"]
print(df[cols_struct].to_string(index=False))

# ─────────────────────────────────────────────
# 7. 关键结论输出
# ─────────────────────────────────────────────
top_drag = drag_channels.iloc[0]
print(f"\n[关键结论]")
print(f"  最大拖累渠道：{top_drag['渠道']}")
print(f"  该渠道 GMV 下降 {abs(top_drag['GMV变化额']):.0f} 万元（{top_drag['GMV变化率%']:.1f}%），")
print(f"  占总跌幅的 {top_drag['拖累贡献度%']:.1f}%，是本周 GMV 下滑的核心原因。")

bright_channels = df[df["GMV变化额"] > 0]
if not bright_channels.empty:
    print(f"\n  正向渠道（亮点）：")
    for _, row in bright_channels.iterrows():
        print(
            f"    {row['渠道']}：+{row['GMV变化额']:.0f} 万元（+{row['GMV变化率%']:.1f}%）"
        )

print("\n分析完成。")
