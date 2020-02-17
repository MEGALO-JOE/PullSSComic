import os

for top, dirs, files in os.walk("./SSComic/naruto"):
    print("{}: {}".format(top,len(files)))