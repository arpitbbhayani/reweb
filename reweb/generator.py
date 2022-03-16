import os
import shutil
import tempfile

import sass
import requests, zipfile

from reweb.templates import render
from reweb.site import read_site, store_site
from reweb.version import next_version


def __generate_css(site):
    with tempfile.TemporaryDirectory() as tempdir:
        tempdir = "/tmp/test"
        resp = requests.get("https://github.com/jgthms/bulma/releases/download/0.9.3/bulma-0.9.3.zip")
        print(tempdir)
        with open(os.path.join(tempdir, "bulma.zip"), "wb") as fp:
            fp.write(resp.content)

        zf = zipfile.ZipFile(os.path.join(tempdir, "bulma.zip"))
        zf.extractall(tempdir)

        if not os.path.exists("dist/static/"):
            os.mkdir("dist/static/")
        
        with open("assets/style.scss") as fp:
            user_style = fp.read()

        with open(os.path.join(tempdir, "custom.scss"), "w") as fp:
            fp.write(render("bulma.jinja3.scss", user_style=user_style))

        with open("dist/static/style.css", "w") as fp:
            fp.write(sass.compile(filename=f'{tempdir}/custom.scss'))


def __generate_bundle(site):
    site.version = next_version(site)
    store_site(site)

    shutil.make_archive(f"{site.name}-{site.version}", 'zip', "dist")


def __generate_distpath(filepath):
    relpath = os.path.relpath(filepath, "pages")
    distpath = os.path.join("dist/", relpath.replace(".md", ".html"))
    try:
        os.makedirs(os.path.dirname(distpath))
    except FileExistsError:
        pass
    return distpath


def __setup_dist():
    if not os.path.exists("dist"):
        os.mkdir("dist")


def __generate_page_md(md_filepath, site):
    distpath = __generate_distpath(md_filepath)

    output = render("layout.jinja3.html", site=site)

    # create the file
    with open(distpath, "w") as fp:
        fp.write(output)


def __generate_page_html(html_filepath, site):
    with open(html_filepath, "r") as fp:
        content = fp.read()

    distpath = __generate_distpath(html_filepath)

    output = render("layout.jinja3.html", site=site, content=content)

    # create the file
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
            else:
                raise Exception("unsupported page: " + path)

def generate():
    site = read_site()
    __setup_dist()
    __generate_css(site)
    __generate_pages(site)
    __generate_bundle(site)
