import data
import scipy
from scipy import stats


class DestructiveTest:

    def __init__(self, path, res_decrease, spec_info):

        self.path = path
        dat = self.read_dat()

        self.specimen_id = dat[0]
        self.test_date = dat[1]
        self.filename = dat[2]
        self.force = dat[3]
        self.disp_ax = dat[4]

        self.decrease_resolution(res_decrease)
        self.offset_zero()
        self.find_test()

        size = self.find_specimen_size(spec_info)
        self.area = size[0]
        self.l0 = size[1]

        MIN_STRAIN = 0.007
        MAX_STRAIN = 0.012
        self.strain_offset = 0.0002

        self.tipping_point = self.find_retract()
        self.strains = self.calculate_strain()
        self.stresses = self.calculate_stress()
        self.comp_modulus = self.calculate_modulus(MIN_STRAIN, MAX_STRAIN)  # [modulus, rsq]

        sigma_y_data = self.calculate_sigma_y(MIN_STRAIN, MAX_STRAIN, self.strain_offset)
        self.sigma_y = sigma_y_data[0]
        self.slope = sigma_y_data[1]
        self.intercept = sigma_y_data[2]

    def read_dat(self):

        dat_name = self.path.split('/')[-1]
        pieces = dat_name.split('_')
        date_of_testing = pieces[0]
        specimen_id = pieces[1].split('.')[0]  # X40Z / X40Y (loadingdir + dimension + lateral disp axis)

        filename = specimen_id + '_' + date_of_testing
        force = ['Compressive Load [N]']  # Compressive load, measured with load cell.
        disp_ax = ['Axial Displacement [mm]']  # Axial displacement, measured with built-in LVDT.

        empty_line_counter = 0
        f = open(self.path, 'rt')
        while True:
            if empty_line_counter < 3:
                try:
                    line = f.readline().strip('\n').split('\t')
                    if len(line) < 2:
                        empty_line_counter += 1
                        continue
                    else:
                        empty_line_counter = 0
                        force.append(-round(float(line[0].replace(',', '.')), 5))
                        disp_ax.append(-round(float(line[1].replace(',', '.')), 5))
                except:
                    pass
            else:
                break
        f.close()

        print(str(specimen_id) + ': Number of data points: ')
        print(str(specimen_id) + ': Force: ' + str(len(force) - 1))  # -1 for the header row
        print(str(specimen_id) + ': Axial Displacement: ' + str(len(disp_ax) - 1))

        if len(force) != len(disp_ax):
            print(str(specimen_id) + ': Faulty DAT file import! The number of data points does not match between different types of data.')
            print(str(specimen_id) + ': Number of data points: ')
            print(str(specimen_id) + ': Force: ' + str(len(force) - 1))  # -1 for the header row
            print(str(specimen_id) + ': Axial Displacement: ' + str(len(disp_ax) - 1))
            return None

        else:
            read_data = [specimen_id,
                         date_of_testing,
                         filename,
                         force,
                         disp_ax]
        return read_data

    def decrease_resolution(self, decrease_x_times):

        self.force = data.average_data(self.force, decrease_x_times)
        self.disp_ax = data.average_data(self.disp_ax, decrease_x_times)

        if len(self.force) == len(self.disp_ax):
            print(str(self.specimen_id) + ': Resolution decreased by ' + str(decrease_x_times) + ' times.')
            pass
        else:
            print(str(self.specimen_id) + ': Error! Datasets with lowered resolution do not have the same length!')

    def find_specimen_size(self, specimen_data):

        result = [None, 45]  # [area, l0_axial]

        for specimen in specimen_data[1:]:  # finds initial area and dimensions of specimen
            if self.specimen_id[:3] == specimen[0]:
                result[0] = specimen[4]
                loading_dir = self.specimen_id[0]
                print(str(self.specimen_id) + ': Loading direction: ' + loading_dir)

                if loading_dir == 'X':
                    result[1] = specimen[1]
                elif loading_dir == 'Y':
                    result[1] = specimen[2]
                else:
                    print(str(self.specimen_id) + ': Loading direction not found!')
                    result[1] = None

        return result

    def offset_zero(self):

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
        print(str(self.specimen_id) + ': Displacement of the series was offset by ' + str(disp_offset) + ' mm.')
        disp_ax_offset = [self.disp_ax[0]]
        for measurand in self.disp_ax[1:]:
            disp_ax_offset.append(round(measurand - disp_offset, 5))

        self.disp_ax = disp_ax_offset

    def find_test(self):

        F_THRES = 1  # N - Force threshold to slice a series.

        test_start_index = 0
        test_end_index = len(self.force) - 1

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
                    test_start_index = self.force.index(i) - COUNT_THRES - OFFSET
                    count = 0
                    if test_start_index < 1:
                        test_start_index = 1
                    # print('Start force [N]: ' + str(i))
            elif not part_of_test and i < F_THRES:
                count = 0

            elif part_of_test and i < F_THRES:
                count += 1
                if count >= COUNT_THRES:
                    part_of_test = False
                    test_end_index = self.force.index(i) + COUNT_THRES + OFFSET
                    count = 0
                    if test_end_index >= len(self.force):
                        test_end_index = len(self.force) - 1
                    print('End force [N]: ' + str(i))
            elif part_of_test and i > F_THRES:
                count = 0

        test_force = self.force[test_start_index:test_end_index]
        test_disp_ax = self.disp_ax[test_start_index:test_end_index]
        test_force.insert(0, self.force[0])
        test_disp_ax.insert(0, self.disp_ax[0])

        self.force = test_force
        self.disp_ax = test_disp_ax

    def find_retract(self):  # Returns index, where unloading starts.

        cont_drop = 0  # How many points in a row have been dropping.
        DROP_THRES = 3  # How many points in a row have to drop.
        LOAD_THRES = -1  # Change in force [N] that will be counted as a drop.
        for i in range(1, len(self.force[1:-1])):
            force_change = self.force[i + 1] - self.force[i]
            if force_change < LOAD_THRES:
                cont_drop += 1
                if cont_drop >= DROP_THRES:
                    return i - DROP_THRES

    def calculate_strain(self):

        strains = ['Compressive Strain [mm/mm]']
        for i in self.disp_ax[1:]:
            strains.append(round(i / self.l0, 8))
        return strains

    def calculate_stress(self):

        stresses = ['Compressive Stress [MPa]']
        for i in self.force[1:]:
            stresses.append(round(i / self.area, 5))
        return stresses

    def calculate_modulus(self, min_strain, max_strain):

        i_min = 1  # not 0 to exclude the data header.
        i_max = 1
        if len(self.stresses) == len(self.strains):
            for i in range(1, len(self.strains)):
                if self.strains[i] > min_strain:
                    i_min = i - 1
                    if i < 1:
                        i_min = 1
                    break
            for i in range(i_min, len(self.strains)):
                if self.strains[i] > max_strain:
                    i_max = i
                    break
            result = scipy.stats.linregress(self.strains[i_min:i_max], self.stresses[i_min:i_max])
            modulus = round(result.slope / 1000, 3)  # GPa
            rsq = round(result.rvalue**2, 5)
            # print(str(self.specimen_id) + ': Compression modulus: ' + str(modulus) + ' GPa')
            # print('R^2: ' + str(rsq))

            return [modulus, rsq]

        else:
            print(str(self.specimen_id) + ': Error in Compression Modulus calculation.')
            print(str(self.specimen_id) + ': Number of stress data points: ' + str(len(self.stresses)))
            print(str(self.specimen_id) + ': Number of strain data points: ' + str(len(self.strains)))
            return None

    def calculate_sigma_y(self, min_strain, max_strain, strain_offset):

        i_min = 1  # not 0 to exclude the data header.
        i_max = 1
        res = [0, 1, 0]
        if len(self.stresses) == len(self.strains):
            for i in range(1, len(self.strains)):
                if self.strains[i] > min_strain:
                    i_min = i - 1
                    if i < 1:
                        i_min = 1
                    break
            for i in range(1, len(self.strains)):
                if self.strains[i] > max_strain:
                    i_max = i
                    break
            result = scipy.stats.linregress(self.strains[i_min:i_max], self.stresses[i_min:i_max])
            slope = result.slope  # MPa
            y_intercept = result.intercept  # MPa
            # print('Compression Modulus: ' + str(round(slope, 5)) + ' MPa; Intercept: ' + str(round(y_intercept, 5)) + ' MPa')

            x_old = max_strain
            y_old = slope * x_old + y_intercept
            x_new = x_old + strain_offset

            y_intercept_new = calc_intercepts([x_new, y_old], slope)[1]
            # print('y_ic_new: ' + str(y_intercept_new))
            # new line: y = slope * x + y_intercept_new

            for i in range(i_max, len(self.strains) - 1):
                strain_0 = self.strains[i]
                strain_1 = self.strains[i + 1]
                stress_0 = self.stresses[i]
                stress_1 = self.stresses[i + 1]
                # print('Stress range: ' + str(stress_0) + ' - ' + str(stress_1))
                pred_stress = slope * strain_0 + y_intercept_new
                # print('Predicted Stress: ' + str(pred_stress))
                if stress_0 < pred_stress <= stress_1:
                    k_data = (stress_1 - stress_0) / (strain_1 - strain_0)
                    y_ic_data = calc_intercepts([strain_0, stress_0], k_data)[1]

                    yield_strain = (y_ic_data - y_intercept_new) / (slope - k_data)
                    yield_stress = round(slope * yield_strain + y_intercept_new, 3)
                    res = [yield_stress, slope, y_intercept_new]
                    break
        return res

    def get_rep_summary(self):
        # headers = ['Specimen ID', 'Date of Testing', 'Yield Stress 0.2% [MPa]',
        #            'Compressive Modulus [GPa]', 'RSQ']
        summary = [self.specimen_id, self.test_date, self.sigma_y,
                    self.comp_modulus[0], self.comp_modulus[1]]
        # summary = [[self.specimen_id, self.test_date,
        #              self.comp_modulus[0], self.comp_modulus[1]]]
        # summary.insert(0, headers)
        return summary


def calc_intercepts(point, slope):

    x0 = point[0]
    y0 = point[1]

    y_ic_res = y0 - slope * x0
    x_ic_res = -y_ic_res / slope

    return[x_ic_res, y_ic_res]


