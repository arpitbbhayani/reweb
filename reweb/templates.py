import os
import importlib
import shutil
import tempfile
from uuid import uuid4
from distutils.dir_util import copy_tree
from jinja2 import Environment, FileSystemLoader


with tempfile.TemporaryDirectory() as tempdir:
    tempdir = "/tmp/test1"
    spec = importlib.util.find_spec("reweb")
    pkgdir = next(iter(spec.submodule_search_locations))  # type: ignore
    template_root = os.path.join(pkgdir, "templates")
    copy_tree(template_root, tempdir)
    copy_tree("./blocks", tempdir + "/blocks")
    copy_tree("./templates", tempdir)
    jenv = Environment(
        extensions=['jinja_markdown.MarkdownExtension'],
        loader=FileSystemLoader(tempdir),
    )


def render(site, content, type="html", page=None):
    name = uuid4().hex
    tpath = os.path.join(tempdir, name)

    if type == "md":
        content = jenv.get_template("blog.html").render(content=content, page=page, site=site)

    with open(tpath, "w") as fp:
        template = "{% extends 'layout.jinja3.html' %}\n" + "{% block content %}" + f"{ content }" + "{% endblock %}"
        fp.write(template)
    print("name", name)
    return jenv.get_template(name).render(site=site, content=content)


def render_by_name(name, **kwargs):
    return jenv.get_template(name).render(**kwargs)
