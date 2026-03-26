"""
pages/4_Advanced_Insights.py
-----------------------------
WHAT THIS FILE DOES:
  Advanced features:
    - Keyword/alert detection
    - Most active hours summary
    - Conversation starters (who initiates)
    - Ghost mode detector (who takes longest to reply)

  Note: Toxicity + full anomaly detection comes in Step 6.
  This page is the skeleton we'll fill in later.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Advanced Insights", page_icon="⚡", layout="wide")
st.title("⚡ Advanced Insights")

# ── Guard ────────────────────────────────────────────────────────
if 'df' not in st.session_state:
    st.warning("Please upload a WhatsApp chat file from the home page first.")
    st.stop()

df = st.session_state.df

# ── Keyword Alert ────────────────────────────────────────────────
st.subheader("Keyword search")
st.caption("Find all messages containing a specific word or phrase")

keyword = st.text_input("Enter a keyword", placeholder="e.g. fight, urgent, sorry")

if keyword:
    # LEARN: .str.contains() searches inside every cell of a column
    # case=False means it ignores uppercase/lowercase
    mask = df['message'].str.contains(keyword, case=False, na=False)
    results = df[mask][['date', 'user', 'message']].copy()

    st.write(f"Found **{len(results)}** messages containing '{keyword}'")

    if not results.empty:
        st.dataframe(results.head(50), use_container_width=True)

st.divider()

# ── Conversation Starters ────────────────────────────────────────
st.subheader("Who starts conversations?")
st.caption("A 'conversation start' = message sent 1+ hour after the previous one")

# LEARN: .diff() calculates the difference between consecutive rows
# So date.diff() gives the time gap between each message and the previous one
df_sorted = df.sort_values('date').copy()
df_sorted['gap'] = df_sorted['date'].diff()

# A new conversation = gap > 1 hour
one_hour = pd.Timedelta(hours=1)
starters = df_sorted[
    (df_sorted['gap'] > one_hour) &
    (df_sorted['user'] != 'group_notification')
]['user'].value_counts()

if not starters.empty:
    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots()
        ax.bar(starters.index, starters.values, color='#7F77DD')
        plt.xticks(rotation='vertical')
        ax.set_ylabel("Times started a conversation")
        st.pyplot(fig)
        plt.close()
    with col2:
        st.dataframe(
            starters.reset_index().rename(
                columns={'index': 'User', 'user': 'Conversations started'}
            ),
            use_container_width=True
        )

st.divider()

# ── Peak Hours ───────────────────────────────────────────────────
st.subheader("Peak messaging hours")

real = df[df['user'] != 'group_notification']
hourly = real.groupby('hour').size().reset_index(name='count')

fig, ax = plt.subplots(figsize=(12, 3))
ax.bar(hourly['hour'], hourly['count'], color='#1D9E75')
ax.set_xlabel("Hour of day (24h)")
ax.set_ylabel("Messages")
ax.set_xticks(range(0, 24))
st.pyplot(fig)
plt.close()

peak_hour = hourly.loc[hourly['count'].idxmax(), 'hour']
st.info(f"Most messages are sent at **{peak_hour}:00 – {peak_hour+1 if peak_hour < 23 else 0}:00**")

st.divider()

# ── Coming in Step 6 ─────────────────────────────────────────────
st.subheader("Coming in Step 6")
col1, col2, col3 = st.columns(3)
col1.info("🔍 **Toxicity detection**\nFlag aggressive messages automatically")
col2.info("📉 **Emotion spikes**\nDetect sudden shifts in mood")
col3.info("🤖 **AI anomalies**\nFind unusual conversation patterns")