from fastapi import Depends, APIRouter, HTTPException
from urllib.parse import urlparse
from pydantic import BaseModel
import validators
import re

from db.crud import get_url_by_sha, get_lecture_by_public_id_and_language
from db.models import URL, Lecture
from db import get_db

from jobs import (
    get_default_queue,
    get_download_queue,
    get_extract_queue,
    get_transcribe_queue,
    get_summarise_queue,
    capture_preview,
    download_lecture,
    extract_audio,
    transcribe_audio,
    summarise_transcript,
)
from tools.web.crawler import get_m3u8
from rq import Queue


router = APIRouter()

class InputModel(BaseModel):
    url: str
    language: str


class OutputModel(BaseModel):
    uri: str


@router.post('/url', dependencies=[Depends(get_db)])
def parse_url(
    input_data: InputModel,
    queue_default: Queue = Depends(get_default_queue),
    queue_download: Queue = Depends(get_download_queue),
    queue_extract: Queue = Depends(get_extract_queue),
    queue_transcribe: Queue = Depends(get_transcribe_queue),
    queue_summarise: Queue = Depends(get_summarise_queue),
) -> OutputModel:
    if input_data.url.strip() == '':
        raise HTTPException(status_code=400, detail='No URL provided, please enter a url such as: https://play.kth.se/media/0_4zo9e4nh')

    if not validators.url(input_data.url):
        raise HTTPException(status_code=400, detail='The URL you entered was not valid, please enter a url such as: https://play.kth.se/media/0_4zo9e4nh')

    domain = urlparse(input_data.url).netloc
    if not domain.endswith('play.kth.se'):
        raise HTTPException(status_code=400, detail='The URL was not valid, it must be kth.play.se video, such as https://play.kth.se/media/0_4zo9e4nh')

    if input_data.language == str(Lecture.Language.ENGLISH):
        lang = Lecture.Language.ENGLISH
    elif input_data.language == str(Lecture.Language.SWEDISH):
        lang = Lecture.Language.SWEDISH
    else:
        raise HTTPException(status_code=400, detail='Unsupported language')

    sha = URL.make_sha(input_data.url)
    url = get_url_by_sha(sha)

    if url is None:
        url = URL(
            url=input_data.url,
            url_hash=URL.make_sha(input_data.url)
        )

        try:
            content_url = urlparse(get_m3u8(input_data.url)).path
        except:
            raise HTTPException(status_code=400, detail='Something went wrong while trying to get the lecture video, make sure its on the form https://play.kth.se/media/0_4zo9e4nh')

        regex = r'^.*entryId\/(\w*)\/.*$'
        matches = re.finditer(regex, content_url, re.MULTILINE)
        match = next(matches)

        if not match:
            raise HTTPException(status_code=400, detail='Could not find the lecture id')

        url.lecture_id = match.group(1)
        url.save()

    lecture = get_lecture_by_public_id_and_language(url.lecture_id, lang)
    if lecture is None:
        lecture = Lecture(public_id=url.lecture_id, language=lang)
        lecture.save()

        queue_default.enqueue(capture_preview.job, lecture.public_id, lecture.language, job_timeout=capture_preview.TIMEOUT)
        job_1 = queue_download.enqueue(download_lecture.job, lecture.public_id, lecture.language, job_timeout=download_lecture.TIMEOUT)
        job_2 = queue_extract.enqueue(extract_audio.job, lecture.public_id, lecture.language, job_timeout=extract_audio.TIMEOUT, depends_on=job_1)
        job_3 = queue_transcribe.enqueue(transcribe_audio.job, lecture.public_id, lecture.language, job_timeout=transcribe_audio.TIMEOUT, depends_on=job_2)
        job_4 = queue_summarise.enqueue(summarise_transcript.job, lecture.public_id, lecture.language, job_timeout=summarise_transcript.TIMEOUT, depends_on=job_3)

    return {
        'uri': url.lecture_uri(lang)
    }
