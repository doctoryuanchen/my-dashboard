import pandas as pd
import plotly.express as px
import streamlit as st

# --- 1. 網頁基本設定 ---
st.set_page_config(page_title="人生升級導航系統", layout="wide")
st.title("🧭 人生升級導航系統 v3.5")

# --- 2. 各分頁 CSV 網址 ---
URL_RESPONSES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRMM2s35c-Mf6UNwgnQ1rAeWTa2n_MiSXNV4mEEeNzP1P9E6WPfjRIrO-Lk-qhhVTHMOzCnbUgtqvM6/pub?gid=1414323635&single=true&output=csv"
URL_GOLD = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRMM2s35c-Mf6UNwgnQ1rAeWTa2n_MiSXNV4mEEeNzP1P9E6WPfjRIrO-Lk-qhhVTHMOzCnbUgtqvM6/pub?gid=869000102&single=true&output=csv"
URL_EFFICIENCY = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRMM2s35c-Mf6UNwgnQ1rAeWTa2n_MiSXNV4mEEeNzP1P9E6WPfjRIrO-Lk-qhhVTHMOzCnbUgtqvM6/pub?gid=1621294329&single=true&output=csv"
URL_REWARDS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRMM2s35c-Mf6UNwgnQ1rAeWTa2n_MiSXNV4mEEeNzP1P9E6WPfjRIrO-Lk-qhhVTHMOzCnbUgtqvM6/pub?gid=683129744&single=true&output=csv"
URL_GOALS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRMM2s35c-Mf6UNwgnQ1rAeWTa2n_MiSXNV4mEEeNzP1P9E6WPfjRIrO-Lk-qhhVTHMOzCnbUgtqvM6/pub?gid=780605673&single=true&output=csv"


# --- 3. 超級清洗與標準化函數 ---
def load_and_clean_data(url, is_efficiency_tab=False):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()

        # 📅 強效日期統整與現代錨定
        date_found = False
        for col in ["日期", "Timestamp", "date"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                if not df[col].str.contains("202").any():
                    df[col] = "2026/" + df[col]

                df["_clean_datetime"] = pd.to_datetime(df[col], errors="coerce")
                df["_clean_date"] = df["_clean_datetime"].dt.date
                date_found = True
                break

        if not date_found or "_clean_date" not in df.columns:
            df["_clean_date"] = pd.to_datetime("today").date()

        # 💡 針對學習效率分頁進行欄位與數值對齊
        if is_efficiency_tab:
            for col in df.columns:
                if "實際投入" in col:
                    df["實際投入時間"] = pd.to_numeric(
                        df[col], errors="coerce"
                    ).fillna(0)
                if "推進時間" in col:
                    df["課程進度推進時間"] = pd.to_numeric(
                        df[col], errors="coerce"
                    ).fillna(0)
                if "效率" in col and col != "效率":
                    val = (
                        df[col]
                        .astype(str)
                        .str.replace("%", "")
                        .str.strip()
                    )
                    df["效率"] = pd.to_numeric(val, errors="coerce")
                    df.loc[df["效率"] > 1, "效率"] = df["效率"] / 100

            if "效率" not in df.columns:
                df["效率"] = df["課程進度推進時間"] / df["實際投入時間"].replace(
                    0, 1
                )
            df["效率"] = pd.to_numeric(df["效率"], errors="coerce").fillna(0)

        df = df[df["_clean_date"] > pd.to_datetime("2025-01-01").date()]
        df = df.dropna(subset=["_clean_date"])
        return df
    except Exception as e:
        return None


# --- 4. 日期篩選函數 ---
def filter_by_date(df, start, end):
    if df is None or df.empty:
        return None
    return df[(df["_clean_date"] >= start) & (df["_clean_date"] <= end)]


# --- 5. 預先載入資料 ---
df_res_raw = load_and_clean_data(URL_RESPONSES)
df_gold_raw = load_and_clean_data(URL_GOLD)
df_eff_raw = load_and_clean_data(URL_EFFICIENCY, is_efficiency_tab=True)
df_reward_raw = load_and_clean_data(URL_REWARDS)
df_goals_raw = load_and_clean_data(URL_GOALS)

# --- 6. 左側邊欄：全域日期區間篩選器 ---
st.sidebar.header("📅 全域導航時間篩選")

all_dates = []
for df in [df_res_raw, df_gold_raw, df_eff_raw]:
    if df is not None and not df.empty:
        valid_dates = [d for d in df["_clean_date"].tolist() if pd.notnull(d)]
        all_dates.extend(valid_dates)

if all_dates:
    min_date = min(all_dates)
    max_date = max(all_dates)
else:
    min_date = pd.to_datetime("today").date()
    max_date = pd.to_datetime("today").date()

start_date, end_date = st.sidebar.date_input(
    "選擇時間區間", [min_date, max_date], min_value=min_date, max_value=max_date
)

# --- 7. 執行篩選過濾 ---
df_res = filter_by_date(df_res_raw, start_date, end_date)
df_gold = filter_by_date(df_gold_raw, start_date, end_date)
df_eff = filter_by_date(df_eff_raw, start_date, end_date)
df_reward = df_reward_raw
df_goals = df_goals_raw

COLOR_MAP = {
    "🟢 穩定運行": "#2ecc71",
    "🔵 能量充盈": "#3498db",
    "🟡 普通": "#f1c40f",
    "🟠 警覺減壓": "#e67e22",
    "🔴 警報修復": "#e74c3c",
}

tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 即時燈號與燃料", "💰 金幣與獎勵", "📖 學習效率", "🎯 目標達成率"]
)

# ==========================================
# --- Tab 1: 即時燈號與燃料 ---
# ==========================================
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💡 目前狀態燈號")
        if df_res is not None and not df_res.empty:
            lamp_col = "運作燈號" if "運作燈號" in df_res.columns else "本次模式"
            if lamp_col in df_res.columns:
                df_res[lamp_col] = df_res[lamp_col].astype(str).str.strip()
                fig_pie = px.pie(
                    df_res,
                    names=lamp_col,
                    hole=0.4,
                    color=lamp_col,
                    color_discrete_map=COLOR_MAP,
                )
                st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        st.subheader("🔥 好奇燃料比趨勢 (每日平均值)")
        if df_res is not None and not df_res.empty and "好奇燃料比" in df_res.columns:
            df_res["好奇燃料比"] = pd.to_numeric(
                df_res["好奇燃料比"], errors="coerce"
            ).fillna(0)
            df_fuel_daily = (
                df_res.groupby("_clean_date")["好奇燃料比"].mean().reset_index()
            )
            df_fuel_daily["顯示日期"] = df_fuel_daily["_clean_date"].astype(str)
            fig_fuel = px.line(
                df_fuel_daily,
                x="顯示日期",
                y="好奇燃料比",
                markers=True,
                labels={"顯示日期": "日期", "好奇燃料比": "日平均燃料比"},
            )
            fig_fuel.update_xaxes(type="category")
            st.plotly_chart(fig_fuel, use_container_width=True)

# ==========================================
# --- Tab 2: 金幣總覽與獎勵 ---
# ==========================================
with tab2:
    if df_gold is not None and not df_gold.empty:
        st.subheader("💰 金幣數據綜合看板")

        all_possible_gold = ["主線金幣", "支線金幣", "每日總金幣", "累積金幣"]
        for col in df_gold.columns:
            if col in all_possible_gold:
                df_gold[col] = pd.to_numeric(df_gold[col], errors="coerce").fillna(
                    0
                )

        if "主線金幣" not in df_gold.columns:
            df_gold["主線金幣"] = 0

        df_gold["每日學習總金幣"] = df_gold["主線金幣"]
        df_gold["累積學習總金幣"] = df_gold["每日學習總金幣"].cumsum()
        df_gold["其他累積金幣"] = df_gold["累積金幣"] - df_gold["累積學習總金幣"]
        
        # 💡【修正錯字】精準防呆，不再亂創變數
        df_gold.loc[df_gold["其他累積金幣"] < 0, "其他累積金幣"] = 0

        df_gold["顯示日期"] = df_gold["_clean_date"].astype(str)

        g_col1, g_col2 = st.columns(2)

        with g_col1:
            st.write("📊 每日金幣進帳對比 (日常總額 vs 純主線學習)")
            df_daily_melt = pd.melt(
                df_gold,
                id_vars=["顯示日期"],
                value_vars=["每日總金幣", "每日學習總金幣"],
                var_name="金幣類型",
                value_name="金幣數量",
            )
            fig_daily_gold = px.bar(
                df_daily_melt,
                x="顯示日期",
                y="金幣數量",
                color="金幣類型",
                barmode="group",
                labels={"顯示日期": "日期", "金幣數量": "金幣數量"},
                color_discrete_map={
                    "每日總金幣": "#2196F3",
                    "每日學習總金幣": "#4CAF50",
                },
            )
            fig_daily_gold.update_xaxes(type="category")
            st.plotly_chart(fig_daily_gold, use_container_width=True)

        with g_col2:
            st.write("📈 長期金幣累積總量 (💡 基礎學習累積在下方作為地基)")
            df_cum_melt = pd.melt(
                df_gold,
                id_vars=["顯示日期"],
                value_vars=["累積學習總金幣", "其他累積金幣"],
                var_name="資產類型",
                value_name="累積總額",
            )
            fig_cum_gold = px.area(
                df_cum_melt,
                x="顯示日期",
                y="累積總額",
                color="資產類型",
                labels={"顯示日期": "日期", "累積總額": "金幣總量"},
                color_discrete_map={
                    "累積學習總金幣": "#FF9800",
                    "其他累積金幣": "#FFE082",
                },
            )
            fig_cum_gold.update_xaxes(type="category")
            st.plotly_chart(fig_cum_gold, use_container_width=True)

    if df_reward is not None and not df_reward.empty:
        st.subheader("🎁 獎勵兌換進度")
        if "還差多少" in df_reward.columns and "獎勵" in df_reward.columns:
            fig_reward = px.bar(
                df_reward,
                x="還差多少",
                y="獎勵",
                orientation="h",
                text="目前累積",
                color="還差多少",
                color_continuous_scale="Reds_r",
            )
            st.plotly_chart(fig_reward, use_container_width=True)

# ==========================================
# --- Tab 3: 學習效率 ---
# ==========================================
with tab3:
    st.subheader("📝 科目學習數據多維度分析")
    if df_eff is not None and not df_eff.empty:
        df_eff_work = df_eff.copy()
        df_eff_work["顯示日期"] = df_eff_work["_clean_date"].astype(str)

        sum_actual = df_eff_work["實際投入時間"].sum()
        sum_progress = df_eff_work["課程進度推進時間"].sum()
        valid_eff = df_eff_work[df_eff_work["效率"] > 0]["效率"]
        avg_efficiency = valid_eff.mean() if not valid_eff.empty else 0

        st.markdown("#### 📊 目前選定時間區段內合計")
        col_card1, col_card2, col_card3 = st.columns(3)
        with col_card1:
            st.metric(
                label="⏳ 區間實際投入總時數", value=f"{sum_actual:.1f} min"
            )
        with col_card2:
            st.metric(
                label="📈 區間進度推進總時數", value=f"{sum_progress:.1f} min"
            )
        with col_card3:
            st.metric(
                label="⚡ 區間平均整體效率", value=f"{avg_efficiency * 100:.1f}%"
            )
        st.write("---")

        df_all_subjects = (
            df_eff_work.groupby("顯示日期")[["實際投入時間", "課程進度推進時間"]]
            .sum()
            .reset_index()
        )
        df_all_subjects["科目"] = "✨ 全科加總"
        df_all_subjects["效率"] = (
            df_all_subjects["課程進度推進時間"]
            / df_all_subjects["實際投入時間"].replace(0, 1)
        )

        df_combined_eff = pd.concat(
            [df_eff_work, df_all_subjects], ignore_index=True
        )
        available_subjects = list(df_combined_eff["科目"].unique())
        sel_sub = st.multiselect(
            "🔍 選擇查看科目 (包含全科統計選項)",
            available_subjects,
            default=available_subjects,
        )
        df_sub_filtered = df_combined_eff[df_combined_eff["科目"].isin(sel_sub)]

        col_eff1, col_eff2 = st.columns(2)
        with col_eff1:
            st.write("⏳ 1. 各科目學習時數 (實際 vs 推進)")
            if not df_sub_filtered.empty:
                df_melted = pd.melt(
                    df_sub_filtered,
                    id_vars=["顯示日期", "科目"],
                    value_vars=["實際投入時間", "課程進度推進時間"],
                    var_name="時間類型",
                    value_name="總時數(min)",
                )
                fig_compare = px.bar(
                    df_melted,
                    x="顯示日期",
                    y="總時數(min)",
                    color="時間類型",
                    barmode="group",
                    facet_col="科目" if len(sel_sub) > 1 else None,
                    labels={"顯示日期": "日期"},
                )
                fig_compare.update_xaxes(type="category")
                st.plotly_chart(fig_compare, use_container_width=True)

        with col_eff2:
            st.write("⚡ 2. 學習效率折線圖")
            if not df_sub_filtered.empty:
                fig_rate = px.line(
                    df_sub_filtered,
                    x="顯示日期",
                    y="效率",
                    color="科目",
                    markers=True,
                    labels={"顯示日期": "日期", "效率": "效率 (推進/投入)"},
                )
                fig_rate.update_xaxes(type="category")
                fig_rate.update_yaxes(tickformat=".1%")
                st.plotly_chart(fig_rate, use_container_width=True)

# ==========================================
# --- Tab 4: 目標達成率 ---
# ==========================================
with tab4:
    st.subheader("🎯 目標達成率指標")
    if df_eff is not None and not df_eff.empty and "效率" in df_eff.columns:
        valid_eff = df_eff[df_eff["效率"] > 0]["效率"]
        current_eff_pct = (valid_eff.mean() * 100) if not valid_eff.empty else 0
    else:
        current_eff_pct = 0

    if current_eff_pct >= 75:
        status_text = "🚀 高效推進"
        status_delta = "表現優異，請保持！"
    elif current_eff_pct >= 45:
        status_text = "🟢 穩定推進中"
        status_delta = "節奏正常"
    else:
        status_text = "⚠️ 需調整狀態"
        status_delta = "效率偏低，建議減壓"

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric(
            label="📊 當前區間平均效率",
            value=f"{current_eff_pct:.1f}%",
            delta="與選擇區間連動",
        )
    with col_m2:
        st.metric(label="📅 區間核心狀態", value=status_text, delta=status_delta)
    with col_m3:
        st.metric(
            label="🏆 數據記錄天數",
            value=f"{(end_date - start_date).days + 1} 天",
        )

    if df_goals is not None and not df_goals.empty:
        st.write("📋 課程目標追蹤明細")
        st.dataframe(df_goals, use_container_width=True)