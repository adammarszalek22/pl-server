from datetime import datetime

def convert_to_datetime(string_date):
    return datetime(
        int(string_date[0:4]),
        int(string_date[5:7]),
        int(string_date[8:10]),
        int(string_date[11:13]),
        int(string_date[14:16]),
        int(string_date[17:19])
        )

def has_passed(start_time):
    return start_time < datetime.now()