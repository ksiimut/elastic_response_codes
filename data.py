import os
import csv
import pandas as pd
import numpy as np
import user_comms


def readDAT(path):

    dat_name = path.split('/')[-1]
    pieces = dat_name.split('_')
    date_of_testing = pieces[0]
    specimen_id = pieces[1].split('.')[0]  # X40Z / X40Y (loadingdir + dimension + lateral disp axis)
    filename = specimen_id + '_' + date_of_testing

    force = ['Compressive Load [N]']                          # Compressive load, measured with load cell.
    disp_ax = ['Axial Displacement [mm]']           # Axial displacement, measured with built-in LVDT.
    disp_lat_l = ['Lateral Displacement (L) [mm]']  # Lateral displacement measured with left disp sensor (Strain 7-1).
    disp_lat_r = ['Lateral Displacement (R) [mm]']  # Lateral displacement measured with right disp sensor (Strain 7-3).
    disp_lat_total = ['Lateral Displacement (Total) [mm]']  # Total lateral displacement.

    empty_line_counter = 0
    f = open(path, 'rt')
    while True:
        if empty_line_counter < 3:
            try:
                line = f.readline().strip('\n').split('\t')
                if len(line) < 4:
                    empty_line_counter += 1
                    continue
                else:
                    empty_line_counter = 0
                    force.append(-round(float(line[0].replace(',', '.')), 5))
                    disp_ax.append(-round(float(line[1].replace(',', '.')), 5))
                    disp_lat_l.append(round(float(line[2].replace(',', '.')), 5))
                    disp_lat_r.append(round(float(line[3].replace(',', '.')), 5))
            except:
                pass
        else:
            break
    f.close()

    print('Number of data points: ')
    print('Force: ' + str(len(force) - 1))  # -1 for the header row
    print('Axial Displacement: ' + str(len(disp_ax) - 1))
    print('Lateral Displacement (L): ' + str(len(disp_lat_l) - 1))
    print('Lateral Displacement (R): ' + str(len(disp_lat_r) - 1))

    if len(force) != len(disp_ax) != len(disp_lat_l) != disp_lat_r:
        print('Faulty DAT file import! The number of data points does not match between different types of data.')
        return None

    else:
        for i in range(1, len(disp_lat_l)):
            disp_lat_total.append(round(disp_lat_l[i] + disp_lat_r[i], 5))

        return [filename, force, disp_ax, disp_lat_total, disp_lat_l, disp_lat_r]


def specimen_info(path):
    # print(path)
    df = pd.DataFrame(pd.read_excel(path, header=None))
    a = df.values.tolist()
    a[0].append('A [mm^2]')

    for specimen in a[1:]:
        loading_dir = specimen[0][0]
        if loading_dir == 'X':
            area = round(specimen[2] * specimen[3], 5)
            specimen.append(area)
        elif loading_dir == 'Y':
            area = round(specimen[1] * specimen[3], 5)
            specimen.append(area)
        else:
            print('Error! Could not find loading direction of specimen!')
    return a


def decrease_resolution(data, decrease_x_times):

    low_res_data = [data[0]]

    for i in range(1, len(data)):
        low_res_data.append(average_data(data[i], decrease_x_times))

    lengths = []
    for dataset in low_res_data:
        if low_res_data.index(dataset) == 0:
            continue
        lengths.append(len(dataset))

    if lengths[0] == lengths[1] == lengths[2] == lengths[3]:
        pass
    else:
        print('Error! Lower resolution datasets do not have the same length!')
    return low_res_data


def average_data(data_list, average_of):  # Averages the datapoints of an input list and returns a new list.

    filtered = [data_list[0]]  # Excludes the column name from calculations.
    temp = []
    for point in data_list[1:]:
        if len(temp) < average_of:
            temp.append(point)
        elif len(temp) == average_of:
            new_point = round(sum(temp)/len(temp), 5)
            filtered.append(new_point)
            temp.clear()

    return filtered


def transpose_list(data, save_dir):  # data: [filename, [dataset1], [dataset2], ...]

    filename = data.pop(0)                          # Removes the filename from the list.
    transposed_list = list(map(list, zip(*data)))     # transposes the data
    transposed_list.insert(0, filename)

    return transposed_list


def offset_zero(force_array, axial_disp_array):  # Input either sliced or non-sliced.
    i = 1
    F_THRES = 2  # N Load threshold for detecting start of test.
    while i < len(force_array):
        if force_array[i] > F_THRES:
            i -= 10
            if i < 0:
                i = 1
            break
        else:
            i += 1

    disp_offset = axial_disp_array[i]
    print('Displacement was offset by: ' + str(disp_offset))
    for measurand in axial_disp_array[1:]:
        measurand -= disp_offset

    return [force_array, axial_disp_array]


def find_retract(data):  # Returns index, where unloading starts.

    force = data[1]

    force_change = 0
    cont_drop = 0  # How many points in a row have been dropping.
    DROP_THRES = 10  # How many points in a row have to drop.
    LOAD_THRES = -10  # Change in force [N] that will be counted as a drop.
    for i in range(2, len(force[2:])):
        force_change = force[i] - force[i - 1]
        if force_change < LOAD_THRES:
            cont_drop += 1
            if cont_drop == DROP_THRES:
                return i - DROP_THRES


def write_to_csv(filename, save_dir, data_to_write):
    with open(os.path.join(save_dir, filename), mode='w+', newline='') as file:
        file_writer = csv.writer(file, delimiter=';')
        for row in data_to_write:
            file_writer.writerow(row)


"""force = ['Force [kN]', 1,2,3,4,5,6,7,8,9,10]
disp_axial = ['Axial Displacement [mm]', 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
disp_lateral = ['Lateral Displacement [mm]',0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
test_list = ['test.csv', force, disp_axial, disp_lateral]
print(transpose_list(test_list, 'dir'))
filepath = user_comms.ask_src_path(0)
excelpath = 'C:\\Users\\Mazin\\Danmarks Tekniske Universitet\\s202962 - General\\3-E21\\' \
            'Spec_Elastic_Response_of_3D_Printed_Forming_Tools\\Experiments\\Specimen Measuring\\' \
            'Specimen Dimensions Summary.xlsx'
print(specimen_info(excelpath))"""

