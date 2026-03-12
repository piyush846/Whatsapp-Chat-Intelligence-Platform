import streamlit as st
import re
import pandas as pd
import preprocessor
import help
import matplotlib.pyplot as plt
import seaborn as sns
st.sidebar.title("Whatsapp Chat Analyser")
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # fetch unique user
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,"Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt to",user_list)

    if st.sidebar.button('Show Analysis'):

        num_messages,word,num_media_msg,links = help.fetch_stats(selected_user,df)
        st.title('Top Statistics')
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)

        with col2:
            st.header("Total Words")
            st.title(word)
        with col3:
            st.header('Media Shared')
            st.title(num_media_msg)
        with col4:
            st.header('Links Shared')
            st.title(links)
        # Monthly Timeline
        st.title('Monthly Timeline')
        timeline = help.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'],color='purple')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Daily Timeline
        st.title('Daily Timeline')
        daily_timeline = help.daily(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['date_only'], daily_timeline['message'],color='purple')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Activity Map
        st.title("Activity Map")

        col1, col2 = st.columns(2)

        with col1:
            st.header("Most Busy day")
            busy_day = help.week_act_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index,busy_day.values,color='purple')
            st.pyplot(fig)

        with col2:
            st.header("Most busy month")
            busy_month = help.month_act_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values,color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        st.title("Weekly Activity map")
        user_heatmap = help.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)


        # finding the busiest users in the group
        if selected_user == 'Overall':
            st.title("Most Busy Users")
            x, newdf = help.most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values,color='purple')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.header("DataFrame")
                st.dataframe(newdf)


        # WordCloud
        st.title('Word Cloud')
        df_wc = help.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # Most Common words
        st.title('Most Common words used in chat')
        most_common_df = help.most_common_words(selected_user, df)

        fig,ax = plt.subplots()
        ax.bar(most_common_df[0],most_common_df[1])
        plt.xticks(rotation ='vertical')
        st.pyplot(fig)

        #Emoji Analysis
        st.title("Emoji Analysis")
        emoji_df = help.emoji_helper(selected_user, df)

        col1 , col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)

        with col2:
            fig, ax = plt.subplots()
            ax.pie(emoji_df['Times used'].head(),labels=emoji_df['Emoji'].head(),autopct="%0.2f")
            st.pyplot(fig)