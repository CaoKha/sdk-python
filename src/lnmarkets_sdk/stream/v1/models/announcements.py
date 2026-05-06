"""Announcement topic payloads."""

from __future__ import annotations

from pydantic import BaseModel

from lnmarkets_sdk.stream.v1._internal.models import BaseConfig


class AnnouncementAdd(BaseModel, BaseConfig):
    """An announcement was added."""

    id: str
    title: str
    message: str
    link: str | None = None


class AnnouncementRemove(BaseModel, BaseConfig):
    """An announcement was removed."""

    id: str


type AnnouncementEvent = AnnouncementAdd | AnnouncementRemove


__all__ = ["AnnouncementAdd", "AnnouncementEvent", "AnnouncementRemove"]
