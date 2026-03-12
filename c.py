def fetch_stats(selected_user,df):
    if selected_user == 'Overall':
        # fetch number of messages
        num_messages = df.shape[0]
        # fetch number of words
        word = []
        for message in df['message']:
            word.extend(message.split())
        return num_messages,len(word)
    else:
        new_df = df[df['user'] == selected_user]
        num_messages = new_df.shape[0]
        word = []
        for message in df['message']:
            word.extend(message.split())

        return num_messages,len(word)