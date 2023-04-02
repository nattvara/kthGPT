from datetime import datetime
import pytest
import pytz

from jobs.tasks.lecture import fetch_metadata
from db.models import Lecture


def test_kth_video_title_is_fetched(mocker, mp4_file):
    mocker.patch('tools.web.crawler.scrape_title_from_page', return_value='some title')
    mocker.patch('tools.web.crawler.scrape_posted_date_from_kthplay')

    lecture = Lecture(
        public_id='some_id',
        language=Lecture.Language.SWEDISH,
        mp4_filepath=mp4_file,
        approved=True,
        source=Lecture.Source.KTH,
    )
    lecture.save()

    fetch_metadata.job(lecture.public_id, lecture.language)
    lecture.refresh()

    assert lecture.title == 'some title'


def test_kth_video_date_is_fetched(mocker, mp4_file):
    now = datetime.now()
    tz = pytz.timezone('UTC')

    mocker.patch('tools.web.crawler.scrape_title_from_page')
    mocker.patch('tools.web.crawler.scrape_posted_date_from_kthplay', return_value=now)

    lecture = Lecture(
        public_id='some_id',
        language=Lecture.Language.SWEDISH,
        mp4_filepath=mp4_file,
        approved=True,
        source=Lecture.Source.KTH,
    )
    lecture.save()

    fetch_metadata.job(lecture.public_id, lecture.language)
    lecture.refresh()

    lecture_date = tz.localize(lecture.date, is_dst=None)
    mocked_date = tz.localize(now, is_dst=None)

    assert lecture_date.isoformat(timespec='seconds') == mocked_date.isoformat(timespec='seconds')


def test_youtube_video_title_is_fetched(mocker, mp4_file):
    mocker.patch('tools.web.crawler.scrape_title_from_page', return_value='some title')
    mocker.patch('tools.youtube.metadata.get_upload_date')

    lecture = Lecture(
        public_id='some_id',
        language=Lecture.Language.SWEDISH,
        mp4_filepath=mp4_file,
        approved=True,
        source=Lecture.Source.YOUTUBE,
    )
    lecture.save()

    fetch_metadata.job(lecture.public_id, lecture.language)
    lecture.refresh()

    assert lecture.title == 'some title'


def test_youtube_video_date_is_fetched(mocker, mp4_file):
    now = datetime.now()
    tz = pytz.timezone('UTC')

    mocker.patch('tools.web.crawler.scrape_title_from_page')
    mocker.patch('tools.youtube.metadata.get_upload_date', return_value=now)

    lecture = Lecture(
        public_id='some_id',
        language=Lecture.Language.SWEDISH,
        mp4_filepath=mp4_file,
        approved=True,
        source=Lecture.Source.YOUTUBE,
    )
    lecture.save()

    fetch_metadata.job(lecture.public_id, lecture.language)
    lecture.refresh()

    lecture_date = tz.localize(lecture.date, is_dst=None)
    mocked_date = tz.localize(now, is_dst=None)

    assert lecture_date.isoformat(timespec='seconds') == mocked_date.isoformat(timespec='seconds')


def test_kth_raw_video_is_untouched(mp4_file):
    lecture = Lecture(
        public_id='some_id',
        language=Lecture.Language.SWEDISH,
        mp4_filepath=mp4_file,
        approved=True,
        source=Lecture.Source.KTH_RAW,
        date=None,  # set to none here because is defaulted to now
    )
    lecture.save()

    fetch_metadata.job(lecture.public_id, lecture.language)
    lecture.refresh()

    assert lecture.date is None
    assert lecture.title is None


def test_job_raises_exception_if_source_type_is_unknown(mp4_file):
    lecture = Lecture(
        public_id='some_id',
        language=Lecture.Language.SWEDISH,
        mp4_filepath=mp4_file,
        approved=True,
        source='something_bad',
    )
    lecture.save()

    with pytest.raises(ValueError, match='unknown source something_bad'):
        fetch_metadata.job(lecture.public_id, lecture.language)
