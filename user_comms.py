from tkinter import filedialog


def ask_src_path(mode_var):
    # mode_var == 0 --> ask for specific file
    # mode_var == 1 --> ask for a directory
    if mode_var == 0:
        path = filedialog.askopenfilename(title='Choose File for Processing...')
    elif mode_var == 1:
        path = filedialog.askdirectory(title="Choose Directory with Files for Processing...")
    else:
        path = ''

    return path


def ask_save_dir():
    dir = filedialog.askdirectory(title='Choose Save Directory...')
    return dir