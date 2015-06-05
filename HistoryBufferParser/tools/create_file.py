　　#!c:\python27\python.exe
# -*- coding: utf-8 -*-

　　import os
import re

　　from os import path
from shutil import rmtree

　　DEL_DIRS = None
DEL_FILES = r'(.+?\.pyc$|.+?\.pyo$|.+?\.log$)'

　　def del_dir(p):
    """Delete a directory."""
    if path.isdir(p):
        rmtree(p)
        print('D : %s' % p)

　　def del_file(p):
    """Delete a file."""
    if path.isfile(p):
        os.remove(p)
        print('F : %s' % p)

　　def gen_deletions(directory, del_dirs=DEL_DIRS, del_files=DEL_FILES):
    """Generate deletions."""
    patt_dirs = None if del_dirs == None else pile(del_dirs)
    patt_files = None if del_files == None else pile(del_files)

　　for root, dirs, files in os.walk(directory):
        if patt_dirs:
            for d in dirs:
                if patt_dirs.match(d):
                    yield path.join(root, d)
        if patt_files:
            for f in files:
                 if patt_files.match(f):
                    yield path.join(root, f)

　　def confirm_deletions(directory):
    import Tkinter
    import tkMessageBox

　　root = Tkinter.Tk()
    root.withdraw()
    res = tkMessageBox.askokcancel("Confirm deletions?",
        "Do you really wish to delete?\n\n"
        "Working directory:\n%s\n\n"
        "Delete conditions:\n(D)%s\n(F)%s"
        % (directory, DEL_DIRS, DEL_FILES))
    if res:
        print('Processing...')
        m, n = 0, 0
        for p in gen_deletions(directory):
            if path.isdir(p):
                del_dir(p)
                m += 1
            elif path.isfile(p):
                del_file(p)
                n += 1
        print('Clean %d dirs and %d files.' % (m, n))
        root.destroy()
    else:
        print('Canceled.')
        root.destroy()

　　root.mainloop()

　　if __name__ == '__main__':
    import sys
    argv = sys.argv
    directory = argv[1] if len(argv) >= 2 else os.getcwd()
    confirm_deletions(directory)
    # import subprocess
    # subprocess.call("pause", shell=True)


