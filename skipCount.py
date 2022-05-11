import pandas as pd

from guiExplorer import create_musicdf

music_df = create_musicdf(dropfile='drop.txt')

music_df = music_df[music_df['Skip Count'].isnull() == False]
music_df = music_df[music_df['Play Count'].isnull() == False]

def skip_play(row):
    return round(row['Skip Count'] / row['Play Count'], 2)

music_df['skip_play_ratio'] = music_df.apply(skip_play, axis=1)

print(f"Number of Songs before Filtering: {len(music_df.index)}")
skip_play_avg = music_df['skip_play_ratio'].mean()
print(f"Average skip / play ratio: {skip_play_avg}", )

music_df = music_df[music_df['skip_play_ratio'] > 0.5]

print(f"Number of Songs after Filtering: {len(music_df.index)}\n")

for index, row in music_df.sort_values('skip_play_ratio').iterrows():
    print(f"{row['skip_play_ratio']} {row['Name']} || {row['Artist']} || {row['Album']}\t {row['Play Count']}\t {row['Skip Count']}")