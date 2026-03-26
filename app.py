"""
app.py  —  WCA entry point
---------------------------
WHAT THIS FILE DOES:
  This is the ONLY file Streamlit runs directly.
  Its job is simple:
    1. Show the file uploader in the sidebar
    2. Parse the uploaded chat
    3. Save the result to st.session_state
       so ALL other pages can access it
 
LEARN — What is st.session_state?
  Normally every time you click anything in Streamlit,
  the entire script re-runs from top to bottom.
  session_state is a dictionary that SURVIVES those reruns.
  Think of it as a shared memory between all your pages.
"""

import streamlit as st
import preprocessor
import help

# ── Page config (must be the FIRST streamlit call) ──────────────
st.set_page_config(
    page_title="ConvoIntel-Whatsapp Chat Intelligence",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)
#Sidebar

st.sidebar.title("ConvoIntel")
st.sidebar.caption("Whatsapp Chat Intelligence")
st.sidebar.divider()

uploaded_file = st.sidebar.file_uploader(
    "Upload your Whatsapp Chat export",
    type=["txt"],
    help ="Export a chat from WhatsApp: Chat > More > Export Chat > Without Media" ,
)
 #Process the file when loaded
if uploaded_file is not None: 
    # Only re-process if it's a NEW file (check filename)
    # LEARN: 'not in' checks if a key exists in the dict

    if 'file_name' not in st.session_state or \
    st.session_state.file_name !=uploaded_file.name:
        try:
            # Read bytes → decode to string → parse
            raw_text = uploaded_file.getvalue().decode("utf-8")
            df = preprocessor.preprocess(raw_text)
            df = help.add_sentiment(df)

   # Save everything to session_state
                # LEARN: any page can now do st.session_state.df
            st.session_state.df = df
            st.session_state.file_name = uploaded_file.name
            st.session_state.chat_info = preprocessor.get_chat_info(df)

            st.sidebar.success(f"Loaded{len(df):,} messages !")

        except ValueError as e:
            st.sidebar.error(str(e))
            st.stop()

        # Show chat info in sidebar if data is loaded
    if 'chat_info' in st.session_state:
        info = st.session_state.chat_info
        st.sidebar.divider()
        st.sidebar.caption("Chat Summary")
        st.sidebar.write(f"**Date range:** {info['date_range']}")
        st.sidebar.write(f"**Messages:** {info['total_messages']:,}")
        st.sidebar.write(f"**Participants:** {', '.join(info['users'])}")

# ── Main page content (shown when no file is uploaded) ───
if 'df' not in st.session_state:
    # Welcome screen
    st.title("💬 WhatsApp Chat Intelligence")
    st.subheader("Turn your chats into insights")
 
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📊 **Dashboard**\nTimelines, activity maps, word clouds")
    with col2:
        st.info("🤖 **AI Assistant**\nAsk questions about your chat")
    with col3:
        st.info("📈 **User Analysis**\nSentiment, response times, emoji stats")
 
    st.divider()
    st.markdown("### How to export your WhatsApp chat")
    st.markdown("""
    1. Open any WhatsApp chat on your phone
    2. Tap the three dots (⋮) → **More** → **Export chat**
    3. Choose **Without Media**
    4. Save the `.txt` file and upload it above
    """)
else:
    # If data is loaded, show a mini dashboard on the home page
    st.title("💬 WhatsApp Chat Intelligence")
    info = st.session_state.chat_info
    df   = st.session_state.df
 
    st.success(f"Chat loaded: **{st.session_state.file_name}**")
 
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total messages", f"{info['total_messages']:,}")
    col2.metric("Participants",   len(info['users']))
    col3.metric("Date range",     info['date_range'].split('→')[0].strip())
    col4.metric("Media messages", f"{df['is_media'].sum():,}")
 
    st.info("Use the sidebar to navigate to Dashboard, AI Assistant, and more.")