import matplotlib.pyplot as plt
import data
import user_comms
import os
import numpy as np


def make_graph(data_to_plot, save_dir):     # Data of one test
    # [filename, [x_data_points], [y1_data_points], [y2_data_points(optional)]]

    filename = data_to_plot[0]

    y_data = data_to_plot[1][1:]  # Force
    y_label = data_to_plot[1][0]

    x1_data = data_to_plot[2][1:]  # Axial displacement
    x1_label = data_to_plot[2][0]

    fig, ax1 = plt.subplots(figsize=(16, 9))

    color = 'tab:red'
    ax1.set_xlabel(x1_label, color=color)
    ax1.set_ylabel(y_label)
    ax1.plot(x1_data, y_data, color=color)
    ax1.tick_params(axis='x', labelcolor=color)
    ax1.set_title(filename)

    ymax = 10000  # max(y_data)  # Change values to customize
    ymin = -100  # min(y_data)
    ystep = 500

    plt.ylim([ymin, ymax])
    ax1.set_xticks(np.arange(ymin, ymax + 0.001, ystep))

    x1max = max(x1_data)
    x1min = min(x1_data)
    x1step = 0.1

    ax1.set_xlim([x1min, x1max])
    ax1.set_xticks(np.arange(x1min, x1max + 0.001, x1step))

    if len(data_to_plot) == 6:
        x2_data = data_to_plot[3][1:]  # Lateral displacement
        x2_label = data_to_plot[3][0]

        ax2 = ax1.twiny()  # Axis for lateral displacement

        color = 'tab:blue'
        ax2.set_xlabel(x2_label, color=color)
        ax2.plot(x2_data, y_data, color=color)
        ax2.tick_params(axis='x', labelcolor=color)

        x2max = max(x2_data)
        x2min = min(x2_data)
        x2step = 0.01

        ax2.set_xlim([x2min, x2max])
        ax2.set_xticks(np.arange(x2min, x2max + 0.001, x2step))

    fig.tight_layout()  # otherwise the right y-label is slightly clipped

    if save_dir == '':
        plt.show()
    else:
        save_path = os.path.join(save_dir, filename)
        # print(save_path)
        plt.savefig(save_path)


def plot_lat_disp(data_to_plot, save_dir):

    filename = data_to_plot[0]

    force_data = data_to_plot[1][1:]
    force_label = data_to_plot[1][0]

    disp_lat_total = data_to_plot[3][1:]
    disp_lat_label = 'Lateral Displacement [mm]'
    disp_lat_left = data_to_plot[4][1:]
    disp_lat_right = data_to_plot[5][1:]

    fig, ax1 = plt.subplots(figsize=(16, 9))

    totalcolor = 'tab:red'
    leftcolor = 'blue'
    rightcolor = 'green'
    ax1.set_xlabel(force_label)
    ax1.set_ylabel(disp_lat_label)
    ax1.plot(force_data, disp_lat_total, color=totalcolor)
    ax1.plot(force_data, disp_lat_left, color=leftcolor)
    ax1.plot(force_data, disp_lat_right, color=rightcolor)
    ax1.tick_params(axis='y')
    ax1.set_title(filename)

    xmax = max(force_data)  # Change values to customize
    xmin = min(force_data)
    xstep = 1

    plt.xlim([xmin, xmax])
    ax1.set_xticks(np.arange(xmin, xmax + 0.001, xstep))

    ymax = max(disp_lat_total)
    ymin = min(disp_lat_total)
    ystep = 0.1

    ax1.set_ylim([ymin, ymax])
    ax1.set_yticks(np.arange(ymin, ymax + 0.001, ystep))

    if save_dir == '':
        plt.show()
    else:
        save_path = os.path.join(save_dir, filename)
        # print(save_path)
        plt.savefig(save_path)


"""force = ['Force [kN]', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
disp_axial = ['Axial Displacement [mm]', 0.1, 0.2, 0.3, 0.4, 0.5, 0.56, 0.61, 0.65, 0.68, 0.7]
disp_lateral = ['Lateral Displacement [mm]', 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
test_list = ['test.csv', force, disp_axial, disp_lateral]
test_list_2 = ['test.csv', force, disp_axial]
save_loc = user_comms.ask_save_dir()
make_graph(test_list, '')
# print(data.transpose_list(test_list, user_comms.ask_save_dir()))"""

