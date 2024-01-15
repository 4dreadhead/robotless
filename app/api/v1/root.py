from fastapi import Request, APIRouter
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/analyze")
def analyze(request: Request):
    return templates.TemplateResponse("analyze.html", {"request": request})


@router.get("/share")
def share(request: Request):
    return templates.TemplateResponse("share.html", {"request": request})
