import fitz
import io, os
from operator import itemgetter
from itertools import groupby
from difflib import SequenceMatcher

folder = "/home/badr/ematchit/ematchitBackend/drop/"

def extract_blocs(filename):
    doc = fitz.open(filename)
    page = doc[0]
    opt = "words"
    mywords = page.getText("words", flags = fitz.TEXT_INHIBIT_SPACES)
    mywords.sort(key=itemgetter(3, 0))  # sort by y1, x0 of word rectangle

    # build word groups on same line
    grouped_lines = groupby(mywords, key=itemgetter(3))
    print (grouped_lines)
    lines = []
    for _,words_in_line in grouped_lines:
        print("\n" * 10)
        for i, w in enumerate(words_in_line):
            print(w)
            if i == 0:  # store first word
                x0, y0, x1, y1, word = w[:5]

                continue
            word = word + ' ' + w[4]
        lines.append([x0,y0,word])





def flags_decomposer(flags):
    """Make font flags human readable."""
    l = []
    if flags & 2 ** 0:
        l.append("superscript")
    if flags & 2 ** 1:
        l.append("italic")
    if flags & 2 ** 2:
        l.append("serifed")
    else:
        l.append("sans")
    if flags & 2 ** 3:
        l.append("monospaced")
    else:
        l.append("proportional")
    if flags & 2 ** 4:
        l.append("bold")
    return ", ".join(l)



def get_text_font(blocks, text):
    for b in blocks:  # iterate through the text blocks
        for l in b["lines"]:
            for s in l["spans"]:
                if SequenceMatcher(None, s["text"].replace(" ","").lower(), text.replace(" ","").lower()).ratio() > 0.9 :
                    return s["font"], s["size"], s["color"]
    return None, None, None

def find_same_fonts(filename, text):
    doc = fitz.open(filename)
    values = []
    for page in doc:
        blocks = page.getText("dict", flags=11)["blocks"]
        font, size, color = get_text_font(blocks, text)
        if font == None:
            continue

        headers = []
        origines = []

        for b in blocks:  # iterate through the text blocks
            for l in b["lines"]:
                for s in l["spans"]:
                    if s["font"] == font and s["size"] == size and s["color"] == color:
                        origines.append(s["origin"][-1])
        origines = list(dict.fromkeys(origines))
        new_dict = {}
        for key in origines:
            new_dict[key] = []

            for b in blocks:  # iterate through the text blocks
                for l in b["lines"]:
                    for s in l["spans"]:
                        if s["origin"][-1] == key:
                            my_list = [s["text"], s["origin"][0], s["origin"], s["bbox"]]
                            new_dict[key].append(my_list)


        for key in new_dict.keys():
            val = new_dict[key]
            line = ''
            val.sort(key=lambda x: x[1])
            for value in val:
                line = line + value[0]
            values.append(line)
    print(values)
    return values


def test_fonts(filename):
    doc = fitz.open(filename)
    page = doc[0]

    # read page text as a dictionary, suppressing extra spaces in CJK fonts
    blocks = page.getText("dict", flags=11)["blocks"]
    for b in blocks:  # iterate through the text blocks
        for l in b["lines"]:  # iterate through the text lines
            # print(l["spans"][:11])
            # print(len(l["spans"]))
            # print("\n"*5)
            for s in l["spans"]:  # iterate through the text spans
                #print("")
                font_properties = "Font: '%s' (%s), size %g, color #%06x" % (
                    s["font"],  # font name
                    flags_decomposer(s["flags"]),  # readable font flags
                    s["size"],  # font size
                    s["color"],  # font color
                )
                # if s["color"] == 8392463 :
                #     print (s["text"])
                #     print(s["origin"])
                #     print(s["bbox"])
                #print("Text: '%s'" % s["text"])  # simple print of text
                #print(font_properties)




if __name__ == '__main__':
    #extract_blocs('C:\\Users\\e3blahsi\\Documents\\CV\\CV Fériel KALAI.pdf', 'pdf')
    #extract_blocs('C:\\Users\\e3blahsi\\Documents\\CV\\CV_Armel Guemto.pdf', 'pdf')
    #extract_blocs('C:\\Users\\e3blahsi\\Documents\\CV\\Noor HADDADI CV.pdf', 'pdf')
    find_same_fonts(folder + 'toto.pdf', "education")