import pandas as pd
from guiExplorer import load_xml_file

with open('drop2.txt', 'r') as drop_file:
    drop_lines = drop_file.readlines()
    drop_lines = [drop.split('  ')[0].strip('\n') for drop in drop_lines]


music_df = pd.DataFrame.from_dict(load_xml_file()['Tracks']).transpose()
music_df = music_df.transpose()

music_df = music_df.drop(df[df'Date Added'].index)
for drop in drop_lines:
    music_df.drop(drop, axis=1, inplace=True)


music_df = music_df[music_df['Play Count'].isnull() == True]

print(f"Number of Songs after Filtering: {len(music_df.index)}\n")

for index, row in music_df.sort_values('Date Added').iterrows():
    print(f"{row['Date Added']}\t {row['Name']} || {row['Artist']} || {row['Album']}")