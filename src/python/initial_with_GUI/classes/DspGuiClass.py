
import PySimpleGUI as sg
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class dsp_gui:

    def __init__(self, dpi, CANVAS_SIZE):
        width, height = CANVAS_SIZE[0] / dpi, CANVAS_SIZE[1] / dpi
        layout_tab1 = [
            [sg.Column([[sg.Canvas(size=CANVAS_SIZE, background_color='white', key='CANVAS0')],
                        [sg.Canvas(size=CANVAS_SIZE, background_color='white', key='CANVAS1')]]),
             sg.Column([[sg.Canvas(size=CANVAS_SIZE, background_color='white', key='CANVAS2')],
                        [sg.Canvas(size=CANVAS_SIZE, background_color='white', key='CANVAS3')]])]
        ]

        layout_tab2 = [
            [sg.Column([[sg.Canvas(size=CANVAS_SIZE, background_color='white', key='CANVAS4')],
                        [sg.Canvas(size=CANVAS_SIZE, background_color='white', key='CANVAS5')]]),
             sg.Column([[sg.Canvas(size=CANVAS_SIZE, background_color='white', key='CANVAS6')],
                        [sg.Canvas(size=CANVAS_SIZE, background_color='white', key='CANVAS7')]])]
        ]

        sliders_col1 = [
            [sg.Text(f'OS', key=f'OverSampling', size=(8, 1)),
                    sg.Slider(range=(2, 16), orientation='h', size=(20, 8), default_value=4, key='OS',
                                      enable_events=True, visible=True)],
            [sg.Text(f'Phase', key=f'Phase Const', size=(8, 1), visible=True),
                    sg.Slider(range=(0, 3), orientation='h', size=(20, 8), default_value=0, key='PConst',
                                      enable_events=True, visible=True)],
            [sg.Text(f'N Bauds', key=f'N B', size=(8, 1)),
             sg.Slider(range=(1, 50), orientation='h', size=(20, 8), default_value=6, key='N Bauds',
                       enable_events=True, visible=True)]

                ]

        sliders_col2 = [
            [sg.Text(f'NB', key=f'Bits_totales', size=(8, 1)),
                    sg.Slider(range=(0, 15), orientation='h', size=(20, 8), default_value=8, key='NB',
                                      enable_events=True, visible=True)],
            [sg.Text(f'NBF', key=f'Bits_fraccionales', size=(8, 1)),
                    sg.Slider(range=(0, 15), orientation='h', size=(20, 8), default_value=7, key='NBF',
                                      enable_events=True, visible=True)],
            [sg.Text(f'Beta', key=f'Beta', size=(8, 1)),
             sg.Slider(range=(0, 1), orientation='h', size=(20, 8), default_value=0.5, key='B', resolution=0.1,
                       enable_events=True, visible=True)]
                ]


        inputT_cBox = [[
                sg.Text('FB[MHz]:', visible=True), sg.InputText(key='FB', size=(10, 1), default_text=1000, enable_events=True, visible=True), #frecuencia de baudio, anteriormente 'Fc[MHz]:'
                sg.Checkbox('t=ON/r=OFF', key='t/r', default=True, enable_events=True, visible=True),
                sg.Checkbox('sat=ON/overF=OFF', key='s/oF', default=True, enable_events=True, visible=True),

                sg.Checkbox('Norm', key='Norm', default=True, enable_events=True, visible=True),
                sg.Checkbox('EnUp', key='EnUp', default=True, enable_events=False, visible=False), #stop el programa
                sg.Checkbox('Fixed', key='Fixed', enable_events=True, default=False),   #habilita o deshabilita las cuantizaciones
                sg.Checkbox('Q/I', key='Q/I', default=True, enable_events=False, visible=False),
                sg.Checkbox('offset', key='offset', default=True, enable_events=False, visible=False),
                sg.Checkbox('RRC', key='RRC', default=False, enable_events=True, visible=True),
                sg.Checkbox('FreeRun', key='freerun', default=False, enable_events=True, visible=True),
                sg.Checkbox('AWGN', key='gauss', default=False, enable_events=True, visible=True),
                sg.Slider(range=(0, 1), orientation='h', size=(8, 5), default_value=0.1, key='sigma', resolution=0.1, enable_events=True, visible=True),
                sg.Text('signed', visible=True), sg.Checkbox('sig=ON/uns=OFF', key='sig/unsig', default=True, enable_events=True, visible=False)
        ]]

        layout = [
            [sg.TabGroup([[sg.Tab('Analisis del filtro', layout_tab1),
                           sg.Tab('Diagrama de ojo', layout_tab2)]], key='tabgroup1', enable_events=True)],
            [sg.Column(inputT_cBox)],
            [sg.Column(sliders_col1), sg.Column(sliders_col2)]
        ]

        self.window = sg.Window('DSP GUI - Plot QPSK', layout, finalize=True, element_justification='center', size=(1000, 650))

        self.figures = []
        self.axes = []
        self.figure_canvas_aggs = []
        for i in range(0, 8):
            if i == 2:
                figure = Figure(figsize=(2*width, height))
            else:
                figure = Figure(figsize=(width, height))
            axes = figure.add_subplot()
            figure.subplots_adjust(bottom=0.2, left=0.15)
            figure_canvas_agg = FigureCanvasTkAgg(figure, self.window[f'CANVAS{i}'].TKCanvas)
            figure_canvas_agg.draw()
            figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
            self.figures.append(figure)
            self.axes.append(axes)
            self.figure_canvas_aggs.append(figure_canvas_agg)


    def dibujar(self, datax, datay, canvas_index, labelx, labely, title, linestyle = '', color='blue', xlim=[], bits=[]):

        self.axes[canvas_index].cla()
        if canvas_index == 0:
            self.axes[canvas_index].semilogx(datax, datay, color=color, linewidth=2)
            #self.axes[canvas_index].set_ylim(-100, 2)  # Establece los límites del eje x

        elif canvas_index == 1 or canvas_index == 3 or canvas_index == 4:

            self.axes[canvas_index].plot(datax, datay, color=color, linewidth=2)
            self.axes[canvas_index].plot(datax, bits, 'o', markersize=3)
            self.axes[canvas_index].set_xlim(xlim[0], xlim[1])  # Establece los límites del eje x

        elif canvas_index == 5:
            self.axes[canvas_index].set_ylim(-2, 2)  # Establece los límites del eje y
            self.axes[canvas_index].set_xlim(-2, 2)  # Establece los límites del eje x
            self.axes[canvas_index].plot(datax, datay, '.', color=color, linewidth=2)

        elif canvas_index == 6:
            self.axes[canvas_index].set_ylim(0, 100)  # Establece los límites del eje y
            self.axes[canvas_index].set_xlim(-0.2, 0.2)  # Establece los límites del eje x
            self.axes[canvas_index].plot(datax, datay, '.', color=color, linewidth=5)

        elif canvas_index == 7:
            for x, y in zip(datax, datay):
                self.axes[canvas_index].plot(x, y, linewidth=2, color=color)
            self.axes[canvas_index].set_xlim(xlim[0], xlim[1])  # Establece los límites del eje x
        else:
            self.axes[canvas_index].plot(datax, datay, color=color, linewidth=2)
        self.axes[canvas_index].grid(True)
        self.axes[canvas_index].set_xlabel(labelx, fontsize=8)
        self.axes[canvas_index].set_ylabel(labely, fontsize=8)
        self.axes[canvas_index].set_title(title, fontsize=8)
        self.figure_canvas_aggs[canvas_index].draw()

