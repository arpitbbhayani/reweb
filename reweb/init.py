import os

import typer

from reweb.templates import render
from reweb.site import Site


def init():
    configfile = "reweb.json"
    if not os.path.exists(configfile):
        name = typer.prompt("Name of the site?")
        description = name
        baseurl = typer.prompt("Baseurl of the site?")
        author = typer.prompt("Name of the author?")
        keywords = []

        content = render(
            "config.jinja3.json",
            site=Site(
                name=name,
                description=description,
                version="0.0.1",
                baseurl=baseurl,
                author=author,
                keywords=keywords
            )
        )

        with open("reweb.json", "w") as fp:
            fp.write(content)

    if not os.path.exists("assets"):
        os.mkdir("assets")

    if not os.path.exists("assets/style.scss"):
        content = render("style.jinja3.scss")
        with open("assets/style.scss", "w") as fp:
            fp.write(content)

    if not os.path.exists("pages"):
        os.mkdir("pages")

    if not os.path.exists("pages/index.html"):
        content = render("index.jinja3.html")
        with open("pages/index.html", "w") as fp:
            fp.write(content)

    if not os.path.exists(".gitignore"):
        content = render("gitignore.jinja3.html")
        with open(".gitignore", "w") as fp:
            fp.write(content)
