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
                    type=self.type
        )


class Timetable:
    def __init__(self, days):
        self.days = days

    def repr_json(self):
        return dict(days=list(map(lambda d: d.repr_json(), self.days)))


class Day:
    def __init__(self, lessons):
        self.lessons = lessons

    def repr_json(self):
        return dict(lessons=list(map(lambda l: l.repr_json(), self.lessons)))


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
        return dict(type=self.type, weeks=self.weeks)


class Combine:
    def __init__(self, subjects, timetables):
        self.subjects = subjects
        self.timetables = timetables

    def repr_json(self):
        return dict(
            subjects=list(map(lambda s: s.repr_json(), self.subjects)),
            timetables=list(map(lambda t: t.repr_json(), self.timetables))
        )


def create_json():
    # url = 'http://webservices.mirea.ru/upload/iblock/c30/КБиСП 4 курс 1 сем.xlsx'
    # url = 'http://webservices.mirea.ru/upload/iblock/043/КБиСП 3 курс 1 сем.xlsx'
    # r = requests.get(url, allow_redirects=True)
    # open(url.rsplit('/', 1)[1], 'wb').write(r.content)
    # ex_data = pd.read_excel(url.rsplit('/', 1)[1], sheet_name='Лист1', header=None)  # весь эксель файл
    # print(url.rsplit('/', 1)[1])
    ex_data = pd.read_excel('КБиСП 3 курс 1 сем.xlsx', sheet_name='Лист1', header=None)  # весь эксель файл
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
            print("")
            print(group)
            print("")
            count = 1
            for j in range(3, 75):

                lessons = str(ex_data[i][j])
                print(lessons, j)
                teachers = str(ex_data[i + 2][j])
                type = 0
                weeks = []
                lesson_type = str(ex_data[i + 1][j])
                room = str(ex_data[i + 3][j])
                link = str(ex_data[i + 2][j])
                location_index = 0

                if re.search('(([0-9]{1,2},{0,1}\\s*)+(|н|нед))', lessons) and lessons != 'nan':
                    lessons_name = re.sub('(( *нед\\.* *)|( н *))', '', lessons)
                    if ";" in lessons_name:
                        lessons_name = lessons_name.split(';')
                        start_x = 0
                        for num, lesson_x in enumerate(lessons_name, start_x):
                            weeks.append(''.join(re.findall('[0-9,.]', lesson_x)))
                            lessons_name[num] = re.sub('[0-9,.]', '', lesson_x)
                    elif "\n" in lessons_name:
                        lessons_name = lessons_name.split('\n')
                        start_x = 0
                        for num, lesson_x in enumerate(lessons_name, start_x):
                            weeks.append(''.join(re.findall('[0-9,.]', lesson_x)))
                            lessons_name[num] = re.sub('[0-9,.]', '', lesson_x)
                    else:
                        weeks = ''.join(re.findall('[0-9,.]', lessons_name))
                        lessons_name = re.sub('[0-9,.]', '', lessons_name)

                    if '*' in room:
                        if 'В-78*' or 'в-78*' in room:
                            room = str(re.sub('(В-78\\*\n)|(В-78\\*)|(в-78\\*)', '', room))
                            location_index = 1

                    if '\n' in room:
                        room = room.split('\n')
                        ws_counter = 0
                        for x in room:
                            if x == '':
                                ws_counter += 1
                        for _ in range(ws_counter):
                            room.remove('')

                    if ' ' in room:
                        room = room.split(' ')
                        ws_counter = 0
                        for x in room:
                            if x == '':
                                ws_counter += 1
                        for _ in range(ws_counter):
                            room.remove('')

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

                    if isinstance(lessons_name, list):
                        ws_counter = 0
                        for x in lessons_name:
                            if x == '':
                                ws_counter += 1
                        for _ in range(ws_counter):
                            lessons_name.remove('')
                        for x in range(len(lessons_name)):
                            lessons_name[x] = lessons_name[x].strip(' ')
                            if not check_if_subject_exist(lessons_name[x], subjects):
                                subjects.append(Subject(lessons_name[x], teachers[x], type))

                            if isinstance(room, list):
                                add_to_timetable(count, subjects, timetables, lessons_name[x],
                                                 Constraint(type, weeks[x]), lesson_type, room[x], location_index)
                            else:
                                add_to_timetable(count, subjects, timetables, lessons_name[x],
                                                 Constraint(type, weeks[x]), lesson_type, room, location_index)
                    else:
                        lessons_name = lessons_name.strip(' ')
                        if not check_if_subject_exist(lessons_name, subjects):
                            subjects.append(Subject(lessons_name, teachers, type))
                        add_to_timetable(count, subjects, timetables, lessons_name, Constraint(type, weeks),
                                         lesson_type, room, location_index)
                elif lessons != 'nan':
                    subjects.append(Subject(lessons, teachers, type))
                    if '*' in room:
                        if 'В-78*' or 'в-78*' in room:
                            room = re.sub('(В-78\\*)|(в-78\\*)', '', room)
                            location_index = 1

                        if '\n' in room:
                            room = room.split('\n')
                            ws_counter = 0
                            for x in room:
                                if x == '':
                                    ws_counter += 1
                            for _ in range(ws_counter):
                                room.remove('')

                        if ' ' in room:
                            room = room.split(' ')
                            ws_counter = 0
                            for x in room:
                                if x == '':
                                    ws_counter += 1
                            for _ in range(ws_counter):
                                room.remove('')

                    add_to_timetable(count,  subjects, timetables, lessons, Constraint(type, weeks), lesson_type, room,
                                     location_index)
                count += 1

            combined = Combine(subjects, timetables)
            dump_to_json(combined, group)


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


def check_if_subject_exist(name, subjects):
    for x in subjects:
        if name == x.name:
            return True

    return False


def dump_to_json(combined, group):
    # Serializing
    data = json.dumps(combined.repr_json(), indent=4, ensure_ascii=False)
    # print(data)
    text_file = open('json_groups/' + group + '.json', "w", encoding='utf-8')
    text_file.write(data)
    text_file.close()


create_json()
