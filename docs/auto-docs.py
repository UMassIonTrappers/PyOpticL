import re

layout_file = "".join(open("PyOptic/freecadOptics/layout.py", 'r').readlines())
optomech_file = "".join(open("PyOptic/freecadOptics/optomech.py", 'r').readlines())
docs = open("docs/README.md", 'w')

docs.write('''# Auto-Generated Documentation  \n''')

docs.write('''## Layout  \n''')

classes = re.findall("class ([^ ]*?):\n +\'\'\'(.*?)\'\'\'", layout_file, re.DOTALL)
functions = re.findall("def (?!__)([^ ]*?)\(self.*?\):\n +\'\'\'(.*?)\'\'\'", layout_file, re.DOTALL)

print(functions[0])

for i in classes:
    name = i[0]
    docstring = i[1].replace("\n", "  \n")
    docs.write("### %s\n"%(name))
    docs.write("%s\n"%(docstring))

for i in functions:
    name = i[0]
    docstring = i[1].replace("\n", "  \n")
    docs.write("### baseplate.%s\n"%(name))
    docs.write("%s\n"%(docstring))

docs.write('''## Optomech  \n''')

classes = re.findall("class ([^ ]*?):\n +\'\'\'(.*?)\'\'\'", optomech_file, re.DOTALL)

for i in classes:
    name = i[0]
    docstring = i[1].replace("\n", "  \n")
    docs.write("### %s\n"%(name))
    docs.write("%s\n"%(docstring))

docs.close()