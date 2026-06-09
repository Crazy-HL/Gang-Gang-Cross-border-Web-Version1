from datetime import datetime


def format_datetime(value: datetime | None) -> str:
    if not value:
        return ''
    return value.strftime('%Y-%m-%d %H:%M')
