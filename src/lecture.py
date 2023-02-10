import hashlib
import paths
import json
import os


class Lecture:

    def __init__(self) -> None:
        self.src_url = ''
        self.m3u8_url = ''
        self.mp4_file = ''
        self.mp3_file = ''
        self.whispr_json = ''
        self.summary_text = ''

    @staticmethod
    def summary_exists(url):
        filename = paths.make_digest_filename(url)
        return os.path.isfile(filename)

    @staticmethod
    def from_summary(url):
        filename = paths.make_digest_filename(url)

        l = Lecture()
        l.src_url = url

        with open(filename, 'r') as f:
            l.summary_text = f.read()

        return l

    def save(self):
        filename = paths.make_digest_filename(self.src_url)
        with open(filename, 'w+') as f:
            f.write(self.summary_text)


    def get_text(self) -> str:
        with open(self.whispr_json, 'r') as f:
            data = json.loads(f.read())
            return data['text']


    def get_segments(self) -> str:
        with open(self.whispr_json, 'r') as f:
            data = json.loads(f.read())
            return data['segments']
