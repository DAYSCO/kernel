import os
import sys


class Config:
    PLATFORM = sys.platform
    if PLATFORM in ['win32', 'cygwin', 'msys']:
        spl = "\\"
    elif PLATFORM in ['linux', 'linux2', 'darwin', 'os2', 'os2emx']:
        spl = "/"
    else:
        raise Exception(f"ERROR: sys.platform unknown {PLATFORM}")
    LOG_PATH = os.environ.get("DAYS_LOG_PATH", os.path.join(os.path.dirname(
        os.path.abspath(__file__)).split(f"app{spl}config")[0], "logs"))
    LOG_PATH = LOG_PATH.rstrip(spl)
    if not os.path.isdir(LOG_PATH):
        try:
            os.mkdir(LOG_PATH)
        except FileNotFoundError:
            folders = LOG_PATH.split(spl)
            while True:
                try:
                    folders.remove("")
                except ValueError:
                    break
            for i in range(1, len(folders) + 1):
                test_dir = spl + spl.join(folders[0:i])
                if not os.path.isdir(test_dir):
                    os.mkdir(test_dir)
    DATA_PATH = os.environ.get("DAYS_DATA_PATH", os.path.join(os.path.dirname(
        os.path.abspath(__file__)).split(f"app{spl}config")[0], "data"))
    DATA_PATH = DATA_PATH.rstrip(spl)