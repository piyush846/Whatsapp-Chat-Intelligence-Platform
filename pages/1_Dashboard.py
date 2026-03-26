"""
pages/1_Dashboard.py
---------------------
WHAT THIS FILE DOES:
  The main analytics dashboard.
  Reads df from st.session_state (set by app.py)
  and shows all the charts.
 
LEARN — Why does this work without importing preprocessor?
  Because app.py already ran preprocessor and stored the
  result in st.session_state.df. This page just reads it.
  session_state is shared across ALL pages.
"""
 
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import help
 
sns.set_theme(style="darkgrid")
 
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Dashboard")
 
# ── Guard: stop if no file uploaded yet ─────────────────────────
# LEARN: Every page needs this check. If someone visits this page
# directly without uploading a file, session_state.df won't exist.
if 'df' not in st.session_state:
    st.warning("Please upload a WhatsApp chat file from the home page first.")
    st.stop()   # stops the script here — nothing below runs
 
# ── Load data from session state ────────────────────────────────
df = st.session_state.df
 
# ── User selector ────────────────────────────────────────────────
user_list = [u for u in df['user'].unique().tolist() if u != 'group_notification']
user_list.sort()
user_list.insert(0, "Overall")
 
selected_user = st.sidebar.selectbox("Analyse by user", user_list)
 
# ── Top Statistics ───────────────────────────────────────────────
st.subheader("Top statistics")
num_messages, word, num_media_msg, links = help.fetch_stats(selected_user, df)
 
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total messages", f"{num_messages:,}")
col2.metric("Total words",    f"{word:,}")
col3.metric("Media shared",   f"{num_media_msg:,}")
col4.metric("Links shared",   f"{links:,}")
 
st.divider()
 
# ── Timelines ────────────────────────────────────────────────────
# LEARN: st.tabs() creates clickable tabs — clean way to
# show multiple charts without scrolling forever
tab1, tab2 = st.tabs(["Monthly timeline", "Daily timeline"])
 
with tab1:
    st.subheader("Monthly timeline")
    timeline = help.monthly_timeline(selected_user, df)
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.plot(timeline['time'], timeline['message'], color='#7F77DD', linewidth=2)
    plt.xticks(rotation='vertical', fontsize=8)
    ax.set_ylabel("Messages")
    st.pyplot(fig)
    plt.close()
 
with tab2:
    st.subheader("Daily timeline")
    daily_timeline = help.daily(selected_user, df)
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.plot(daily_timeline['date_only'], daily_timeline['message'], color='#1D9E75', linewidth=1.5)
    plt.xticks(rotation='vertical', fontsize=7)
    ax.set_ylabel("Messages")
    st.pyplot(fig)
    plt.close()
 
st.divider()
 
# ── Activity Map ─────────────────────────────────────────────────
st.subheader("Activity map")
 
col1, col2 = st.columns(2)
 
with col1:
    st.caption("Most busy day")
    busy_day = help.week_act_map(selected_user, df)
    fig, ax = plt.subplots()
    ax.bar(busy_day.index, busy_day.values, color='#7F77DD')
    plt.xticks(rotation='vertical')
    st.pyplot(fig)
    plt.close()
 
with col2:
    st.caption("Most busy month")
    busy_month = help.month_act_map(selected_user, df)
    fig, ax = plt.subplots()
    ax.bar(busy_month.index, busy_month.values, color='#1D9E75')
    plt.xticks(rotation='vertical')
    st.pyplot(fig)
    plt.close()
 
# ── Weekly Heatmap ───────────────────────────────────────────────
st.subheader("Weekly activity heatmap")
user_heatmap = help.activity_heatmap(selected_user, df)
 
if user_heatmap.empty:
    st.info("Not enough data to build a heatmap.")
else:
    fig, ax = plt.subplots(figsize=(14, 4))
    sns.heatmap(user_heatmap, ax=ax, cmap='Purples')
    st.pyplot(fig)
    plt.close()
 
st.divider()
 
# ── Busiest Users (only shown in Overall mode) ───────────────────
if selected_user == 'Overall':
    st.subheader("Most active users")
    x, newdf = help.most_busy_users(df)
 
    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots()
        ax.bar(x.index, x.values, color='#D85A30')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)
        plt.close()
    with col2:
        st.dataframe(newdf, use_container_width=True)
 
st.divider()
 
# ── Word Cloud ───────────────────────────────────────────────────
st.subheader("Word cloud")
# LEARN: @st.cache_data caches the result so it doesn't regenerate
# every time the user clicks something. The underscore before df
# tells Streamlit not to hash the df argument (it's too big).
@st.cache_data
def get_wordcloud(_df, user):
    return help.create_wordcloud(user, _df)
 
try:
    df_wc = get_wordcloud(df, selected_user)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(df_wc)
    ax.axis('off')
    st.pyplot(fig)
    plt.close()
except Exception as e:
    st.info(f"Could not generate word cloud: {e}")
 
# ── Most Common Words ────────────────────────────────────────────
st.subheader("Most common words")
try:
    most_common_df = help.most_common_words(selected_user, df)
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.bar(most_common_df[0], most_common_df[1], color='#7F77DD')
    plt.xticks(rotation='vertical')
    st.pyplot(fig)
    plt.close()
except Exception as e:
    st.info(f"Could not generate word frequency: {e}")
 
# ── Emoji Analysis ───────────────────────────────────────────────
st.divider()
st.subheader("Emoji analysis")
emoji_df = help.emoji_helper(selected_user, df)
 
if emoji_df.empty:
    st.info("No emojis found in this chat.")
else:
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(emoji_df.head(20), use_container_width=True)
    with col2:
        fig, ax = plt.subplots()
        ax.pie(
            emoji_df['Times used'].head(8),
            labels=emoji_df['Emoji'].head(8),
            autopct="%0.1f%%"
        )
        st.pyplot(fig)
        plt.close()