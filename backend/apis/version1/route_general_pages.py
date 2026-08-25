from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


# объект Jinja2Templates, directory - что ему нужно искать HTML-файлы внутри папки шаблонов.
templates = Jinja2Templates(directory="templates")
# экземпляр APIRouter - для чистоты кодовой базы
general_pages_router = APIRouter()


@general_pages_router.get('/')
async def home(request: Request):
    return templates.TemplateResponse(request=request, name='general_pages/homepage.html')
