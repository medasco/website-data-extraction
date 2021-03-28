import pandas as pd

df = pd.read_csv('twitchStreamers.csv')
df.drop_duplicates(inplace=True)
df.to_csv('streamers.csv', index=False)
