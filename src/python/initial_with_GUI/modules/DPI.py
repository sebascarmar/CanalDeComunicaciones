import PySimpleGUI as sg

def get_dpi():
    window = sg.Window('Get DPI', [[sg.Text('DPI:'), sg.Text(key='DPI')]])
    window.read(timeout=0)
    dpi = window.TKroot.winfo_fpixels('1i')
    window.close()
    return dpi






