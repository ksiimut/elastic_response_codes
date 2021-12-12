import os
import user_comms
import data
import plotting
from DestructiveTest import DestructiveTest
from TestSeries import TestSeries


def make_dirs(parent, namelist):

    for d in namelist:
        try:
            dir_path = os.path.join(parent, d)
            os.mkdir(dir_path)
        except OSError as error:
            print(error)


def calculate_deltas(summary_list):

    headers_check = ['Repetition', 'Zero Offset [mm]', 'Compressive Modulus [MPa]', 'Poisson\'s Ratio']
    summary_list[0].append('delta_Offset [mm]')
    summary_list[0].append('delta_Modulus [MPa]')
    summary_list[0].append('delta_Poisson')

    i_list = []

    for header in summary_list[0]:
        for word in headers_check:
            if header == word:
                i_list.append(summary_list[0].index(header))

    i_rep = i_list[0]  # Index of repetition column

    for i in range(1, len(summary_list)):
        if summary_list[i][i_rep] == 1:  # If repetition = 1.
            summary_list[i].append(0)  # delta offset
            summary_list[i].append(0)  # delta modulus
            summary_list[i].append(0)  # delta poisson
        else:
            d_offset = summary_list[i][i_list[1]] - summary_list[i - 1][i_list[1]]
            d_modulus = summary_list[i][i_list[2]] - summary_list[i - 1][i_list[2]]
            d_poisson = summary_list[i][i_list[3]] - summary_list[i - 1][i_list[3]]

            summary_list[i].append(round(d_offset, 5))
            summary_list[i].append(round(d_modulus, 5))
            summary_list[i].append(round(d_poisson, 5))


if __name__ == '__main__':
    specimen_info_excel_path_LT = 'C:\\Users\\kaare\\Danmarks Tekniske Universitet\\s202962 - General\\3-E21\\' \
                                  'Spec_Elastic_Response_of_3D_Printed_Forming_Tools\\Experiments\\Specimen Measuring\\' \
                                  'Specimen Dimensions Summary.xlsx'
    specimen_info_excel_path_PC = 'C:\\Users\\Mazin\\Danmarks Tekniske Universitet\\s202962 - General\\3-E21\\' \
                                  'Spec_Elastic_Response_of_3D_Printed_Forming_Tools\\Experiments\\Specimen Measuring\\' \
                                  'Specimen Dimensions Summary.xlsx'
    specimen_sizes = data.specimen_info(specimen_info_excel_path_PC)

    var = int(input('Test batch (0) or single file (9): '))
    plt_var = input('Show plots (sh), save plots (sa), no plots (n)?')
    sum_var = input('Show summary (sh), save summary (sa), no summary (n)?')
    summary = [['Specimen ID', 'Loading Direction', 'Area [mm^2]', 'Shell/Infill Ratio', 'Date of Testing',
                'Batch', 'Repetition', 'Zero Offset [mm]',
                'Compressive Modulus [MPa]', 'RSQ',
                'Poisson Direction', 'Poisson\'s Ratio', 'RSQ']]
    if var == 0:
        data_path = user_comms.ask_src_path(1)  # Ask user for folder path

        if plt_var == 'sh':

            for f in os.listdir(data_path):
                series_data_path = os.path.join(data_path, f).replace('\\', '/')
                a = TestSeries(series_data_path, 5, specimen_sizes)  # Create instance of TestSeries

                slices = a.slice_series()
                for rep in slices:
                    summary.append(rep.get_rep_summary())
                    text = '$E_C = %.1f MPa$ \n $\\nu = %.3f$' \
                           % (rep.comp_modulus[0], rep.poisson[0])
                    plotting.create_fig(rep.title,
                                        rep.get_strain_percent(axial=True),
                                        rep.stresses,
                                        retract_index=rep.tipping_point,
                                        x2=rep.get_strain_percent(axial=False),
                                        text=text,
                                        line=[rep.comp_modulus[0]/100, rep.comp_modulus[1]])
            if sum_var == 'sh':
                calculate_deltas(summary)
                for line in summary:
                    print(line)

            elif sum_var == 'sa':
                calculate_deltas(summary)
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
                    text = '$E_C = %.1f MPa$ \n $\\nu = %.3f$' \
                           % (rep.comp_modulus[0], rep.poisson[0])
                    plotting.create_fig(rep.title,
                                        rep.get_strain_percent(axial=True),
                                        rep.stresses,
                                        retract_index=rep.tipping_point,
                                        x2=rep.get_strain_percent(axial=False),
                                        text=text,
                                        line=[rep.comp_modulus[0]/100, rep.comp_modulus[1]],
                                        save_dir=rep_save_dir)
            if sum_var == 'sh':
                calculate_deltas(summary)
                for line in summary:
                    print(line)

            elif sum_var == 'sa':
                calculate_deltas(summary)
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
                calculate_deltas(summary)
                for line in summary:
                    print(line)

            elif sum_var == 'sa':
                calculate_deltas(summary)
                summary_save_dir = user_comms.ask_save_dir('Choose Save Directory for Summary...')
                summary_name = input('Enter summary file name (ending.csv)')
                data.write_to_csv(summary_name, summary_save_dir, summary)

    elif var == 9:
        path = user_comms.ask_src_path(0)  # Ask user for file path
        a = TestSeries(path, 5, specimen_sizes)  # Create instance of TestSeries
        slices = a.slice_series()  # Slice series to individual repetitions

        if plt_var == 'sh':
            for rep in slices:
                summary.append(rep.get_rep_summary())
                text = '$E_C = %.1f~MPa$ \n $\\nu_{%s} = %.3f$' \
                       % (rep.comp_modulus[0], rep.lat_dir, rep.poisson[0])
                plotting.create_fig(rep.title,
                                    rep.get_strain_percent(axial=True),
                                    rep.stresses,
                                    retract_index=rep.tipping_point,
                                    x2=rep.get_strain_percent(axial=False),
                                    text=text,
                                    line=[rep.comp_modulus[0]/100, rep.comp_modulus[1]])

            if sum_var == 'sh':
                calculate_deltas(summary)
                for line in summary:
                    print(line)

            elif sum_var == 'sa':
                calculate_deltas(summary)
                summary_save_dir = user_comms.ask_save_dir('Choose Save Directory for Summary...')
                summary_name = input('Enter summary file name (ending.csv)')
                data.write_to_csv(summary_name, summary_save_dir, summary)

        elif plt_var == 'sa':
            plt_save_dir = user_comms.ask_save_dir('Choose Save Directory for Plots...')

            for rep in slices:
                summary.append(rep.get_rep_summary())
                text = '$E_C = %.1f MPa$ \n $\\nu = %.3f$' \
                       % (rep.comp_modulus[0], rep.poisson[0])
                plotting.create_fig(rep.title,
                                    rep.get_strain_percent(axial=True),
                                    rep.stresses,
                                    retract_index=rep.tipping_point,
                                    x2=rep.get_strain_percent(axial=False),
                                    text=text,
                                    save_dir=plt_save_dir,
                                    line=[rep.comp_modulus[0]/100, rep.comp_modulus[1]])

            if sum_var == 'sh':
                calculate_deltas(summary)
                for line in summary:
                    print(line)

            elif sum_var == 'sa':
                calculate_deltas(summary)
                summary_save_dir = user_comms.ask_save_dir('Choose Save Directory for Summary...')
                summary_name = input('Enter summary file name (ending.csv)')
                data.write_to_csv(summary_name, summary_save_dir, summary)

        elif plt_var == 'n':

            for rep in slices:
                summary.append(rep.get_rep_summary())

            if sum_var == 'sh':
                calculate_deltas(summary)
                for line in summary:
                    print(line)

            elif sum_var == 'sa':
                calculate_deltas(summary)
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
