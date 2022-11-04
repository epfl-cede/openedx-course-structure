# Open edX course structure

This is a simple course structute builder from Open edX course exported tar.gz file

## Usage

### CLI

``` pip install git+https://github.com/epfl-cede/openedx-course-structure.git```

```python -m openedx_course_structure ~/Downloads/ORG+DemoCourse+2022.tar.gz```

### Python

```
from openedx_course_structure import course_structure

print(course_structure.structure('~/Downloads/ORG+DemoCourse+2022.tar.gz'))
```
