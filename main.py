import json
import math

import regex as re
import pandas as pd


class Subject:
    def __init__(self, name, teacher):
        self.name = name
        self.teacher = teacher


class Timetable:
    def __init__(self, days):
        self.days = days


class Day:
    def __init__(self, lessons):
        self.lessons = lessons


class Lesson:
    def __init__(self, subjectIndex, constraint, type, room, locationIndex):
        self.subjectIndex = subjectIndex
        self.constraint = constraint
        self.type = type
        self.room = room
        self.room = locationIndex


class Constraint:
    def __init__(self, type, weeks):
        self.type = type
        self.weeks = weeks


def create_json():
    ex_data = pd.read_excel('C:\\Users\\Georgy\\Desktop\\КБиСП 3 курс 1 сем .xlsx', sheet_name='Лист1', header=None)  # весь эксель файл

    for i in range(359):
        jsonfile = {}

        subjects = []
        timetables = []

        even_monday = []
        even_tuesday = []
        even_wednesday = []
        even_thursday = []
        even_friday = []
        even_saturday = []
        even_week = [Day(even_monday), Day(even_tuesday), Day(even_wednesday),
                     Day(even_thursday), Day(even_friday), Day(even_saturday)]

        uneven_monday = []
        uneven_tuesday = []
        uneven_wednesday = []
        uneven_thursday = []
        uneven_friday = []
        uneven_saturday = []
        uneven_week = [Day(uneven_monday), Day(uneven_tuesday), Day(uneven_wednesday),
                       Day(uneven_thursday), Day(uneven_friday), Day(uneven_saturday)]

        timetables.append(Timetable(even_week))
        timetables.append(Timetable(uneven_week))

        group = str(ex_data[i][1])
        if re.search('[А-Я]{4}-[0-9]{2}-[0-9]{2}', group):
            for j in range(3, 75):
                lessons = str(ex_data[i][j])
                teachers = str(ex_data[i + 2][j])

                if re.search('(([0-9]{1,2},{0,1}\\s*)+(|н|нед))', lessons) and lessons != 'nan':
                    lessons_name = re.sub('[0-9,.]', '', lessons)
                    lessons_name = re.sub('(( *нед\\.* *)|( *н *))', '', lessons_name)

                    type = 0
                    weeks = re.match('[0-9,.]', lessons)
                    lesson_type = str(ex_data[i + 1][j])
                    room = str(ex_data[i + 3][j])
                    link = str(ex_data[i + 2][j])

                    if ";" in lessons_name:
                        lessons_name = lessons_name.split(";")
                        teachers = teachers.split('       ')
                    elif "/n" in lessons_name:
                        lessons_name = lessons_name.split("/n")
                        teachers = teachers.split('/n')

                    if isinstance(lessons_name, list):
                        for x in range(len(lessons_name)):
                            if lessons_name[x][0] == ' ' or lessons_name[x][len(lessons_name[x]) - 1] == ' ':
                                lessons_name[x] = lessons_name[x].strip(' ')
                            if not check_if_subject_exist(lessons_name[x], subjects):
                                subjects.append(Subject(lessons_name[x], teachers[x]))
                    else:
                        if lessons_name[0] == ' ' or lessons_name[0] == ' ':
                            lessons_name = lessons_name.strip(' ')
                        if not check_if_subject_exist(lessons_name, subjects):
                            subjects.append(Subject(lessons_name, teachers))
                elif lessons != 'nan':
                    subjects.append(Subject(lessons, teachers))


def add_to_timetable(even, timetables):
    if even:
        timetables[0].days.append(Lesson)
    else:
        timetables[1].days.append()


def check_if_subject_exist(name, subjects):
    for x in subjects:
        if name == x.name:
            return True

    return False


create_json()





