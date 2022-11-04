from os import path
import tempfile
import tarfile
import xml.etree.ElementTree as ET

class OpenEdxCourseStructureException(BaseException):
    pass

def structure(course_file):
    def _children(root, name):
        result = []
        roots = []

        for child in root.findall(name):
            filename = tmpdir + '/course/%s/%s.xml' % (child.tag, child.attrib['url_name'])
            if path.exists(filename):
                root = ET.parse(filename).getroot()
                result.append({
                    'id': child.attrib['url_name'],
                    'type': child.tag,
                    'name': root.attrib['display_name'] if 'display_name' in root.attrib else "",
                })
                roots.append(root)
        return result, roots

    org, session, run = path.basename(course_file).split('.')[0].split('+')
    structure = {}
    with tarfile.open(course_file) as fp:
        with tempfile.TemporaryDirectory() as tmpdir:
            fp.extractall(tmpdir)

            # filter xml files only
            xml_files = list(filter(lambda name: name.endswith('.xml'), fp.getnames()))

            # find entry point file
            ep = '/course/course/%s.xml' % run
            if '.%s' % ep not in xml_files:
                raise OpenEdxCourseStructureException("Course entry point <%s> not found" % ep)

            root = ET.parse(tmpdir + ep).getroot()
            structure = {
                'name': root.attrib['display_name'],
                'children': [],
            }
            chapters, chapter_roots = _children(root, 'chapter')
            structure['children'] = chapters

            for chapter in structure['children']:
                sequentials, sequential_roots = _children(chapter_roots.pop(0), 'sequential')
                chapter['children'] = sequentials

                for sequential in chapter['children']:
                    verticals, vertical_roots = _children(sequential_roots.pop(0), 'vertical')
                    sequential['children'] = verticals

                    for unit in sequential['children']:
                        units, unit_roots = _children(vertical_roots.pop(0), "*")
                        unit['children'] = units

        fp.close()

    return structure
