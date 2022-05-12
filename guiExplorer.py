import PySimpleGUI as sg
import plistlib as pl
import pandas as pd


def get_xml_file():
    event, values = sg.Window('XML Importer',
                              [[sg.Text('Library.xml')],
                               [sg.Input(),
                               sg.FileBrowse(file_types=(("Library XML files", "*.xml"),))],
                               [sg.OK(), sg.Cancel()]]).Read()
    file = values["Browse"] if values["Browse"] != '' else 'Library.xml'

    return file


def load_xml_file():
    with open(get_xml_file(), 'rb') as file:
        return pl.load(file)


def create_musicdf(dropfile=False):
    music_df = pd.DataFrame.from_dict(load_xml_file()['Tracks']).transpose()

    if dropfile:
        with open(dropfile, 'r') as drop_file:
            drop_lines = drop_file.readlines()

        drop_lines = [drop.split('  ')[0].strip('\n') for drop in drop_lines]
        music_df.drop([drop for drop in drop_lines if drop in music_df.columns], axis=1, inplace=True)

    return music_df
