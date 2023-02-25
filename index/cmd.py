from tqdm import tqdm

import index.courses as courses_index
import index.lecture as lecture_index
from db.crud import (
    get_all_ready_lectures,
    get_all_courses,
)


def index_all_courses():
    print('re-indexing all courses')

    courses = get_all_courses()
    courses_index.clean()
    courses_index.create()
    with tqdm(total=len(courses)) as pbar:
        for course in courses:
            courses_index.index(course)
            pbar.update(1)


def index_all_lectures():
    print('re-indexing all lectures')

    lectures = get_all_ready_lectures()
    lecture_index.clean()
    lecture_index.create()
    with tqdm(total=len(lectures)) as pbar:
        for lecture in lectures:
            lecture_index.index(lecture)
            pbar.update(1)
