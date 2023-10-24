import re

optomech_file = "".join(open("Mod/Optics/freecadOptics/optomech.py", 'r').readlines())

matches = re.findall("class ([^ ]*?):\n +\'\'\'(.*?)\'\'\'", optomech_file, re.DOTALL)

optomech_docs = open("docs/README.md", 'w')

optomech_docs.write('''
Testing
''')

for i in matches:
    class_name = i[0]
    docstring = i[1].replace("\n", "  \n").replace("\n    ", "\n")
    optomech_docs.write("### %s\n"%(class_name))
    optomech_docs.write("%s\n"%(docstring))

optomech_docs.close()