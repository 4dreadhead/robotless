from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


class HtmlPages:
    def __init__(self, app):
        self.app = app
        self.templates = Jinja2Templates(directory="templates")

        self.register_handlers()

    def register_handlers(self):
        self.app.get("/analyze", response_class=HTMLResponse)(self.read_analyze)
        self.app.get("/share", response_class=HTMLResponse)(self.read_share)

    async def read_analyze(self, request: Request):
        return self.templates.TemplateResponse("analyze.html", {"request": request})

    async def read_share(self, request: Request):
        return self.templates.TemplateResponse("share.html", {"request": request})
