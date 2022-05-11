from matplotlib import pyplot as plt
from collections import defaultdict
from celluloid import Camera
import time
import numpy as np
from random import shuffle

import pandas as pd
from guiExplorer import load_xml_file

from matplotlib.animation import PillowWriter
'''
start_time = time.time()
INTERP_FRAMES = 15
MIN_PCT = 1
COLORMAP = 'tab20c'
FONTSIZE = 13
future_month = -1

MONTHS_TO_NUM = {
  'Jan': 1,
  'Feb': 2,
  'Mar': 3,
  'Apr': 4,
  'May': 5,
  'Jun': 6,
  'Jul': 7,
  'Aug': 8,
  'Sep': 9,
  'Oct': 10,
  'Nov': 11,
  'Dec': 12,
}

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
'''

# loads dict of song name: artist, genre, playcount, duratoin, mth day, year at hh:mm
# with open('musicdata/musicdata.json', 'rb') as f:
#   line = f.readline()
#   music_dict = json.loads(line)

music_df = pd.DataFrame.from_dict(load_xml_file()['Tracks']).transpose()

with open('drop3.txt', 'r') as drop_file:
  drop_lines = drop_file.readlines()
  drop_lines = [drop.split('  ')[0].strip('\n') for drop in drop_lines]

for drop in drop_lines:
  music_df.drop(drop, axis=1, inplace=True)


music_df = music_df[music_df['Date Added'].isnull() == False]

music_df['year'] = pd.DatetimeIndex(music_df['Date Added']).year.astype(str)
music_df['month'] = pd.DatetimeIndex(music_df['Date Added']).month.astype(str)
music_df['sort_date'] = music_df['year'].astype(str) + music_df['month'].astype(str).str.zfill(2)
music_df.sort_values('sort_date')
print(music_df.head())

unique_dates = music_df['sort_date'].unique()
unique_dates.sort()
print(unique_dates)
'''
def split_duration(duration):
  minutes, seconds = map(int, duration.split(':'))
  return 60*minutes + seconds


def split_dateadded(line):
  month, day, year, _, _ = line.split()
  day = day[0:-1]
  month = MONTHS_TO_NUM[month]
  year = int(year)
  return month, day, year


def format_duration(duration):
  days = duration // 86400
  hours = (duration - 86400 * days) // 3600
  minutes = (duration - 86400 * days - 3600 * hours) // 60
  seconds = duration % 60
  return f'{days:.0f} days, {hours:02.0f} hours, {minutes:02.0f} min, {seconds:02.0f} sec'

def count_month(year, month):
  artist_count = defaultdict(int)
  total = 0
  total_duration = 0
  for y in range(min(date_songs.keys()), year):
    for m in range(min(date_songs[y].keys()), 13):
      for song in date_songs[y][m]:
        total += count_plays(song, artist_count)
        total_duration += count_duration(song)
  for m in range(min(date_songs[year].keys()), month+1):
    for song in date_songs[year][m]:
        total += count_plays(song, artist_count)
        total_duration += count_duration(song)
  return artist_count, total, total_duration


def count_plays(song, count_dict):
  artist, genre, playcount, _, _ = music_dict[song]
  playcount = int(playcount)
  count_dict[artist] += playcount
  return playcount


def count_duration(song, count_dict=None):
  artist, _, playcount, duration, _ = music_dict[song]
  duration = split_duration(duration) * int(playcount)
  if count_dict is not None:
    count_dict[artist] += duration
  return duration


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


def plt_data(ax1, camera, year, month, colors):
  global future_month
  global future_year
  artist_count, total, duration_total = count_month(year, month)
  chart_sizes, chart_labels, chart_explosion = create_data(artist_count, total)
  #plt.savefig('musicVisPie.svg')
  #plt.show()
  # if its the last frame
  if year == max(date_songs.keys()) and month == max(date_songs[year].keys()):
    for i in range(15):
      ax1.annotate(f'{year} - {NUM_TO_MONTHS[month]}', (1, -1), fontSize=30)
      ax1.annotate(f'{format_duration(duration_total)}', (0.45, 1.55), fontSize=16)
      ax1.annotate('Total Listening Time', (0.48, 1.65), fontSize=25)
      pie_wedges = ax1.pie(chart_sizes, labels=chart_labels, explode=chart_explosion, autopct='%1.1f%%', startangle=90,
              rotatelabels=True, textprops={'fontsize': FONTSIZE}, labeldistance=1.05)[0]
      for wedge in pie_wedges:
        wedge.set_facecolor(colors[wedge.get_label()])
      ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
      camera.snap()
  else:

    if month <= future_month and year <= future_year:
      return
    next_month = (month + 1) % 13
    interp_months = 1
    next_year = year
    if next_month == 0:
      next_year = year + 1
      next_month += 1
    next_artist_count, next_total, next_duration_total = count_month(next_year, next_month)
    while next_total < total+50 and (next_year < max(date_songs.keys()) or next_month <= 4):
      next_month += 1
      future_month = next_month-1
      future_year = next_year
      interp_months += 1
      next_artist_count, next_total, next_duration_total = count_month(next_year, next_month)

    # adjust the valeus of artists counts

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

fig1, ax1 = plt.subplots(figsize=(12, 12), dpi=130)
camera = Camera(fig1)
artists_used = set()



for year in sorted(date_songs.keys()):
  for month in sorted(date_songs[year].keys()):
    temp_artist_count = defaultdict(int)
    temp_total = 0
    for y in range(min(date_songs.keys()), year):
      for m in range(min(date_songs[y].keys()), 13):
        for song in date_songs[y][m]:
          temp_total += count_plays(song, temp_artist_count)
    for m in range(min(date_songs[year].keys()), month+1):
      for song in date_songs[year][m]:
        temp_total += count_plays(song, temp_artist_count)
    for artist, count in temp_artist_count.items():
      if count / temp_total > MIN_PCT/100:
        artists_used.add(artist)

artists_used = list(artists_used) + ['Other < 1%']
shuffle(artists_used)
cmap = plt.get_cmap(COLORMAP)
colors = cmap(np.linspace(0., 1., len(artists_used)))
artist_colors = {}
for artist, color in zip(artists_used,colors):
  artist_colors[artist] = color
print(artists_used)
print(temp_total)
future_month = -1
future_year = -1
for year in sorted():
  for month in sorted(date_songs[year].keys()):
    plt_data(ax1, camera, year, month, artist_colors)
print('animating')
animation = camera.animate(interval=1000/30,blit=True)
# for mp4's code is 'celluloid_subplots.mp4'
# for debug's code is'celluloid_subplots.gif', writer=PillowWriter(30)
animation.save('celluloid_subplots.gif', writer=PillowWriter(30))

# prints the number of seconds it took to animate
print(time.time() - start_time)
'''
'''
interp by using enumerate instead of just iteration, get difference between this month and next and gradually adjust'''
