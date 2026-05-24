import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

# ── 頁面設定（與原 HTML 標題與風格呼應） ──────────────────────────────────
st.set_page_config(page_title="資產系統 · 決策與計算總表", page_icon="📊", layout="wide")

# ── 注入原 HTML 的高級暗黑風 CSS 樣式 ──────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&family=DM+Mono:wght@400;500&display=swap');

  /* 全域基本背景與字型 */
  .stApp {
    background-color: #111413 !important;
    color: #e8ede9 !important;
    font-family: 'Noto Sans TC', sans-serif;
  }
  
  /* 調整 Streamlit 元件邊距與外觀 */
  .block-container { padding-top: 2rem; max-width: 1200px; }
  
  /* 原 HTML 變數與卡片風格改寫為 Streamlit 適用 class */
  .metric-card {
    background: #191d1b; border: 1px solid #333a36;
    border-radius: 8px; padding: 14px 18px; margin-bottom: 6px;
  }
  .section-label {
    font-family: 'DM Mono', monospace;
    font-size: 13px; color: #a3e635; letter-spacing: 1px;
    text-transform: uppercase; margin: 24px 0 12px;
    border-left: 4px solid #a3e635; padding-left: 8px;
  }
  
  /* 自訂狀態提示盒 */
  .action-box {
    background: #1e3010; border: 1px solid #3a5a20;
    border-radius: 6px; padding: 12px 16px; margin-top: 8px;
    color: #a3e635; font-size: 14px;
  }
  .warn-box {
    background: #3d2e0a; border: 1px solid #6b4a10;
    border-radius: 6px; padding: 12px 16px; margin-top: 8px;
    color: #fbbf24; font-size: 14px;
  }
  .danger-box {
    background: #3d1515; border: 1px solid #6b2020;
    border-radius: 6px; padding: 12px 16px; margin-top: 8px;
    color: #f87171; font-size: 14px;
  }
  
  /* 頂部 Header 風格 */
  .custom-header {
    display: flex; justify-content: space-between; align-items: flex-end;
    margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #333a36;
  }
  .header-left h1 { font-size: 28px; font-weight: 700; color: #a3e635; margin:0; }
  .header-left p { font-size: 13px; color: #b0c4b8; margin-top: 4px; font-family: 'DM Mono', monospace; }
  .header-right { font-size: 13px; color: #7a9080; font-family: 'DM Mono', monospace; text-align: right; }
  
  /* 核心原則 Banner */
  .principle-banner {
    background: #1e3010; border: 1px solid #3d5a1a; border-radius: 6px;
    padding: 12px 16px; margin-bottom: 24px; font-size: 15px;
  }
  .principle-banner span { color: #b0c4b8; font-weight: 300; }
</style>
""", unsafe_allow_html=True)

# ── 系統頂部標題列 (與 HTML 一致) ──────────────────────────────────
st.markdown("""
<div class="custom-header">
  <div class="header-left">
    <h1>資產系統 · 決策與計算總表</h1>
    <p>INVESTMENT SYSTEM · DECISION & CALCULATION REFERENCE</p>
  </div>
  <div class="header-right">
    更新日期: 2026.05.16<br>
    版本: v1.0 · 建倉期適用 (Streamlit 整合版)
  </div>
</div>
<div class="principle-banner">
  ⚡ 核心原則 <span>全部決策 = 看「市值佔比」⇒ 對照規則 ⇒ 執行動作。不判斷市場，不臨場決策。</span>
</div>
""", unsafe_allow_html=True)

# ── 建立分頁標籤 (Tabs) ──────────────────────────────────────────
tab1, tab2 = st.tabs(["📊 資產動態平衡計算器", "📜 系統運作規則與決策總表"])

# ==========================================
# TAB 1: 資產動態平衡計算器
# ==========================================
with tab1:
    # ── 目標佔比設定 ──
    st.markdown('<div class="section-label">📊 1. 目標佔比設定（可自行調整，需合計 100%）</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        t_vt    = st.number_input("🌍 VT 目標 (%)",       min_value=0.0, max_value=100.0, value=65.0, step=0.5, format="%.1f")
    with col2:
        t_div   = st.number_input("💰 高息 ETF 目標 (%)", min_value=0.0, max_value=100.0, value=15.0, step=0.5, format="%.1f")
    with col3:
        t_stock = st.number_input("📈 個股目標 (%)",     min_value=0.0, max_value=100.0, value=5.0,  step=0.5, format="%.1f")
    with col4:
        t_cash  = st.number_input("🏦 現金目標 (%)",     min_value=0.0, max_value=100.0, value=15.0, step=0.5, format="%.1f")

    total_target = t_vt + t_div + t_stock + t_cash
    if abs(total_target - 100) < 0.1:
        st.success(f"✓ 目標比例合計：{total_target:.1f}%")
    else:
        st.error(f"⚠ 目標比例合計：{total_target:.1f}%，請調整資產權重至 100%")

    # ── 目前市值輸入 ──
    st.markdown('<div class="section-label">💵 2. 輸入當前資產資金市值（NT$）</div>', unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        a_vt    = st.number_input("🌍 VT 當前市值",       min_value=0, value=0, step=10000, format="%d")
    with c2:
        a_div   = st.number_input("💰 高息 ETF 當前市值", min_value=0, value=0, step=10000, format="%d")
    with c3:
        a_stock = st.number_input("📈 個股當前市值",       min_value=0, value=0, step=10000, format="%d")
    with c4:
        a_cash  = st.number_input("🏦 現金當前金額",       min_value=0, value=0, step=10000, format="%d")

    total_amt = a_vt + a_div + a_stock + a_cash

    if total_amt > 0:
        def fmt(n):
            if n >= 100_000_000: return f"{n/100_000_000:.2f} 億"
            if n >= 10_000:      return f"{n/10_000:.1f} 萬"
            return f"{n:,}"

        st.markdown(f"<h3 style='color:#e8ede9;'>💼 當前總資產規模：<span style='color:#a3e635;'>NT$ {fmt(total_amt)}</span></h3>", unsafe_allow_html=True)

        # 資料計算
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

        # ── 視覺化圖表 ──
        st.markdown('<div class="section-label">📈 3. 資產權重與目標差距圖表</div>', unsafe_allow_html=True)
        
        g1, g2 = st.columns(2)
        
        with g1:
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
                marker_color=colors, opacity=0.25,
                text=[f"{v:.1f}%" for v in targets],
                textposition="outside",
            ))
            fig.update_layout(
                barmode="group",
                title=dict(text="實際佔比 vs 目標佔比", font=dict(color="#e8ede9", size=14)),
                plot_bgcolor="#111413", paper_bgcolor="#111413",
                font=dict(color="#b0c4b8", family="monospace"),
                yaxis=dict(title="佔比 %", gridcolor="#333a36", zerolinecolor="#333a36"),
                xaxis=dict(gridcolor="#333a36"),
                legend=dict(bgcolor="#191d1b", bordercolor="#333a36", borderwidth=1),
                height=350, margin=dict(t=50, b=10, l=10, r=10),
            )
            st.plotly_chart(fig, use_container_width=True)

        with g2:
            diffs = [a["diff"] for a in assets]
            diff_colors = ["#a3e635" if abs(d) < 2 else ("#fbbf24" if abs(d) < 5 else "#f87171") for d in diffs]

            fig2 = go.Figure(go.Bar(
                x=labels, y=diffs,
                marker_color=diff_colors, opacity=0.85,
                text=[f"{d:+.1f}%" for d in diffs],
                textposition="outside",
            ))
            fig2.add_hline(y=0, line_color="#7a9080", line_width=1)
            fig2.update_layout(
                title=dict(text="分配偏離度（實際% − 目標%）", font=dict(color="#e8ede9", size=14)),
                plot_bgcolor="#111413", paper_bgcolor="#111413",
                font=dict(color="#b0c4b8", family="monospace"),
                yaxis=dict(title="偏離 pp", gridcolor="#333a36", zerolinecolor="#333a36"),
                xaxis=dict(gridcolor="#333a36"),
                height=350, margin=dict(t=50, b=10, l=10, r=10),
                showlegend=False,
            )
            st.plotly_chart(fig2, use_container_width=True)

        # ── 數據明細 ──
        df = pd.DataFrame([{
            "資產類別": a["label"],
            "當前市值": f"NT$ {fmt(a['amount'])}",
            "實際佔比": f"{a['actual']:.1f}%",
            "目標佔比": f"{a['target']:.1f}%",
            "偏離度": f"{a['diff']:+.1f}%",
            "平衡狀態": "✓ 正常" if abs(a["diff"]) < 2 else ("⚠ 觀察" if abs(a["diff"]) < 5 else "✕ 嚴重失衡"),
        } for a in assets])
        st.dataframe(df, use_container_width=True, hide_index=True)

        # ── 自動觸發決策狀態與操作建議 ──
        st.markdown('<div class="section-label">⚡ 4. 系統自動對照規則 · 建議執行動作</div>', unsafe_allow_html=True)
        
        # 抓取關鍵指標：VT佔比與現金佔比
        vt_actual = next(a["actual"] for a in assets if "VT" in a["label"])
        cash_actual = next(a["actual"] for a in assets if "現金" in a["label"])
        
        # 動態規則診斷
        c_rule1, c_rule2 = st.columns(2)
        with c_rule1:
            st.markdown("**🥇 VT 佔比決策診斷：**")
            if vt_actual > 75:
                st.markdown('<div class="danger-box">🚨 <b>【狀態：牛市過熱 (&gt;75%)】</b><br>• <b>停止</b> DCA VT。<br>• 投資現金轉補高息或累積現金，持續觀察 6 個月。<br>• 6個月後若高息&lt;15%且現金&lt;5%，方可小幅賣出 VT。</div>', unsafe_allow_html=True)
            elif 65 <= vt_actual <= 75:
                st.markdown('<div class="action-box">🟩 <b>【狀態：正常區 (65–75%)】</b><br>• <b>持續定期定額 (DCA) VT</b>。<br>• 保持紀律，不做任何額外變更。</div>', unsafe_allow_html=True)
            elif 55 <= vt_actual < 65:
                st.markdown('<div class="warn-box">🟨 <b>【狀態：關注區 (55–65%)】</b><br>• 持續 DCA VT。<br>• 提高注意力，檢查市場距離歷史高點跌幅，確認是否觸發機會現金條件。</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="danger-box">🟥 <b>【狀態：警示區 (&lt;55%)】</b><br>• 持續 DCA VT。<br>• 檢查是否觸發機會現金分批買進機制。<br>• 若持續 3 個月未觸發跌幅條件，啟動 10% 機會現金安全閥。</div>', unsafe_allow_html=True)
                
        with c_rule2:
            st.markdown("**🥉 現金佔比決策診斷：**")
            if cash_actual > 20:
                st.markdown('<div class="action-box">🟩 <b>【狀態：現金充裕 (&gt;20%)】</b><br>• 正常系統運作，允許進行季度再平衡，持續 DCA VT。</div>', unsafe_allow_html=True)
            elif 10 <= cash_actual <= 20:
                st.markdown('<div class="warn-box">🟨 <b>【狀態：現金觀察區 (10–20%)】</b><br>• 僅允許使用新流入資金（薪資/股息）進行配置調整。<br>• <b>嚴禁賣出 VT</b>。</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="danger-box">🟥 <b>【狀態：鎖定模式 (&lt;10%)】</b><br>• <b>全面停止再平衡與賣出操作</b>。<br>• 處於 Fully Invested 狀態，讓市場自由運轉，靜待新資金流入或市場回檔。</div>', unsafe_allow_html=True)

        # 具體買賣補倉金額建議
        st.write("")
        st.markdown("**🔧 再平衡操作調整細節：**")
        need_action = [a for a in assets if abs(a["diff"]) >= 2]
        need_action.sort(key=lambda a: abs(a["diff"]), reverse=True)
        
        if not need_action:
            st.info("💡 目前所有資產配置偏離度均在 ±2% 內，資產結構完美，無需進行手動再平衡。")
        else:
            for a in need_action:
                if a["diff"] > 0:
                    st.markdown(f"• **{a['label']}** 實際比重過高（{a['actual']:.1f}%），高出目標 {a['diff']:+.1f}%。建議**暫緩買入**，若想完全調回平衡，該項目市值需減少約 **NT$ {fmt(a['gap_amt'])}**。")
                else:
                    st.markdown(f"• **{a['label']}** 實際比重不足（{a['actual']:.1f}%），低於目標 {a['diff']:+.1f}%。建議新資金優先導向補倉，需補入約 **NT$ {fmt(a['gap_amt'])}** 達到目標。")
                    
    else:
        st.info("💡 請在上方輸入各資產的當前市值（NT$），系統將會自動為您計算出各資產精準比例、繪製對照圖表，並同步輸出決策動作指引！")

# ==========================================
# TAB 2: 系統運作規則與決策總表 (原本的完整 HTML)
# ==========================================
with tab2:
    st.markdown('<div class="section-label">📜 靜態決策規則手冊（完整底層邏輯對照）</div>', unsafe_allow_html=True)
    
    # 這裡將你原本提供的精美 HTML 規則代碼直接嵌入
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
    <meta charset="UTF-8">
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&family=DM+Mono:wght@400;500&display=swap');
      :root {
        --bg: #111413; --surface: #191d1b; --surface2: #202520; --border: #333a36; --border-soft: #262d28;
        --text: #e8ede9; --text-muted: #b0c4b8; --text-dim: #7a9080; --green: #4ade80; --green-dim: #1a3d26;
        --yellow: #fbbf24; --yellow-dim: #3d2e0a; --red: #f87171; --red-dim: #3d1515; --blue: #60a5fa; --blue-dim: #0f2444; --accent: #a3e635; --accent-dim: #1e3010;
      }
      * { box-sizing: border-box; margin: 0; padding: 0; }
      body { background: var(--bg); color: var(--text); font-family: 'Noto Sans TC', sans-serif; font-size: 14px; line-height: 1.5; padding: 10px; }
      .section-label { font-family: 'DM Mono', monospace; font-size: 12px; color: var(--accent); text-transform: uppercase; margin-bottom: 8px; margin-top: 15px; }
      .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
      .card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 14px; }
      .card-title { font-size: 13px; font-weight:700; text-transform: uppercase; color: var(--text); margin-bottom: 10px; border-bottom: 1px solid var(--border-soft); padding-bottom: 4px;}
      .vt-table { width: 100%; border-collapse: collapse; margin-bottom: 8px; }
      .vt-table th { font-size: 12px; border-bottom: 1px solid var(--border); font-family: 'DM Mono', monospace; color: var(--text-muted); text-align: left; padding: 4px;}
      .vt-table td { padding: 6px 4px; border-bottom: 1px solid var(--border-soft); vertical-align: top; font-size: 13px; }
      .vt-table tr:last-child td { border-bottom: none; }
      .range { font-family: 'DM Mono', monospace; font-weight: bold; }
      .badge { display: inline-block; padding: 1px 6px; border-radius: 3px; font-size: 11px; }
      .badge-green { background: var(--green-dim); color: var(--green); border: 1px solid #2a6040; }
      .badge-yellow { background: var(--yellow-dim); color: var(--yellow); border: 1px solid #6b4a10; }
      .badge-red { background: var(--red-dim); color: var(--red); border: 1px solid #6b2020; }
      .badge-dim { background: var(--surface2); color: var(--text-muted); border: 1px solid var(--border); }
      .action-list { list-style: none; }
      .action-list li { font-size: 12.5px; color: var(--text-muted); }
      .action-list li::before { content: '› '; color: var(--text-dim); }
      .highlight { color: var(--accent); }
      .warn { color: var(--yellow); }
      .stop { color: var(--red); font-weight: 700; }
      .note-box { background: #1a1400; border: 1px solid #3d3000; border-radius: 5px; padding: 6px 10px; font-size: 12px; color: var(--text-muted); margin-top: 6px; }
      .kv { display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid var(--border-soft); font-size: 12.5px; }
      .kv-key { color: var(--text-muted); }
      .kv-val { font-family: 'DM Mono', monospace; color: var(--text); }
      .batch-row { display: flex; gap: 6px; margin-top: 6px; }
      .batch-item { flex: 1; background: var(--surface2); border: 1px solid var(--border); border-radius: 5px; padding: 6px; text-align: center; }
      .batch-item .day { font-size: 11px; color: var(--text-dim); }
      .batch-item .pct { font-size: 18px; font-weight: 700; color: var(--accent); }
      .batch-item .desc { font-size: 11px; color: var(--text-muted); }
      .phase-bar { display: flex; gap: 8px; margin-top: 6px; }
      .phase-item { flex: 1; border-radius: 5px; padding: 8px; border: 1px solid; font-size: 12px; }
      .phase-item.active { background: #1a2e10; border-color: #3a5a20; }
      .phase-item.future { background: var(--surface2); border-color: var(--border); }
      .phase-now { display: inline-block; font-size: 10px; background: var(--accent); color: #0d1a05; font-weight: 700; padding: 0px 4px; border-radius: 2px; }
      .opp-table { width: 100%; border-collapse: collapse; }
      .opp-table th { font-size: 11px; color: var(--text-dim); padding: 4px; border-bottom: 1px solid var(--border); text-align: left;}
      .opp-table td { padding: 6px 4px; border-bottom: 1px solid var(--border-soft); font-size: 12.5px; }
      .mono { font-family: 'DM Mono', monospace; }
      .annual-box { background: var(--surface2); border: 1px solid var(--border); border-radius: 6px; padding: 12px; display: flex; align-items: center; gap: 12px; margin-top: 10px;}
      .annual-date { font-family: 'DM Mono', monospace; font-size: 18px; font-weight: 700; color: var(--accent); }
    </style>
    </head>
    <body>

    <div class="section-label">📊 每月必看 · 兩個佔比</div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">🥇 VT 佔比 · 決策表</div>
        <table class="vt-table">
          <tr><th>VT 佔比</th><th>狀態</th><th>執行動作</th></tr>
          <tr><td class="range" style="color:var(--red);">&gt; 75%</td><td><span class="badge badge-red">牛市過熱</span></td><td><ul class="action-list"><li><span class="stop">停止</span> DCA VT</li><li>投資現金轉補高息/累積</li><li class="warn">6個月後偏低再小幅賣</li></ul></td></tr>
          <tr><td class="range" style="color:var(--accent);">65–75%</td><td><span class="badge badge-green">正常區</span></td><td><ul class="action-list"><li class="highlight">持續 DCA VT</li><li>不做額外動作</li></ul></td></tr>
          <tr><td class="range" style="color:var(--yellow);">55–65%</td><td><span class="badge badge-yellow">關注區</span></td><td><ul class="action-list"><li>持續 DCA VT</li><li>檢查市場距高點與機會現金</li></ul></td></tr>
          <tr><td class="range" style="color:var(--red);">&lt; 55%</td><td><span class="badge badge-red">警示區</span></td><td><ul class="action-list"><li>持續 DCA VT</li><li class="warn">未觸發跌幅3個月啟動安全閥</li></ul></td></tr>
        </table>
        <div class="note-box">⚠ VT 佔比下降是「提高注意力」訊號。是否操作，看機會現金與再平衡條件。</div>
      </div>

      <div class="card">
        <div class="card-title">🥉 現金佔比 · 決策表</div>
        <table class="vt-table">
          <tr><th>現金佔比</th><th>狀態</th><th>執行動作</th></tr>
          <tr><td class="range" style="color:var(--accent);">&gt; 20%</td><td><span class="badge badge-green">充裕</span></td><td><ul class="action-list"><li>系統正常，可再平衡</li><li>持續 DCA VT</li></ul></td></tr>
          <tr><td class="range" style="color:var(--yellow);">10–20%</td><td><span class="badge badge-yellow">觀察區</span></td><td><ul class="action-list"><li>只用新資金調整</li><li class="stop">不賣 VT</li></ul></td></tr>
          <tr><td class="range" style="color:var(--red);">&lt; 10%</td><td><span class="badge badge-red">鎖定模式</span></td><td><ul class="action-list"><li class="stop">停止再平衡與賣出</li><li>現金低 = Fully Invested</li></ul></td></tr>
        </table>
        <div style="margin-top:8px;">
          <div class="kv"><span class="kv-key">🔒 防守現金</span><span class="kv-val">5% · 永遠不動</span></div>
          <div class="kv"><span class="kv-key">⚡ 機會現金</span><span class="kv-val">5–10% · 條件觸發</span></div>
          <div class="kv"><span class="kv-key">🔄 投資現金</span><span class="kv-val">動態 · 主要 DCA VT</span></div>
        </div>
      </div>
    </div>

    <div class="section-label">⚡ 機會現金 · 觸發條件與執行</div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">📉 市場距離史高 · 觸發表</div>
        <table class="opp-table">
          <tr><th>市場跌幅</th><th>動用比例</th><th>時間鎖</th><th>DCA加速</th></tr>
          <tr><td class="mono" style="color:var(--yellow);">−20%</td><td><span class="badge badge-yellow">15%</span></td><td class="mono">≥2週→下階段</td><td><span class="badge badge-dim">×1.25</span></td></tr>
          <tr><td class="mono" style="color:var(--red);">−30%</td><td><span class="badge badge-red">25%</span></td><td class="mono">≥2週→下階段</td><td><span class="badge badge-dim">×1.5</span></td></tr>
          <tr><td class="mono" style="color:var(--red);">−40%</td><td><span class="badge badge-red">25%</span></td><td class="mono">≥1週→下階段</td><td><span class="badge badge-dim">×1.75</span></td></tr>
          <tr><td class="mono" style="color:#ff4444;">−50%</td><td><span class="badge badge-red">15%</span></td><td class="mono">3個月→永久</td><td><span class="badge badge-dim">×2.0</span></td></tr>
        </table>
        <div class="note-box">🔒 安全閥：VT &lt; 50% 持續 3 個月未觸發跌幅，可啟動 10% 機會現金。</div>
      </div>

      <div class="card">
        <div class="card-title">🎯 每階段分批買進 · 3-2-1 法</div>
        <div class="batch-row">
          <div class="batch-item"><div class="day">DAY 1</div><div class="pct">40%</div><div class="desc">確認觸發立即投</div></div>
          <div class="batch-item"><div class="day">DAY 3–4</div><div class="pct">35%</div><div class="desc">觀察2天投第二批</div></div>
          <div class="batch-item"><div class="day">DAY 7–10</div><div class="pct">25%</div><div class="desc">最後一批緩衝</div></div>
        </div>
        <div class="note-box"><b>Q: 分批期間繼續大跌？</b><br>未投入部分合併到下一階段，重新用 3-2-1 法計算。</div>
        <div style="margin-top:6px;">
          <div class="kv"><span class="kv-key">查詢工具</span><span class="kv-val">Google Finance (VT) / TradingView</span></div>
        </div>
      </div>
    </div>

    <div class="section-label">⚖️ 再平衡與 DCA 參數</div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">⚖️ 再平衡 · 三步驟優先序</div>
        <div class="kv"><span class="kv-key">Step 1 優先</span><span class="kv-val" style="color:var(--green)">優先用新資金注入</span></div>
        <div class="kv"><span class="kv-key">Step 2 次之</span><span class="kv-val" style="color:var(--yellow)">暫停某過高資產買進</span></div>
        <div class="kv"><span class="kv-key">Step 3 最後</span><span class="kv-val" style="color:var(--red)">才手動賣出（最後手段）</span></div>
        <div class="note-box"><b>允許賣出 VT 唯一條件：</b><br>VT&gt;75% 且持續6-12個月，且高息&lt;15%與現金&lt;5%全部成立。</div>
      </div>

      <div class="card">
        <div class="card-title">📌 DCA 模式 · 建倉期參數</div>
        <div class="phase-bar">
          <div class="phase-item active">
            <div class="phase-now">NOW</div>
            <div class="phase-label"><b>建倉期（24M）</b></div>
            <div class="phase-content">前12M: 3%/月<br>後12M: 2%/月</div>
          </div>
          <div class="phase-item future">
            <div class="phase-label">穩定期 (VT≈65%)</div>
            <div class="phase-content">固定速度 DCA<br>禁止任意改邏輯</div>
          </div>
        </div>
        <div style="margin-top:6px;">
          <div class="kv"><span class="kv-key">🌍 VT 基準目標</span><span class="kv-val">65%</span></div>
          <div class="kv"><span class="kv-key">💰 高息 ETF</span><span class="kv-val">15–20%</span></div>
          <div class="kv"><span class="kv-key">🏦 現金總池</span><span class="kv-val">10–15%</span></div>
        </div>
      </div>
    </div>

    <div class="section-label">📅 年度系統審查</div>
    <div class="annual-box">
      <div class="annual-date">12 / 31</div>
      <div class="annual-desc">每年12月底評估重大人生變化。是穩定期修改比例與邏輯的唯一合法視窗。</div>
    </div>

    </body>
    </html>
    """
    # 使用 streamlit HTML 組件完美嵌入，自適應高度
    components.html(html_content, height=720, scrolling=True)

# ── 頁尾 ──────────────────────────────────────────────────
st.divider()
st.markdown("<p style='text-align: center; color: #7a9080; font-family: monospace; font-size: 12px;'>資產系統決策表 · v1.0 · 核心原則：看佔比 → 對照規則 → 執行 → 回日常模式</p>", unsafe_allow_html=True)