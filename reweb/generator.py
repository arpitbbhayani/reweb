import os
import json
import gzip
import shutil
import tempfile
from hashlib import md5
from distutils.dir_util import copy_tree
from distutils.file_util import copy_file
from datetime import datetime

import sass
import frontmatter
import markdown
from markdown.extensions import fenced_code
import requests, zipfile

from reweb.templates import render, render_by_name, render_raw
from reweb.site import read_site, store_site
from reweb.version import next_version

import xml.etree.cElementTree as ET

PAGES = []

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
        
        with open(os.path.join(tempdir, "minify.js"), "w") as fp:
            fp.write(render_by_name("minify.jinja3.js"))

        os.system("node " + os.path.join(tempdir, "minify.js"))

        with open("dist/static/style.min.css", "r") as fp:
            site.data["style"] = fp.read()


def __generate_bundle(site):
    site.version = next_version(site)
    store_site(site)

    # TODO: ZIP
    shutil.make_archive(f"{site.name}", 'zip', "dist")


def __generate_distpath(filepath, filename=None):
    relpath = os.path.relpath(filepath, "pages")
    distpath = os.path.join("dist/", relpath.replace(".md", ".html"))
    if filename:
        distpath = os.path.dirname(distpath) + "/" + filename
    try:
        os.makedirs(os.path.dirname(distpath))
    except FileExistsError:
        pass

    url = distpath.replace(".md", ".html").replace(".html", "").replace("dist/", "")
    if url.endswith("/index"):
        url = url.replace("/index", "")
    print(url)
    return distpath, url


def __setup_dist():
    if not os.path.exists("dist"):
        os.mkdir("dist")

    copy_tree("root", "dist")


def __generate_page_md(md_filepath, site):
    page = frontmatter.load(md_filepath)
    content = markdown.markdown(page.content, extensions=[fenced_code.FencedCodeExtension()])
    distpath, url = __generate_distpath(md_filepath)
    meta = page.to_dict()
    output = render(site=site, content=content, type="md", seo={
        "title": meta["title"],
        "description": meta["description"],
        "img": meta["image"],
        "url": "https://arpitbhayani.me/blogs/" + meta["id"],
    }, page=meta)
    # create the file
    with open(distpath, "w") as fp:
        fp.write(output)

    PAGES.append(url)


def __generate_page_html(html_filepath, site):
    with open(html_filepath, "r") as fp:
        content = fp.read()

    seo = {}
    if "===" in content:
        seo = json.loads(content.split("===")[0])
        content = content.split("===")[1]

    distpath, url = __generate_distpath(html_filepath)

    output = render(site=site, content=content, seo=seo)

    # create the file
    with open(distpath, "wb") as fp:
        # fp.write(gzip.compress(output.encode()))
        fp.write(output.encode())

    PAGES.append(url)


def __generate_pattern_json(pattern_filepath, site):
    name = os.path.basename(pattern_filepath)[1:].split(".")[0]
    with open(pattern_filepath, "r") as fp:
        meta = json.loads(fp.read())

    source = meta["source"]
    template = meta["template"]
    pagepath_template = meta["pagepath_template"]

    with open(source, "r") as fp:
        for item in json.loads(fp.read()):
            kwargs = { name: item, "site": site }
            content = render_by_name(template, **kwargs)
            seo_url = render_raw(meta["seo"]["url"], **item)
            output = render(site=site, content=content, seo={
                "title": render_raw(meta["seo"]["title"], **item),
                "description": render_raw(meta["seo"]["description"], **item),
                "url": seo_url,
                "img": render_raw(meta["seo"]["img"], **item),
            })
            
            distpath, url = __generate_distpath(
              pattern_filepath,
              filename=render_raw(pagepath_template, **item)
            )

            # create the file
            with open(distpath, "w") as fp:
                fp.write(output)
            
            PAGES.append(seo_url)


def __generate_pages(site):
    basepath = "./pages"
    for (root, _, filepaths) in os.walk(basepath):
        for path in filepaths:
            filepath = os.path.join(root, path)
            # if "competitive-programming-solutions" in filepath:
            #     continue
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
    
    if os.path.exists("./templates/robots.txt"):
        copy_file("./templates/robots.txt", "dist/robots.txt")


def __generate_sitemap(site):
    schema_loc = ("http://www.sitemaps.org/schemas/sitemap/0.9 "
                  "http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd")

    root = ET.Element("urlset")
    root.attrib['xmlns:xsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
    root.attrib['xsi:schemaLocation'] = schema_loc
    root.attrib['xmlns'] = "http://www.sitemaps.org/schemas/sitemap/0.9"
    
    dt = datetime.now().strftime("%Y-%m-%d")  # <-- Get current date and time.

    tree = ET.ElementTree(root)

    doc = ET.SubElement(root, "url")
    ET.SubElement(doc, "loc").text = site.baseurl
    ET.SubElement(doc, "lastmod").text = dt
    ET.SubElement(doc, "changefreq").text = 'weekly'
    ET.SubElement(doc, "priority").text = "1.0"

    for url in PAGES:
        doc = ET.SubElement(root, "url")
        ET.SubElement(doc, "loc").text = (f"{site.baseurl}{url}")
        ET.SubElement(doc, "lastmod").text = dt
        ET.SubElement(doc, "changefreq").text = 'weekly'
        ET.SubElement(doc, "priority").text = "0.6"

    tree.write("dist/sitemap.xml",
                encoding='utf-8', xml_declaration=True)


def generate():
    site = read_site()
    __setup_dist()
    __copy_static()
    __generate_pages(site)
    __generate_css(site)
    __generate_pages(site)
    __generate_sitemap(site)
    __generate_bundle(site)
