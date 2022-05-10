import pandas as pd
import plistlib as pl

with open('drop2.txt', 'r') as drop_file:
    drop_lines = drop_file.readlines()
    drop_lines = [drop.split('  ')[0].strip('\n') for drop in drop_lines]


with open('Library.xml', 'rb') as file:
    lib = pl.load(file)

tracks = lib['Tracks']

df = pd.DataFrame.from_dict(tracks)
df = df.transpose()
for drop in drop_lines:
    df.drop(drop, axis=1, inplace=True)


df = df[df['Play Count'].isnull() == True]

print(f"Number of Songs after Filtering: {len(df.index)}\n")

for index, row in df.sort_values('Date Added').iterrows():
    print(f"{row['Date Added']}\t {row['Name']} || {row['Artist']} || {row['Album']}")