from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
import emoji
from collections import Counter

extract  = URLExtract()
def fetch_stats(selected_user,df):
    if selected_user != 'Overall':

        df = df[df['user'] == selected_user]
    #fetch number of messages
    num_messages = df.shape[0]
    #fetch number of words
    word = []
    for message in df['message']:
        word.extend(message.split())
    #fetch numberr of media
    num_media_msg = df[df['message'] == '<Media omitted>\n'].shape[0]
    #fetch number of link shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))



    return num_messages,len(word),num_media_msg,len(links)


def most_busy_users(df):
    df = df[df['user'] != 'group_notification']
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts()/df.shape[0])*100,2).reset_index().rename(columns={'index':'name','user':'percent'})
    return x, df

def create_wordcloud(selected_user,df):

     if selected_user != 'Overall':
         df =df[df['user'] == selected_user]

     f = open('stop_hinglish.txt', 'r')
     stop_words = f.read()

     temp = df[df['user'] != 'group_notification']
     temp = temp[temp['message'] != '<Media omitted>\n']

     def remove_stopwords(message):
         y = []
         for word in message.lower().split():
             if word not in stop_words:
                 y.append(word)
         return " ".join(y)


     wc = WordCloud(width=500,height=500,min_font_size=10,background_color='white')
     temp['message'] = temp['message'].apply(remove_stopwords)
     df_wc = wc.generate(temp['message'].str.cat(sep=" "))
     return df_wc

def most_common_words(selected_user,df):

    f = open('stop_hinglish.txt','r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    from collections import Counter
    most_common_df = pd.DataFrame(Counter(words).most_common(25))
    return most_common_df

def emoji_helper(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis)))).rename(columns={0:'Emoji',1:'Times used'})

    return emoji_df
def monthly_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
    timeline['time'] = time

    return timeline

def daily(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby(['date_only']).count()['message'].reset_index()

    return daily_timeline

def week_act_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_act_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap


