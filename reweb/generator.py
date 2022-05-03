import os
import json
import tempfile
from hashlib import md5
from distutils.dir_util import copy_tree

import sass
import frontmatter
import markdown
from markdown.extensions import fenced_code
import requests, zipfile

from reweb.templates import render, render_by_name
from reweb.site import read_site, store_site
from reweb.version import next_version


def __generate_css(site):
    with tempfile.TemporaryDirectory() as tempdir:
        tempdir = "/tmp/test3"
        resp = requests.get("https://github.com/jgthms/bulma/releases/download/0.9.3/bulma-0.9.3.zip")
        with open(os.path.join(tempdir, "bulma.zip"), "wb") as fp:
            fp.write(resp.content)

        zf = zipfile.ZipFile(os.path.join(tempdir, "bulma.zip"))
        zf.extractall(tempdir)

        if not os.path.exists("dist/static/"):
            os.mkdir("dist/static/")
        
        with open("assets/style.scss") as fp:
            user_style = fp.read()

        with open(os.path.join(tempdir, "custom.scss"), "w") as fp:
            fp.write(render_by_name("bulma.jinja3.scss", user_style=user_style))

        with open("dist/static/style.css", "w") as fp:
            fp.write(sass.compile(filename=f'{tempdir}/custom.scss'))


def __generate_bundle(site):
    site.version = next_version(site)
    store_site(site)

    # TODO: ZIP
    # shutil.make_archive(f"{site.name}-{site.version}", 'zip', "dist")


def __generate_distpath(filepath, filename=None):
    relpath = os.path.relpath(filepath, "pages")
    distpath = os.path.join("dist/", relpath.replace(".md", ".html"))
    if filename:
        distpath = os.path.dirname(distpath) + "/" + filename
    try:
        os.makedirs(os.path.dirname(distpath))
    except FileExistsError:
        pass
    return distpath


def __setup_dist():
    if not os.path.exists("dist"):
        os.mkdir("dist")


def __generate_page_md(md_filepath, site):
    page = frontmatter.load(md_filepath)
    content = markdown.markdown(page.content, extensions=[fenced_code.FencedCodeExtension()])
    distpath = __generate_distpath(md_filepath)
    output = render(site=site, content=content, type="md", page=page.to_dict())
    # create the file
    with open(distpath, "w") as fp:
        fp.write(output)


def __generate_page_html(html_filepath, site):
    with open(html_filepath, "r") as fp:
        content = fp.read()

    distpath = __generate_distpath(html_filepath)

    output = render(site=site, content=content)

    # create the file
    with open(distpath, "w") as fp:
        fp.write(output)


def __generate_pattern_json(pattern_filepath, site):
    name = os.path.basename(pattern_filepath)[1:].split(".")[0]
    with open(pattern_filepath, "r") as fp:
        meta = json.loads(fp.read())

    source = meta["source"]
    template = meta["template"]
    basepath_attr = meta["basepath_attr"]

    with open(source, "r") as fp:
        for item in json.loads(fp.read()):
            kwargs = { name: item, "site": site }
            content = render_by_name(template, **kwargs)
            output = render(site=site, content=content)
            
            distpath = __generate_distpath(pattern_filepath, filename=f"{item[basepath_attr]}.html")

            # create the file
            print(distpath)
            with open(distpath, "w") as fp:
                fp.write(output)


def __generate_pages(site):
    basepath = "./pages"
    for (root, _, filepaths) in os.walk(basepath):
        for path in filepaths:
            filepath = os.path.join(root, path)
            if path.endswith(".md"):
                __generate_page_md(filepath, site)
            elif path.endswith(".html"):
                __generate_page_html(filepath, site)
            elif path.startswith("_") and path.endswith(".json"):
                __generate_pattern_json(filepath, site)
            else:
                raise Exception("unsupported page: " + path)


def __copy_static():
    if os.path.exists("./static"):
        copy_tree("./static", "dist/static")

def generate():
    site = read_site()
    __setup_dist()
    __generate_css(site)
    __generate_bundle(site)
    __copy_static()
    __generate_pages(site)
