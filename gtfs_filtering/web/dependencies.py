import typing

from fastapi import Depends

from gtfs_filtering.web.config import Settings, get_settings

SettingsDep = typing.Annotated[Settings, Depends(get_settings)]
