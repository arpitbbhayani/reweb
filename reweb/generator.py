import os

from reweb.templates import render


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


def __generate_page_md(md_filepath):
    distpath = __generate_distpath(md_filepath)

    output = render("layout.jinja3.html")

    # create the file
    with open(distpath, "w") as fp:
        fp.write(output)


def __generate_pages():
    basepath = "./pages"
    for (root, _, filepaths) in os.walk(basepath):
        for path in filepaths:
            filepath = os.path.join(root, path)
            if path.endswith(".md"):
                __generate_page_md(filepath)
            else:
                raise Exception("unsupported page: " + path)

def generate():
    __setup_dist()
    __generate_pages()
