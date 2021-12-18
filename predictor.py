import numpy as np
import math
import plotting
import data
import user_comms

"""
NOMENCLATURE
sir - shell/infill ratio
a - cube footprint side length
l0 - cube height in loading direction
t - shell thickness

SUBSCRIPTS:
t - total
c - center
i - infill
s - shell
ic - center infill
sc - shell infill
"""


def find_size(sir, t, l0):
    # a = l0 - sir * l0 + 2 * t * sir
    # b = sir * l0 - 2 * t * sir
    # c = 2 * sir * t**2 - t * l0 * sir

    a = (l0 - 2 * t) * (sir + 1) - l0
    b = (8 * t**2 - 4 * l0 * t) * (sir + 1)
    c = (4 * l0 * t**2 - 8 * t**3) * (sir + 1)

    disc = b**2 - 4 * a * c

    if disc >= 0:
        sol1 = round((-b + math.sqrt(disc)) / (2 * a), 5)
        return sol1
    else:
        raise ValueError('Complex solutions for quadratic equation')


def calc_total_modulus(t, a, l0):
    # ASSUMPTION:
        # Shell thickness is constant around the specimen
        # Specimen width and length are equal (footprint is square)

    a_c = (a - 2 * t)**2

    v_t = (a**2) * l0
    v_c = a_c * l0
    v_ic = a_c * (l0 - 2 * t)

    f_c = v_c / v_t
    f_ic = v_ic / v_c

    e_c = E_S * E_I / (f_ic * E_S + (1 - f_ic) * E_I)
    e_t = f_c * (e_c - E_S) + E_S

    return e_t


def calc_ratio(a, t, l0):
    v_t = a**2 * l0
    v_i = ((a - 2 * t)**2) * (l0 - 2 * t)
    v_s = v_t - v_i
    sir = round(v_s / v_i, 5)
    return sir


def transpose(data):  # data = [[name1, dp11, dp12, ...], [name2, dp21, dp22, ...]]

    transposed_list = list(map(list, zip(*data)))

    return transposed_list


if __name__ == '__main__':

    e_x_0 = 334  # Experimental results of pure infill specimens in X direction
    e_y_0 = 263  # Experimental results of pure infill specimens in Y direction
    e_interaction_x = 60.5  # Difference between expected and actual intercept
    e_interaction_y = 128  # Difference between expected and actual intercept
    E_S = 1000  # Compressive modulus of pure shell (100% infill), experimental result
    E_I = e_x_0 + e_interaction_x  # Compressive modulus of pure infill (50% triangular)
    L0 = 45         # Initial length in mm in loading direction

    mode_var = input('Choose variable. Enter "Size" or "Shell": ')
    while True:
        if mode_var == 'Size' or mode_var == 'Shell':
            break
        else:
            print('Invalid input! Please try again!')
            mode_var = input('Choose variable. Enter "Size" or "Shell": ')

    save_var = input('Choose action for results. Enter "Save" or "Show": ')
    while True:
        if save_var == 'Save' or save_var == 'Show':
            break
        else:
            print('Invalid input! Please try again!')
            save_var = input('Choose action for results. Enter "Save" or "Show": ')

    if mode_var == 'Size':
        wt = round(float(input('Enter shell thickness in millimeters: ')), 3)
        size_low = round(float(input('Enter lower bound of specimen side length in millimeters: ')), 2)
        size_high = round(float(input('Enter higher bound of specimen side length in millimeters: ')), 2)
        step = round((size_high - size_low) / 20, 2)
        size_array = list(np.arange(size_low, size_high + step/10, step))
        size_array.insert(0, 'Side length [mm]')

        sirs = ['Shell/Infill ratio']
        for size in size_array[1:]:
            sirs.append(calc_ratio(size, wt, L0))

        e_array = ['Specimen Modulus [MPa]']
        for i in range(1, len(sirs)):
            e_total = round(calc_total_modulus(wt, size_array[i], L0), 3)
            e_array.append(e_total)

        data_joined = [sirs, e_array]
        dtw = transpose(data_joined)
        text = '$E_S=%i~MPa$ \n $E_I=%i~MPa$ \n $t = %.2f~mm$ \n $l_0=%i~mm$' % (E_S, E_I, wt, L0)

        if save_var == 'Save':
                savedir = user_comms.ask_save_dir('Choose save directory for results...')
                name = input('Enter file name: ')
                plotting.create_fig(name, sirs, e_array, text=text, save_dir=savedir)
                data.write_to_csv(name + '_size.csv', savedir, dtw)

        else:
            name = 'Size Method'
            plotting.create_fig(name, sirs, e_array, text=text)
            for i in dtw:
                print(i)

    elif mode_var == 'Shell':
        size = round(float(input('Enter specimen side length in millimeters: ')), 2)
        wt_low = round(float(input('Enter lower bound of shell thickness in millimeters: ')), 3)
        wt_high = round(float(input('Enter higher bound of shell thickness in millimeters: ')), 3)
        step = round((wt_high - wt_low) / 20, 2)
        if wt_low == 0:
            wt_low += 0.01
        wt_array = list(np.arange(wt_low, wt_high + step/10, step))
        wt_array.insert(0, 'Side length [mm]')

        sirs = ['Shell/Infill ratio']
        for wt in wt_array[1:]:
            sirs.append(calc_ratio(size, wt, L0))

        e_array = ['Specimen Modulus [MPa]']
        for i in range(1, len(sirs)):
            e_total = round(calc_total_modulus(wt_array[i], size, L0), 3)
            e_array.append(e_total)

        data_joined = [sirs, e_array]
        dtw = transpose(data_joined)

        text = '$E_S=%i~MPa$ \n $E_I=%i~MPa$ \n $a = %i~mm$ \n $l_0=%i~mm$' % (E_S, E_I, size, L0)
        if save_var == 'Save':
            savedir = user_comms.ask_save_dir('Choose save directory for results...')
            name = input('Enter file name: ')
            plotting.create_fig(name, sirs, e_array, text=text, save_dir=savedir)

            data.write_to_csv(name + '_shell.csv', savedir, dtw)

        else:
            name = 'Shell Method'
            plotting.create_fig(name, sirs, e_array, text=text)
            for i in dtw:
                print(i)

    else:
        raise Exception('Entered variable not recognized. Please try again.')

    """f_infill_array = ['Infill Fraction']
    e_total_array = ['Specimen Modulus [MPa]']
    wt_array = list(np.arange(0, 5, 0.2))
    wt_array.insert(0, 'Wall thickness [mm]')
    # print(wt_array)
    si_array = ['Shell/Infill Ratio']
    for i in wt_array[1:]:
        si_array.append(calc_ratio(WIDTH, i, L0))
    # si_array = list(np.arange(0, 0.16, 0.01))
    # si_array.insert(0, 'Shell/Infill Ratio')
    for i in range(1, len(si_array[1:]) + 1):
        f_infill_array.append(1 / (si_array[i] + 1))
        e_total = round(calc_total_modulus(wt_array[i], WIDTH, L0), 5)
        # e_total = calc_total_modulus(WT, find_size(si, WT, L0), L0)
        e_total_array.append(e_total)
    print(e_total_array)
    print(si_array)
    saved = user_comms.ask_save_dir('Choose save dir...')
    data_array = [si_array, e_total_array]

    name = input('Enter simulation name: ')

    data.write_to_csv(name + '.csv', saved, data_array)
    # text = '$E_S=%i~MPa$ \n $E_I=%i~MPa$ \n $t=%.2f~mm$ \n $l_0=%i~mm$' % (E_S, E_I, WT, L0)
    text = '$E_S=%i~MPa$ \n $E_I=%i~MPa$ \n $a=l_0=%i~mm$' % (E_S, E_I, L0)
    plotting.create_fig(name, si_array, e_total_array, text=text, save_dir=saved)"""
