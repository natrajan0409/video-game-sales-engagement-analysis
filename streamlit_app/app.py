"""
Video Game Sales and Engagement Analysis
Streamlit Interactive Dashboard
"""
import os
import sys

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Path setup ───────────────────────────────────────────────────────────────
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.data_loader import DataLoader
from src.data_cleaner import clean_games, clean_vgsales, merge_datasets

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Video Game Analytics",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Plot helpers ─────────────────────────────────────────────────────────────
def px_scatter_with_optional_ols(*args, trendline="ols", **kwargs):
    if trendline == "ols":
        try:
            import statsmodels.api  # noqa: F401
        except ImportError:
            st.warning("`statsmodels` is not installed; trendlines have been disabled.")
            return px.scatter(*args, **kwargs)
    return px.scatter(*args, trendline=trendline, **kwargs)


def subheader_chart(title: str, chart_type: str):
    st.subheader(title)
    st.caption(f"Chart Type: {chart_type}")

# ── Data loading (cached) ────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading datasets...")
def load_all_data():
    loader = DataLoader(os.path.join(ROOT, "Rawdata"))
    raw_games = loader.load_games()
    raw_sales = loader.load_vgsales()
    games = clean_games(raw_games)
    sales = clean_vgsales(raw_sales)
    merged = merge_datasets(games, sales)
    return games, sales, merged


games_df, sales_df, merged_df = load_all_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🎮 Video Game Analytics")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["Overview & KPIs", "Game Engagement", "Sales Analysis", "Merged Insights"],
)

st.sidebar.markdown("---")
st.sidebar.caption("Data: games.csv + vgsales.csv")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 0 — OVERVIEW & KPIs
# ═══════════════════════════════════════════════════════════════════════════════
if page == "Overview & KPIs":
    st.title("🎮 Video Game Sales and Engagement Analysis")
    st.markdown("**Domain:** Gaming and Entertainment Analytics | **Source:** GUVI Capstone Project")
    st.markdown("---")

    # KPI row
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Games (Engagement)", f"{len(games_df):,}")
    k2.metric("Total Sales Records", f"{len(sales_df):,}")
    k3.metric("Avg User Rating", f"{games_df['Rating'].mean():.2f} / 5")
    k4.metric("Global Sales (B)", f"{sales_df['Global_Sales'].sum()/1000:.2f}B")
    k5.metric("Merged Records", f"{len(merged_df):,}")

    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        subheader_chart("Top 10 Best-Selling Games", "Horizontal Bar Chart")
        top10 = (sales_df.groupby("Name")["Global_Sales"]
                 .sum().nlargest(10).reset_index())
        fig = px.bar(top10, x="Global_Sales", y="Name", orientation="h",
                     color="Global_Sales", color_continuous_scale="Blues",
                     labels={"Global_Sales": "Global Sales (M)", "Name": ""})
        fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False,
                          height=380)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        subheader_chart("Regional Sales Share", "Pie Chart")
        region_sales = pd.Series({
            "North America": sales_df["NA_Sales"].sum(),
            "Europe":        sales_df["EU_Sales"].sum(),
            "Japan":         sales_df["JP_Sales"].sum(),
            "Other":         sales_df["Other_Sales"].sum(),
        })
        fig = px.pie(values=region_sales.values, names=region_sales.index,
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)

    subheader_chart("Platform Sales Landscape", "Bar Chart")
    plat_sales = (sales_df.groupby("Platform")["Global_Sales"]
                  .sum().nlargest(15).reset_index())
    fig = px.bar(plat_sales, x="Platform", y="Global_Sales",
                 color="Global_Sales", color_continuous_scale="Viridis",
                 labels={"Global_Sales": "Global Sales (M)"})
    fig.update_layout(coloraxis_showscale=False, height=350)
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — GAME ENGAGEMENT (games.csv)
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Game Engagement":
    st.title("📊 Game Engagement Analysis")
    st.markdown("*Based on games.csv — ratings, plays, wishlists, backlogs*")
    st.markdown("---")

    # Filter controls
    col_f1, col_f2 = st.columns(2)
    min_rating = col_f1.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.1)
    genres_available = sorted(games_df["Primary Genre"].unique().tolist())
    selected_genres = col_f2.multiselect("Filter by Genre", genres_available,
                                          default=genres_available[:5])

    filtered = games_df[
        (games_df["Rating"] >= min_rating) &
        (games_df["Primary Genre"].isin(selected_genres if selected_genres else genres_available))
    ]

    r1c1, r1c2 = st.columns(2)

    with r1c1:
        subheader_chart("Q1 — Top Rated Games", "Horizontal Bar Chart")
        top_rated = filtered.nlargest(10, "Rating")[["Title", "Rating", "Plays"]]
        fig = px.bar(top_rated, x="Rating", y="Title", orientation="h",
                     color="Rating", color_continuous_scale="RdYlGn",
                     labels={"Rating": "User Rating", "Title": ""})
        fig.update_layout(yaxis=dict(autorange="reversed"),
                          coloraxis_showscale=False, height=380)
        st.plotly_chart(fig, use_container_width=True)

    with r1c2:
        subheader_chart("Q6 — Rating Distribution", "Histogram")
        fig = px.histogram(filtered, x="Rating", nbins=20,
                           marginal="box", color_discrete_sequence=["#2196F3"])
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)

    r2c1, r2c2 = st.columns(2)

    with r2c1:
        subheader_chart("Q3 — Genre Distribution", "Horizontal Bar Chart")
        genre_counts = filtered["Primary Genre"].value_counts().reset_index()
        genre_counts.columns = ["Genre", "Count"]
        fig = px.bar(genre_counts.head(12), x="Count", y="Genre", orientation="h",
                     color="Count", color_continuous_scale="Blues")
        fig.update_layout(yaxis=dict(autorange="reversed"),
                          coloraxis_showscale=False, height=380)
        st.plotly_chart(fig, use_container_width=True)

    with r2c2:
        subheader_chart("Q7 — Top 10 Most Wishlisted Games", "Horizontal Bar Chart")
        top_wish = filtered.nlargest(10, "Wishlist")[["Title", "Wishlist", "Rating"]]
        fig = px.bar(top_wish, x="Wishlist", y="Title", orientation="h",
                     color="Rating", color_continuous_scale="RdYlGn")
        fig.update_layout(yaxis=dict(autorange="reversed"), height=380)
        st.plotly_chart(fig, use_container_width=True)

    subheader_chart("Q5 — Game Release Trend", "Area Chart")
    release = (filtered.dropna(subset=["Release Year"])
               .groupby("Release Year").size().reset_index(name="Count"))
    fig = px.area(release, x="Release Year", y="Count",
                  labels={"Count": "Games Released"})
    st.plotly_chart(fig, use_container_width=True)

    subheader_chart("Q4 — Backlog vs Wishlist (Top 20 by Backlogs)", "Grouped Bar Chart")
    bw = filtered.nlargest(20, "Backlogs")[["Title", "Backlogs", "Wishlist"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=bw["Title"], y=bw["Backlogs"], name="Backlogs"))
    fig.add_trace(go.Bar(x=bw["Title"], y=bw["Wishlist"], name="Wishlist"))
    fig.update_layout(barmode="group", xaxis_tickangle=-45, height=400)
    st.plotly_chart(fig, use_container_width=True)

    subheader_chart("Q8 — Avg Plays per Genre", "Horizontal Bar Chart")
    plays_genre = (games_df.groupby("Primary Genre")["Plays"]
                   .mean().sort_values(ascending=False).reset_index())
    plays_genre.columns = ["Genre", "Avg Plays"]
    fig = px.bar(plays_genre.head(12), x="Avg Plays", y="Genre", orientation="h",
                 color="Avg Plays", color_continuous_scale="Purples")
    fig.update_layout(yaxis=dict(autorange="reversed"),
                      coloraxis_showscale=False, height=380)
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — SALES ANALYSIS (vgsales.csv)
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Sales Analysis":
    st.title("💰 Sales Analysis")
    st.markdown("*Based on vgsales.csv — regional sales, platforms, publishers*")
    st.markdown("---")

    year_min = int(sales_df["Year"].min())
    year_max = int(sales_df["Year"].max())
    year_range = st.slider("Year Range", year_min, year_max, (1995, 2016))
    filtered_sales = sales_df[sales_df["Year"].between(*year_range)]

    r1c1, r1c2 = st.columns(2)

    with r1c1:
        subheader_chart("Q11 — Best-Selling Platforms", "Horizontal Bar Chart")
        plat = (filtered_sales.groupby("Platform")["Global_Sales"]
                .sum().nlargest(10).reset_index())
        fig = px.bar(plat, x="Global_Sales", y="Platform", orientation="h",
                     color="Global_Sales", color_continuous_scale="Teal")
        fig.update_layout(yaxis=dict(autorange="reversed"),
                          coloraxis_showscale=False, height=380)
        st.plotly_chart(fig, use_container_width=True)

    with r1c2:
        subheader_chart("Q13 — Top Publishers by Sales", "Horizontal Bar Chart")
        pub = (filtered_sales.groupby("Publisher")["Global_Sales"]
               .sum().nlargest(10).reset_index())
        fig = px.bar(pub, x="Global_Sales", y="Publisher", orientation="h",
                     color="Global_Sales", color_continuous_scale="Oranges")
        fig.update_layout(yaxis=dict(autorange="reversed"),
                          coloraxis_showscale=False, height=380)
        st.plotly_chart(fig, use_container_width=True)

    subheader_chart("Q12 — Game Releases & Sales Over Years", "Combined Bar + Line Chart")
    yearly = (filtered_sales.groupby("Year")
              .agg(game_count=("Name", "count"), total_sales=("Global_Sales", "sum"))
              .reset_index())
    fig = go.Figure()
    fig.add_trace(go.Bar(x=yearly["Year"], y=yearly["game_count"],
                         name="Games Released", yaxis="y", opacity=0.6))
    fig.add_trace(go.Scatter(x=yearly["Year"], y=yearly["total_sales"],
                              name="Global Sales (M)", yaxis="y2", mode="lines+markers",
                              line=dict(color="red", width=2)))
    fig.update_layout(
        yaxis=dict(title="Games Released"),
        yaxis2=dict(title="Global Sales (M)", overlaying="y", side="right"),
        height=400, legend=dict(x=0.01, y=0.99)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Q17 — Regional Genre Preferences (Heatmap)")
    region_genre = (filtered_sales.groupby("Genre")[["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]]
                    .sum().reset_index())
    fig = px.imshow(
        region_genre.set_index("Genre")[["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]],
        color_continuous_scale="YlOrRd",
        aspect="auto",
        labels=dict(color="Sales (M)"),
    )
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Q16 — Platform Sales Evolution")
    top6 = sales_df.groupby("Platform")["Global_Sales"].sum().nlargest(6).index.tolist()
    selected_platforms = st.multiselect("Select Platforms", top6, default=top6)
    pt = (filtered_sales[filtered_sales["Platform"].isin(selected_platforms)]
          .groupby(["Year", "Platform"])["Global_Sales"].sum().reset_index())
    fig = px.line(pt, x="Year", y="Global_Sales", color="Platform",
                  markers=True, labels={"Global_Sales": "Sales (M)"})
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — MERGED INSIGHTS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Merged Insights":
    st.title("🔗 Merged Insights — Sales + Engagement")
    st.markdown("*Inner join of games.csv and vgsales.csv on game title*")
    st.markdown("---")

    r1c1, r1c2 = st.columns(2)

    with r1c1:
        st.subheader("Q22 — Rating vs Global Sales")
        fig = px_scatter_with_optional_ols(
            merged_df,
            x="Rating",
            y="Global_Sales",
            color="Genre",
            hover_data=["Title", "Platform"],
            opacity=0.6,
            labels={"Global_Sales": "Global Sales (M)"},
        )
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

    with r1c2:
        st.subheader("Q21 — Genre vs Global Sales")
        genre_sales = (merged_df.groupby("Genre")["Global_Sales"]
                       .sum().sort_values(ascending=False).reset_index())
        fig = px.pie(genre_sales, values="Global_Sales", names="Genre",
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Q26 — Genre: Engagement Score vs Avg Sales")
    merged_df["engagement_score"] = merged_df["Plays"] + merged_df["Wishlist"]
    eng_sales = (merged_df.groupby("Genre")
                 .agg(avg_engagement=("engagement_score", "mean"),
                      avg_sales=("Global_Sales", "mean"),
                      game_count=("Title", "count"))
                 .reset_index())
    fig = px.scatter(eng_sales, x="avg_sales", y="avg_engagement",
                     size="game_count", color="Genre", text="Genre",
                     labels={"avg_sales": "Avg Sales (M)",
                              "avg_engagement": "Avg Engagement (Plays + Wishlist)"},
                     size_max=40)
    fig.update_traces(textposition="top center")
    fig.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    r2c1, r2c2 = st.columns(2)

    with r2c1:
        st.subheader("Q25 — Wishlist vs Global Sales")
        fig = px_scatter_with_optional_ols(
            merged_df,
            x="Wishlist",
            y="Global_Sales",
            color="Genre",
            opacity=0.5,
            labels={"Global_Sales": "Global Sales (M)",
                    "Wishlist": "Wishlist Count"},
        )
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)

    with r2c2:
        st.subheader("Q27 — Correlation Matrix")
        cols = ["Rating", "Plays", "Wishlist", "Backlogs", "Global_Sales"]
        corr = merged_df[cols].corr()
        fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r",
                        zmin=-1, zmax=1, aspect="auto")
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Q29 — Top Genre + Platform Combinations")
    gp = (merged_df.groupby(["Genre", "Platform"])["Global_Sales"]
          .sum().sort_values(ascending=False).head(15).reset_index())
    gp["combo"] = gp["Genre"] + " + " + gp["Platform"]
    fig = px.bar(gp, x="Global_Sales", y="combo", orientation="h",
                 color="Global_Sales", color_continuous_scale="Viridis",
                 labels={"Global_Sales": "Global Sales (M)", "combo": ""})
    fig.update_layout(yaxis=dict(autorange="reversed"),
                      coloraxis_showscale=False, height=480)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Q30 — Regional Sales Heatmap by Genre")
    hm = (merged_df.groupby("Genre")[["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]]
          .sum()
          .rename(columns={"NA_Sales": "North America", "EU_Sales": "Europe",
                            "JP_Sales": "Japan", "Other_Sales": "Other"}))
    fig = px.imshow(hm, text_auto=".1f", color_continuous_scale="YlOrRd",
                    aspect="auto", labels=dict(color="Sales (M)"))
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Q23 — Platforms with High-Rated Games (Rating >= 4.0)")
    high = merged_df[merged_df["Rating"] >= 4.0]["Platform"].value_counts().head(10).reset_index()
    high.columns = ["Platform", "Count"]
    fig = px.bar(high, x="Count", y="Platform", orientation="h",
                 color="Count", color_continuous_scale="Greens")
    fig.update_layout(yaxis=dict(autorange="reversed"),
                      coloraxis_showscale=False, height=360)
    st.plotly_chart(fig, use_container_width=True)
