import pandas as pd
import plistlib as pl
from guiExplorer import get_xml_file

with open('drop.txt', 'r') as drop_file:
    drop_lines = drop_file.readlines()
    drop_lines = [drop.split('  ')[0].strip('\n') for drop in drop_lines]


with open(get_xml_file(), 'rb') as file:
    lib = pl.load(file)

tracks = lib['Tracks']

df = pd.DataFrame.from_dict(tracks)
df = df.transpose()
for drop in drop_lines:
    df.drop(drop, axis=1, inplace=True)



df = df[df['Skip Count'].isnull() == False]
df = df[df['Play Count'].isnull() == False]

def skip_play(row):
    return round(row['Skip Count'] / row['Play Count'], 2)

df['skip_play_ratio'] = df.apply(skip_play, axis=1)

print(f"Number of Songs before Filtering: {len(df.index)}")
skip_play_avg = df['skip_play_ratio'].mean()
print(f"Average skip / play ratio: {skip_play_avg}", )

df = df[df['skip_play_ratio'] > 0.5]

print(f"Number of Songs after Filtering: {len(df.index)}\n")

for index, row in df.sort_values('skip_play_ratio').iterrows():
    print(f"{row['skip_play_ratio']} {row['Name']} || {row['Artist']} || {row['Album']}\t {row['Play Count']}\t {row['Skip Count']}")