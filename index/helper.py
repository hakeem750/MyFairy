import jwt
from datetime import *
from django.core.mail import EmailMessage
from decouple import config
import math


class Helper:
    def __init__(self, request):
        self.request = request
        self.secret_key = config("secret_key")
        self.algorithm = config("algorithm")

    def is_autheticated(self):
        try:
            jwt_str = self.request.headers.get("Authorization")
            payload = jwt.decode(jwt_str, self.secret_key, algorithms=[self.algorithm])
            return {"status": True, "payload": payload}
        except:
            return {"status": False, "payload": None}

    def return_token(self):
        try:
            jwt_str = self.request.query_params.get('token')##self.request.headers.get("Authorization")
            payload = jwt.decode(jwt_str, self.secret_key, algorithms=[self.algorithm])
            return {"payload": payload}
        except:
            return {"payload": None}

    def get_verify_token(self, user):
        payload = {
            "user_id": user.id,
            "exp": datetime.utcnow() + timedelta(minutes=3600),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def get_token(self, id, usertype):
        payload = {
            "id": id,
            "name": usertype,
            "exp": datetime.utcnow() + timedelta(minutes=3600),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def modify_audio_input(self, audio_id, audio):
        dict = {}
        dict["audio_id"] = audio_id
        dict["audio"] = audio
        return dict

    def calculate_age(born):
        today = datetime.today().date()
        try:
            birthday = born.replace(year=today.year)
        except ValueError:
            # raised when birth date is February 29 and the current year is not a leap year
            birthday = born.replace(year=today.year, month=born.month + 1, day=1)
        if birthday > today:
            return today.year - born.year - 1
        else:
            return today.year - born.year

    @staticmethod
    def send_email(data):

        email = EmailMessage(
            subject=data["subject"], body=data["body"], to=[data["user_email"]]
        )
        email.send()

def get_data(post):
    a = dict(post)
    data = {}
    data = {i:a[i][0] for i in a}
    return data

def date_converter(date_string):
    dates = date_string.split("-")
    date_item = [int(item) for item in dates]
    try:
        new_date = date(date_item[0], date_item[1], date_item[2])
        return new_date
    except ValueError:
        return date(9030, 12, 30)


def period_start_dates(last_period, cycle_averages, start_str, end_str):
    last_period_date = date_converter(last_period)
    end_date = date_converter(end_str)
    start_date = date_converter(start_str)
    if last_period_date > start_date:
        return {"error": "date not in range"}
    if start_date > end_date:
        return {"error": "date not in range"}
    date_list = []
    while last_period_date < end_date:
        cycle_average = timedelta(days=cycle_averages)
        last_period_date = last_period_date + cycle_average
        if start_date <= last_period_date <= end_date:
            date_list.append(last_period_date)
    return date_list


def period_start_list(last_period, cycle_averages, start_str, end_str):
    last_period_date = date_converter(last_period)
    end_date = date_converter(end_str)
    start_date = date_converter(start_str)

    if last_period_date > start_date:
        return {"error": "date not in range"}
    if start_date > end_date:
        return {"error": "date not in range"}
    date_list = []
    while last_period_date <= end_date:
        cycle_average = timedelta(days=cycle_averages)
        last_period_date = last_period_date + cycle_average
        date_list.append(last_period_date)
    return date_list


def get_closest_date_from_list(
    cycle_event_date, last_period, cycle_averages, start_str, end_str
):
    event_date = date_converter(cycle_event_date)
    end_date = date_converter(end_str)
    start_date = date_converter(start_str)

    if event_date < start_date:
        return {"error": "date not in range"}
    if event_date > end_date:
        return {"error": "date not in range"}

    date_list = period_start_list(last_period, cycle_averages, start_str, end_str)
    cloz_dict = {abs(event_date - date): date for date in date_list}
    res = cloz_dict[min(cloz_dict.keys())]
    res_check = (event_date - res).days

    if res_check < 0:
        res_index = date_list.index(res)
        last_period_date = date_list[res_index - 1]
        return [last_period_date, res]
    else:
        res_index = date_list.index(res)
        next_period_date = date_list[res_index + 1]
        return [res, next_period_date]


def check_date_between_range(start_date, check_date, end_date):
    date_range = (end_date - start_date).days
    date_diff = (check_date - start_date).days
    if date_diff > 0 and date_diff < date_range:
        return True
    return False


def cycle_event_analyst(
    last_period, cycle_date, cycle_average, period_average, next_period
):
    cycle_event_date = date_converter(cycle_date)
    if cycle_event_date == last_period:
        return {"event": "period_start_date", "date": cycle_event_date}

    period_end_date = last_period + timedelta(days=period_average)
    if cycle_event_date == period_end_date:
        return {"event": "period_end_date", "date": cycle_event_date}

    period = check_date_between_range(last_period, cycle_event_date, period_end_date)
    if period:
        return {"event": "in_period", "date": cycle_event_date}

    cycle_avg = math.floor(cycle_average / 2)
    ovulation_date = last_period + timedelta(days=cycle_avg)
    if cycle_event_date == ovulation_date:
        return {"event": "ovulation_date", "date": cycle_event_date}

    fertility_window_begins = ovulation_date - timedelta(days=5)
    fertility_window_ends = ovulation_date + timedelta(days=5)
    fore_fertility = check_date_between_range(
        fertility_window_begins, cycle_event_date, ovulation_date
    )
    if fore_fertility:
        return {"event": "fertility_window", "date": cycle_event_date}

    next_fertility = check_date_between_range(
        ovulation_date, cycle_event_date, fertility_window_ends
    )
    if next_fertility:
        return {"event": "fertility_window", "date": cycle_event_date}

    pre_ovulation_ends = ovulation_date - timedelta(days=4)
    pre_ovulation_window = check_date_between_range(
        period_end_date, cycle_event_date, pre_ovulation_ends
    )
    if pre_ovulation_window:
        return {"event": "pre_ovulation_window", "date": cycle_event_date}

    post_ovulation_starts = ovulation_date + timedelta(days=4)
    post_ovulation_window = check_date_between_range(
        post_ovulation_starts, cycle_event_date, next_period
    )
    if post_ovulation_window:
        return {"event": "post_ovulation_window", "date": cycle_event_date}

    if cycle_event_date == next_period:
        return {"event": "period_start_date", "date": cycle_event_date}
    else:
        return {"event": "date_not_in_range", "date": cycle_event_date}


def cycle_events(last_period, cycle_length, period_length):

    mid = math.floor(cycle_length / 2)
    
    next_period = last_period + timedelta(days=cycle_length)
    period_end = next_period + timedelta(days=period_length)
    ovulation = next_period + timedelta(days=mid)
    ovulation_end = ovulation + timedelta(days=1)
    free_period = period_end + timedelta(days=1)
    luteal = ovulation_end + timedelta(days=1)

    Free_period_days = (ovulation - free_period).days
    Ovulation_days = (ovulation_end - ovulation).days

    return {
        "Next_period": next_period,
        "period_days": period_length,

        "Free_period": free_period,
        "Free_period_days": Free_period_days,

        "Ovulation": ovulation,
        "Ovulation_days": Ovulation_days,
        
        "Luteal_phase": luteal,
        "Luteal_days": cycle_length - (period_length + Free_period_days + Ovulation_days),

        "Last_period_date": last_period

    }
