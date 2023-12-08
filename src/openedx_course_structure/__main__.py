import sys
import json

from course_structure import structure


def usage():
    print("Usage: %s course.tar.gz" % sys.argv[0])
    exit(1)


if (__name__ == '__main__'):
    if len(sys.argv) <= 1:
        usage()

    structure = structure(sys.argv[1])
    print(json.dumps(structure, sort_keys=False, indent=4))
