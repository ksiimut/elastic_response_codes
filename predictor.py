import numpy as np
import math
import plotting

def find_size(B, W, L0):
    # a = L0 - B * L0 + 2 * W * B
    # b = B * L0 - 2 * W * B
    # c = 2 * B * W**2 - W * L0 * B

    a = (L0 - 2 * W) * (B + 1) - L0
    b = (8 * W**2 - 4 * L0 * W) * (B + 1)
    c = (4 * L0 * W**2 - 8 * W**3) * (B + 1)

    disc = b**2 - 4 * a * c

    if disc >= 0:
        sol1 = round((-b + math.sqrt(disc)) / (2 * a), 5)
        return sol1
    else:
        raise ValueError('Complex solutions for quadratic equation')


def calc_total_modulus(wall, width, l0):
    # ASSUMPTION:
        # Shell thickness is constant around the specimen
        # Specimen width and length are equal (footprint is square)

    area_center = (width - 2 * wall)**2
    v_shell_center = area_center * 2 * wall
    v_infill_center = area_center * (l0 - 2 * wall)
    v_total_center = v_shell_center + v_infill_center
    f_infill_center = v_infill_center / v_total_center
    e_center = E_SHELL * E_INFILL / ((1 - f_infill_center) * E_SHELL + f_infill_center * E_SHELL)

    v_total = width**2 * l0
    f_center = v_total_center / v_total
    e_total = f_center * e_center + (1 - f_center) * E_SHELL

    return e_total


def calc_ratio(width, wall, len_init):
    volume_total = width**2 * len_init
    volume_infill = (width - 2 * wall)**2 * (len_init - 2 * wall)
    volume_shell = volume_total - volume_infill
    si_ratio = round(volume_shell / volume_infill, 5)
    return si_ratio


if __name__ == '__main__':

    E_SHELL = 1000  # Compressive modulus of pure shell (100% infill)
    E_INFILL = 250  # Compressive modulus of pure infill (50% triangular)
    # SI = 0.1        # Shell/Infill ratio
    WT = 0.55          # Wall thickness in mm
    L0 = 45         # Initial length in mm in loading direction

    f_infill_array = ['Infill Fraction']
    e_total_array = ['Specimen Modulus [MPa]']
    si_array = list(np.arange(0, 0.16, 0.01))
    si_array.insert(0, 'Shell/Infill Ratio')
    for si in si_array[1:]:
        f_infill_array.append(1 / (si + 1))
        e_total = calc_total_modulus(WT, find_size(si, WT, L0), L0)
        e_total_array.append(e_total)

    text = '$E_S=%i~MPa$ \n $E_I=%i~MPa$ \n $t=%.2f~mm$ \n $l_0=%i~mm$' % (E_SHELL, E_INFILL, WT, L0)
    plotting.create_fig('test1', si_array, e_total_array)
