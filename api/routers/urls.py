from fastapi import Depends, APIRouter, HTTPException
from urllib.parse import urlparse, parse_qs
from pydantic import BaseModel
import validators
import re

from db.crud import (
    get_lecture_by_public_id_and_language,
    get_url_by_sha,
)
from jobs import schedule_analysis_of_lecture
from db.models import URL, Lecture, Analysis
from db import get_db

from tools.web.crawler import get_m3u8


router = APIRouter()


class InputModel(BaseModel):
    url: str
    language: str


class OutputModel(BaseModel):
    uri: str


@router.post('/url/kth', dependencies=[Depends(get_db)])
def parse_kth_url(
    input_data: InputModel,
) -> OutputModel:
    if input_data.url.strip() == '':
        raise HTTPException(status_code=400, detail='No URL provided, please enter a url such as: https://play.kth.se/media/0_4zo9e4nh')  # noqa: E501

    if not validators.url(input_data.url):
        raise HTTPException(status_code=400, detail='The URL you entered was not valid, please enter a url such as: https://play.kth.se/media/0_4zo9e4nh')  # noqa: E501

    domain = urlparse(input_data.url).netloc
    if not domain.endswith('play.kth.se'):
        raise HTTPException(status_code=400, detail='The URL was not valid, it must be kth.play.se video, such as https://play.kth.se/media/0_4zo9e4nh')  # noqa: E501

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
            url_hash=URL.make_sha(input_data.url),
        )

        try:
            content_url = urlparse(get_m3u8(input_data.url)).path
        except Exception:
            raise HTTPException(status_code=400, detail='Something went wrong while trying to get the lecture video, make sure its on the form https://play.kth.se/media/0_4zo9e4nh')  # noqa: E501

        regex = r'^.*entryId\/(\w*)\/.*$'
        matches = re.finditer(regex, content_url, re.MULTILINE)
        match = next(matches)

        if not match:
            raise HTTPException(status_code=400, detail='Could not find the lecture id')

        url.lecture_id = match.group(1)
        url.save()

    lecture = get_lecture_by_public_id_and_language(url.lecture_id, lang)
    if lecture is None:
        lecture = Lecture(
            public_id=url.lecture_id,
            language=lang,
            approved=True,
            source=Lecture.Source.KTH,
        )
        lecture.save()

    should_analyse = False
    analysis = lecture.get_last_analysis()

    if analysis is None:
        should_analyse = True
    else:
        if analysis.state == Analysis.State.FAILURE:
            should_analyse = True

        if analysis.seems_to_have_crashed():
            should_analyse = True

    if should_analyse:
        analysis = schedule_analysis_of_lecture(lecture)

    return {
        'uri': url.lecture_uri(lang)
    }


@router.post('/url/kth_raw', dependencies=[Depends(get_db)])
def parse_kth_raw_url(
    input_data: InputModel,
) -> OutputModel:
    if input_data.url.strip() == '':
        raise HTTPException(status_code=400, detail='No URL provided, please enter a url such as: https://vod-cache.kaltura.nordu.net/...')  # noqa: E501

    if not validators.url(input_data.url):
        raise HTTPException(status_code=400, detail='The URL you entered was not valid, please enter a url such as: https://vod-cache.kaltura.nordu.net/...')  # noqa: E501

    domain = urlparse(input_data.url).netloc
    if not domain.endswith('vod-cache.kaltura.nordu.net'):
        raise HTTPException(status_code=400, detail='The URL was not valid, it must be kaltura.nordu.net video, such as https://vod-cache.kaltura.nordu.net/...')  # noqa: E501

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
            url_hash=URL.make_sha(input_data.url),
        )

        regex = r'^.*entryId\/(\w*)\/.*$'
        matches = re.finditer(regex, input_data.url, re.MULTILINE)
        match = next(matches)

        if not match:
            raise HTTPException(status_code=400, detail='Could not find the lecture id')

        url.lecture_id = match.group(1)
        url.save()

    lecture = get_lecture_by_public_id_and_language(url.lecture_id, lang)
    if lecture is None:
        lecture = Lecture(
            public_id=url.lecture_id,
            language=lang,
            approved=True,
            source=Lecture.Source.KTH_RAW,
            raw_content_link=input_data.url,
        )
        lecture.save()

    should_analyse = False
    analysis = lecture.get_last_analysis()

    if analysis is None:
        should_analyse = True
    else:
        if analysis.state == Analysis.State.FAILURE:
            should_analyse = True

        if analysis.seems_to_have_crashed():
            should_analyse = True

    if should_analyse:
        analysis = schedule_analysis_of_lecture(lecture)

    return {
        'uri': url.lecture_uri(lang)
    }


@router.post('/url/youtube', dependencies=[Depends(get_db)])
def parse_youtube_url(
    input_data: InputModel,
) -> OutputModel:
    if input_data.url.strip() == '':
        raise HTTPException(status_code=400, detail='No URL provided, please enter a url such as: https://www.youtube.com/watch?v=nnkCEN4suxs')  # noqa: E501

    if not validators.url(input_data.url):
        raise HTTPException(status_code=400, detail='The URL you entered was not valid, please enter a url such as: https://www.youtube.com/watch?v=nnkCEN4suxs')  # noqa: E501

    domain = urlparse(input_data.url).netloc
    if not domain.endswith('youtube.com'):
        raise HTTPException(status_code=400, detail='The URL was not valid, it must be a youtube video, such as https://www.youtube.com/watch?v=nnkCEN4suxs')  # noqa: E501

    query_params = parse_qs(urlparse(input_data.url).query)
    if 'v' not in query_params:
        raise HTTPException(status_code=400, detail='The URL you entered was not valid, its missing a video id, please enter a url such as: https://www.youtube.com/watch?v=nnkCEN4suxs')  # noqa: E501

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
            url_hash=URL.make_sha(input_data.url),
            lecture_id=query_params['v'][0],
        )
        url.save()

    lecture = get_lecture_by_public_id_and_language(url.lecture_id, lang)
    if lecture is None:
        lecture = Lecture(
            public_id=url.lecture_id,
            language=lang,
            source=Lecture.Source.YOUTUBE
        )
        lecture.save()

    should_analyse = False
    analysis = lecture.get_last_analysis()

    if analysis is None:
        should_analyse = True
    else:
        if analysis.state == Analysis.State.FAILURE:
            should_analyse = True

        if analysis.seems_to_have_crashed():
            should_analyse = True

    if should_analyse:
        analysis = schedule_analysis_of_lecture(lecture)

    return {
        'uri': url.lecture_uri(lang)
    }
