

from db.crud import get_all_lectures


def invalidate_all_query_caches():
    print('invalidating all query caches')

    lectures = get_all_lectures()
    for lecture in lectures:
        print(f'invalidating cache for lecture {lecture}: ', end='')
        queries = lecture.queries()
        print(f'found {len(queries)} queries', end='')
        for query in queries:
            query.cache_is_valid = False
            query.save()
        print(' done.')
