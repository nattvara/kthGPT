from pathlib import Path
import hashlib
import os


HOME_DIR = os.path.join(Path.home(), '.kthgpt')


def ensure_kthgpt_dir():
    if not os.path.isdir:
        os.mkdir(HOME_DIR)


def make_url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


def make_mp4_filename(url: str) -> str:
    ensure_kthgpt_dir()
    return os.path.join(HOME_DIR, f'{make_url_hash(url)}.mp4')


def make_mp3_filename(url: str) -> str:
    ensure_kthgpt_dir()
    return os.path.join(HOME_DIR, f'{make_url_hash(url)}.mp3')


def make_transcript_filename(url: str) -> str:
    ensure_kthgpt_dir()
    return os.path.join(HOME_DIR, f'{make_url_hash(url)}.json')


def make_digest_filename(url: str) -> str:
    ensure_kthgpt_dir()
    return os.path.join(HOME_DIR, f'{make_url_hash(url)}.txt')
