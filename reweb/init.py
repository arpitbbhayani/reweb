import os

import typer

from reweb.templates import render
from reweb.site import Site


def init():
    configfile = "reweb.json"

    if os.path.exists(configfile):
        raise Exception("cannot reinitialize reweb")

    name = typer.prompt("Name of the site?")
    description = name
    baseurl = typer.prompt("Baseurl of the site?")
    author = typer.prompt("Name of the author?")
    keywords = []

    config = render(
        "config.jinja3.json",
        site=Site(
            name=name,
            description=description,
            baseurl=baseurl,
            author=author,
            keywords=keywords
        )
    )
    
    with open("reweb.json", "w") as fp:
        fp.write(config)
