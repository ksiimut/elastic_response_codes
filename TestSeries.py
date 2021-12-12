import data
import scipy
from scipy import stats


class TestSeries:

    def __init__(self, filepath, res_decrease, specimen_info):

        print('Class TestSeries initiated.')
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

        self.infill_spec = True
        if len(self.filename.split('_')) == 4:
            self.infill_spec = False

        sizes = self.find_specimen_size(specimen_info)
        self.area = sizes[0]
        self.l0_axial = sizes[1]
        self.l0_lateral = sizes[2]

        self.find_auto_offset()
        self.decrease_resolution(res_decrease)
        self.offset_series_zero()

    def read_dat(self):

        dat_name = self.path.split('/')[-1]
        pieces = dat_name.split('_')
        # print(pieces)
        date_of_testing = pieces[0]
        specimen_id = pieces[1] + '_' + pieces[2]  # X40Z / X40Y (loadingdir + dimension + lateral disp axis)
        series_rep = pieces[3].split('.')[0]

        filename = '%s_%s_%s' % (date_of_testing, specimen_id, series_rep)
        # print(filename)
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

        print('%s: Number of data points: ' % specimen_id)
        print('\tForce: ' + str(len(force) - 1))  # -1 for the header row
        print('\tAxial Displacement: ' + str(len(disp_ax) - 1))
        print('\tLateral Displacement (L): ' + str(len(disp_lat_l) - 1))
        print('\tLateral Displacement (R): ' + str(len(disp_lat_r) - 1))

        if len(force) != len(disp_ax) or len(force) != len(disp_lat_l) or \
                len(force) != len(disp_lat_r) or len(disp_ax) != len(disp_lat_l) or \
                len(disp_ax) != len(disp_lat_r) or len(disp_lat_l) != len(disp_lat_r):
            print('%s: Faulty DAT file import! '
                  'The number of data points does not match between different types of data.' % filename)
            print('\tNumber of data points: ')
            print('\tForce: ' + str(len(force) - 1))  # -1 for the header row
            print('\tAxial Displacement: ' + str(len(disp_ax) - 1))
            print('\tLateral Displacement (L): ' + str(len(disp_lat_l) - 1))
            print('\tLateral Displacement (R): ' + str(len(disp_lat_r) - 1))

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

        result = [None, 45, 1]  # [area, l0_axial, l0_lateral]
        print(specimen_data)
        for specimen in specimen_data[1:]:  # finds initial area and dimensions of specimen
            if self.infill_spec:
                if self.specimen_id[:3] == specimen[0]:
                    result[0] = specimen[4]
                    loading_direction = self.specimen_id[0]
                    lateral_disp_measuring_direction = self.specimen_id[3]
                    print('\tLoading direction: %s' % loading_direction)
                    print('\tLateral direction: %s' % lateral_disp_measuring_direction)

                    if loading_direction == 'X':
                        result[1] = specimen[1]
                    elif loading_direction == 'Y':
                        result[1] = specimen[2]

                    if lateral_disp_measuring_direction == 'X':
                        result[2] = specimen[1]
                    elif lateral_disp_measuring_direction == 'Y':
                        result[2] = specimen[2]
                    elif lateral_disp_measuring_direction == 'Z':
                        result[2] = specimen[3]

            else:
                if self.specimen_id[:5] == specimen[0]:
                    result[0] = specimen[4]
                    loading_direction = self.specimen_id[0]
                    lateral_disp_measuring_direction = self.specimen_id[5]
                    print('\tLoading direction: %s' % loading_direction)
                    print('\tLateral direction: %s' % lateral_disp_measuring_direction)

                    if loading_direction == 'X':
                        result[1] = specimen[1]
                    elif loading_direction == 'Y':
                        result[1] = specimen[2]

                    if lateral_disp_measuring_direction == 'X':
                        result[2] = specimen[1]
                    elif lateral_disp_measuring_direction == 'Y':
                        result[2] = specimen[2]
                    elif lateral_disp_measuring_direction == 'Z':
                        result[2] = specimen[3]

        if result[0] is None:
            print('\tNo area calculated for specimen.')
        return result

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
            print('\tResolution decreased by %i times.' % decrease_x_times)
            pass
        else:
            print('\tError! Datasets with lowered resolution do not have the same length!')
            print(lengths)

    def slice_series(self):

        F_THRES_START = 5  # N - Force threshold to slice a series.
        F_THRES_FINISH = 2  # N - Force threshold to slice a series.

        test_start_indices = []
        test_end_indices = []

        part_of_test = False
        count = 0  # How many points in a row are over the threshold.
        COUNT_THRES = 3  # How many points need to be over the threshold.
        OFFSET = 20  # Number of data points outside the test to include (on both sides).

        for i in range(1, len(self.force[1:])):
            # print('Count: ' + str(count) + '. Force: ' + str(i))
            if not part_of_test and self.force[i] > F_THRES_START:
                count += 1
                if count >= COUNT_THRES:
                    index = i - COUNT_THRES - OFFSET
                    if index < 1:
                        index = 1
                    test_start_indices.append(index)
                    count = 0
                    part_of_test = True
                    # print('Start force [N]: ' + str(i))

            elif part_of_test and self.force[i] < F_THRES_FINISH:
                count += 1
                if count >= COUNT_THRES:
                    index = i + COUNT_THRES + OFFSET
                    print('End index: %i' % index)
                    print(self.force[i-20:i+20])
                    if index > len(self.force) - 1:
                        index = len(self.force) - 1
                    test_end_indices.append(index)
                    count = 0
                    part_of_test = False
                    # print('End force [N]: ' + str(i))

            elif (part_of_test and i > F_THRES_FINISH) or (not part_of_test and i < F_THRES_START):
                count = 0

        # print(test_start_indices)
        # print(test_end_indices)

        if len(test_start_indices) != len(test_end_indices):
            print('\tError with series slicing!')
            print('\tStarts of test found: %i' % len(test_start_indices))
            print('\tEnds of test found: %i' % len(test_end_indices))
            return None

        else:
            reps = len(test_start_indices)  # Number of repetitions made during one test.
            print('\tSlicing of %s successful: %i repetitions found in series.' % (self.specimen_id, reps))
            tests = []  # Repetition class instances

            for i in range(reps):
                i_start = test_start_indices[i]
                i_finish = test_end_indices[i]
                # print('Istart: %i; Ifinish: %i' % (i_start, i_finish))

                slicename = '%s_Rep_%i' % (self.filename, i + 1)
                force_slice = self.force[i_start:i_finish]
                disp_ax_slice = self.disp_ax[i_start:i_finish]
                disp_lat_total_slice = self.disp_lat_total[i_start:i_finish]
                disp_lat_l_slice = self.disp_lat_l[i_start:i_finish]
                disp_lat_r_slice = self.disp_lat_r[i_start:i_finish]

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

    def find_auto_offset(self):

        VALUE_THRES = 0.001
        COUNT_THRES = 10
        count = 0

        for i in range(1, len(self.disp_ax)):
            this_disp_ax = abs(self.disp_ax[i])
            this_disp_lat_l = abs(self.disp_lat_l[i])
            this_disp_lat_r = abs(self.disp_lat_r[i])

            if this_disp_ax < VALUE_THRES and this_disp_lat_l < VALUE_THRES and this_disp_lat_r < VALUE_THRES:
                count += 1
                if count >= COUNT_THRES:
                    index = i - COUNT_THRES
                    if index < 1:
                        index = 1
                        print('Index override at series auto offset.')
                    new_force = self.force[index:]
                    new_disp_ax = self.disp_ax[index:]
                    new_disp_total = self.disp_lat_total[index:]
                    new_disp_lat_l = self.disp_lat_l[index:]
                    new_disp_lat_r = self.disp_lat_r[index:]

                    self.force = new_force
                    self.disp_ax = new_disp_ax
                    self.disp_lat_total = new_disp_total
                    self.disp_lat_l = new_disp_lat_l
                    self.disp_lat_r = new_disp_lat_r

                    print('\tSeries auto offset found at index %i.' % (index))
                    break

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
        print('\tDisplacement of the series was offset by: %f mm.' % disp_offset)
        disp_ax_offset = [self.disp_ax[0]]
        for measurand in self.disp_ax[1:]:
            disp_ax_offset.append(round(measurand - disp_offset, 5))

        self.disp_ax = disp_ax_offset


class Repetition(TestSeries):

    def __init__(self, title, force, disp_ax, disp_lat_total, disp_lat_l, disp_lat_r, area, l0_axial, l0_lateral):

        self.title = title  # YYYYMMDD_X10Z_1_Rep_1 or YYYYMMDD_X00_1Y_1_Rep_1
        pcs = self.title.split('_')

        if len(pcs) == 5:  # Is infill specimen
            self.specimen_id = pcs[1][:3]
            self.test_date = pcs[0]
            self.ax_dir = self.specimen_id[0]
            self.lat_dir = pcs[1][3]
            self.repetition = int(pcs[-1])
            self.batch = int(pcs[-3])

        elif len(pcs) == 6:
            self.specimen_id = pcs[1] + '_' + pcs[2][0]
            self.test_date = pcs[0]
            self.ax_dir = self.specimen_id[0]
            self.lat_dir = pcs[2][1]
            self.repetition = int(pcs[-1])
            self.batch = int(pcs[-3])

        self.force = force
        self.disp_ax = disp_ax
        self.disp_lat_total = disp_lat_total
        self.disp_lat_l = disp_lat_l
        self.disp_lat_r = disp_lat_r
        self.area = area
        self.l0_axial = l0_axial
        self.l0_lateral = l0_lateral

        self.rep_offset = self.offset_rep_zero()

        self.tipping_point = self.find_retract()
        self.axial_strains = self.calculate_axial_strain()
        self.lateral_strains = self.calculate_lateral_strain()
        self.stresses = self.calculate_stress()

        MIN_STRAIN = 0.005
        MAX_STRAIN = 0.01

        self.comp_modulus = self.calculate_modulus(MIN_STRAIN, MAX_STRAIN)  # [modulus, intercept, rsq]
        self.poisson = self.calculate_poisson(MIN_STRAIN, MAX_STRAIN)  # [poisson, rsq]

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
        print('\t\tDisplacement of repetition %i was offset by: %f mm.' % (self.repetition, disp_offset))
        disp_ax_offset = [self.disp_ax[0]]
        for measurand in self.disp_ax[1:]:
            disp_ax_offset.append(round(measurand - disp_offset, 5))

        self.disp_ax = disp_ax_offset
        return disp_offset

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

    def calculate_modulus(self, min_strain, max_strain):

        i_min = 1  # not 0 to exclude the data header.
        i_max = len(self.axial_strains) - 1
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
            modulus = round(result.slope, 3)  # MPa
            intercept = round(result.intercept, 3)
            rsq = round(result.rvalue**2, 5)
            # print('Young\'s modulus: ' + str(modulus) + ' GPa')
            # print('R^2: ' + str(rsq))

            return [modulus, intercept, rsq]

        else:
            print('\t\tError in Compression Modulus calculation.')
            print('\t\tNumber of stress data points: %i' % len(self.stresses))
            print('\t\tNumber of strain data points: %i' % len(self.axial_strains))
            return None

    def calculate_poisson(self, min_strain, max_strain):  # Pars: AXIAL strain values!!

        i_min = 1
        i_max = len(self.axial_strains) - 1

        if len(self.axial_strains) == len(self.lateral_strains):
            for i in range(1, len(self.axial_strains)):
                if self.axial_strains[i] > min_strain:
                    i_min = i - 1
                    if i < 1:
                        i_min = 1
                    break
            for i in range(i_min, len(self.axial_strains)):
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
            print('\t\tError in Poisson\'s Ratio calculation.')
            print('\t\tNumber of axial strain data points: %i' % len(self.axial_strains))
            print('\t\tNumber of lateral strain data points: %i' % len(self.lateral_strains))
            return None

    def get_strain_percent(self, axial=True):  # axial - boolean: True - axial strain; False - Lateral Strain

        strain_percent = []

        if axial:
            strain_percent.append('Axial Strain [%]')
            for i in self.axial_strains[1:]:
                strain_percent.append(i * 100)

        else:
            strain_percent.append('Lateral Strain [%]')
            for i in self.lateral_strains[1:]:
                strain_percent.append(i * 100)

        return strain_percent

    def get_rep_summary(self):
        # headers = ['Specimen ID', 'Loading Direction', 'Area [mm2]', 'Date of Testing', 'Batch', 'Repetition',
        #            'Zero offset [mm]', 'Compressive Modulus [MPa]', 'RSQ',
        #            'Poisson Direction', 'Poisson\'s Ratio', 'RSQ']
        summary = [self.specimen_id, self.ax_dir, self.area, self.test_date, self.batch, self.repetition,
                   self.rep_offset, self.comp_modulus[0], self.comp_modulus[2],
                   self.lat_dir, self.poisson[0], self.poisson[1]]
        return summary

    def get_inputs(self):
        ary = [self.specimen_id, self.test_date, self.repetition, self.lat_dir, self.area, self.tipping_point]
        print(ary)
