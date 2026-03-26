from urlextract import URLExtract
from wordcloud import WordCloud
from textblob import TextBlob
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

def create_wordcloud(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # LEARN: read stop words as a SET of individual words (not one big string)
    # set() makes lookups instant — checking "word in set" is O(1)
    with open('stop_hinglish.txt', 'r') as f:
        stop_words = set(f.read().split())

    # WhatsApp system / junk words that slip through the chat
    JUNK_WORDS = {
        'media', 'omitted', 'deleted', 'message', 'null',
        'missed', 'voice', 'call', 'video', 'image', 'gif',
        'sticker', 'audio', 'document', 'joined', 'left',
        'added', 'removed', 'changed', 'created', 'group',
        'https', 'http', 'www', 'end-to-end', 'encrypted',
        'tap', 'learn', 'more', 'waiting', 'messages',
        'this', 'you', 'chat', 'https','http'
    }

    # Merge both sets — | is the union operator for sets
    all_stop = stop_words | JUNK_WORDS

    # Filter junk rows — catches ALL variants of media/system messages
    temp = df[df['user'] != 'group_notification'].copy()
    temp = temp[~temp['message'].str.contains(
        'omitted|null|end-to-end|encrypted|missed voice|missed video',
        case=False, na=False
    )]

    def clean_message(message):
        words = []
        for word in str(message).lower().split():
            # Strip punctuation from word edges: "hello," → "hello"
            clean = word.strip('.,!?()[]<>"\':;-_@#*/')
            # Only keep if: not empty, not a junk word, longer than 1 char
            if clean and clean not in all_stop and len(clean) > 1:
                words.append(clean)
        return " ".join(words)

    temp = temp.copy()
    temp['message'] = temp['message'].apply(clean_message)
    temp = temp[temp['message'].str.strip() != '']

    if temp.empty:
        raise ValueError("Not enough text to generate a word cloud.")

    wc = WordCloud(
        width=800, height=400,
        min_font_size=10,
        background_color='white',
        colormap='viridis',
        max_words=150
    )
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user, df):

    # Same fix as create_wordcloud — read as a SET not a raw string
    with open('stop_hinglish.txt', 'r') as f:
        stop_words = set(f.read().split())

    JUNK_WORDS = {
        'media', 'omitted', 'deleted', 'message', 'null',
        'missed', 'voice', 'call', 'video', 'image', 'gif',
        'sticker', 'audio', 'document', 'joined', 'left',
        'added', 'removed', 'changed', 'created', 'group',
        'https', 'http', 'www', 'end-to-end', 'encrypted',
        'tap', 'learn', 'more', 'waiting', 'messages', 'chat'
    }
    all_stop = stop_words | JUNK_WORDS

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification'].copy()
    temp = temp[~temp['message'].str.contains(
        'omitted|null|end-to-end|encrypted',
        case=False, na=False
    )]

    words = []
    for message in temp['message']:
        for word in str(message).lower().split():
            clean = word.strip('.,!?()[]<>"\':;-_@#*/')
            if clean and clean not in all_stop and len(clean) > 1:
                words.append(clean)

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

def get_sentiment(message):
    try:
        message = str(message)

        if message == "<Media omitted>\n":
            return "Neutral"

        analysis = TextBlob(message)
        polarity = analysis.sentiment.polarity

        if polarity > 0:
            return "Positive"
        elif polarity < 0:
            return "Negative"
        else:
            return "Neutral"

    except:
        return "Neutral"


def add_sentiment(df):

    df["sentiment"] = df["message"].apply(get_sentiment)

    return df