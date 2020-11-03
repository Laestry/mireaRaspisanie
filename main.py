import json
import math

import regex as re
import pandas as pd


class Subject:
    def __init__(self, name, teacher):
        self.name = name
        self.teacher = teacher

    @classmethod
    def from_json(cls, data):
        return cls(**data)


class Timetable:
    def __init__(self, days):
        self.days = days

    @classmethod
    def from_json(cls, data):
        return cls(**data)


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
    def __init__(self, type: str, weeks: str):
        self.type = type
        self.weeks = weeks


class Combine:
    def __init__(self, combined):
        self.combined = combined

    @classmethod
    def from_json(cls, data):
        students = list(map(Subject.from_json, data["subjects"]))
        return cls(students)


def create_json():
    ex_data = pd.read_excel('C:\\Users\\Georgy\\Desktop\\КБиСП 3 курс 1 сем .xlsx', sheet_name='Лист1', header=None)  # весь эксель файл


    for i in range(359):
        print("i", i)

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
            print(group)
            count = 1
            for j in range(3, 75):
                print("j", j)

                lessons = str(ex_data[i][j])
                teachers = str(ex_data[i + 2][j])
                type = 0
                weeks = re.match('[0-9,.]', lessons)
                lesson_type = str(ex_data[i + 1][j])
                room = str(ex_data[i + 3][j])
                link = str(ex_data[i + 2][j])

                if re.search('(([0-9]{1,2},{0,1}\\s*)+(|н|нед))', lessons) and lessons != 'nan':
                    lessons_name = re.sub('[0-9,.]', '', lessons)
                    lessons_name = re.sub('(( *нед\\.* *)|( н *))', '', lessons_name)

                    if ";" in lessons_name:
                        lessons_name = lessons_name.split(';')
                    elif "/n" in lessons_name:
                        lessons_name = lessons_name.split('/n')

                    if '/n' in teachers:
                        teachers = teachers.split('/n')
                    elif ' ' in teachers:
                        teachers = teachers.split(' ')
                        ws_counter = 0
                        for x in teachers:
                            if x == '':
                                ws_counter += 1
                        for _ in range(ws_counter):
                            teachers.remove('')

                        teachers[0: 2] = [' '.join(teachers[0: 2])]
                        teachers[1: 3] = [' '.join(teachers[1: 3])]

                    if isinstance(lessons_name, list):
                        for x in range(len(lessons_name)):
                            if lessons_name[x][0] == ' ' or lessons_name[x][len(lessons_name[x]) - 1] == ' ':
                                lessons_name[x] = lessons_name[x].strip(' ')
                            if not check_if_subject_exist(lessons_name[x], subjects):
                                subjects.append(Subject(lessons_name[x], teachers[x]))
                            add_to_timetable(count, subjects, timetables, lessons_name[x], Constraint(type, weeks),
                                             lesson_type, room, 1)
                    else:
                        if lessons_name[0] == ' ' or lessons_name[0] == ' ':
                            lessons_name = lessons_name.strip(' ')
                        if not check_if_subject_exist(lessons_name, subjects):
                            subjects.append(Subject(lessons_name, teachers))
                        add_to_timetable(count, subjects, timetables, lessons_name, Constraint(type, weeks),
                                         lesson_type, room, 1)
                elif lessons != 'nan':
                    subjects.append(Subject(lessons, teachers))
                    add_to_timetable(count,  subjects, timetables, lessons, Constraint(type, weeks), lesson_type, room, 1)
                count += 1

            team = Combine(combined=[subjects, timetables])
            dump_to_json(team)


def add_to_timetable(count, subjects, timetables, lesson_name, constraint, type, room, locationindex):
    i = -1
    start = 0
    for num, x in enumerate(subjects, start):
        if x.name == lesson_name:
            i = num

    if count % 2:
        timetables[0].days[((count - 1) // 2) // 6].lessons.append(Lesson(i, constraint, type, room, locationindex))
    else:
        timetables[1].days[((count - 1) // 2) // 6].lessons.append(Lesson(i, constraint, type, room, locationindex))


def check_if_subject_exist(name, subjects):
    for x in subjects:
        if name == x.name:
            return True

    return False


def dump_to_json(team):
    # Serializing
    data = json.dumps(team, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    print(data)


create_json()




