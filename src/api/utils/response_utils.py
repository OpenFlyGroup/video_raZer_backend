from datetime import datetime
from django.utils.timezone import make_aware
from rest_framework import status
from rest_framework.response import Response


def response_handler(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            print(e)
            return Response(
                data={"message": "An error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return wrapper


def date_to_str(date: datetime) -> str:
    if date:
        return date.strftime(format="%d.%m.%Y")
    else:
        return None


def str_to_date(date: str) -> datetime:
    if date:
        naive_date = datetime.strptime(date, "%d.%m.%Y")
        aware_date = make_aware(naive_date)
        return aware_date
    else:
        return None
