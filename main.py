import json
import requests
import regex as re
import pandas as pd


class Subject:
    def __init__(self, name, teacher, type):
        self.name = name
        self.teacher = ''.join(teacher)
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
    def __init__(self, type, weeks):
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
    return pd.read_excel(url.rsplit('/', 1)[1], sheet_name='Лист1', header=None)


def check_if_subject_exist(name, subject_type, subjects):
    for x in subjects:
        if name == x.name and subject_type == x.type:
            return True
    return False


def whitespace_remover(string):
    if '\n' in string:
        string = string.split('\n')

    if ' ' in string:
        string = string.split(' ')

    ws_counter = 0
    for x in string:
        if x == '':
            ws_counter += 1
    for _ in range(ws_counter):
        string.remove('')

    return string


def format_room_and_get_location(room, location_index):
    if '\n' in room:
        room = room.split('\n')
    if ' ' in room:
        room = room.split(' ')
    room = whitespace_remover(room)

    if isinstance(room, list):
        location_index = []
        start = 0
        for num, room_x in enumerate(room, start):
            if 'В-78*' or 'в-78*' in room_x:
                room[num] = str(re.sub('(В-78\\*\n)|(В-78\\*)|(в-78\\*)', '', room_x))
                location_index.append(1)
            else:
                location_index.append(0)

    elif 'В-78*' or 'в-78*' in room:
        room = str(re.sub('(В-78\\*\n)|(В-78\\*)|(в-78\\*)', '', room))
        location_index = 1

    whitespace_remover(room)
    return room, location_index


def add_to_timetable(count, subjects, timetables, lesson_name, constraint, room, location_index):
    i = -1
    start = 0
    for num, x in enumerate(subjects, start):
        if x.name == lesson_name:
            i = num

    if count % 2:
        timetables[0].days[((count - 1) // 2) // 6].lessons.append(Lesson(i, constraint, room, location_index))
    else:
        timetables[1].days[((count - 1) // 2) // 6].lessons.append(Lesson(i, constraint, room, location_index))


def split_lessons_and_weeks(lessons, weeks):
    lessons = re.sub('(( *нед\\.* *)|( н *))', ' ', lessons)
    # TODO: make somehow groups work
    groups = re.findall('(1 +гр)|(2 +гр)', lessons)
    lessons = re.sub('(1 +гр)|(2 +гр)', ' ', lessons)
    weeks = re.findall('(?:[0-9]{1,2},|. *)*(?:[0-9]{1,2} *)+', lessons)
    start = 0

    if len(weeks) > 1:
        lessons = lessons.strip(' ')
        lessons = re.split('([0-9]{1,2},|. *)*([0-9]{1,2} *)+', lessons)

    if isinstance(lessons, list) and len(lessons) > 1:
        if None in lessons:
            lessons = list(filter(None, lessons))
        start = 0
        for num, x in enumerate(lessons, start):
            lessons[num] = re.sub('(?:[0-9]{1,2},|. *)*(?:[0-9]{1,2} *)+|[,;\n]', '', x)
    else:
        lessons = re.sub('(?:[0-9]{1,2},|. *)*(?:[0-9]{1,2} *)+|[,;\n]', '', lessons)

    whitespace_remover(lessons)
    return lessons, weeks


def split_teachers(teachers):
    if '\n' in teachers:
        teachers = teachers.split('\n')
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
    teachers = whitespace_remover(teachers)
    return teachers


def dump_to_json(combined, group):
    # Serializing
    data = json.dumps(combined.repr_json(), indent=4, ensure_ascii=False)
    # print(data)
    text_file = open('json_groups/' + group + '.json', "w", encoding='utf-8')
    text_file.write(data)
    text_file.close()


def parse_timetable():
    # ex_data = download_timetable(1)
    ex_data = pd.read_excel('КБиСП 3 курс 1 сем.xlsx', sheet_name='Лист1', header=None)

    for i in range(359):
        print("i", i)
        group = str(ex_data[i][1])
        if re.search('[А-Я]{4}-[0-9]{2}-[0-9]{2}', group):
            print('\n', group, '\n')
            count = 1
            # <editor-fold desc="Resetting lists">
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
            # </editor-fold>
            for j in range(3, 75):
                # <editor-fold desc="Parsing information in excel">
                lessons = str(ex_data[i][j])
                print(lessons, j)
                teachers = str(ex_data[i + 2][j])
                type = 0
                weeks = []
                lesson_type = str(ex_data[i + 1][j])
                room = str(ex_data[i + 3][j])
                link = str(ex_data[i + 2][j])
                location_index = 0
                # </editor-fold>

                if len(list(re.findall('([0-9]{1,2}, *)*([0-9]{1,2} *)+', lessons))) > 0:

                    lessons, weeks = split_lessons_and_weeks(lessons, weeks)
                    room, location_index = format_room_and_get_location(room, location_index)
                    teachers = split_teachers(teachers)

                    if not isinstance(lessons, list):
                        if not check_if_subject_exist(lessons, lesson_type, subjects):
                            subjects.append(Subject(lessons, teachers, lesson_type))
                        add_to_timetable(count, subjects, timetables, lessons,
                                         Constraint(type, weeks), room, location_index)
                    else:
                        for x in range(len(lessons)):
                            # lessons[x] = lessons[x].strip(' ')
                            # teachers[x] = teachers[x].strip(' ')
                            if not check_if_subject_exist(lessons[x], lesson_type, subjects):
                                if len(lessons) == len(teachers):
                                    subjects.append(Subject(lessons[x], teachers[x], lesson_type))
                                else:
                                    subjects.append(Subject(lessons[x], teachers, lesson_type))

                            if isinstance(room, list) and len(room) > 1:
                                add_to_timetable(count, subjects, timetables, lessons[x],
                                                 Constraint(type, weeks[x]), room[x], location_index)
                            elif len(room) == 1:
                                add_to_timetable(count, subjects, timetables, lessons[x],
                                                 Constraint(type, weeks[x]), room[0], location_index)
                            else:
                                add_to_timetable(count, subjects, timetables, lessons[x],
                                                 Constraint(type, weeks[x]), room, location_index)

                else:
                    if not check_if_subject_exist(lessons, lesson_type, subjects):
                        subjects.append(Subject(lessons, teachers, lesson_type))
                    room, location_index = format_room_and_get_location(room, location_index)
                    add_to_timetable(count,  subjects, timetables, lessons,
                                     Constraint(type, weeks), room, location_index)
                count += 1

            combined = Combine(subjects, timetables)
            dump_to_json(combined, group)


parse_timetable()
