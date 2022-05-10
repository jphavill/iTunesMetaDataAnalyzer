import PySimpleGUI as sg


def get_xml_file():
    event, values = sg.Window('XML Importer', [[sg.Text('Library.xml')], [sg.Input(), sg.FileBrowse(file_types=(("Library XML files", "*.xml"),))], [sg.OK(), sg.Cancel()] ]).Read()
    return values["Browse"]