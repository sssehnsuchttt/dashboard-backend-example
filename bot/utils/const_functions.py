import time
from datetime import datetime

def get_date(arg=None):
    this_date = datetime.today().replace(microsecond=0)
    if arg==None:
        this_date = this_date.strftime("%d.%m.%Y %H:%M:%S")
    else:
        this_date = this_date.strftime(f"%{arg}")

    return this_date

def do_round(number):
    try:
        int_part = str(number).split(".")[0]
        float_part = str(number).split(".")[1]
        return float(f"{int_part}.{float_part[:2]}")
    except:
        return float(number)

def progressbar(number, current_number):
    unfilled = "⬛"
    filled = "🟩"
    percent = round(((current_number/number)*100), 2)
    sections_filled = int(percent/10)
    sections_unfilled = 10 - sections_filled

    unfilledbar = unfilled * (10 - sections_filled)
    filledbar = filled * sections_filled
    progressbar = f"{filledbar}{unfilledbar} {percent}% ({current_number}/{number})"
    return progressbar