import PySimpleGUI as sg


def get_xml_file():
    # open a window which lets the user select and xml file to import
    sg.change_look_and_feel('Dark Blue 3')
    event, values = sg.Window('XML Importer',
                              [[sg.Text('Library.xml')],
                               [sg.Input(),
                               sg.FileBrowse(file_types=(("Library XML files", "*.xml"),))],
                               [sg.OK(), sg.Cancel()]]).Read()
    # if no file chosen, read in the default example data
    return values["Browse"] if values["Browse"] != '' else 'ExampleData/Library.xml'


