import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="資產配置計算器", page_icon="📊", layout="centered")

# ── 樣式 ──────────────────────────────────────────────────
st.markdown("""
<style>
  .block-container { padding-top: 2rem; max-width: 760px; }
  .metric-card {
    background: #191d1b; border: 1px solid #333a36;
    border-radius: 10px; padding: 14px 18px; margin-bottom: 6px;
  }
  .section-label {
    font-size: 11px; color: #7a9080; letter-spacing: 2px;
    font-family: monospace; margin: 18px 0 8px;
  }
  .action-box {
    background: #1e3010; border: 1px solid #2a4010;
    border-radius: 8px; padding: 12px 16px; margin-top: 8px;
    color: #a3e635; font-size: 13px;
  }
  .warn-box {
    background: #3d2e0a; border: 1px solid #fbbf24;
    border-radius: 8px; padding: 12px 16px; margin-top: 8px;
    color: #fbbf24; font-size: 13px;
  }
  .danger-box {
    background: #3d1515; border: 1px solid #f87171;
    border-radius: 8px; padding: 12px 16px; margin-top: 8px;
    color: #f87171; font-size: 13px;
  }
</style>
""", unsafe_allow_html=True)

# ── 標題 ──────────────────────────────────────────────────
st.markdown("#### `ASSET ALLOCATION · CALCULATOR`")
st.title("📊 資產配置計算器")
st.caption("輸入目標佔比與各資產市值，即時查看差距與建議動作")
st.divider()

# ── 目標佔比設定 ──────────────────────────────────────────
st.markdown('<div class="section-label">── 目標佔比設定（可自行調整，需合計 100%）</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    t_vt    = st.number_input("🌍 VT",       min_value=0.0, max_value=100.0, value=65.0, step=0.5, format="%.1f")
with col2:
    t_div   = st.number_input("💰 高息 ETF", min_value=0.0, max_value=100.0, value=20.0, step=0.5, format="%.1f")
with col3:
    t_stock = st.number_input("📈 個股",     min_value=0.0, max_value=100.0, value=5.0,  step=0.5, format="%.1f")
with col4:
    t_cash  = st.number_input("🏦 現金",     min_value=0.0, max_value=100.0, value=10.0, step=0.5, format="%.1f")

total_target = t_vt + t_div + t_stock + t_cash

if abs(total_target - 100) < 0.5:
    st.success(f"✓ 目標合計 {total_target:.1f}%")
else:
    st.error(f"⚠ 目標合計 {total_target:.1f}%，請調整至 100%")

st.divider()

# ── 目前市值輸入 ──────────────────────────────────────────
st.markdown('<div class="section-label">── 目前各資產市值（NT$）</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    a_vt    = st.number_input("🌍 VT 市值",       min_value=0, value=0, step=1000, format="%d")
with c2:
    a_div   = st.number_input("💰 高息 ETF 市值", min_value=0, value=0, step=1000, format="%d")
with c3:
    a_stock = st.number_input("📈 個股市值",       min_value=0, value=0, step=1000, format="%d")
with c4:
    a_cash  = st.number_input("🏦 現金",           min_value=0, value=0, step=1000, format="%d")

total_amt = a_vt + a_div + a_stock + a_cash

if total_amt > 0:
    def fmt(n):
        if n >= 100_000_000: return f"{n/100_000_000:.2f} 億"
        if n >= 10_000:      return f"{n/10_000:.1f} 萬"
        return f"{n:,}"

    st.metric("💼 總資產", f"NT$ {fmt(total_amt)}")
    st.divider()

    # ── 計算 ──────────────────────────────────────────────
    assets = [
        {"label": "🌍 VT",       "target": t_vt,    "amount": a_vt,    "color": "#a3e635"},
        {"label": "💰 高息 ETF", "target": t_div,   "amount": a_div,   "color": "#fbbf24"},
        {"label": "📈 個股",     "target": t_stock,  "amount": a_stock, "color": "#60a5fa"},
        {"label": "🏦 現金",     "target": t_cash,  "amount": a_cash,  "color": "#4ade80"},
    ]

    for a in assets:
        a["actual"] = a["amount"] / total_amt * 100
        a["diff"]   = a["actual"] - a["target"]
        a["gap_amt"] = abs(a["amount"] - total_amt * a["target"] / 100)

    # ── 視覺化：雙層長條圖 ────────────────────────────────
    st.markdown('<div class="section-label">── 配置分布</div>', unsafe_allow_html=True)

    labels  = [a["label"]  for a in assets]
    actuals = [a["actual"] for a in assets]
    targets = [a["target"] for a in assets]
    colors  = [a["color"]  for a in assets]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="實際佔比", x=labels, y=actuals,
        marker_color=colors, opacity=0.85,
        text=[f"{v:.1f}%" for v in actuals],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name="目標佔比", x=labels, y=targets,
        marker_color=colors, opacity=0.3,
        text=[f"{v:.1f}%" for v in targets],
        textposition="outside",
    ))
    fig.update_layout(
        barmode="group",
        plot_bgcolor="#111413", paper_bgcolor="#111413",
        font=dict(color="#b0c4b8", family="monospace"),
        yaxis=dict(title="佔比 %", range=[0, max(max(actuals), max(targets)) + 10],
                   gridcolor="#333a36", zerolinecolor="#333a36"),
        xaxis=dict(gridcolor="#333a36"),
        legend=dict(bgcolor="#191d1b", bordercolor="#333a36", borderwidth=1),
        height=340, margin=dict(t=20, b=10, l=10, r=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── 差距圖 ────────────────────────────────────────────
    diffs      = [a["diff"] for a in assets]
    diff_colors = []
    for d in diffs:
        if abs(d) < 2:   diff_colors.append("#a3e635")
        elif abs(d) < 5: diff_colors.append("#fbbf24")
        else:            diff_colors.append("#f87171")

    fig2 = go.Figure(go.Bar(
        x=labels, y=diffs,
        marker_color=diff_colors, opacity=0.85,
        text=[f"{d:+.1f}%" for d in diffs],
        textposition="outside",
    ))
    fig2.add_hline(y=0, line_color="#7a9080", line_width=1)
    fig2.add_hline(y=2,  line_dash="dot", line_color="#a3e635", line_width=1, opacity=0.4)
    fig2.add_hline(y=-2, line_dash="dot", line_color="#a3e635", line_width=1, opacity=0.4)
    fig2.update_layout(
        title=dict(text="差距（實際% − 目標%）", font=dict(color="#7a9080", size=12)),
        plot_bgcolor="#111413", paper_bgcolor="#111413",
        font=dict(color="#b0c4b8", family="monospace"),
        yaxis=dict(title="差距 pp", gridcolor="#333a36", zerolinecolor="#333a36"),
        xaxis=dict(gridcolor="#333a36"),
        height=280, margin=dict(t=40, b=10, l=10, r=10),
        showlegend=False,
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ── 明細表 ────────────────────────────────────────────
    st.markdown('<div class="section-label">── 明細</div>', unsafe_allow_html=True)

    df = pd.DataFrame([{
        "資產":   a["label"],
        "市值":   f"NT$ {fmt(a['amount'])}",
        "實際%":  f"{a['actual']:.1f}%",
        "目標%":  f"{a['target']:.1f}%",
        "差距":   f"{a['diff']:+.1f}%",
        "狀態":   "✓ 達標" if abs(a["diff"]) < 2 else ("⚠ 偏移" if abs(a["diff"]) < 5 else "✕ 過偏"),
    } for a in assets])

    st.dataframe(df, use_container_width=True, hide_index=True)

    # ── 建議動作 ──────────────────────────────────────────
    st.divider()
    st.markdown('<div class="section-label">── 建議動作</div>', unsafe_allow_html=True)

    need_action = [a for a in assets if abs(a["diff"]) >= 2]
    need_action.sort(key=lambda a: abs(a["diff"]), reverse=True)

    if not need_action:
        st.markdown('<div class="action-box">✓ 所有資產均在目標 ±2% 內，系統平衡，無需操作。</div>', unsafe_allow_html=True)
    else:
        for a in need_action:
            over = a["diff"] > 0
            box_class = "warn-box" if abs(a["diff"]) < 5 else "danger-box"
            arrow = "▲ 過高" if over else "▼ 不足"
            if over:
                msg = f"暫緩買入，新資金優先導向不足的資產<br>若要立即調回，需減少約 NT${fmt(a['gap_amt'])}"
            else:
                msg = f"優先用新資金補足<br>需補入約 <b>NT${fmt(a['gap_amt'])}</b> 才能達到目標佔比"
            st.markdown(
                f'<div class="{box_class}">'
                f'<b>{arrow} {a["label"]}</b>　'
                f'{a["actual"]:.1f}% → 目標 {a["target"]:.1f}%（差 {a["diff"]:+.1f}%）<br>'
                f'{msg}</div>',
                unsafe_allow_html=True
            )

    st.markdown("""
    <div class="action-box" style="margin-top:14px;">
      💡 再平衡優先序：① 新資金導向不足項目　② 暫停過高項目買入　③ 最後才賣出
    </div>
    """, unsafe_allow_html=True)

else:
    st.info("👆 請在上方輸入各資產市值，系統將自動計算佔比與差距")

st.divider()
st.caption("資產系統決策表 · v1.0 · 建倉期適用")