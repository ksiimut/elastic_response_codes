import matplotlib.pyplot as plt
import data
import user_comms
import os
import numpy as np


def make_graph(data_to_plot, save_dir):  # Data of one test

    filename = data_to_plot[0]

    force_data = data_to_plot[1][1:]
    force_label = data_to_plot[1][0]

    disp_axial_data = data_to_plot[2][1:]
    disp_ax_label = data_to_plot[2][0]

    fig, ax1 = plt.subplots(figsize=(16, 9))

    color = 'tab:red'
    ax1.set_xlabel(force_label)
    ax1.set_ylabel(disp_ax_label, color=color)
    ax1.plot(force_data, disp_axial_data, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_title(filename)

    xmax = max(force_data)  # Change values to customize
    xmin = min(force_data)
    xstep = 1

    plt.xlim([xmin, xmax])
    ax1.set_xticks(np.arange(xmin, xmax + 0.001, xstep))

    y1max = max(disp_axial_data)
    y1min = min(disp_axial_data)
    y1step = 0.1

    ax1.set_ylim([y1min, y1max])
    ax1.set_yticks(np.arange(y1min, y1max + 0.001, y1step))

    if len(data_to_plot) == 4:
        disp_lateral_data = data_to_plot[3][1:]
        disp_lat_label = data_to_plot[3][0]

        ax2 = ax1.twinx()  # Axis for lateral displacement

        color = 'tab:blue'
        ax2.set_ylabel(disp_lat_label, color=color)
        ax2.plot(force_data, disp_lateral_data, color=color)
        ax2.tick_params(axis='y', labelcolor=color)

        y2max = max(disp_lateral_data)
        y2min = min(disp_lateral_data)
        y2step = 0.01

        ax2.set_ylim([y2min, y2max])
        ax2.set_yticks(np.arange(y2min, y2max + 0.001, y2step))

    fig.tight_layout()  # otherwise the right y-label is slightly clipped

    save_path = os.path.join(save_dir, filename)
    # print(save_path)

    # plt.savefig(save_path)
    plt.show()


force = ['Force [kN]', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
disp_axial = ['Axial Displacement [mm]', 0.1, 0.2, 0.3, 0.4, 0.5, 0.56, 0.61, 0.65, 0.68, 0.7]
disp_lateral = ['Lateral Displacement [mm]', 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
test_list = ['test.csv', force, disp_axial, disp_lateral]
test_list_2 = ['test.csv', force, disp_axial]
save_loc = user_comms.ask_save_dir()
make_graph(test_list, save_loc)
# print(data.transpose_list(test_list, user_comms.ask_save_dir()))

