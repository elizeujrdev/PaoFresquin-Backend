"""Datas e horários no fuso de Brasília (America/Sao_Paulo)."""
from __future__ import annotations

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from django.utils import timezone

TZ_BR = ZoneInfo("America/Sao_Paulo")


def localdate() -> date:
    return timezone.localdate()


def localnow() -> datetime:
    return timezone.localtime(timezone.now())


def start_of_day(d: date) -> datetime:
    return timezone.make_aware(datetime.combine(d, time.min), TZ_BR)


def end_of_day(d: date) -> datetime:
    return timezone.make_aware(datetime.combine(d, time.max), TZ_BR)


def aware_br(dt: datetime) -> datetime:
    if timezone.is_aware(dt):
        return timezone.localtime(dt)
    return timezone.make_aware(dt, TZ_BR)


def format_date_br(value: date | datetime | None) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return timezone.localtime(value).strftime("%d/%m/%Y")
    return value.strftime("%d/%m/%Y")


def format_datetime_br(value: datetime | None) -> str:
    if value is None:
        return ""
    return timezone.localtime(value).strftime("%d/%m/%Y %H:%M")


def format_datetime_sec_br(value: datetime | None) -> str:
    if value is None:
        return ""
    return timezone.localtime(value).strftime("%d/%m/%Y %H:%M:%S")


def format_time_br(value: datetime | None) -> str:
    if value is None:
        return ""
    return timezone.localtime(value).strftime("%H:%M")
