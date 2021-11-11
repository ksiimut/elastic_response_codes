import scipy.stats

import data
import plotting
from scipy import stats


def slice_series(series_data):
    filename = series_data[0]

    force = series_data[1]
    disp_axial = series_data[2]
    disp_lateral = series_data[3]

    F_THRES = 0.01  # kN - Force threshold to slice a series.

    test_start_indices = []
    test_end_indices = []

    part_of_test = False
    for i in force:
        if not part_of_test and i > F_THRES:
            part_of_test = True
            test_start_indices.append(force.index(i))
        elif part_of_test and i < F_THRES:
            part_of_test = False
            test_end_indices.append(force.index(i))

    tests = []  # [[filename_1, [force_data_1], [disp_ax_data_1], [disp_lat_total_1], [disp_lat_left_1], [disp_lat_right_1]], [filename_2, ...]]

    if len(test_start_indices) != len(test_end_indices):
        print('Error with series slicing!')
        print('Starts of test found: ' + str(len(test_start_indices)))
        print('Ends of test found: ' + str(len(test_end_indices)))

    else:
        reps = len(test_start_indices)  # Number of repetitions made during one test.
        print('Slicing successful: ' + str(reps) + ' repetitions found in series.')

        OFFSET = 10  # number of data points outside the test to include (on both sides).
        for i in range(reps):
            test_start_indices[i] -= OFFSET
            test_end_indices[i] += OFFSET

        for i in range(reps):
            tests.append([filename + '_' + str(i + 1),
                          force[test_start_indices[i]:test_end_indices[i]],
                          disp_axial[test_start_indices[i]:test_end_indices[i]],
                          disp_lateral[test_start_indices[i]:test_end_indices[i]]])

    return tests


def analyse_test(test_data):

    filename = test_data[0]
    force = test_data[1]
    disp_axial = test_data[2]
    disp_lateral = test_data[3]

    for specimen in specimen_data[1:]:  # finds initial area and dimensions of specimen
        if filename[:3] == specimen[1]:
            area = specimen[4]

            if filename[0] == 'X':
                l0_axial = specimen[1]
            elif filename[0] == 'Y':
                l0_axial = specimen[2]

            if filename[3] == 'X':
                l0_lateral = specimen[1]
            elif filename[3] == 'Y':
                l0_lateral = specimen[2]
            break

    stress_data = calculate_stress(area, force[1:])
    stress_data.insert(0, 'Stress [MPa]')
    strain_axial = calculate_strain(l0_axial, disp_axial[1:])
    strain_axial.insert(0, 'Axial Strain')
    strain_lateral = calculate_strain(l0_lateral, disp_lateral[1:])
    strain_lateral.insert(0, 'Lateral Strain')

    plotting.make_graph(test_data, '')
    plotting.make_graph([stress_data, strain_axial, strain_lateral], '')


def calculate_strain(init_dim, disp_data):

    strains = []
    for i in disp_data:
        strains.append((i / init_dim) - 1)

    return strains


def calculate_stress(area, force_data):

    stresses = []  # Stresses in MPa. MAKE SURE FORCES ARE IN NEWTONS!!!
    for i in force_data:
        stresses.append(i / area)
    return stresses


def calculate_modulus(axial_strains, stresses):
    ######################
    min_strain = 0.0025
    max_strain = 0.005
    ######################
    i_min = 0
    i_max = 0

    if len(stresses) == len(axial_strains):
        for i in range(len(axial_strains)):
            if axial_strains[i] > min_strain:
                i_min = i - 1
                break
        for i in range(len(axial_strains)):
            if axial_strains[i] > max_strain:
                i_max = i + 1
                break

        result = scipy.stats.linregress(axial_strains[i_min:i_max], stresses[i_min:i_max])
        modulus = result.slope
        rvalue = result.rvalue
        print('Young\'s modulus: ' + str(modulus / 1000) + ' GPa')
        print('R^2: ' + str(rvalue))

        return [modulus, rvalue]

    else:
        print('Error in Young\'s Modulus calculation.')
        print('Number of stress data points: ' + str(len(stresses)))
        print('Number of strain data points: ' + str(len(axial_strains)))
        return None


def calculate_poisson(strain_axial, strain_lateral):
    ######################
    min_strain = 0.0025  # min and max AXIAL strains to use for calculations.
    max_strain = 0.005
    ######################
    i_min = 0
    i_max = 0

    if len(strain_axial) == len(strain_lateral):
        for i in range(len(strain_axial)):
            if strain_axial[i] > min_strain:
                i_min = i - 1
                break
        for i in range(len(strain_axial)):
            if strain_axial[i] > max_strain:
                i_max = i + 1
                break

        result = scipy.stats.linregress(strain_axial[i_min:i_max], strain_lateral[i_min:i_max])
        poisson = -result.slope
        rvalue = result.rvalue
        print('Poisson\'s Ratio: ' + str(poisson))
        print('R^2: ' + str(rvalue))

        return [poisson, rvalue]

    else:
        print('Error in Poisson\'s Ratio calculation.')
        print('Number of axial strain data points: ' + str(len(strain_axial)))
        print('Number of lateral strain data points: ' + str(len(strain_lateral)))
        return None




specimen_info_excel_path = 'C:\\Users\\Mazin\\Danmarks Tekniske Universitet\\s202962 - General\\3-E21\\' \
                           'Spec_Elastic_Response_of_3D_Printed_Forming_Tools\\Experiments\\Specimen Measuring\\' \
                           'Specimen Dimensions Summary.xlsx'
specimen_data = data.specimen_info(specimen_info_excel_path)
