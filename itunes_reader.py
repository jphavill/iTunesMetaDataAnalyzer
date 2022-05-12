import plistlib as pl
import pandas as pd
from guiExplorer import get_xml_file

# list of all available fields for an itunes song
itunes_fields = ['Track ID', 'Name', 'Artist', 'Album Artist', 'Album', 'Genre', 'Kind',
                 'Size', 'Total Time', 'Disc Number', 'Disc Count', 'Track Number',
                 'Track Count', 'Year', 'Date Modified', 'Date Added', 'Bit Rate',
                 'Sample Rate', 'Volume Adjustment', 'Equalizer', 'Play Count',
                 'Play Date', 'Play Date UTC', 'Skip Count', 'Skip Date', 'Release Date',
                 'Normalization', 'Artwork Count', 'Sort Album', 'Sort Artist',
                 'Sort Name', 'Persistent ID', 'Track Type', 'Protected', 'Apple Music',
                 'Location', 'File Folder Count', 'Library Folder Count', 'Start Time',
                 'Stop Time', 'Loved', 'Composer', 'Compilation', 'Purchased', 'Matched',
                 'Comments', 'Explicit', 'Sort Album Artist', 'Sort Composer',
                 'Disliked', 'Part Of Gapless Album', 'Clean', 'Playlist Only',
                 'Album Loved', 'Grouping', 'Work', 'Movement Name']


def load_xml_file():
    with open(get_xml_file(), 'rb') as file:
        return pl.load(file)


def create_musicdf(required_fields=('Name', 'Artist', 'Album Artist', 'Play Count', 'Skip Count', 'Album')):
    # extract the tracks (songs) from the xml file and convert them to a pandas dataframe
    music_df = pd.DataFrame.from_dict(load_xml_file()['Tracks']).transpose()
    # filter out any extraneous meta data fields
    if required_fields:
        # difference between all fields and required fields
        drop_fields = list(set(itunes_fields) - set(required_fields))
        # drop the difference as they are not required fields
        music_df.drop([drop for drop in drop_fields if drop in music_df.columns], axis=1, inplace=True)

    return music_df
