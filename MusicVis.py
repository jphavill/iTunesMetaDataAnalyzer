from matplotlib import pyplot as plt
from collections import defaultdict
from celluloid import Camera
import time
import numpy as np
from random import shuffle
import bisect

import pandas as pd
from itunes_reader import create_musicdf

from matplotlib.animation import PillowWriter

INTERP_FRAMES_PER_MONTH = 1
MIN_PCT = 1
COLORMAP = 'tab20c'
FONTSIZE = 13


NUM_TO_MONTHS = {
  1: 'Jan',
  2: 'Feb',
  3: 'Mar',
  4: 'Apr',
  5: 'May',
  6: 'Jun',
  7: 'Jul',
  8: 'Aug',
  9: 'Sep',
  10: 'Oct',
  11: 'Nov',
  0: 'Dec',
}


# if 'Start Time' in musicdf.columns and 'Stop Time' in musicdf.columns call start_stop else call total
def song_duration_start_stop(row: pd.Series) -> int:
    if not np.isnan(row['Stop Time']) and not np.isnan(row['Start Time']):
      return (row['Stop Time'] - row['Start Time']) * row['Play Count']
    else:
      return row['Total Time'] * row['Play Count']


def create_date_plays_table() -> pd.DataFrame:
  monthly_sums_df = music_df.groupby(['sort_date', 'Artist'])['duration'].sum().reset_index()
  table = pd.pivot_table(monthly_sums_df, values='duration', index=['sort_date'],
                         columns=['Artist'], fill_value=0)
  # add sum of each row as a column so percentages can be easily calculated
  table['total_duration'] = table.sum(axis=1)
  # running summation of the songs per month block
  table = table.cumsum()
  tablepct = table.div(table.total_duration, axis=0)
  tablepct['total_duration'] = table.total_duration
  return tablepct

def format_duration(duration):
  days = duration // 86400
  hours = (duration - 86400 * days) // 3600
  minutes = (duration - 86400 * days - 3600 * hours) // 60
  seconds = duration % 60
  return f'{days:.0f} days, {hours:02.0f} hours, {minutes:02.0f} min, {seconds:02.0f} sec'


def count_month(year_month) -> tuple:
  # mult the vector of play count with duration of sorted df of each artist
  artist_count = defaultdict(int)
  total = music_df.loc[music_df['sort_date'] <= year_month]['Play Count'].sum()
  total_duration = music_df.loc[music_df['sort_date'] <= year_month]['duration'].sum()
  for art in music_df[music_df['sort_date'] <= year_month]['Artist'].unique():
    artist_count[art] = music_df.loc[(music_df['sort_date'] <= year_month) & (music_df['Artist'] == art)]['Play Count'].sum()
    # artist_count[art] = music_df.loc[(music_df['sort_date'] <= year_month) & (music_df['Artist'] == art)]['duration'].sum()

  return artist_count, total, total_duration


def create_data_vector(s: pd.Series) -> tuple:
  s = s.drop('total_duration')
  others = s[s < 0.01]
  other_value = others.sum()
  not_others = s[s > 0.01]
  chart_labels = list(not_others.index)
  chart_sizes = list(not_others.values)
  if other_value > MIN_PCT/100:
    others_index = bisect.bisect(chart_sizes, other_value)

    chart_sizes.insert(others_index, other_value)
    chart_labels.insert(others_index, f'Other < {MIN_PCT}%')
  # sort the wedge labels and size by size of section
  chart_sizes, chart_labels = zip(*sorted(zip(chart_sizes, chart_labels)))
  chart_explosion = [0.0007 / i ** (1.5) for i in chart_sizes]

  return chart_sizes, chart_labels, chart_explosion


def add_interp_rows(df: pd.DataFrame):
  n = year_month_diff(df.index[0], df.index[-1]) * INTERP_FRAMES_PER_MONTH
  interp_index = [year_month_add(df.index[0], i//INTERP_FRAMES_PER_MONTH) for i in range(n+1)]
  interp_df = pd.DataFrame(np.nan, index=interp_index, columns=df.columns)
  interp_df = interp_df.fillna(df)
  return interp_df.interpolate()



def interp(x1, x2, interp_frames, i):
  return x1 + (x2-x1)/interp_frames * i


def year_month_add(ym: str, add_months: int) -> str:
  total_months = int(ym[:4]) * 12 + int(ym[4:]) + add_months
  year = total_months // 12
  months = total_months % 12
  return str(year) + str(months).zfill(2)


'''returns the number of months between year_month dates'''
def year_month_diff(ym1: str, ym2: str) -> int:
  return (int(ym2[:4]) * 12 + int(ym2[4:])) - (int(ym1[:4]) * 12 + int(ym1[4:]))


def animate_frame(year_month, duration_total, colours, chart_sizes, chart_labels, chart_explosion):
  ax1.annotate(f'{year_month[:4]} - {NUM_TO_MONTHS[int(year_month[4:])]}', (1, -1), fontSize=30)
  ax1.annotate(f'{format_duration(duration_total)}', (0.45, 1.55), fontSize=16)
  ax1.annotate('Total Listening Time', (0.48, 1.65), fontSize=25)
  pie_wedges = ax1.pie(chart_sizes, labels=chart_labels, explode=chart_explosion, autopct='%1.1f%%', startangle=90,
                       rotatelabels=True, textprops={'fontsize': FONTSIZE}, labeldistance=1.05)[0]
  for wedge in pie_wedges:
    wedge.set_facecolor(colours[wedge.get_label()])
  ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
  camera.snap()


def plt_data_vector(s: pd.Series, colours):
  year_month = s.name
  chart_sizes, chart_labels, chart_explosion = create_data_vector(s)
  animate_frame(year_month, s["total_duration"], colours, chart_sizes, chart_labels, chart_explosion)

  # if its the last frame hold it for a total of 15 frames, half a second
  if year_month == END_DATE:
    for i in range(14):
      animate_frame(year_month, s["total_duration"], colours, chart_sizes, chart_labels, chart_explosion)

music_df = create_musicdf(required_fields=('Date Added', 'Artist', 'Play Count', 'Start Time', 'Stop Time', 'Total Time'))
start_time = time.time()

music_df = music_df[music_df['Date Added'].notnull()]

music_df['year'] = pd.DatetimeIndex(music_df['Date Added']).year.astype(str)
music_df['month'] = pd.DatetimeIndex(music_df['Date Added']).month.astype(str)
music_df['sort_date'] = music_df['year'].astype(str) + music_df['month'].astype(str).str.zfill(2)
music_df.sort_values('sort_date')


# all unique dates in increments of 1 month
unique_dates = music_df['sort_date'].unique()
unique_dates.sort()
START_DATE = unique_dates[0]
END_DATE = unique_dates[-1]

# filter music data frame to only be the selected time span
music_df = music_df.loc[(START_DATE <= music_df['sort_date']) & (music_df['sort_date'] <= END_DATE)]

# if some songs have custom start and stop times
if 'Start Time' in music_df.columns and 'Stop Time' in music_df.columns:
  music_df['duration'] = music_df.apply(song_duration_start_stop, axis=1)
  music_df.drop(['Start Time', 'Stop Time'], axis=1, inplace=True)
else:
  music_df['duration'] = music_df.apply(lambda x: x['Total Time'], axis=1)
# now that duration is computed total time is redundant
music_df.drop('Total Time', axis=1)
music_df['duration'] = music_df['duration'].floordiv(1000)

artists_used = list(music_df['Artist'].unique()) + ['Other < 1%']
shuffle(artists_used)
cmap = plt.get_cmap(COLORMAP)
colors = cmap(np.linspace(0., 1., len(artists_used)))
artist_colors = {}
for artist, color in zip(artists_used,colors):
  artist_colors[artist] = color
# don't need artists list, just get all artists that are in a given range.

fig1, ax1 = plt.subplots(figsize=(12, 12), dpi=130)
camera = Camera(fig1)

artist_df = create_date_plays_table()

artist_df = add_interp_rows(artist_df)

for index, row in artist_df.iterrows():
    plt_data_vector(row, artist_colors)


print(time.time() - start_time)
print('animating')
ani_start_time = time.time()
animation = camera.animate(interval=1000/30,blit=True)
# for mp4's code is 'celluloid_subplots.mp4'
animation.save('celluloid_subplots.mp4')
# for debug's code is 'celluloid_subplots.gif', writer=PillowWriter(30)
# animation.save('celluloid_subplots.gif', writer=PillowWriter(30))

# prints the number of seconds it took to animate
print(time.time() - start_time)
