from tqdm import tqdm

from index.courses import index, clean
from db.crud import get_all_courses
from db.models import Course


def index_all_courses():
    print('re-indexing all courses')

    courses = get_all_courses()
    clean()
    with tqdm(total=len(courses)) as pbar:
        for course in courses:
            index(course)
            pbar.update(1)
