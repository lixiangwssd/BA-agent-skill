#!/usr/bin/env python3
"""
策略优化求解脚本
目标：在 90 万周预算约束下，最大化 DAU 增量
约束：整体 ROI >= 3.0，整体 CAC <= 15 元
互斥：同一(人群, 渠道, 时段)最多选 1 条策略

按置信度分三版方案分别求解：
- 保守方案：仅高置信度策略
- 推荐方案：高+中置信度策略
- 激进方案：全部策略（高+中+低）

生成日期：2026-05-17
"""

import pandas as pd
from pulp import *
import os

# ============================================================
# 1. 数据读取
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

# 从策略库读取策略效果数据（来自 strategy-library/strategies.csv）
strategies_path = os.path.join(PROJECT_DIR, "strategy-library", "strategies.csv")
df = pd.read_csv(strategies_path, encoding='utf-8-sig')

print(f"策略库总数：{len(df)} 条")
print(f"置信度分布：")
print(df['置信度'].value_counts().to_string())
print()

# ============================================================
# 2. 参数定义（来源标注）
# ============================================================

# 来自 wiki/metrics.md: 目标函数 = 最大化 DAU增量
OBJECTIVE = 'DAU增量'

# 来自 wiki/metrics.md: ROI >= 3.0
ROI_THRESHOLD = 3.0

# 来自 wiki/metrics.md: CAC <= 15 元
CAC_THRESHOLD = 15.0

# 来自 wiki/constraints.md: 周预算 90 万
TOTAL_BUDGET = 900000  # 单位：元

# 来自 strategy-library/mutual-exclusion.md:
# 同一(人群, 渠道, 时段)最多选 1 个(素材类型, 补贴档位)组合
MUTUAL_EXCLUSION_KEYS = ['人群', '渠道', '时段']

# ============================================================
# 3. 计算每条策略的投入金额和收入
# ============================================================

# 投入金额 = CAC × DAU增量（因为 CAC = 投入金额 / 新客数）
df['投入金额'] = df['CAC'] * df['DAU增量']

# GMV = ROI × 投入金额（因为 ROI = GMV / 投入金额）
df['GMV'] = df['ROI'] * df['投入金额']

print(f"目标函数：最大化 {OBJECTIVE}")
print(f"约束：ROI >= {ROI_THRESHOLD}, CAC <= {CAC_THRESHOLD}, 周预算 <= {TOTAL_BUDGET/10000:.0f} 万")
print(f"投入金额范围：{df['投入金额'].min():.0f} ~ {df['投入金额'].max():.0f} 元")
print(f"DAU增量范围：{df['DAU增量'].min()} ~ {df['DAU增量'].max()}")
print()

# ============================================================
# 4. 按置信度分组
# ============================================================

df_high = df[df['置信度'] == '高'].copy()
df_mid = df[df['置信度'].isin(['高', '中'])].copy()
df_all = df.copy()

print(f"保守方案策略池（高置信度）：{len(df_high)} 条")
print(f"推荐方案策略池（高+中置信度）：{len(df_mid)} 条")
print(f"激进方案策略池（全部）：{len(df_all)} 条")
print()

# ============================================================
# 5. 优化求解函数
# ============================================================

def solve_optimization(subset_df, plan_name):
    """
    对给定策略子集求解 0-1 整数线性规划

    决策变量：x[i] ∈ {0, 1}，表示策略 i 是否被选中
    目标函数：max Σ x[i] * DAU增量[i]
    约束：
      1. 预算约束：Σ x[i] * 投入金额[i] <= 90万
      2. ROI约束：Σ x[i] * GMV[i] - 3.0 * Σ x[i] * 投入金额[i] >= 0
      3. CAC约束：Σ x[i] * 投入金额[i] - 15 * Σ x[i] * DAU增量[i] <= 0
      4. 互斥约束：每个(人群, 渠道, 时段)最多选 1 条策略
    """

    if len(subset_df) == 0:
        print(f"  [{plan_name}] 策略池为空，无法求解")
        return None, None

    prob = LpProblem(f"策略优化_{plan_name}", LpMaximize)

    # 决策变量
    indices = subset_df.index.tolist()
    x = {i: LpVariable(f"x_{subset_df.loc[i, '策略ID']}", cat='Binary') for i in indices}

    # 目标函数：最大化 DAU 增量总和
    prob += lpSum(x[i] * subset_df.loc[i, 'DAU增量'] for i in indices), "最大化DAU增量"

    # 约束1：总预算 <= 90万（来自 wiki/constraints.md）
    prob += lpSum(x[i] * subset_df.loc[i, '投入金额'] for i in indices) <= TOTAL_BUDGET, "预算约束"

    # 约束2：整体 ROI >= 3.0（来自 wiki/metrics.md）
    prob += (
        lpSum(x[i] * subset_df.loc[i, 'GMV'] for i in indices) -
        ROI_THRESHOLD * lpSum(x[i] * subset_df.loc[i, '投入金额'] for i in indices) >= 0
    ), "ROI约束"

    # 约束3：整体 CAC <= 15 元（来自 wiki/metrics.md）
    prob += (
        lpSum(x[i] * subset_df.loc[i, '投入金额'] for i in indices) -
        CAC_THRESHOLD * lpSum(x[i] * subset_df.loc[i, 'DAU增量'] for i in indices) <= 0
    ), "CAC约束"

    # 约束4：互斥约束（来自 strategy-library/mutual-exclusion.md）
    groups = subset_df.groupby(MUTUAL_EXCLUSION_KEYS)
    for group_key, group_df in groups:
        group_indices = group_df.index.tolist()
        if len(group_indices) > 1:
            prob += lpSum(x[i] for i in group_indices) <= 1, f"互斥_{group_key}"

    # 求解
    prob.solve(PULP_CBC_CMD(msg=0))

    status = LpStatus[prob.status]
    print(f"  [{plan_name}] 求解状态：{status}")

    if status != 'Optimal':
        print(f"  [{plan_name}] 未找到最优解")
        return None, {'方案版本': plan_name, '求解状态': status}

    # 提取选中的策略
    selected = [i for i in indices if value(x[i]) == 1]
    result_df = subset_df.loc[selected].copy()
    result_df['方案版本'] = plan_name

    # 汇总指标
    total_dau = result_df['DAU增量'].sum()
    total_cost = result_df['投入金额'].sum()
    total_gmv = result_df['GMV'].sum()
    overall_roi = total_gmv / total_cost if total_cost > 0 else 0
    overall_cac = total_cost / total_dau if total_dau > 0 else 0

    print(f"  [{plan_name}] 选中策略数：{len(result_df)}")
    print(f"  [{plan_name}] 预期 DAU 增量：{total_dau:,.0f}")
    print(f"  [{plan_name}] 总投入：{total_cost:,.0f} 元（预算利用率 {total_cost/TOTAL_BUDGET*100:.1f}%）")
    print(f"  [{plan_name}] 整体 ROI：{overall_roi:.2f}（阈值 {ROI_THRESHOLD}）")
    print(f"  [{plan_name}] 整体 CAC：{overall_cac:.2f} 元（阈值 {CAC_THRESHOLD}）")
    print()

    summary = {
        '方案版本': plan_name,
        'DAU增量': total_dau,
        '总投入': total_cost,
        '总GMV': total_gmv,
        'ROI': overall_roi,
        'CAC': overall_cac,
        '策略数': len(result_df),
        '预算利用率': total_cost / TOTAL_BUDGET,
        '求解状态': status
    }

    return result_df, summary


# ============================================================
# 6. 分别求解三版方案
# ============================================================

print("=" * 60)
print("开始求解...")
print("=" * 60)
print()

results = []
summaries = []

for subset, name in [(df_high, '保守方案'), (df_mid, '推荐方案'), (df_all, '激进方案')]:
    result_df, summary = solve_optimization(subset, name)
    if result_df is not None:
        results.append(result_df)
    if summary is not None:
        summaries.append(summary)

# ============================================================
# 7. 输出结果
# ============================================================

OUTPUT_DIR = os.path.join(PROJECT_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 7.1 输出结果 CSV
if results:
    all_results = pd.concat(results, ignore_index=True)

    output_cols = ['方案版本', '策略ID', '人群', '渠道', '时段', '素材类型', '补贴档位',
                   'DAU增量', 'ROI', 'CAC', 'CTR', 'CVR', '单用户GMV',
                   '投入金额', 'GMV', '数据来源', '置信度', '最早执行', '最近执行']

    available_cols = [c for c in output_cols if c in all_results.columns]
    result_csv_path = os.path.join(OUTPUT_DIR, "optimization-2026-05-17-result.csv")
    all_results[available_cols].to_csv(result_csv_path, index=False, encoding='utf-8-sig')
    print(f"\n结果已保存：{result_csv_path}")

# 7.2 输出 Markdown 报告
if summaries:
    report_path = os.path.join(OUTPUT_DIR, "optimization-2026-05-17.md")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 下周投放策略优化方案\n\n")
        f.write("生成日期：2026-05-17\n\n")

        # 结论
        f.write("## 结论\n\n")
        rec = next((s for s in summaries if s['方案版本'] == '推荐方案' and s['求解状态'] == 'Optimal'), None)
        if rec is None:
            rec = next((s for s in summaries if s['求解状态'] == 'Optimal'), None)
        if rec:
            f.write(f"推荐采用**推荐方案**（高+中置信度策略），预期周 DAU 增量 ")
            f.write(f"**{rec['DAU增量']:,.0f}**，ROI {rec['ROI']:.2f}，CAC {rec['CAC']:.1f} 元，")
            f.write(f"兼顾收益确定性与规模。\n\n")

        # 三版方案对比
        f.write("## 三版方案对比\n\n")
        f.write("| 指标 | 保守方案 | 推荐方案 | 激进方案 |\n")
        f.write("|------|---------|---------|--------|\n")

        def get_s(name):
            return next((s for s in summaries if s['方案版本'] == name), None)

        con = get_s('保守方案')
        rec_s = get_s('推荐方案')
        agg = get_s('激进方案')

        def fv(s, key, fmt_str):
            if s is None or s.get('求解状态') != 'Optimal':
                return "N/A"
            return fmt_str.format(s[key])

        def fmt_cost(s):
            if s is None or s.get('求解状态') != 'Optimal':
                return "N/A"
            return f"{s['总投入']/10000:,.1f}"

        def fmt_util(s):
            if s is None or s.get('求解状态') != 'Optimal':
                return "N/A"
            return f"{s['预算利用率']*100:.1f}%"

        f.write(f"| DAU增量 | {fv(con, 'DAU增量', '{:,.0f}')} | {fv(rec_s, 'DAU增量', '{:,.0f}')} | {fv(agg, 'DAU增量', '{:,.0f}')} |\n")
        f.write(f"| 总投入(万) | {fmt_cost(con)} | {fmt_cost(rec_s)} | {fmt_cost(agg)} |\n")
        f.write(f"| ROI | {fv(con, 'ROI', '{:.2f}')} | {fv(rec_s, 'ROI', '{:.2f}')} | {fv(agg, 'ROI', '{:.2f}')} |\n")
        f.write(f"| CAC(元) | {fv(con, 'CAC', '{:.1f}')} | {fv(rec_s, 'CAC', '{:.1f}')} | {fv(agg, 'CAC', '{:.1f}')} |\n")
        f.write(f"| 策略数 | {fv(con, '策略数', '{}')} | {fv(rec_s, '策略数', '{}')} | {fv(agg, '策略数', '{}')} |\n")
        f.write(f"| 预算利用率 | {fmt_util(con)} | {fmt_util(rec_s)} | {fmt_util(agg)} |\n")
        f.write("\n")

        # 推荐方案明细
        f.write("## 推荐方案明细\n\n")
        rec_df = next((r for r in results if r['方案版本'].iloc[0] == '推荐方案'), None)
        if rec_df is None and results:
            rec_df = results[-1]

        if rec_df is not None:
            f.write("### 策略明细\n\n")
            f.write("| 策略ID | 人群 | 渠道 | 时段 | 素材类型 | 补贴档位 | DAU增量 | ROI | CAC | 置信度 |\n")
            f.write("|--------|------|------|------|---------|---------|---------|-----|-----|--------|\n")
            for _, row in rec_df.sort_values('DAU增量', ascending=False).iterrows():
                f.write(f"| {row['策略ID']} | {row['人群']} | {row['渠道']} | {row['时段']} | {row['素材类型']} | {row['补贴档位']} | {row['DAU增量']:,.0f} | {row['ROI']:.2f} | {row['CAC']:.1f} | {row['置信度']} |\n")
            f.write("\n")

            # 按人群分布
            f.write("### 按人群分布\n\n")
            f.write("| 人群 | 策略数 | DAU增量 | 投入金额(万) | 整体ROI |\n")
            f.write("|------|--------|---------|------------|--------|\n")
            for crowd, grp in rec_df.groupby('人群'):
                grp_roi = grp['GMV'].sum() / grp['投入金额'].sum() if grp['投入金额'].sum() > 0 else 0
                f.write(f"| {crowd} | {len(grp)} | {grp['DAU增量'].sum():,.0f} | {grp['投入金额'].sum()/10000:.1f} | {grp_roi:.2f} |\n")
            f.write("\n")

            # 按渠道分布
            f.write("### 按渠道分布\n\n")
            f.write("| 渠道 | 策略数 | DAU增量 | 投入金额(万) | 整体ROI |\n")
            f.write("|------|--------|---------|------------|--------|\n")
            for channel, grp in rec_df.groupby('渠道'):
                grp_roi = grp['GMV'].sum() / grp['投入金额'].sum() if grp['投入金额'].sum() > 0 else 0
                f.write(f"| {channel} | {len(grp)} | {grp['DAU增量'].sum():,.0f} | {grp['投入金额'].sum()/10000:.1f} | {grp_roi:.2f} |\n")
            f.write("\n")

        # 风险说明
        f.write("## 风险说明\n\n")
        if rec_df is not None:
            low_count = len(rec_df[rec_df['置信度'] == '低'])
            mid_count = len(rec_df[rec_df['置信度'] == '中'])
            high_count = len(rec_df[rec_df['置信度'] == '高'])
            f.write(f"- 推荐方案中：高置信度 {high_count} 条，中置信度 {mid_count} 条\n")
            if low_count > 0:
                f.write(f"- 低置信度策略：{low_count} 条（建议小流量验证）\n")
            f.write("- 建议验证方式：对中置信度策略设置监控，效果偏离超 20% 时触发人工复核\n")
        f.write("\n")

        # 数据校验信息
        f.write("## 数据校验信息\n\n")
        f.write(f"- 策略池总数：{len(df)} 条（高 {len(df[df['置信度']=='高'])} / 中 {len(df[df['置信度']=='中'])} / 低 {len(df[df['置信度']=='低'])}）\n")
        for s in summaries:
            f.write(f"- {s['方案版本']}求解状态：{s['求解状态']}\n")
        f.write(f"- 约束配置：ROI≥{ROI_THRESHOLD}, CAC≤{CAC_THRESHOLD}元, 预算≤{TOTAL_BUDGET/10000:.0f}万\n")
        f.write(f"- 复现方式：`python3 outputs/optimization-2026-05-17.py`\n")

    print(f"报告已保存：{report_path}")

print("\n求解完成。")
