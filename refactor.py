import json
import requests
import regex as re
import pandas as pd


class Subject:
    def __init__(self, name, teacher):
        self.name = name
        self.teacher = teacher
        self.type = type

    def repr_json(self):
        return dict(name=self.name,
                    teacher=self.teacher,
                    type=self.type)


class Timetable:
    def __init__(self, days):
        self.days = days

    def repr_json(self):
        return dict(days=list(map(lambda d: d.repr_json(),
                                  self.days)))


class Day:
    def __init__(self, lessons):
        self.lessons = lessons

    def repr_json(self):
        return dict(lessons=list(map(lambda l: l.repr_json(),
                                     self.lessons)))


class Lesson:
    def __init__(self, subjectIndex, constraint, room, locationIndex):
        self.subjectIndex = subjectIndex
        self.constraint = constraint
        self.room = room
        self.locationIndex = locationIndex

    def repr_json(self):
        return dict(subjectIndex=self.subjectIndex,
                    constraint=self.constraint.repr_json(),
                    room=self.room,
                    locationIndex=self.locationIndex)


class Constraint:
    def __init__(self, type: str, weeks: str):
        self.type = type
        self.weeks = weeks

    def repr_json(self):
        return dict(type=self.type,
                    weeks=self.weeks)


class Combine:
    def __init__(self, subjects, timetables):
        self.subjects = subjects
        self.timetables = timetables

    def repr_json(self):
        return dict(
            subjects=list(map(lambda s: s.repr_json(),
                              self.subjects)),
            timetables=list(map(lambda t: t.repr_json(),
                                self.timetables))
        )


def download_timetable(i):
    if i == 0:
        url = 'http://webservices.mirea.ru/upload/iblock/c30/КБиСП 4 курс 1 сем.xlsx'
    elif i == 1:
        url = 'http://webservices.mirea.ru/upload/iblock/043/КБиСП 3 курс 1 сем.xlsx'

    r = requests.get(url, allow_redirects=True)
    open(url.rsplit('/', 1)[1], 'wb').write(r.content)
    return pd.read_excel(url.rsplit('/', 1)[1], sheet_name='Лист1', header=None)  # весь эксель файл


def parse_timetable():
    pass