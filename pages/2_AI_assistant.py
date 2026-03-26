"""
pages/2_AI_Assistant.py
------------------------
WHAT THIS FILE DOES:
  The AI chat interface.
  For now it's a placeholder that shows the UI shell.
  The actual RAG + Ollama integration comes in Step 3.

LEARN — st.chat_input and st.chat_message:
  These are Streamlit's built-in chat UI components.
  st.chat_input()   → renders the text box at the bottom
  st.chat_message() → renders a chat bubble (user or assistant)
"""

import streamlit as st

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")
st.title("🤖 AI Assistant")

# ── Guard ────────────────────────────────────────────────────────
if 'df' not in st.session_state:
    st.warning("Please upload a WhatsApp chat file from the home page first.")
    st.stop()

df = st.session_state.df
info = st.session_state.chat_info

# ── Info banner ──────────────────────────────────────────────────
st.info(
    f"Chat loaded: **{len(df):,} messages** from "
    f"{info['date_range']}  |  "
    f"Participants: {', '.join(info['users'])}"
)

# ── Coming soon message ──────────────────────────────────────────
st.subheader("RAG-powered chat — coming in Step 3")
st.markdown("""
When Step 3 is complete, you'll be able to ask questions like:

- *"Summarize what happened last week"*
- *"Who talks the most about food?"*
- *"What were the most emotional moments?"*
- *"When did Alice and Bob last argue?"*

The AI will search through your actual messages using
**FAISS vector embeddings** and answer using **Ollama (local LLM)**
— completely private, no data leaves your computer.
""")

# ── Preview of the chat UI (non-functional for now) ─────────────
st.divider()
st.caption("Preview of what the interface will look like:")

# Show a few fake example messages so you can see the UI components
with st.chat_message("user"):
    st.write("Who sends the most messages?")

with st.chat_message("assistant"):
    top_user = df[df['user'] != 'group_notification']['user'].value_counts().index[0]
    count    = df[df['user'] != 'group_notification']['user'].value_counts().iloc[0]
    st.write(
        f"Based on your chat, **{top_user}** sends the most messages "
        f"with **{count:,}** total messages."
    )

with st.chat_message("user"):
    st.write("What time is the group most active?")

with st.chat_message("assistant"):
    peak = df.groupby('hour').size().idxmax()
    st.write(
        f"The group is most active around **{peak}:00 – {peak+1 if peak < 23 else 0}:00**. "
        f"You can see the full breakdown in the Advanced Insights page."
    )

# ── Actual (disabled) chat input ────────────────────────────────
st.divider()
prompt = st.chat_input("Ask anything about your chat... (AI coming in Step 3)")
if prompt:
    st.info("AI assistant not connected yet — come back after Step 3!")