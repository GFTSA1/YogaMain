import json

from redis.asyncio import Redis

from ..models import YogaCourse

COURSES_IDS_KEY = "courses:ids"
COURSE_KEY_TMPL = "course:{id}"
CACHE_TTL = 60 * 30


def _serialize(course: YogaCourse) -> dict:
    return {k: json.dumps(v) for k, v in course.model_dump().items()}


def _deserialize(raw: dict) -> dict:
    return {k: json.loads(v) for k, v in raw.items()}


async def get_all_courses_from_cache(redis: Redis) -> list[dict] | None:
    ids = await redis.smembers(COURSES_IDS_KEY)
    if not ids:
        return None

    pipe = redis.pipeline()
    for course_id in ids:
        pipe.hgetall(COURSE_KEY_TMPL.format(id=course_id))
    results = await pipe.execute()

    courses = [_deserialize(r) for r in results if r]
    courses.sort(key=lambda c: c["id"])
    return courses


async def set_all_courses_to_cache(redis: Redis, courses: list[YogaCourse]) -> None:
    if not courses:
        return
    pipe = redis.pipeline()
    ids = [str(c.id) for c in courses]
    pipe.sadd(COURSES_IDS_KEY, *ids)
    pipe.expire(COURSES_IDS_KEY, CACHE_TTL)
    for course in courses:
        key = COURSE_KEY_TMPL.format(id=course.id)
        pipe.hset(key, mapping=_serialize(course))
        pipe.expire(key, CACHE_TTL)
    await pipe.execute()


async def get_course_from_cache(redis: Redis, course_id: int) -> dict | None:
    raw = await redis.hgetall(COURSE_KEY_TMPL.format(id=course_id))
    return _deserialize(raw) if raw else None


async def set_course_to_cache(redis: Redis, course: YogaCourse) -> None:
    key = COURSE_KEY_TMPL.format(id=course.id)
    pipe = redis.pipeline()
    pipe.hset(key, mapping=_serialize(course))
    pipe.expire(key, CACHE_TTL)
    pipe.sadd(COURSES_IDS_KEY, str(course.id))
    await pipe.execute()


async def invalidate_course_cache(redis: Redis, course_id: int) -> None:
    await redis.delete(COURSE_KEY_TMPL.format(id=course_id))
    await redis.srem(COURSES_IDS_KEY, str(course_id))


async def invalidate_courses_list_cache(redis: Redis) -> None:
    await redis.delete(COURSES_IDS_KEY)
