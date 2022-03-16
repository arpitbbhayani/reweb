import os
import shutil
import tempfile

import sass

from reweb.templates import render
from reweb.site import read_site, store_site
from reweb.version import next_version


def __generate_css(site):
    with tempfile.TemporaryDirectory() as tempdir:
        tempdir = "/tmp"
        path_bulma = os.path.join(tempdir, "bulma.sass")
        with open(path_bulma, "w") as fp:
            fp.write(render("bulma.sass"))
        with open("final.css", "w") as fp:
            css_template = render("custom.jinja3.scss", path_bulma=path_bulma)
            fp.write(css_template)
            print(css_template)
            with open("final.css", "r") as fp1:
                content = fp1.read()
                print(content)
                print(sass.compile(string=content))


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
