import datetime
from dateutil.relativedelta import relativedelta
import pytz

def get_first_day_of_month(text):
    try:
        dt = datetime.datetime.strptime(text, '%Y-%m')
        return dt
    except:
        pass
    raise ValueError('no valid date format found')

def get_month_strs(base_month_str):
    try:
        the_month = get_first_day_of_month(base_month_str)
    except ValueError:
        if base_month_str != 'prev_month':
            raise ValueError('no valid date format found')
        the_month = pytz.timezone('Asia/Taipei').localize(datetime.datetime.today().replace(day=1))

    the_month_str = the_month.strftime('%Y-%m-%d')
    the_next_month = the_month + relativedelta(months=1)
    the_next_month_str = the_next_month.strftime('%Y-%m-%d')
    the_prev_month = (the_month - datetime.timedelta(days=1)).replace(day=1)
    the_prev_month_str = the_prev_month.strftime('%Y-%m-%d')
    return (the_month_str, the_prev_month_str, the_next_month_str)
