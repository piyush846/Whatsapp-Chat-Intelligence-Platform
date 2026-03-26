"""
preprocessor.py  —  WCA (WhatsApp Chat Intelligence)
-----------------------------------------------------
WHAT THIS FILE DOES:
  Takes raw text from a WhatsApp export and turns it into a
  clean pandas DataFrame that every other part of the app uses.

WHY WE UPGRADED:
  Old version only worked with ONE date format (e.g. 12/3/23, 14:05 - )
  WhatsApp exports look different depending on:
    • Your phone's region (India vs US vs UK vs Europe)
    • iOS vs Android
    • 12-hour vs 24-hour clock
  This version handles ALL of those.
"""

import re
import pandas as pd


# ─────────────────────────────────────────────
# 1. DATE FORMAT PATTERNS
# ─────────────────────────────────────────────
# LEARN: These are "regex" patterns. Each one matches a different
# way WhatsApp writes the date+time at the start of each message.
#
# \d{1,2}  →  1 or 2 digit number  (e.g. "3" or "12")
# \s       →  a space
# [,/]     →  either a comma OR a slash
# ?        →  the previous character is optional

DATE_FORMATS = [
    # Android 24hr:  "12/3/23, 14:05 - "   (most common in India)
    (r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s', True),

    # Android 12hr:  "12/3/23, 2:05 pm - "
    (r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[ap]m\s-\s', True),

    # iOS 24hr:       "[12/3/23, 14:05:30] "
    (r'\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\]\s', False),

    # iOS 12hr:       "[12/3/23, 2:05:30 PM] "
    (r'\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s[APap][Mm]\]\s', False),

    # European:       "12.03.2023, 14:05 - "
    (r'\d{1,2}\.\d{1,2}\.\d{2,4},\s\d{1,2}:\d{2}\s-\s', True),
]


# ─────────────────────────────────────────────
# 2. HELPER: DETECT WHICH FORMAT THIS FILE USES
# ─────────────────────────────────────────────
def detect_format(data: str):
    """
    Tries each pattern above on the first 3000 characters of the file.
    Returns the pattern that matches the most times.

    WHY: Instead of making the user tell us the format, we figure it out
    automatically. Smart apps do this — they adapt to the data.
    """
    sample = data[:3000]  # only check the beginning, it's faster

    best_pattern = None
    best_count = 0
    best_dayfirst = True

    for pattern, dayfirst in DATE_FORMATS:
        matches = re.findall(pattern, sample)
        if len(matches) > best_count:
            best_count = len(matches)
            best_pattern = pattern
            best_dayfirst = dayfirst

    return best_pattern, best_dayfirst


# ─────────────────────────────────────────────
# 3. HELPER: CLEAN A SINGLE DATE STRING
# ─────────────────────────────────────────────
def clean_date_string(raw: str) -> str:
    """
    Removes the messy parts around the date so pandas can read it.

    Examples:
      "[12/3/23, 14:05:30] "  →  "12/3/23, 14:05:30"
      "12/3/23, 14:05 - "     →  "12/3/23, 14:05"
    """
    # remove square brackets (iOS format)
    cleaned = raw.replace('[', '').replace(']', '')
    # remove trailing " - " (Android format)
    cleaned = cleaned.replace(' - ', '')
    return cleaned.strip()


# ─────────────────────────────────────────────
# 4. HELPER: SPLIT ONE RAW LINE INTO USER + MESSAGE
# ─────────────────────────────────────────────
def extract_user_message(raw_message: str):
    """
    Each message line looks like:
        "Alice: Hey how are you?\n"
    We split on the FIRST colon+space to get:
        user    = "Alice"
        message = "Hey how are you?\n"

    If there's no colon, it's a system notification like
    "Alice joined using this group's invite link"
    """
    # split only on the FIRST ": " we find
    # LEARN: split(': ', 1)  means "split at most 1 time"
    parts = raw_message.split(': ', 1)

    if len(parts) == 2:
        user = parts[0].strip()
        message = parts[1].strip()

        # Sanity check: user names are usually short (under 30 chars)
        # If "user" is very long it's probably a system message, not a name
        if len(user) < 30 and '\n' not in user:
            return user, message

    # fallback: treat as group notification
    return 'group_notification', raw_message.strip()


# ─────────────────────────────────────────────
# 5. MAIN FUNCTION: preprocess()
# ─────────────────────────────────────────────
def preprocess(data: str) -> pd.DataFrame:
    """
    THE MAIN FUNCTION — this is what app.py calls.

    INPUT:  raw string of the entire WhatsApp export file
    OUTPUT: a clean pandas DataFrame with one row per message

    DataFrame columns:
        date, user, message,
        year, month_num, month, date_only,
        day_name, day, hour, minute, period
    """

    # ── Step A: Figure out what format this chat uses ──
    pattern, dayfirst = detect_format(data)

    if pattern is None:
        # LEARN: We raise an error with a helpful message instead of
        # silently returning garbage data. Always fail loudly!
        raise ValueError(
            "Could not detect WhatsApp date format.\n"
            "Please make sure you uploaded a valid WhatsApp export (.txt file)."
        )

    # ── Step B: Split the file into individual messages ──
    # re.split(pattern, data) cuts the text everywhere a date appears
    # [1:] skips the very first empty piece before the first date
    raw_messages = re.split(pattern, data)[1:]
    raw_dates    = re.findall(pattern, data)

    # Safety: both lists must be the same length
    # LEARN: zip() pairs items from two lists together
    min_len = min(len(raw_messages), len(raw_dates))
    raw_messages = raw_messages[:min_len]
    raw_dates    = raw_dates[:min_len]

    # ── Step C: Build a basic DataFrame ──
    df = pd.DataFrame({
        'raw_message': raw_messages,
        'raw_date':    raw_dates
    })

    # ── Step D: Parse dates ──
    # clean_date_string removes brackets/dashes first
    df['date'] = pd.to_datetime(
        df['raw_date'].apply(clean_date_string),
        dayfirst=dayfirst,   # True = day comes before month (03/12 = 3rd Dec)
        errors='coerce'      # if a date can't be parsed, put NaT (not an error)
    )

    # Drop rows where date parsing completely failed
    bad_rows = df['date'].isna().sum()
    if bad_rows > 0:
        print(f"[preprocessor] Warning: {bad_rows} rows had unparseable dates and were dropped.")
    df = df.dropna(subset=['date']).reset_index(drop=True)

    # ── Step E: Extract user and message from each raw_message ──
    # LEARN: .apply() runs a function on every row — much cleaner than a for loop
    df[['user', 'message']] = df['raw_message'].apply(
        lambda m: pd.Series(extract_user_message(m))
    )

    # ── Step F: Drop columns we no longer need ──
    df.drop(columns=['raw_message', 'raw_date'], inplace=True)

    # ── Step G: Add time-based columns (these power all the charts) ──
    df['year']      = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month']     = df['date'].dt.month_name()
    df['date_only'] = df['date'].dt.date
    df['day_name']  = df['date'].dt.day_name()
    df['day']       = df['date'].dt.day
    df['hour']      = df['date'].dt.hour
    df['minute']    = df['date'].dt.minute

    # ── Step H: Build the "period" column (used in the heatmap) ──
    # This turns hour=14 into the string "14-15"
    # LEARN: .apply() with a lambda is shorthand for a small function
    def make_period(hour):
        if hour == 23:
            return "23-00"
        elif hour == 0:
            return "00-01"
        else:
            return f"{hour}-{hour + 1}"

    df['period'] = df['hour'].apply(make_period)

    # ── Step I: Add a word count column (useful for stats later) ──
    df['word_count'] = df['message'].apply(lambda m: len(str(m).split()))

    # ── Step J: Flag media messages ──
    # WhatsApp replaces images/videos with this placeholder text
    df['is_media'] = df['message'].str.contains('<Media omitted>', na=False)

    return df


# ─────────────────────────────────────────────
# 6. BONUS: get_chat_info()  — a summary function
# ─────────────────────────────────────────────
def get_chat_info(df: pd.DataFrame) -> dict:
    """
    Returns a quick summary dict about the chat.
    Useful for showing a "chat loaded" confirmation in the UI.

    Example output:
        {
          'total_messages': 4821,
          'users': ['Alice', 'Bob', 'Carol'],
          'date_range': '01 Jan 2023  →  15 Mar 2024',
          'format_detected': True
        }
    """
    users = [u for u in df['user'].unique().tolist() if u != 'group_notification']
    users.sort()

    start = df['date'].min().strftime('%d %b %Y')
    end   = df['date'].max().strftime('%d %b %Y')

    return {
        'total_messages': len(df),
        'users': users,
        'date_range': f"{start}  →  {end}",
        'is_group_chat': len(users) > 2
    }