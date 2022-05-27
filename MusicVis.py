from matplotlib import pyplot as plt
from collections import defaultdict
from celluloid import Camera
import time
import numpy as np
from random import shuffle

import pandas as pd
from itunes_reader import create_musicdf

from matplotlib.animation import PillowWriter

INTERP_FRAMES = 15
MIN_PCT = 1
COLORMAP = 'tab20c'
FONTSIZE = 13
future_month = -1


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
  12: 'Dec',
}


# if 'Start Time' in musicdf.columns and 'Stop Time' in musicdf.columns call start_stop else call total
def song_duration_start_stop(row: pd.Series) -> int:
    if not np.isnan(row['Stop Time']) and not np.isnan(row['Start Time']):
      return (row['Stop Time'] - row['Start Time']) * row['Play Count']
    else:
      return row['Total Time'] * row['Play Count']


def count_month_plays(year_month: str):
  return music_df[START_DATE <= music_df['sort_date'] <= year_month]['Play Count'].sum()

def count_month_duration(year_month: str):
  return music_df[START_DATE <= music_df['sort_date'] <= year_month]['duration'].sum()


def sum_total_duration() -> int:
  return music_df['duration'].sum()


def artist_duration(artist: str) -> int:
  return music_df[music_df['Artist'] == artist]['duration'].sum()


'''
I think don't do iteratively by row right away, first do group by to group of year and artist sums which should give every artists sum per year'''

def create_date_plays_table(start_date: str, end_date: str) -> pd.DataFrame:
  # go back and only do it for the year range
  table = pd.DataFrame(index=music_df['sort_date'].unique(), columns=list(music_df['Artist'].unique()) + ['Duration_Total'])
  # table[start_date] =
  # for ym in table.index[1:]:
  #   table[ym] =
  # want the function to vectorized, all it does is go through every song entry that matches the year_month and
  # adds it to corresponding artist column in the current year_month row
  # can vectorize making sums of duration total after the fact by simply summing each row
  # populate table with 0s to start? so then i can sum even tho duration total would have been nan

  # use group by, group by year_month and artist
  # now i need to extract the sorted bits into their own rows and columns.
  monthly_sums_df = music_df.groupby(['sort_date', 'Artist'])['duration'].sum().reset_index()
  # monthly_sums_df = monthly_sums_df.pivot(index='sort_date', columns='')
  table = pd.pivot_table(monthly_sums_df, values='duration', index=['sort_date'],
                         columns=['Artist'], fill_value=0)

  # WE DID IT LETS GOOOOOOOOOOOOOOOO!!!!!!!!!!!!
  return table

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


def create_data(artist_count, total):
  xy = list(artist_count.items())
  xy.sort(key=lambda x: x[1])
  chart_labels = []
  chart_sizes = []
  other_total = 0
  for key, value in xy:
    if value/total > MIN_PCT/100:
      chart_labels.append(key)
      chart_sizes.append(value/total)
    else:
      other_total += value

  other_value = other_total/total

  if other_value > MIN_PCT/100:
    i = 0
    for i in range(len(chart_sizes)):
      if chart_sizes[i] > other_value:
        i -= 1
        break
      i += 1

    chart_sizes.insert(i+1, other_value)
    chart_labels.insert(i + 1, f'Other < {MIN_PCT}%')

  chart_explosion = [0.0007 / i**(1.5) for i in chart_sizes]
  return chart_sizes, chart_labels, chart_explosion


def interp(x1, x2, interp_frames, i):
  return x1 + (x2-x1)/interp_frames * i


def annotate_time(year_month, duration_total, chart_sizes, chart_labels, chart_explosion):
  ax1.annotate(f'{year_month[:4]} - {NUM_TO_MONTHS[int(year_month[4:])]}', (1, -1), fontSize=30)
  ax1.annotate(f'{format_duration(duration_total)}', (0.45, 1.55), fontSize=16)
  ax1.annotate('Total Listening Time', (0.48, 1.65), fontSize=25)
  pie_wedges = ax1.pie(chart_sizes, labels=chart_labels, explode=chart_explosion, autopct='%1.1f%%', startangle=90,
                       rotatelabels=True, textprops={'fontsize': FONTSIZE}, labeldistance=1.05)[0]
  for wedge in pie_wedges:
    wedge.set_facecolor(colors[wedge.get_label()])
  ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
  camera.snap()



def plt_data(ax1, camera, year_month, colors):
  global future_month
  global future_year
  artist_count, total, duration_total = count_month(year_month)
  chart_sizes, chart_labels, chart_explosion = create_data(artist_count, total)
  # if its the last frame
  if year_month == END_DATE:
    for i in range(15):
      ax1.annotate(f'{year_month[:4]} - {NUM_TO_MONTHS[int(year_month[4:])]}', (1, -1), fontSize=30)
      ax1.annotate(f'{format_duration(duration_total)}', (0.45, 1.55), fontSize=16)
      ax1.annotate('Total Listening Time', (0.48, 1.65), fontSize=25)
      pie_wedges = ax1.pie(chart_sizes, labels=chart_labels, explode=chart_explosion, autopct='%1.1f%%', startangle=90,
              rotatelabels=True, textprops={'fontsize': FONTSIZE}, labeldistance=1.05)[0]
      for wedge in pie_wedges:
        wedge.set_facecolor(colors[wedge.get_label()])
      ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
      camera.snap()
  else:
    year = int(year_month[:4])
    month = int(year_month[4:])
    if month <= future_month and year <= future_year:
      return
    next_month = (month + 1) % 13
    interp_months = 1
    next_year = year
    if next_month == 0:
      next_year = year + 1
      next_month += 1
    next_year_month = str(next_year) + str(next_month).zfill(2)
    next_artist_count, next_total, next_duration_total = count_month(next_year_month)
    while next_total < total+50 and int(next_year_month) < int(music_df['sort_date'].max() and next_month <= 4):
      next_month += 1
      future_month = next_month-1
      future_year = next_year
      interp_months += 1
      next_artist_count, next_total, next_duration_total = count_month(next_year_month)

    # adjust the values of artists counts

    deltas = defaultdict(int)
    for key in set(list(artist_count.keys()) + list(next_artist_count.keys())):
      deltas[key] = next_artist_count[key] - artist_count[key]
    total_interp_frames = INTERP_FRAMES * interp_months

    for m in range(1, interp_months+1):
      for i in range(1+(m-1)*INTERP_FRAMES,1+(m)*INTERP_FRAMES):
        interp_artist_count = defaultdict(int)
        for key, value in deltas.items():
          interp_artist_count[key] = artist_count[key] + (deltas[key]/total_interp_frames) * i
        interp_total = interp(total, next_total, total_interp_frames, i)
        interp_chart_sizes, interp_labels, interp_chart_explosion = create_data(interp_artist_count, interp_total)
        ax1.annotate(f'{year+ (1 if (month+m-1 > 12) else 0)} - {NUM_TO_MONTHS[(month+m-1)%13 + (1 if (month+m-1>12) else 0)]}', (1, -1), fontSize=30)
        ax1.annotate(f'{format_duration(interp(duration_total, next_duration_total, total_interp_frames, i))}',(0.45, 1.55), fontSize=16)
        ax1.annotate('Total Listening Time',
                     (0.48, 1.65), fontSize=25)
        pie_wedges = ax1.pie(interp_chart_sizes, labels=interp_labels, explode=interp_chart_explosion, autopct='%1.1f%%', startangle=90,
                             rotatelabels=True, textprops={'fontsize': FONTSIZE}, labeldistance=1.05)[0]
        for wedge in pie_wedges:
          wedge.set_facecolor(colors[wedge.get_label()])
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        camera.snap()


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
END_DATE = unique_dates[5]

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
future_month = -1
future_year = -1
# don't need artists list, just get all artists that are in a given range.

fig1, ax1 = plt.subplots(figsize=(12, 12), dpi=130)
camera = Camera(fig1)
artists_used = set()

# print(music_df.Artist.unique())
print(create_date_plays_table(START_DATE, END_DATE).to_string())
# # probably have to deal with the fact that unique won't have every month year combo
# for date in unique_dates[5:31]:
#   plt_data(ax1, camera, date, artist_colors)
#
# print(time.time() - start_time)
# print('animating')
# animation = camera.animate(interval=1000/30,blit=True)
# # for mp4's code is 'celluloid_subplots.mp4'
# # for debug's code is 'celluloid_subplots.gif', writer=PillowWriter(30)
# animation.save('celluloid_subplots.gif', writer=PillowWriter(30))
#
# # prints the number of seconds it took to animate



#interp by using enumerate instead of just iteration, get difference between this month and next and gradually adjust'''
