from typing import List

from pydantic import BaseModel, validator

from src.misc.constant.message import MESSAGE_WARNING_FILENAME_EMPTY, MESSAGE_WARNING_ENCODED_FILE_EMPTY, \
    MESSAGE_WARNING_INVALID_FILE_EXTENSION, MESSAGE_WARNING_URL_PAYLOAD_EMPTY
from src.misc.helper.helper import check_image_ext_validity


class EncodedUpload(BaseModel):
    filename: str
    encoded_file: str

    @validator("filename")
    def filename_not_empty(cls, filename):
        if not filename:
            raise ValueError(MESSAGE_WARNING_FILENAME_EMPTY)
        if not check_image_ext_validity(filename):
            raise ValueError(MESSAGE_WARNING_INVALID_FILE_EXTENSION)
        return filename

    @validator("encoded_file")
    def encoded_file_not_empty(cls, encoded_file):
        if not encoded_file:
            raise ValueError(MESSAGE_WARNING_ENCODED_FILE_EMPTY)
        return encoded_file


class UrlUpload(BaseModel):
    url: List[str]

    @validator("url")
    def url_not_empty(cls, url):
        if len(url) <= 0:
            raise ValueError(MESSAGE_WARNING_URL_PAYLOAD_EMPTY)
        return url
