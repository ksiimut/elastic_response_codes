import matplotlib.pyplot as plt
import data
import user_comms
import os
import numpy as np
import math


def make_graph(data_to_plot, save_dir, retract_index):     # Data of one test
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

    x1max = round(max(x1_data), 1) + 0.1
    x1min = round(min(x1_data), 1) - 0.1
    x1step = 0.1

    ax1.set_xlim([x1min, x1max])
    ax1.set_xticks(np.arange(x1min, x1max + 0.001, x1step))

    if len(data_to_plot) == 4:
        x2_data = data_to_plot[3][1:]  # Lateral displacement
        x2_label = data_to_plot[3][0]

        ax2 = ax1.twiny()  # Axis for lateral displacement

        color = 'tab:blue'
        ax2.set_xlabel(x2_label, color=color)
        ax2.plot(x2_data, y_data, color=color)
        ax2.tick_params(axis='x', labelcolor=color)

        x2max = round(max(x2_data), 2) + 0.01
        x2min = round(min(x2_data), 2) - 0.01
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


def plot_lat_disp(data_to_plot, save_dir, retract_index):

    filename = data_to_plot[0]

    force_data = data_to_plot[1][1:]
    force_label = data_to_plot[1][0]
    disp_ax_data = data_to_plot[2][1:]
    disp_ax_label = data_to_plot[2][0]
    disp_lat_total = data_to_plot[3][1:]
    disp_lat_label = 'Lateral Displacement [mm]'
    disp_lat_left = data_to_plot[4][1:]
    disp_lat_right = data_to_plot[5][1:]

    fig, ax1 = plt.subplots(figsize=(15, 8))

    totalcolor = 'tab:red'
    leftcolor = 'blue'
    rightcolor = 'green'
    ax1.set_xlabel(disp_lat_label)
    ax1.set_ylabel(disp_ax_label, color=totalcolor)
    ax1.plot(disp_ax_data[:retract_index], disp_lat_total[:retract_index], color=totalcolor)
    ax1.plot(disp_ax_data[retract_index:-1], disp_lat_total[retract_index:-1], '--', color=totalcolor)
    # ax1.plot(disp_ax_data, disp_lat_left, color=leftcolor)
    # ax1.plot(disp_ax_data, disp_lat_right, color=rightcolor)
    ax1.tick_params(axis='y', labelcolor=totalcolor)
    ax1.set_title(filename)
    # fig.legend()

    ax2 = ax1.twinx()  # Axis for force displacement

    color = 'tab:blue'
    ax2.set_ylabel(force_label, color=color)
    ax2.plot(disp_ax_data[:retract_index], force_data[:retract_index], color=color)
    ax2.plot(disp_ax_data[retract_index:-1], force_data[retract_index:-1], '--', color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    xmax = round(max(disp_ax_data) + 0.05, 1)  # Change values to customize
    xmin = round(min(disp_ax_data) - 0.05, 1)
    xstep = 0.1

    plt.xlim([xmin, xmax])
    ax1.set_xticks(np.arange(xmin, xmax + 0.001, xstep))

    ymax = round(max(disp_lat_total), 2) + 0.01
    ymin = round(min(disp_lat_total), 2) - 0.005
    ystep = 0.01

    ax1.set_ylim([ymin, ymax])
    ax1.set_yticks(np.arange(ymin + 0.005, ymax + 0.001, ystep))

    y2max = round(max(force_data), -3) + 500
    # y2min = 0  # round(min(force_data), 2) - 100
    y2min = round((ymin / ymax) * y2max, -3)
    y2step = 1000  # round(abs(y2max - y2min) / 10, -3)

    ax2.set_ylim([y2min, y2max])
    ax2.set_yticks(np.arange(y2min, y2max + 0.001, y2step))

    if save_dir == '':
        plt.show()
    else:
        save_path = os.path.join(save_dir, filename)
        # print(save_path)
        plt.savefig(save_path)


def create_fig(title, x1, y1, retract_index=None, save_dir=None, x2=None, y2=None, lines=None, text=None):

    font = {'family': 'Arial',
            'weight': 'normal',
            'size': 8}
    title_font = {'family': 'Arial',
                  'weight': 'normal',
                  'size': 12}
    label_rot_x = 45
    cm = 1/2.54
    fig, ax1 = plt.subplots(figsize=(16*cm, 9*cm))  # AX1 is Y-axis
    plt.rc('font', **font)
    color = 'tab:red'
    ax1.set_xlabel(x1[0], font=font)
    ax1.set_ylabel(y1[0], color=color, font=font)
    if retract_index is not None:
        ax1.plot(x1[1:retract_index], y1[1:retract_index], color=color, label='Loading', linewidth=1)
        ax1.plot(x1[retract_index:], y1[retract_index:], '--', color=color, label='Unloading', linewidth=1)
    else:
        ax1.plot(x1[1:], y1[1:], color=color, linewidth=1)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_title(title, **title_font)

    y1_info = calc_limits(y1[1:])

    plt.ylim([y1_info[0], y1_info[1]])
    ax1.set_yticks(y1_info[2])

    for tick in ax1.get_yticklabels():
        tick.set_fontproperties(font)

    x1_info = calc_limits(x1[1:])

    ax1.set_xlim([x1_info[0], x1_info[1]])
    ax1.set_xticks(x1_info[2])

    for tick in ax1.get_xticklabels():
        tick.set_fontproperties(font)

    if text is not None:
        ax1.text(0.17, 0.07, text,
                 horizontalalignment='right',
                 verticalalignment='bottom',
                 transform=ax1.transAxes)

    if x2 is not None:
        ax2 = ax1.twiny()

        color = 'tab:blue'
        ax2.set_xlabel(x2[0], color=color, font=font)
        if retract_index is not None:
            ax2.plot(x2[1:retract_index], y1[1:retract_index], color=color, linewidth=1)
            ax2.plot(x2[retract_index:], y1[retract_index:], '--', color=color, linewidth=1)
        else:
            ax2.plot(x2[1:], y1[1:], color=color, linewidth=1)
        ax2.tick_params(axis='x', labelcolor=color)

        x2_info = calc_limits(x2[1:])

        ax2.set_xlim([x2_info[0], x2_info[1]])
        ax2.set_xticks(x2_info[2])

        for tick in ax2.get_xticklabels():
            tick.set_fontproperties(font)

    if y2 is not None:
        ax3 = ax1.twinx()

        color = 'tab:green'
        ax3.set_ylabel(y2[0], color=color, font=font)
        if retract_index is not None:
            ax3.plot(x1[1:retract_index], y2[1:retract_index], color=color, linewidth=1)
            ax3.plot(x1[retract_index:], y2[retract_index:], '--', color=color, linewidth=1)
        else:
            ax3.plot(x1[1:], y2[1:], color=color, linewidth=1)
        ax3.tick_params(axis='y', labelcolor=color)

        y2_info = calc_limits(y2[1:])

        ax3.set_ylim([y2_info[0], y2_info[1]])
        ax3.set_yticks(y2_info[2])

        for tick in ax3.get_yticklabels():
            tick.set_fontproperties(font)

    if lines is not None:
        modulus_line = lines[0]
        slope = modulus_line[0]
        intercept = modulus_line[1]

        y_line_1 = [y1_info[0], y1_info[1]]
        x_line_1 = []

        for i in y_line_1:
            x_line_1.append((i - intercept) / slope)

        ax1.plot(x_line_1, y_line_1, ':', color='b')

        if len(lines) == 2:
            poisson_line = lines[1]
            slope_2 = poisson_line[0]
            intercept_2 = poisson_line[1]

            x_line_2 = [x1_info[0], x1_info[1]]
            y_line_2 = []

            for i in x_line_2:
                y_line_2.append(slope_2 * i + intercept_2)

            ax3.plot(x_line_2, y_line_2, ':', color='black')

    # fig.legend(loc='upper left')
    fig.tight_layout()  # otherwise the right y-label is slightly clipped

    if save_dir is None:
        plt.show()
    else:
        save_path = os.path.join(save_dir, title)
        # print(save_path)
        plt.savefig(save_path)
        plt.close()


def calc_limits(data_set):
    digit = highest_digit(max([abs(max(data_set)), abs(min(data_set))])) - 1
    # print('Max: ' + str(max(data_set)) + '; Min: ' + str(min(data_set)))
    # print('Digit: ' + str(digit))

    lim_max = round_up(max(data_set), -digit)
    lim_min = round_down(min(data_set), -digit)
    tick_step = round((lim_max - lim_min) / 10, -digit)
    if tick_step == 0:
        tick_step = round((lim_max - lim_min) / 10, -(digit - 1))
    # print('Max: ' + str(lim_max) + '; Min: ' + str(lim_min) + '; Step: ' + str(tick_step))
    tick_array = np.arange(lim_min, lim_max, tick_step)

    return [lim_min, lim_max, tick_array]


def highest_digit(num):
    # print('Input: ' + str(num) + '; Output: ' + str(math.floor(math.log(num, 10))))
    return math.floor(math.log(num, 10))


def round_down(num, digits):
    multiplier = 10 ** digits
    inter = math.floor(num * multiplier)
    result = inter / multiplier
    return result


def round_up(num, digits):
    multiplier = 10 ** digits
    inter = math.ceil(num * multiplier)
    result = inter / multiplier
    return result


"""force = ['Force [kN]', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
disp_axial = ['Axial Displacement [mm]', 0.1, 0.2, 0.3, 0.4, 0.5, 0.56, 0.61, 0.65, 0.68, 0.7]
disp_lateral = ['Lateral Displacement [mm]', 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
test_list = ['test.csv', force, disp_axial, disp_lateral]
test_list_2 = ['test.csv', force, disp_axial]
save_loc = user_comms.ask_save_dir()
make_graph(test_list, '')
# print(data.transpose_list(test_list, user_comms.ask_save_dir()))"""

