import re
from docxtpl import DocxTemplate, RichText

category_list = ["experience","education","misc","others","skills"]
filename = 'cibles/cible.docx'
def write_cv( dict):

    template_values = {}
    document = DocxTemplate(filename)
    name = dict["name"]
    template_values["name"] = name
    template_values["phone"] = dict["phone"]

    template_values["email"] = dict["email"]

    for category in category_list:

        result = RichText((dict[category]))
        template_values[category] = result

    generated = "CV_" + name + ".docx"
    document.render(template_values)
    document.save("cibles/" + generated)
    return generated