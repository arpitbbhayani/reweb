from jinja2 import Environment, PackageLoader, select_autoescape

jenv = Environment(
    loader=PackageLoader("reweb"),
    autoescape=select_autoescape()
)


def render(name, **kwargs):
    return jenv.get_template(name).render(**kwargs)
