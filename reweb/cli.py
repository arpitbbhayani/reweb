import typer
import reweb

app = typer.Typer()

@app.command("run")
def run():
    reweb.generate()


@app.command("init")
def init():
    reweb.init()


@app.command("version")
def version():
    print(reweb.version)
