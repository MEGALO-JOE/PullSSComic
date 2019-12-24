import os

for top, dirs, files in os.walk("./SSComic/data"):
    print("{}: {}".format(top,len(files)))