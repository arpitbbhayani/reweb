import typer
import reweb
from reweb.site import read_site

app = typer.Typer()

@app.command("build")
def build():
    reweb.generate()


@app.command("init")
def init():
    reweb.init()


@app.command("version")
def version():
    site = read_site()
    print(site.version)
