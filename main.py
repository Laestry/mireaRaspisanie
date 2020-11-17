import json
import requests
import regex as re
import pandas as pd
from bs4 import BeautifulSoup

# <editor-fold desc="Data classes">
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
    def __init__(self, lessonNumber, subjectIndex, constraint, room, locationIndex):
        self.lessonNumber = lessonNumber
        self.subjectIndex = subjectIndex
        self.constraint = constraint
        if isinstance(room, list) and len(room) > 1:
            self.room = ' '.join(room)
        else:
            self.room = ''.join(room)
        if isinstance(locationIndex, list):
            self.locationIndex = locationIndex[0]
        else:
            self.locationIndex = locationIndex

    def repr_json(self):
        return dict(lessonNumber=self.lessonNumber,
                    subjectIndex=self.subjectIndex,
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
# </editor-fold>


def download_timetable():
    req = requests.get('https://www.mirea.ru/schedule/')
    soup = BeautifulSoup(req.text, 'lxml')
    url = []
    for a in soup.find_all('a', class_='uk-link-toggle', href=True):
        if 'pdf' not in a['href'] and 'xlsx' in a['href'] or 'XLSX' in a['href']:
            url.append(a['href'])
            print(a['href'])

    for url_x in url:
        r = requests.get(url_x, allow_redirects=True)
        open(url_x.rsplit('/', 1)[1], 'wb').write(r.content)
        parse_timetable(url_x.rsplit('/', 1)[1])


def check_if_subject_exist(name, subject_type, subjects):
    for x in subjects:
        if name == x.name and subject_type == x.type:
            return True
    return False


def whitespace_remover(string):
    if '\n' in string:
        if not isinstance(string, list):
            string = string.split('\n')

    if ' ' in string:
        if not isinstance(string, list):
            string = string.split(' ')
        else:
            for num in range(len(string)):
                string[num] = string[num].strip(" ")

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

    # TODO : add more locations and for three lessons in one day
    if isinstance(room, list):
        location_index = []
        start = 0
        for num, room_x in enumerate(room, start):
            if 'Д' in room_x or 'д' in room_x:
                location_index.append(-1)
            elif 'В-78*' in room_x or 'в-78*' in room_x:
                room[num] = str(re.sub('(В-78\\*\n)|(В-78\\*)|(в-78\\*)', '', room_x))
                location_index.append(1)
                whitespace_remover(room)
            elif 'МП*-1' in room or 'мп*-1' in room:
                room[num] = str(re.sub('(МП\\*-1\n)|(МП\\*-1)|(мп\\*-1)', '', room_x))
                location_index.append(2)
                whitespace_remover(room)
            else:
                location_index.append(0)
                whitespace_remover(room)

    elif 'Д' in room or 'д' in room:
        location_index = -1
    elif 'В-78*' in room or 'в-78*' in room:
        room = str(re.sub('(В-78\\*\n)|(В-78\\*)|(в-78\\*)', '', room))
        location_index = 1
    elif 'МП*-1' in room or 'мп*-1' in room:
        room = str(re.sub('(МП\\*-1\n)|(МП\\*-1)|(мп\\*-1)', '', room))
        location_index = 2

    whitespace_remover(room)
    return room, location_index


def add_to_timetable(lessons_num, count, subjects, timetables, lesson_name, constraint, room, location_index):
    i = -1
    start = 0
    for num, x in enumerate(subjects, start):
        if x.name == lesson_name:
            i = num

    if count % 2:
        timetables[0].days[((count - 1) // 2) // 6].lessons.append(Lesson(lessons_num, i, constraint, room, location_index))
    else:
        timetables[1].days[((count - 1) // 2) // 6].lessons.append(Lesson(lessons_num, i, constraint, room, location_index))


regex_string = '(?![12] гр|[12] п/г)(?:(?:(?:кр\\.* *)*[0-9]{1,2})[,.-] *)*(?:(?:кр\\.* *)*[0-9]{1,2} *)+'
# кр[\.\s]+[\d,]+


def split_lessons_and_weeks(lessons, weeks, type):
    lessons = re.sub('( *нед[\\. ]*)|( н[\\. ]*)', ' ', lessons)
    weeks = re.findall(regex_string, lessons)

    start = 0
    if isinstance(weeks, list) and len(weeks) > 1:
        lessons = lessons.strip(' ')
        lessons = re.split(regex_string, lessons)
        whitespace_remover(lessons)
        if isinstance(lessons, list) and len(lessons) < 2:
            lessons = ''.join(lessons)
            if ';' in lessons:
                lessons = lessons.split(';')
            elif '\n' in lessons:
                lessons = lessons.split('\n')
        whitespace_remover(lessons)

        for num, weeks_x in enumerate(weeks, start):
            if 'кр ' in weeks_x or 'кр. ' in weeks_x:
                type.append('кр')
                weeks_x = re.sub('(кр\\.* *)', '', weeks_x)
                weeks[num] = weeks_x
            else:
                type.append('н')
            weeks_x = re.split('(,|\\.)', weeks_x)
            start = 0
            for num_x, weeks_xx in enumerate(weeks_x, start):
                weeks_x[num_x] = re.sub('[,;\n ]', '', weeks_xx)
                weeks[num] = weeks_x
            ws_counter = 0
            for x in weeks_x:
                if x == '':
                    ws_counter += 1
            for _ in range(ws_counter):
                weeks_x.remove('')
            lessons[num] = lessons[num].strip(' ')
    else:
        if 'кр' in weeks or 'кр. ' in weeks:
            type = 'кр'
            weeks = re.sub('(кр\\.* *)', '', weeks)
        else:
            type = 'н'
        weeks = re.split('(,|\\.)', weeks[0])
        for num, weeks_x in enumerate(weeks, start):
            weeks_x = re.sub('[,;\n ]', '', weeks_x)
            weeks_x = weeks_x.strip(' ')
            weeks[num] = weeks_x
        ws_counter = 0
        for x in weeks_x:
            if x == '':
                ws_counter += 1
        for _ in range(ws_counter):
            weeks_x.remove('')

    if isinstance(lessons, list) and len(lessons) > 1:
        if None in lessons:
            lessons = list(filter(None, lessons))
        start = 0
        for num, x in enumerate(lessons, start):
            lessons[num] = re.sub(regex_string + '|[,;\n]', '', x)
    else:
        lessons = re.sub(regex_string + '|[,;\n]', '', lessons)
        lessons = lessons.strip(' ')

    whitespace_remover(weeks)
    whitespace_remover(lessons)
    return lessons, weeks, type


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


def parse_timetable(faculty_class):
    ex_data = pd.read_excel(faculty_class, sheet_name='Лист1', header=None)

    for i in range(359):  # 359
        print("i", i)
        try:
            ex_data[i][1]
        except:
            continue

        group = str(ex_data[i][1])
        if re.search('[А-Я]{4}-[0-9]{2}-[0-9]{2}', group):
            print('\n', group, '\n')
            count = 1
            lessons_number_counter = 1
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
            # </editor-fold>\
            for j in range(3, 75):
                # <editor-fold desc="Parsing information in excel">
                lessons = str(ex_data[i][j])
                print(lessons, j)
                teachers = str(ex_data[i + 2][j])
                type = []
                weeks = []
                lesson_type = str(ex_data[i + 1][j])
                room = str(ex_data[i + 3][j])
                link = str(ex_data[i + 2][j])
                location_index = 0
                # </editor-fold>

                if len(list(re.findall(regex_string, lessons))) > 0:
                    lessons_error = lessons
                    lessons, weeks, type = split_lessons_and_weeks(lessons, weeks, type)
                    room, location_index = format_room_and_get_location(room, location_index)
                    teachers = split_teachers(teachers)
                    lesson_type = whitespace_remover(lesson_type)

                    if not isinstance(lessons, list):
                        if not check_if_subject_exist(lessons, lesson_type, subjects):
                            subjects.append(Subject(lessons, teachers, lesson_type))
                        add_to_timetable(lessons_number_counter, count, subjects, timetables, lessons,
                                         Constraint(type, weeks), room, location_index)
                    else:
                        for x in range(len(lessons)):
                            lesson_type_temp = lesson_type
                            if isinstance(lesson_type, list) and len(lesson_type) == len(lessons):
                                lesson_type_temp = lesson_type[x]

                            if not check_if_subject_exist(lessons[x], lesson_type_temp, subjects):
                                if len(lessons) == len(teachers):
                                    subjects.append(Subject(lessons[x], teachers[x], lesson_type_temp))
                                else:
                                    subjects.append(Subject(lessons[x], teachers, lesson_type_temp))

                            if isinstance(room, list) and len(room) > 1 and isinstance(location_index, list) \
                                    and len(location_index) > 1:
                                add_to_timetable(lessons_number_counter, count, subjects, timetables, lessons[x],
                                                 Constraint(type[x], weeks[x]), room[x], location_index[x])
                            elif isinstance(room, list) and len(room) > 1:
                                add_to_timetable(lessons_number_counter, count, subjects, timetables, lessons[x],
                                                 Constraint(type[x], weeks[x]), room[x], location_index)
                            elif len(room) == 1:
                                add_to_timetable(lessons_number_counter, count, subjects, timetables, lessons[x],
                                                 Constraint(type[x], weeks[x]), room[0], location_index)
                            else:
                                add_to_timetable(lessons_number_counter, count, subjects, timetables, lessons[x],
                                                 Constraint(type[x], weeks[x]), room, location_index)

                else:
                    if not check_if_subject_exist(lessons, lesson_type, subjects):
                        subjects.append(Subject(lessons, teachers, lesson_type))
                    room, location_index = format_room_and_get_location(room, location_index)
                    add_to_timetable(lessons_number_counter, count,  subjects, timetables, lessons,
                                     Constraint(type, weeks), room, location_index)

                if count % 2:
                    lessons_number_counter += 1

                if lessons_number_counter == 7:
                    lessons_number_counter = 1
                count += 1

            combined = Combine(subjects, timetables)
            dump_to_json(combined, group)


parse_timetable('КБиСП 3 курс 1 сем.xlsx')
# download_timetable()
