import os
import user_comms
import data
import plotting
from DestructiveTest import DestructiveTest
from TestSeries import TestSeries

"""
class TestSeries:

    def __init__(self, filepath, specimen_info):
        self.path = filepath
        dat = self.read_dat()

        self.specimen_id = dat[0]
        self.test_date = dat[1]
        self.filename = dat[2]
        self.force = dat[3]
        self.disp_ax = dat[4]
        self.disp_lat_total = dat[5]
        self.disp_lat_l = dat[6]
        self.disp_lat_r = dat[7]

        sizes = self.find_specimen_size(specimen_info)
        self.area = sizes[0]
        self.l0_axial = sizes[1]
        self.l0_lateral = sizes[2]

    def read_dat(self):
        print('Class TestSeries initiated.')

        dat_name = self.path.split('/')[-1]
        pieces = dat_name.split('_')
        date_of_testing = pieces[0]
        specimen_id = pieces[1].split('.')[0]  # X40Z / X40Y (loadingdir + dimension + lateral disp axis)

        filename = specimen_id + '_' + date_of_testing
        force = ['Compressive Load [N]']  # Compressive load, measured with load cell.
        disp_ax = ['Axial Displacement [mm]']  # Axial displacement, measured with built-in LVDT.
        disp_lat_l = ['Lateral Displacement (L) [mm]']  # Lateral displacement measured with Strain 7-1 (left).
        disp_lat_r = ['Lateral Displacement (R) [mm]']  # Lateral displacement measured with Strain 7-3 (right).
        disp_lat_total = ['Lateral Displacement (Total) [mm]']  # Total lateral displacement, sum of L and R.

        empty_line_counter = 0
        f = open(self.path, 'rt')
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

        if len(force) != len(disp_ax) or len(force) != len(disp_lat_l) or \
                len(force) != len(disp_lat_r) or len(disp_ax) != len(disp_lat_l) or \
                len(disp_ax) != len(disp_lat_r) or len(disp_lat_l) != len(disp_lat_r):
            print('Faulty DAT file import! The number of data points does not match between different types of data.')
            print('Number of data points: ')
            print('Force: ' + str(len(force) - 1))  # -1 for the header row
            print('Axial Displacement: ' + str(len(disp_ax) - 1))
            print('Lateral Displacement (L): ' + str(len(disp_lat_l) - 1))
            print('Lateral Displacement (R): ' + str(len(disp_lat_r) - 1))

        else:
            for i in range(1, len(disp_lat_l)):
                disp_lat_total.append(round(-(disp_lat_l[i] + disp_lat_r[i]), 5))

        read_data = [specimen_id,
                     date_of_testing,
                     filename,
                     force,
                     disp_ax,
                     disp_lat_total,
                     disp_lat_l,
                     disp_lat_r]
        return read_data

    def find_specimen_size(self, specimen_data):
        for specimen in specimen_data[1:]:  # finds initial area and dimensions of specimen
            if self.specimen_id[:3] == specimen[0]:
                area = specimen[4]
                loading_direction = self.specimen_id[0]
                lateral_disp_measuring_direction = self.specimen_id[3]
                print('Loading direction: ' + loading_direction)
                print('Lateral direction: ' + lateral_disp_measuring_direction)

                if loading_direction == 'X':
                    l0_axial = specimen[1]
                elif loading_direction == 'Y':
                    l0_axial = specimen[2]

                if lateral_disp_measuring_direction == 'X':
                    l0_lateral = specimen[1]
                elif lateral_disp_measuring_direction == 'Y':
                    l0_lateral = specimen[2]
                elif lateral_disp_measuring_direction == 'Z':
                    l0_lateral = specimen[3]
                return [area, l0_axial, l0_lateral]

    def decrease_resolution(self, decrease_x_times):

        self.force = data.average_data(self.force, decrease_x_times)
        self.disp_ax = data.average_data(self.disp_ax, decrease_x_times)
        self.disp_lat_total = data.average_data(self.disp_lat_total, decrease_x_times)
        self.disp_lat_l = data.average_data(self.disp_lat_l, decrease_x_times)
        self.disp_lat_r = data.average_data(self.disp_lat_r, decrease_x_times)

        lengths = [len(self.force),
                   len(self.disp_ax),
                   len(self.disp_lat_total),
                   len(self.disp_lat_l),
                   len(self.disp_lat_r)]

        equal = True
        for i in range(len(lengths) - 1):  # Check all combinations of values in lengths to check for equality.
            for j in range(i + 1, len(lengths)):
                if lengths[i] != lengths[j]:
                    equal = False
        if equal:
            print('Resolution decreased by ' + str(decrease_x_times) + ' times.')
            pass
        else:
            print('Error! Datasets with lowered resolution do not have the same length!')

    def slice_series(self):

        F_THRES = 1  # N - Force threshold to slice a series.

        test_start_indices = []
        test_end_indices = []

        part_of_test = False
        count = 0  # How many points in a row are over the threshold.
        COUNT_THRES = 3  # How many points need to be over the threshold.
        OFFSET = 5  # Number of data points outside the test to include (on both sides).

        for i in self.force[1:]:
            # print('Count: ' + str(count) + '. Force: ' + str(i))
            if not part_of_test and i > F_THRES:
                count += 1
                if count >= COUNT_THRES:
                    part_of_test = True
                    test_start_indices.append(self.force.index(i) - COUNT_THRES - OFFSET)
                    count = 0
                    # print('Start force [N]: ' + str(i))
            elif not part_of_test and i < F_THRES:
                count = 0

            elif part_of_test and i < F_THRES:
                count += 1
                if count >= COUNT_THRES:
                    part_of_test = False
                    test_end_indices.append(self.force.index(i) + COUNT_THRES + OFFSET)
                    count = 0
                    # print('End force [N]: ' + str(i))
            elif part_of_test and i > F_THRES:
                count = 0

        # print(test_start_indices)
        # print(test_end_indices)

        if len(test_start_indices) != len(test_end_indices):
            print('Error with series slicing!')
            print('Starts of test found: ' + str(len(test_start_indices)))
            print('Ends of test found: ' + str(len(test_end_indices)))
            return None

        else:
            reps = len(test_start_indices)  # Number of repetitions made during one test.
            print('Slicing successful: ' + str(reps) + ' repetitions found in series.')
            tests = []  # Repetition class instances

            for i in range(reps):
                slicename = self.filename + '_Rep_' + str(i + 1)
                force_slice = self.force[test_start_indices[i]:test_end_indices[i]]
                disp_ax_slice = self.disp_ax[test_start_indices[i]:test_end_indices[i]]
                disp_lat_total_slice = self.disp_lat_total[test_start_indices[i]:test_end_indices[i]]
                disp_lat_l_slice = self.disp_lat_l[test_start_indices[i]:test_end_indices[i]]
                disp_lat_r_slice = self.disp_lat_r[test_start_indices[i]:test_end_indices[i]]

                # Add data headers to first position.
                force_slice.insert(0, self.force[0])
                disp_ax_slice.insert(0, self.disp_ax[0])
                disp_lat_total_slice.insert(0, self.disp_lat_total[0])
                disp_lat_l_slice.insert(0, self.disp_lat_l[0])
                disp_lat_r_slice.insert(0, self.disp_lat_r[0])

                tests.append(Repetition(slicename,
                                        force_slice,
                                        disp_ax_slice,
                                        disp_lat_total_slice,
                                        disp_lat_l_slice,
                                        disp_lat_r_slice,
                                        self.area,
                                        self.l0_axial,
                                        self.l0_lateral))

        return tests

    def offset_series_zero(self):

        F_THRES = 2  # N Load threshold for detecting start of test.
        i = 1
        count = 0
        for load in self.force[1:]:
            COUNT_THRES = 5
            # print('Count: ' + str(count) + '. Force: ' + str(load))
            if load > F_THRES:
                count += 1
                if count >= COUNT_THRES:
                    i = self.force.index(load)
                    i -= COUNT_THRES
                    if i < 1:
                        i = 1
                    break

        disp_offset = self.disp_ax[i]
        print('Displacement of the series was offset by: ' + str(disp_offset) + ' mm.')
        disp_ax_offset = [self.disp_ax[0]]
        for measurand in self.disp_ax[1:]:
            disp_ax_offset.append(round(measurand - disp_offset, 5))

        self.disp_ax = disp_ax_offset


class Repetition(TestSeries):

    def __init__(self, title, force, disp_ax, disp_lat_total, disp_lat_l, disp_lat_r, area, l0_axial, l0_lateral):

        self.title = title
        self.specimen_id = title[:3]
        self.test_date = title.split('_')[1]
        self.lat_dir = title[3]
        self.repetition = title.split('_')[2]
        self.force = force
        self.disp_ax = disp_ax
        self.disp_lat_total = disp_lat_total
        self.disp_lat_l = disp_lat_l
        self.disp_lat_r = disp_lat_r
        self.area = area
        self.l0_axial = l0_axial
        self.l0_lateral = l0_lateral
        self.tipping_point = self.find_retract()
        self.axial_strains = self.calculate_axial_strain()
        self.lateral_strains = self.calculate_lateral_strain()
        self.stresses = self.calculate_stress()
        self.comp_modulus = self.calculate_modulus()  # [modulus, rsq]
        self.poisson = self.calculate_poisson()  # [poisson, rsq]

    def find_retract(self):  # Returns index, where unloading starts.

        cont_drop = 0  # How many points in a row have been dropping.
        DROP_THRES = 3  # How many points in a row have to drop.
        LOAD_THRES = -5  # Change in force [N] that will be counted as a drop.
        for i in range(1, len(self.force[1:-1])):
            force_change = self.force[i + 1] - self.force[i]
            if force_change < LOAD_THRES:
                cont_drop += 1
                if cont_drop >= DROP_THRES:
                    return i - DROP_THRES

    def offset_rep_zero(self):
        F_THRES = 2  # N Load threshold for detecting start of test.
        i = 1
        count = 0
        for load in self.force[1:]:
            COUNT_THRES = 5
            # print('Count: ' + str(count) + '. Force: ' + str(load))
            if load > F_THRES:
                count += 1
                if count >= COUNT_THRES:
                    i = self.force.index(load)
                    i -= COUNT_THRES
                    if i < 1:
                        i = 1
                    break

        disp_offset = self.disp_ax[i]
        print('Displacement of repetition ' + self.repetition + ' was offset by: ' + str(disp_offset) + ' mm.')
        disp_ax_offset = [self.disp_ax[0]]
        for measurand in self.disp_ax[1:]:
            disp_ax_offset.append(round(measurand - disp_offset, 5))

        self.disp_ax = disp_ax_offset

    def calculate_axial_strain(self):

        strains = ['Compressive Strain [mm/mm]']
        for i in self.disp_ax[1:]:
            strains.append(round(i / self.l0_axial, 8))
        return strains

    def calculate_lateral_strain(self):

        strains = ['Lateral Strain [mm/mm]']
        for i in self.disp_lat_total[1:]:
            strains.append(round(i / self.l0_lateral, 8))
        return strains

    def calculate_stress(self):

        stresses = ['Compressive Stress [MPa]']
        for i in self.force[1:]:
            stresses.append(round(i / self.area, 5))
        return stresses

    def calculate_modulus(self):
        ######################
        min_strain = 0.004
        max_strain = 0.01
        ######################
        i_min = 1  # not 0 to exclude the data header.
        i_max = 1
        if len(self.stresses) == len(self.axial_strains):
            for i in range(1, len(self.axial_strains)):
                if self.axial_strains[i] > min_strain:
                    i_min = i - 1
                    if i < 1:
                        i_min = 1
                    break
            for i in range(1, len(self.axial_strains)):
                if self.axial_strains[i] > max_strain:
                    i_max = i
                    break
            result = scipy.stats.linregress(self.axial_strains[i_min:i_max], self.stresses[i_min:i_max])
            modulus = round(result.slope / 1000, 3)  # GPa
            rsq = round(result.rvalue**2, 5)
            # print('Young\'s modulus: ' + str(modulus) + ' GPa')
            # print('R^2: ' + str(rsq))

            return [modulus, rsq]

        else:
            print('Error in Young\'s Modulus calculation.')
            print('Number of stress data points: ' + str(len(self.stresses)))
            print('Number of strain data points: ' + str(len(self.axial_strains)))
            return None

    def calculate_poisson(self):
        ######################
        min_strain = 0.004  # min and max AXIAL strains to use for calculations.
        max_strain = 0.01
        ######################
        i_min = 1
        i_max = 1

        if len(self.axial_strains) == len(self.lateral_strains):
            for i in range(1, len(self.axial_strains)):
                if self.axial_strains[i] > min_strain:
                    i_min = i - 1
                    if i < 1:
                        i_min = 1
                    break
            for i in range(1, len(self.axial_strains)):
                if self.axial_strains[i] > max_strain:
                    i_max = i + 1
                    break

            result = scipy.stats.linregress(self.axial_strains[i_min:i_max], self.lateral_strains[i_min:i_max])
            poisson = round(-result.slope, 5)
            rsq = round(result.rvalue**2, 5)
            # print('Poisson\'s Ratio: ' + str(poisson))
            # print('R^2: ' + str(rsq))

            return [poisson, rsq]

        else:
            print('Error in Poisson\'s Ratio calculation.')
            print('Number of axial strain data points: ' + str(len(self.axial_strains)))
            print('Number of lateral strain data points: ' + str(len(self.lateral_strains)))
            return None

    def get_rep_summary(self):
        headers = ['Specimen ID', 'Date of Testing', 'Repetition',
                   'Compressive Modulus [GPa]', 'RSQ',
                   'Poisson Direction', 'Poisson\'s Ratio', 'RSQ']
        summary = [self.specimen_id, self.test_date, self.repetition,
                   self.comp_modulus[0], self.comp_modulus[1],
                   self.lat_dir, self.poisson[0], self.poisson[1]]
        return summary

    def get_inputs(self):
        ary = [self.specimen_id, self.test_date, self.repetition, self.lat_dir, self.area, self.tipping_point]
        print(ary)

"""


def make_dirs(parent, namelist):

    for d in namelist:
        try:
            dir_path = os.path.join(parent, d)
            os.mkdir(dir_path)
        except OSError as error:
            print(error)


if __name__ == '__main__':
    specimen_info_excel_path_LT = 'C:\\Users\\kaare\\Danmarks Tekniske Universitet\\s202962 - General\\3-E21\\' \
                                  'Spec_Elastic_Response_of_3D_Printed_Forming_Tools\\Experiments\\Specimen Measuring\\' \
                                  'Specimen Dimensions Summary.xlsx'
    specimen_info_excel_path_PC = 'C:\\Users\\Mazin\\Danmarks Tekniske Universitet\\s202962 - General\\3-E21\\' \
                                  'Spec_Elastic_Response_of_3D_Printed_Forming_Tools\\Experiments\\Specimen Measuring\\' \
                                  'Specimen Dimensions Summary.xlsx'
    specimen_sizes = data.specimen_info(specimen_info_excel_path_LT)

    var = int(input('Test batch (0) or single file (9): '))
    plt_var = input('Show plots (sh), save plots (sa), no plots (n)?')
    sum_var = input('Show summary (sh), save summary (sa), no summary (n)?')
    if var == 0:
        data_path = user_comms.ask_src_path(1)  # Ask user for folder path
        summary = [['Specimen ID', 'Date of Testing', 'Repetition', 'Zero Offset [mm]',
                    'Compressive Modulus [MPa]', 'RSQ',
                    'Poisson Direction', 'Poisson\'s Ratio', 'RSQ']]
        if plt_var == 'sh':

            for f in os.listdir(data_path):
                series_data_path = os.path.join(data_path, f).replace('\\', '/')
                a = TestSeries(series_data_path, 5, specimen_sizes)  # Create instance of TestSeries

                slices = a.slice_series()
                for rep in slices:
                    summary.append(rep.get_rep_summary())
                    text = 'Compressive Modulus: %.1f MPa \n Poisson\'s Ratio: %.3f' \
                           % (rep.comp_modulus[0], rep.poisson[0])
                    plotting.create_fig(rep.title,
                                        rep.axial_strains,
                                        rep.stresses,
                                        retract_index=rep.tipping_point,
                                        x2=rep.lateral_strains,
                                        text=text,
                                        line=rep.comp_modulus[:2])
            if sum_var == 'sh':
                for l in summary:
                    print(l)

            elif sum_var == 'sa':
                summary_save_dir = user_comms.ask_save_dir('Choose Save Directory for Summary...')
                summary_name = input('Enter summary file name (ending.csv)')
                data.write_to_csv(summary_name, summary_save_dir, summary)

        elif plt_var == 'sa':

            plt_save_dir = user_comms.ask_save_dir('Choose Save Directory for Plots...')

            spec_dirs = []
            for f in os.listdir(data_path):
                spec_dirs.append(f.strip('.dat'))
            make_dirs(plt_save_dir, spec_dirs)

            for f in os.listdir(data_path):
                series_data_path = os.path.join(data_path, f).replace('\\', '/')
                a = TestSeries(series_data_path, 5, specimen_sizes)  # Create instance of TestSeries
                rep_save_dir = os.path.join(plt_save_dir, a.filename)

                slices = a.slice_series()
                for rep in slices:
                    summary.append(rep.get_rep_summary())
                    text = 'Compressive Modulus: %.1f MPa \n Poisson\'s Ratio: %.3f' \
                           % (rep.comp_modulus[0], rep.poisson[0])
                    plotting.create_fig(rep.title,
                                        rep.axial_strains,
                                        rep.stresses,
                                        retract_index=rep.tipping_point,
                                        x2=rep.lateral_strains,
                                        text=text,
                                        line=rep.comp_modulus[:2],
                                        save_dir=rep_save_dir)
            if sum_var == 'sh':
                for l in summary:
                    print(l)

            elif sum_var == 'sa':
                summary_save_dir = user_comms.ask_save_dir('Choose Save Directory for Summary...')
                summary_name = input('Enter summary file name (ending.csv)')
                data.write_to_csv(summary_name, summary_save_dir, summary)

        elif plt_var == 'n':

            for f in os.listdir(data_path):
                series_data_path = os.path.join(data_path, f).replace('\\', '/')
                a = TestSeries(series_data_path, 5, specimen_sizes)  # Create instance of TestSeries

                slices = a.slice_series()
                for rep in slices:
                    summary.append(rep.get_rep_summary())

            if sum_var == 'sh':
                for l in summary:
                    print(l)

            elif sum_var == 'sa':
                summary_save_dir = user_comms.ask_save_dir('Choose Save Directory for Summary...')
                summary_name = input('Enter summary file name (ending.csv)')
                data.write_to_csv(summary_name, summary_save_dir, summary)

    elif var == 9:
        path = user_comms.ask_src_path(0)  # Ask user for file path
        a = TestSeries(path, 5, specimen_sizes)  # Create instance of TestSeries
        slices = a.slice_series()  # Slice series to individual repetitions
        summary = [['Specimen ID', 'Date of Testing', 'Repetition', 'Zero Offset [mm]',
                    'Compressive Modulus [MPa]', 'RSQ',
                    'Poisson Direction', 'Poisson\'s Ratio', 'RSQ']]

        if plt_var == 'sh':
            for rep in slices:
                summary.append(rep.get_rep_summary())
                text = 'Compressive Modulus: %.1f MPa \n Poisson\'s Ratio: %.3f' \
                       % (rep.comp_modulus[0], rep.poisson[0])

                plotting.create_fig(rep.title,
                                    rep.axial_strains,
                                    rep.stresses,
                                    retract_index=rep.tipping_point,
                                    x2=rep.lateral_strains,
                                    text=text,
                                    line=rep.comp_modulus[:2])

            if sum_var == 'sh':
                for l in summary:
                    print(l)

            elif sum_var == 'sa':
                summary_save_dir = user_comms.ask_save_dir('Choose Save Directory for Summary...')
                summary_name = input('Enter summary file name (ending.csv)')
                data.write_to_csv(summary_name, summary_save_dir, summary)

        elif plt_var == 'sa':
            plt_save_dir = user_comms.ask_save_dir('Choose Save Directory for Plots...')

            for rep in slices:
                summary.append(rep.get_rep_summary())
                text = 'Compressive Modulus: %.1f MPa \n Poisson\'s Ratio: %.3f' \
                       % (rep.comp_modulus[0], rep.poisson[0])
                plotting.create_fig(rep.title,
                                    rep.axial_strains,
                                    rep.stresses,
                                    retract_index=rep.tipping_point,
                                    x2=rep.lateral_strains,
                                    text=text,
                                    save_dir=plt_save_dir,
                                    line=rep.comp_modulus[:2])

            if sum_var == 'sh':
                for l in summary:
                    print(l)

            elif sum_var == 'sa':
                summary_save_dir = user_comms.ask_save_dir('Choose Save Directory for Summary...')
                summary_name = input('Enter summary file name (ending.csv)')
                data.write_to_csv(summary_name, summary_save_dir, summary)

        elif plt_var == 'n':

            for rep in slices:
                summary.append(rep.get_rep_summary())

            if sum_var == 'sh':
                for l in summary:
                    print(l)

            elif sum_var == 'sa':
                summary_save_dir = user_comms.ask_save_dir('Choose Save Directory for Summary...')
                summary_name = input('Enter summary file name (ending.csv)')
                data.write_to_csv(summary_name, summary_save_dir, summary)
    else:
        pass

    """summary = [['Specimen ID', 'Date of Testing', 'Yield Stress 0.02% [MPa]', 'Compressive Modulus [GPa]', 'RSQ']]
    for f in os.listdir(path):
        a = DestructiveTest(os.path.join(path, f).replace('\\', '/'), 10, specimen_sizes)
        summary.append(a.get_rep_summary())

        # strain_percent = [a.strains[0]]
        # for strain in a.strains[1:]:
        #     strain_percent.append(strain * 100)  # In percents
        if a.slope == 1:
            plotting.create_fig(a.filename,
                                a.strains,
                                a.stresses,
                                save_dir=save_dir)
        else:
            plotting.create_fig(a.filename,
                                a.strains,
                                a.stresses,
                                line=[a.slope, a.intercept],
                                save_dir=save_dir)
    data.write_to_csv('20211118_destructive.csv', save_dir, summary)"""

    """a = DestructiveTest(path, 10, specimen_sizes)
    print(a.get_rep_summary())
    plotting.create_fig(a.filename,
                        a.strains,
                        a.stresses,
                        line=[a.slope, a.intercept])"""




