import os
import platform
import time


def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        t = os.path.getctime(path_to_file)
        t = time.ctime(t)
        return format_date(t)
    else:
        stat = os.stat(path_to_file)
        try:
            t = stat.st_birthtime
            t = time.ctime(t)
            return format_date(t)
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            t = stat.st_mtime
            t = time.ctime(t)
            return format_date(t)


def format_date(date):
    """Only keep the date of the file creation/modification."""
    d = date.split()
    day_num = d[2]
    day = d[0]
    mon = d[1]
    year = d[-1]

    date = "{} {} {} {}".format(day, day_num, mon, year)
    return date
