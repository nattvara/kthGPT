import logging

from db.crud import find_course_code
import index.courses as course_index


def job(course_code: str):
    logger = logging.getLogger('rq.worker')

    course = find_course_code(course_code)
    if course is None:
        raise ValueError(f'course {course} not found')

    course_index.index(course)

    logger.info('done.')


# Test run the job
if __name__ == '__main__':
    course = find_course_code('SF2972')
    course.reindex()
