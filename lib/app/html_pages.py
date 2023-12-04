import os
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
load_dotenv()


class HtmlPages:
    def __init__(self, app):
        self.app = app
        self.templates = Jinja2Templates(directory="templates")

        if os.getenv("API_HOST") in ["localhost", "127.0.0.1", "0.0.0.0"]:
            self.base = ""
        elif os.getenv("API_SUBDOMAIN_ALIAS"):
            self.base = "https://" + os.getenv("API_SUBDOMAIN_ALIAS") + "." + os.getenv("API_HOST")
        else:
            self.base = "https://" + os.getenv("API_HOST")

        self.register_handlers()

    def register_handlers(self):
        self.app.get("/analyze", response_class=HTMLResponse)(self.read_analyze)
        self.app.get("/share", response_class=HTMLResponse)(self.read_share)

    async def read_analyze(self, request: Request):
        return self.templates.TemplateResponse("analyze.html", {"request": request, "base_url": self.base})

    async def read_share(self, request: Request):
        return self.templates.TemplateResponse("share.html", {"request": request, "base_url": self.base})
