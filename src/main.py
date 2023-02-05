from crawler.crawler import get_m3u8
from crawler.downloader import download_mp4_from_m3u8
from transcribe.converter import extract_mp3
from transcribe.parse import extract_text
from summarise.summary import create_summary, create_chunks
from lecture import Lecture
from query import ask
import beeprint
import sys
import os


def main():
    url = sys.argv[1]
    query = sys.argv[2]
    api_key = os.getenv('OPENAI_API_KEY')

    if Lecture.summary_exists(url):
        lecture = Lecture.from_summary(url)
    else:
        lecture = Lecture()
        lecture.src_url = url

        print('fetching content link...')
        lecture.m3u8_url = get_m3u8(url)
        print('downloading lecture...')
        lecture.mp4_file = download_mp4_from_m3u8(lecture.m3u8_url)
        print('extracting audio...')
        lecture.mp3_file = extract_mp3(lecture.mp4_file)
        print('transcribing lecture...')
        lecture.whispr_json = extract_text(lecture.mp3_file, lecture.src_url)

        print('generating a digested summary...')
        size = 10
        chunks = create_chunks(lecture.get_segments(), size)
        lecture.summary_text = create_summary(chunks, size, api_key)
        lecture.save()


    print(ask(lecture, query, api_key))


if __name__ == '__main__':
    main()
