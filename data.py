import os
import csv

def readDAT(path):

    dat_name = path.split('/')[-1]
    pieces = dat_name.split('.')[-2].split('_')
    date = pieces[2]
    specimen_id = pieces[3]  # X40Z / X40Y (loadingdir + dimension + lateral disp axis)
    filename = specimen_id + '_' + date

    force = ['Force [kN]']                          # Compressive load, measured with load cell.
    disp_ax = ['Axial Displacement [mm]']           # Axial displacement, measured with built-in LVDT.
    disp_lat_l = ['Lateral Displacement (L) [mm]']  # Lateral displacement measured with left disp sensor.
    disp_lat_r = ['Lateral Displacement (R) [mm]']  # Lateral displacement measured with right disp sensor.

    empty_line_counter = 0
    f = open(path, 'rt')
    while True:
        if empty_line_counter < 3:
            try:
                line = f.readline().strip('\n').split(' ')
                if len(line) < 4:
                    empty_line_counter += 1
                    continue
                else:
                    empty_line_counter = 0
                    disp_ax.append(round(float(line[0].replace(',', '.')), 5))
                    force.append(round(float(line[1].replace(',', '.')), 5))
                    disp_lat_l.append(round(float(line[2].replace(',', '.')), 5))
                    disp_lat_r.append(round(float(line[3].replace(',', '.')), 5))
            except:
                pass
        else:
            break
    f.close()

    print('Number of data points: ')
    print('Force: ' + str(len(force) - 1))
    print('Axial Displacement: ' + str(len(disp_ax) - 1))
    print('Lateral Displacement (L): ' + str(len(disp_lat_l) - 1))
    print('Lateral Displacement (R): ' + str(len(disp_lat_r) - 1))

    return [filename, force, disp_ax, disp_lat_l, disp_lat_r]


def decrease_resolution(data, decrease_x_times):

    low_res_data = [data[0]]

    i = 1
    while i < len(data):
        low_res_data.append(average_data(data[i], decrease_x_times))
        i += 1

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
            if len(temp) == average_of:
                new_point = round(sum(temp)/len(temp), 5)
                filtered.append(new_point)
                temp.clear()

    return filtered


def transpose_list(data, save_dir):  # data: [filename, [dataset1], [dataset2], ...]

    filename = data.pop(0)                          # Removes the filename from the list.
    transposed_list = list(map(list, zip(*data)))     # transposes the data
    transposed_list.insert(0, filename)

    return transposed_list


def write_to_csv(filename, save_dir, data_to_write):
    with open(os.path.join(save_dir, filename), mode='w+', newline='') as file:
        file_writer = csv.writer(file, delimiter=';')
        for row in data_to_write:
            file_writer.writerow(row)


"""force = ['Force [kN]', 1,2,3,4,5,6,7,8,9,10]
disp_axial = ['Axial Displacement [mm]', 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
disp_lateral = ['Lateral Displacement [mm]',0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
test_list = ['test.csv', force, disp_axial, disp_lateral]
print(transpose_list(test_list, 'dir'))"""


