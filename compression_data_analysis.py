

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
            test_end_indices[i] -= OFFSET

        tests = []  # [[filename_1, [forcedata_1], [disp_ax_data_1], [disp_lat_data_1]], [filename_2, ...]]

        for i in range(reps):
            tests.append([filename + '_' + str(i + 1),
                          force[test_start_indices[i]:test_end_indices[i]],
                          disp_axial[test_start_indices[i]:test_end_indices[i]],
                          disp_lateral[test_start_indices[i]:test_end_indices[i]]])




def analyse_test(test_data):
    filename = test_data[0]

    force = test_data[1]
    disp_axial = test_data[2]
    disp_lateral = test_data[3]
