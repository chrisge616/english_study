from __future__ import annotations

from pathlib import Path
from string import Template
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from application.facade import EasyModeFacade
from ui_shell.routes import dispatch_action
from ui_shell.viewmodels import render_result_html


TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "index.html"


def _load_template() -> Template:
    return Template(TEMPLATE_PATH.read_text(encoding="utf-8"))


def create_app(*, facade: EasyModeFacade | None = None):
    active_facade = facade or EasyModeFacade()
    template = _load_template()

    def app(environ, start_response):
        method = environ.get("REQUEST_METHOD", "GET").upper()
        path = environ.get("PATH_INFO", "/")

        if method == "GET" and path == "/":
            return _respond_ok(start_response, template, None)

        if method == "POST" and path == "/action":
            content_length = int(environ.get("CONTENT_LENGTH") or "0")
            body = environ["wsgi.input"].read(content_length).decode("utf-8")
            params = parse_qs(body)
            action_name = params.get("action", [""])[0]
            path_value = params.get("path", [""])[0]
            review_markdown = params.get("review_markdown", [""])[0]
            result = dispatch_action(active_facade, action_name, path=path_value, review_markdown=review_markdown)
            return _respond_ok(start_response, template, result)

        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"Not Found"]

    return app


def _respond_ok(start_response, template: Template, result) -> list[bytes]:
    html = template.substitute(result_panel=render_result_html(result))
    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
    return [html.encode("utf-8")]


def run_server(*, host: str = "0.0.0.0", port: int = 8000) -> None:
    app = create_app()
    with make_server(host, port, app) as httpd:
        print(f"Easy Mode UI shell running at http://{host}:{port}")
        httpd.serve_forever()
