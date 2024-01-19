
from modules.tx_rcosine_procom import *


def build_tab(current_tab, t, filt, dot, B, T, OS, values, Nbaud, aplicacion, symbolsI_tx, symbolsQ_tx,
    berI_rx, berQ_rx, Q_I, offsetQ, offsetI, bits_salI, bits_salQ, bits_upSI_plot, bits_upSQ_plot, phase, bits_salI_first_stage, bits_salQ_first_stage):


    if Q_I:
        ber = berQ_rx
        symbols_tx = symbolsQ_tx
        sel = 'Q'
        col = 'green'
        symb_out = bits_salQ    #Q
        offset = offsetQ
    else:
        ber = berI_rx
        symbols_tx = symbolsI_tx
        sel = 'I'
        col = 'red'
        symb_out = bits_salI    #I
        offset = offsetI

    if current_tab == 'Analisis del filtro':
        (x1, y1) = bode(filt, T / OS, Nfreqs)
        aplicacion.dibujar(x1, y1, 0, 'Frequencia [Hz]', 'Magnitud [dB]',
                           f"Grafico de Bode TX*RX: fB[MHz]={values['FB']} /OS={OS} /NBAUDS={Nbaud}")
        ###############################################
        aplicacion.dibujar(t, filt, 2, 'Tiempo', 'Magnitud', f"Grafico de pulso TX*RX en funcion de roll-off(B) - DOT = {dot}")
        ###############################################
        aplicacion.dibujar(np.arange(len(bits_salI)), bits_salI, 1, 'Muestras', 'Magnitud',
                           f"Conv. Filtro (TX*RX) *Simbolos - B = {B} / I(real) / Offset = {offsetI}",
                           color="red", bits=bits_upSI_plot, xlim=[0, 150])
        ###############################################
        aplicacion.dibujar(np.arange(len(bits_salQ)), bits_salQ, 3, 'Muestras', 'Magnitud',
                           f"Conv. Filtro (TX*RX) * Simbolos - B = {B} / Q(imag) / Offset = {offsetQ}",
                           color="green", bits=bits_upSQ_plot, xlim=[0, 150])
    elif current_tab == 'Diagrama de ojo':

        ###############################################
        eye_d = eyediagram(int(OS), int(values['PConst']), Nbaud, bits_salI_first_stage)
        datax = [x for x, y in eye_d[0]]
        datay = [y for x, y in eye_d[0]]
        aplicacion.dibujar(datax, datay, 7, 'Muestras', 'Magnitud', f"Diagrama de ojo TX - {sel}", color=col,
                           xlim=eye_d[1])
        ###############################################

        (x1, y1) = dispersion(int(values['PConst']), int(OS), bits_salI, bits_salQ)
        aplicacion.dibujar(x1, y1, 5, 'Real', 'Imag', f"Diagrama de constelaciones TX (Dispersion)", color=col)
        ###############################################
        # Plot DownSampling
        downSamp = symb_out[phase::int(OS)]
        downSamp = downSampling(downSamp)  # DownSampled signal, with integer values
        x = np.arange(len(downSamp))
        aplicacion.dibujar(x, downSamp, 4, 'Muestras', 'Magnitud', f"Salida DownSampling - {sel} / Offset = {offset}",
                          color=col, bits=symbols_tx, xlim=[0, 50])
        # Plot BER
        b_e_r = round(ber.calculo_BER(), 2)
        errores = ber.bits_errores
        aplicacion.dibujar([0], b_e_r, 6, '', 'BER%', f"Bits Error Rate Counter {sel} - BER = {b_e_r}% - Counter = {errores}",
                          color=col)

    return


