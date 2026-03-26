"""
pages/3_User_Analysis.py
-------------------------
WHAT THIS FILE DOES:
  Per-user deep dive:
    - Sentiment breakdown
    - Response time stats
    - Message length stats
  All powered by the same df from session_state.
"""

import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import help

sns.set_theme(style="darkgrid")

st.set_page_config(page_title="User Analysis", page_icon="📈", layout="wide")
st.title("📈 User Analysis")

# ── Guard ────────────────────────────────────────────────────────
if 'df' not in st.session_state:
    st.warning("Please upload a WhatsApp chat file from the home page first.")
    st.stop()

df = st.session_state.df

# ── User selector ────────────────────────────────────────────────
user_list = [u for u in df['user'].unique().tolist() if u != 'group_notification']
user_list.sort()
user_list.insert(0, "Overall")
selected_user = st.sidebar.selectbox("Analyse by user", user_list)

# ── Sentiment Analysis ───────────────────────────────────────────
st.subheader("Sentiment analysis")

# Filter df for selected user
if selected_user != 'Overall':
    plot_df = df[df['user'] == selected_user]
else:
    plot_df = df

tab1, tab2 = st.tabs(["Overall sentiment", "Sentiment over time"])

with tab1:
    sentiment_counts = plot_df['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['sentiment', 'count']

    col1, col2 = st.columns(2)

    with col1:
        # Metric cards per sentiment
        pos = sentiment_counts[sentiment_counts['sentiment'] == 'Positive']['count'].sum()
        neu = sentiment_counts[sentiment_counts['sentiment'] == 'Neutral']['count'].sum()
        neg = sentiment_counts[sentiment_counts['sentiment'] == 'Negative']['count'].sum()
        total = len(plot_df)

        c1, c2, c3 = st.columns(3)
        c1.metric("Positive", f"{pos:,}", f"{pos/total*100:.1f}%")
        c2.metric("Neutral",  f"{neu:,}", f"{neu/total*100:.1f}%")
        c3.metric("Negative", f"{neg:,}", f"{neg/total*100:.1f}%")

    with col2:
        fig, ax = plt.subplots()
        colors = ['#1D9E75', '#888780', '#D85A30']
        sns.barplot(
            x='sentiment', y='count',
            data=sentiment_counts,
            palette=colors, ax=ax
        )
        ax.set_title("Sentiment distribution")
        ax.set_xlabel("")
        st.pyplot(fig)
        plt.close()

with tab2:
    # Group by month and sentiment
    # LEARN: groupby() + unstack() is a powerful combo —
    # it creates a table where rows=months, columns=sentiments
    monthly_sentiment = plot_df.groupby(
        ['year', 'month_num', 'month', 'sentiment']
    ).size().reset_index(name='count')

    # Build time label
    monthly_sentiment['time'] = (
        monthly_sentiment['month'] + '-' +
        monthly_sentiment['year'].astype(str)
    )

    pivot = monthly_sentiment.pivot_table(
        index='time', columns='sentiment',
        values='count', fill_value=0
    )

    if not pivot.empty:
        fig, ax = plt.subplots(figsize=(12, 4))
        colors_map = {
            'Positive': '#1D9E75',
            'Neutral':  '#888780',
            'Negative': '#D85A30'
        }
        for col in pivot.columns:
            ax.plot(
                pivot.index, pivot[col],
                label=col,
                color=colors_map.get(col, '#7F77DD'),
                linewidth=2
            )
        ax.legend()
        plt.xticks(rotation='vertical', fontsize=7)
        ax.set_ylabel("Messages")
        st.pyplot(fig)
        plt.close()

st.divider()

# ── Message Length Stats ─────────────────────────────────────────
st.subheader("Message length stats")

real_messages = plot_df[
    (~plot_df['is_media']) &
    (plot_df['user'] != 'group_notification')
].copy()

col1, col2, col3 = st.columns(3)
col1.metric("Avg words/message", f"{real_messages['word_count'].mean():.1f}")
col2.metric("Longest message",   f"{real_messages['word_count'].max()} words")
col3.metric("Shortest message",  f"{real_messages['word_count'].min()} words")

fig, ax = plt.subplots(figsize=(10, 3))
ax.hist(
    real_messages['word_count'].clip(upper=50),
    bins=30, color='#7F77DD', edgecolor='white'
)
ax.set_xlabel("Words per message (capped at 50)")
ax.set_ylabel("Number of messages")
st.pyplot(fig)
plt.close()

st.divider()

# ── Per-user sentiment comparison (only in Overall mode) ─────────
if selected_user == 'Overall':
    st.subheader("Per-user sentiment comparison")

    users = [u for u in df['user'].unique() if u != 'group_notification']
    rows = []
    for u in users:
        udf = df[df['user'] == u]
        total = len(udf)
        if total == 0:
            continue
        rows.append({
            'User':     u,
            'Positive': round(udf[udf['sentiment']=='Positive'].shape[0] / total * 100, 1),
            'Neutral':  round(udf[udf['sentiment']=='Neutral'].shape[0]  / total * 100, 1),
            'Negative': round(udf[udf['sentiment']=='Negative'].shape[0] / total * 100, 1),
            'Messages': total
        })

    compare_df = pd.DataFrame(rows).sort_values('Messages', ascending=False)
    st.dataframe(compare_df, use_container_width=True)