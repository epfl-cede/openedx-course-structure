from os import path
import json
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
                res = {
                    'id': child.attrib['url_name'],
                    'type': child.tag,
                    'name': root.attrib['display_name'] if 'display_name' in root.attrib else "",
                }
                if child.tag == "video":
                    if 'edx_video_id' in root.attrib:
                        res['edx_video_id'] = root.attrib['edx_video_id']
                    if 'html5_sources' in root.attrib:
                        res['html5_sources'] = json.loads(root.attrib['html5_sources'])
                    if 'youtube_id_1_0' in root.attrib:
                        res['youtube_id_1_0'] = root.attrib['youtube_id_1_0']
                result.append(res)
                roots.append(root)
        return result, roots

    structure = {}
    with tarfile.open(course_file) as fp:
        with tempfile.TemporaryDirectory() as tmpdir:
            fp.extractall(tmpdir)

            ep = f'{tmpdir}/course/course.xml'
            if not path.exists(ep):
                raise OpenEdxCourseStructureException("Course main file <%s> not found" % ep)

            root = ET.parse(ep).getroot()
            url_name = root.attrib["url_name"]

            # entry point file
            ep = f'{tmpdir}/course/course/{url_name}.xml'
            if not path.exists(ep):
                raise OpenEdxCourseStructureException("Course entry point <%s> not found" % ep)

            root = ET.parse(ep).getroot()
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
