from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app import models
# 1. Добавен admin тук:
from app.routers import ships, permits, inspections, logbook, tickets, admin
from app.translations import get_translator

app = FastAPI(title="IARA System")

app.include_router(ships.router)
app.include_router(permits.router)
app.include_router(inspections.router)
app.include_router(logbook.router)
app.include_router(tickets.router)
# 2. Добавен рутер тук:
app.include_router(admin.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


def get_lang(request: Request) -> str:
    return request.cookies.get("lang", "en")


templates.env.globals["get_lang"] = get_lang


@app.middleware("http")
async def inject_translator(request: Request, call_next):
    lang = get_lang(request)
    request.state.t = get_translator(lang)
    request.state.lang = lang
    response = await call_next(request)
    return response


@app.get("/set-lang/{lang}")
def set_lang(lang: str, request: Request):
    referer = request.headers.get("referer", "/")
    response = RedirectResponse(url=referer)
    response.set_cookie(key="lang", value=lang, max_age=60 * 60 * 24 * 365)
    return response


@app.get("/")
def root(request: Request):
    t = request.state.t
    return templates.TemplateResponse(request=request, name="home.html", context={"t": t, "lang": request.state.lang})

@app.get("/contact")
def contact(request: Request):
    t = request.state.t
    return templates.TemplateResponse(request=request, name="contact.html", context={"t": t, "lang": request.state.lang})
