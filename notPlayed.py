import pandas as pd
from itunes_reader import create_musicdf

music_df = create_musicdf(required_fields=('Date Added', 'Name', 'Play Count', 'Artist', 'Album'))

music_df = music_df[music_df['Play Count'].isnull() == True]

print(f"Number of Songs after Filtering: {len(music_df.index)}\n")

for index, row in music_df.sort_values('Date Added').iterrows():
    print(f"{row['Date Added']}\t {row['Name']} || {row['Artist']} || {row['Album']}")