import io
from pdfminer3.converter import TextConverter, PDFPageAggregator
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfpage import PDFPage
from pdfminer3.layout import LAParams, LTTextBox, LTTextLine
from pdfminer3.high_level import  extract_text_to_fp
from difflib import SequenceMatcher
from langdetect import detect
import subprocess, os, re
#from tools.fitz_extracter import find_same_fonts
from math import sqrt
from string import printable

blocs_origin_en = dict()
blocs_origin_en['xp'] = ['professionalexperience','experiences', 'experience',
                      'workexperience', 'work', 'workexperiences', 'jobs', 'clients']
blocs_origin_en['education'] = ['diplomas', 'education', 'schools',  'diplomas', 'etudes']
blocs_origin_en['skills'] = ['skills', 'itskills', 'othercompetences', 'competences',
                             'other skills', 'skillsandcertification', 'certification', 'keyskills'
                             'skills&certification',
                             'programming',
                             'softwareskills']
blocs_origin_en['others'] = ['other', 'hobbies', 'misc', 'interests', 'activities',
                             'miscellaneous','activitiesandinterests', 'languages', 'extracurricularactivities',
                             'activities&interests', 'additional']


blocs_origin_fr = dict()
blocs_origin_fr['xp'] = ['expériencesprofessionnelles', 'experiencesprofessionnelles', 'clients']
blocs_origin_fr['education'] = ['diplomas', 'cursusuniversitaire',  'etudes', 'formation', 'diplomes',
                                'formationacadémique']
blocs_origin_fr['skills'] = ['competencestechniques', 'compétences','certifications','logiciels','informatique'
                             ,'programmation'
                             , 'Domainesdecompétences']
blocs_origin_fr['others'] = ["centres dinterets", "interets", "centres d'interet", 'misc', 'miscellaneous'
                             "langues",'interetsetlangues']

def print_iter(lobj):
    print(str(lobj))
    try:
        for toto in lobj:
            print_iter(toto)
    except:
        print(str(lobj) + "is not iterable")

def find_phone(text):

    regex_phone = '((\+|00)33|0)[0-9]{9,10}'
    match_phone = re.search(regex_phone, text.replace(" ", "").replace("-", "").replace("(", "").replace(")", ""))

    if match_phone:
        return match_phone.group(0)
    else:
        return ''

def find_email(text):
    regex_email = '[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.(com|fr)'
    match_phone = re.search(regex_email, text.lower())
    if match_phone:
        return match_phone.group(0)
    else:
        return ''

def compute_distance(origin, line):
    x0 = (line[0] - origin[0]) ** 2
    x1 = (line[2] - origin[2]) ** 2
    diff_x = line[0] - origin[2]
    y = line [1] - origin[1]
    if y < 0 :
        return 10**6
    y0 = (2*y)**2
    return sqrt(y0 + x0) + sqrt(y0 + x1)

def compute_distance_to_list(origin_list, line):
    distances = []
    for value in origin_list:
        distances.append(compute_distance(value,line))



def is_similar_to_origin(a, b):
    return SequenceMatcher(None, a, b).ratio() > 0.8

def get_blocs(origines, lines):
    blocs = dict()
    list_of_keys = []
    extended_origines = {}
    extended_origines_debut = {}
    extended_blocs = {}
    origines_to_modified = {}
    for value in origines:
        blocs[value] = []
        origines_to_modified[value] = []
        for key in origines[value]:
            extended_origines[key[-1]] = key + [2]
            extended_origines_debut[key[-1]] = key[0]
            extended_blocs[key[-1]] = []
            list_of_keys.append(key[-1])
            origines_to_modified[value].append(key[-1])

    blocs['nocat'] = []
    for line in lines:
        distances = []
        for key in list_of_keys:
            distances.append(compute_distance(extended_origines[key], line))
        if min(distances) >= 10 ** 6:
            blocs['nocat'].append(line[-1])
        #elif min(distances) == 0:
         #   continue
        else :
            min_index = distances.index(min(distances))
            extended_blocs[list_of_keys[min_index]].append(line[-1])
            old = extended_origines[list_of_keys[min_index]]
            extended_origines[list_of_keys[min_index]] = [old[0] + (line[0] - old[0])/old[4],
                                                          old[1] + (line[1] - old[1])/old[4],
                                                          old[2] + (line[2] - old[2])/old[4],
                                                            line[-1],
                                                           old[4] + 1]

    for bloc_key in origines_to_modified:
        for val in extended_blocs:
            if val in origines_to_modified[bloc_key]:
                blocs[bloc_key] = blocs[bloc_key] + extended_blocs[val]

    for bl in blocs:
        if (bl == 'xp' or bl == 'education') and len(blocs[bl]) > 2:
            blocs[bl] = blocs[bl][1:]
    return blocs


def get_blocs_origins(langage):
    if langage == 'fr':
        return blocs_origin_fr
    if langage == 'en':
        return blocs_origin_en
    raise NotImplementedError('langage not implemented')

def extract_exact_origin_from_lines(lines, langage):
    origins_coordinates = dict()
    blocs_origin = get_blocs_origins(langage)

    keys = list(blocs_origin.keys())
    for key in keys:
        origins_coordinates[key] = None
    for line in lines:
        text = line[-1].strip().lower()
        for key in keys:
            if not origins_coordinates[key]:
                if text in blocs_origin[key]:
                    origins_coordinates[key] = line
    return origins_coordinates

def extract_origin_from_lines(lines, langage):
    origins_coordinates = dict()

    blocs_origin = get_blocs_origins(langage)
    keys = list(blocs_origin.keys())
    for key in keys:
        origins_coordinates[key] = []
    for line in lines:
        text = line[-1].replace(" ", "").replace(":", "")
        text = text.rstrip("\n").lower()
        for key in keys:
            for val in blocs_origin[key]:
                if is_similar_to_origin(val, text):
                    #print (val + "   val et txt  " + text)
                    if not line in origins_coordinates[key]:
                        origins_coordinates[key].append(line)

    #print(origins_coordinates)
    return origins_coordinates

def extract_lines_from_pdf(pdf_path):
    fp = open(pdf_path, 'rb')
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    pages = PDFPage.get_pages(fp)
    lines = []
    page_margin = 0
    txt = ''
    phone = ''
    email = ''
    for page in pages:
        page_lines = []
        ordonates = []
        #print('Processing next page...')
        interpreter.process_page(page)
        layout = device.get_result()
        for lobj1 in layout:
            #print_iter(lobj)


            if isinstance(lobj1, LTTextBox):
                for lobj in lobj1 :
                    if lobj.get_text().strip() :
                        x0, y0, x1, y1, text = lobj.bbox[0], lobj.bbox[1],lobj.bbox[2] , lobj.bbox[3], lobj.get_text()
                        #print('At %r =>: %s' % ((x0, y0, x1, y1), text))
                        ordonates.append(y0)
                        if text[0] == "o":
                            if len(text) < 4:
                                continue
                            else:
                                text = text[1:]
                        if phone == '' and email == '':
                            phone = find_phone(text)
                            email = find_email(text)
                            if phone != '' or email != '':
                                continue
                        if email == '':
                            email = find_email(text)
                            if email != '':
                                continue
                        if phone == '':
                            phone = find_phone(text)
                            if phone != '':
                                continue

                        text = ''.join(list(filter(lambda x: x in printable + "éè£€êô’", text)))

                        page_lines.append([x0, y0 ,x1, text])
                        txt = txt + text
        if ordonates :
            max_page = max(ordonates)
            page_lines[:] = [[x[0], max_page - x[1] + page_margin, x[2], x[3]] for x in page_lines]
            page_margin += max_page + 1
            page_lines.sort(key=lambda x: x[1])

            lines = lines + page_lines
    language = detect(txt)

    return lines, language, phone, email



def process_pdf(filename, look_for_similar_fonts = False):
    lines, language, phone, email = extract_lines_from_pdf(filename)
    print(email)
    print(phone)

    origines = extract_origin_from_lines(lines, language)
    keys = list(origines.keys())
    additional_origines = []
    for key in keys:
        if origines[key] == []:
            #print (key + 'not found')
            del origines[key]
        else:
            if look_for_similar_fonts:
                for value in origines[key]:
                    similar_origines = []#find_same_fonts(filename, value[-1].rstrip("\n"))
                    additional_origines = additional_origines + similar_origines

    blocs = get_blocs(origines, lines)
    for key in keys + ['nocat']:
        if key not in blocs or blocs[key] == []:
            blocs[key] = ''
        else:
            blocs[key] = ''.join(blocs[key])
    blocs["phone"] = phone
    blocs["email"] = email
    return blocs



def extract_blocs(filename, extension):
    #with open(filename, 'r') as f:
     #   data = f.read()

    if extension == 'pdf':
        #print('in pdf extension')

        blocs = process_pdf(filename)

    elif extension == 'docx':
        blocs = extract_blocs_from_word(filename)
    else :
        blocs = {}
    return blocs

def extract_blocs_from_word(filename):

    folder = os.path.join(os.getcwd(), 'drop/')
    args = ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', folder, filename]

    process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pdf_name = filename.rsplit('.', 1)[0] + '.pdf'
    print(filename)

    return process_pdf(pdf_name)


if __name__ == '__main__':

    folder = "/home/badr/ematchit/ematchitBackend/drop/"
    filename = folder + 'test.pdf'
    extract_blocs(filename, filename.rsplit('.', 1)[1].lower())


