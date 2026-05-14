"""
注册转化率漏斗异动分析
分析本月注册转化率从 3.2% 下降至 2.1%，损失约 8000 名注册用户的根因
"""

import pandas as pd
import numpy as np

# ============================================================
# 1. 原始数据构建
# ============================================================

data = {
    "步骤": ["落地页访问", "点击注册按钮", "填写表单", "提交成功"],
    "上月UV": [500000, 125000, 62500, 16000],
    "本月UV": [520000, 109200, 49140, 10920],
    "上月步骤转化率": [None, 0.250, 0.500, 0.256],
    "本月步骤转化率": [None, 0.210, 0.450, 0.222],
}

df = pd.DataFrame(data)

# ============================================================
# 2. 整体指标确认
# ============================================================

last_landing = df.loc[0, "上月UV"]
curr_landing = df.loc[0, "本月UV"]
last_reg     = df.loc[3, "上月UV"]
curr_reg     = df.loc[3, "本月UV"]

last_overall_cvr = last_reg / last_landing
curr_overall_cvr = curr_reg / curr_landing
delta_cvr        = curr_overall_cvr - last_overall_cvr
lost_users       = last_landing * last_overall_cvr - curr_landing * curr_overall_cvr   # 理论口径
# 题目给定损失 8000，以题目口径为准
given_lost_users = 8000

print("=" * 60)
print("【整体指标】")
print(f"  落地页UV：上月 {last_landing:,}  → 本月 {curr_landing:,}  (+{(curr_landing/last_landing-1)*100:.1f}%)")
print(f"  注册成功UV：上月 {last_reg:,}  → 本月 {curr_reg:,}")
print(f"  整体注册转化率：上月 {last_overall_cvr*100:.2f}%  → 本月 {curr_overall_cvr*100:.2f}%")
print(f"  转化率绝对下降：{delta_cvr*100:.2f} ppt")
print(f"  注册用户损失（题目口径）：约 {given_lost_users:,} 人")

# ============================================================
# 3. 各步骤转化率变化 & 步骤间UV流失
# ============================================================

print("\n" + "=" * 60)
print("【各漏斗步骤详情】")

steps = df["步骤"].tolist()
last_uvs = df["上月UV"].tolist()
curr_uvs = df["本月UV"].tolist()
last_cvrs = df["上月步骤转化率"].tolist()
curr_cvrs = df["本月步骤转化率"].tolist()

step_results = []
for i in range(len(steps)):
    uv_delta      = curr_uvs[i] - last_uvs[i]
    uv_delta_pct  = uv_delta / last_uvs[i] * 100
    if i == 0:
        cvr_delta = None
        cvr_delta_abs = None
    else:
        cvr_delta     = (curr_cvrs[i] - last_cvrs[i]) * 100   # ppt
        cvr_delta_abs = curr_cvrs[i] - last_cvrs[i]
    step_results.append({
        "步骤": steps[i],
        "上月UV": last_uvs[i],
        "本月UV": curr_uvs[i],
        "UV变化": uv_delta,
        "UV变化率%": round(uv_delta_pct, 2),
        "上月步骤转化率%": None if last_cvrs[i] is None else round(last_cvrs[i]*100, 2),
        "本月步骤转化率%": None if curr_cvrs[i] is None else round(curr_cvrs[i]*100, 2),
        "转化率变化ppt": None if cvr_delta is None else round(cvr_delta, 2),
    })

df_result = pd.DataFrame(step_results)
print(df_result.to_string(index=False))

# ============================================================
# 4. 各步骤对整体转化率下降的贡献拆解（链式求导法）
# ============================================================
# 整体转化率 = CVR1 * CVR2 * CVR3（步骤1=点击注册按钮，2=填写表单，3=提交成功）
# 用"其余步骤保持上月水平"来单独估算每步骤的贡献

print("\n" + "=" * 60)
print("【各步骤对整体转化率下降的贡献拆解（单因素敏感性）】")

CVR_last = [last_cvrs[1], last_cvrs[2], last_cvrs[3]]   # 上月各步骤转化率
CVR_curr = [curr_cvrs[1], curr_cvrs[2], curr_cvrs[3]]   # 本月各步骤转化率

baseline_overall = CVR_last[0] * CVR_last[1] * CVR_last[2]

contributions = []
for i, step_name in enumerate(["点击注册按钮", "填写表单", "提交成功"]):
    # 只改变第 i 步，其余保持上月
    cvr_mix = list(CVR_last)
    cvr_mix[i] = CVR_curr[i]
    scenario_overall = cvr_mix[0] * cvr_mix[1] * cvr_mix[2]
    contrib_ppt = (scenario_overall - baseline_overall) * 100
    contributions.append({
        "步骤": step_name,
        "单因素影响(ppt)": round(contrib_ppt, 3),
        "占总降幅比例%": round(contrib_ppt / (delta_cvr * 100) * 100, 1)
    })

df_contrib = pd.DataFrame(contributions)
print(df_contrib.to_string(index=False))

# 各步骤对损失注册用户数的贡献
print("\n【各步骤对损失注册用户的贡献估算（单因素，基于本月落地页UV）】")
for row in contributions:
    lost_by_step = abs(row["单因素影响(ppt)"] / 100) * curr_landing
    print(f"  {row['步骤']}：约损失 {lost_by_step:,.0f} 个注册用户  ({row['占总降幅比例%']}%)")

# ============================================================
# 5. 优先级排序（按影响量从大到小）
# ============================================================

print("\n" + "=" * 60)
print("【问题步骤优先级排序】")
df_contrib_sorted = df_contrib.sort_values("单因素影响(ppt)").reset_index(drop=True)
for rank, row in df_contrib_sorted.iterrows():
    lost_by_step = abs(row["单因素影响(ppt)"] / 100) * curr_landing
    print(f"  P{rank+1}  {row['步骤']}  | 转化率影响 {row['单因素影响(ppt)']} ppt "
          f"| 占总降幅 {row['占总降幅比例%']}%"
          f"| 估计损失注册用户 {lost_by_step:,.0f}")

# ============================================================
# 6. 漏斗各步骤 UV 绝对流失
# ============================================================

print("\n" + "=" * 60)
print("【漏斗各步骤绝对UV流失（本月 vs 上月）】")
for i in range(1, len(steps)):
    # 在上月进入量相同的假设下，本步骤因转化率下降导致的流失
    uv_loss_due_to_cvr = (CVR_last[i-1] - CVR_curr[i-1]) * last_uvs[i-1]
    print(f"  {steps[i-1]} → {steps[i]}：转化率 {last_cvrs[i]*100:.1f}% → {curr_cvrs[i]*100:.1f}%，"
          f"因转化率下降估计多流失 {uv_loss_due_to_cvr:,.0f} UV")

print("\n分析完成。")
