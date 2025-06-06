from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.routes import router as api_router
from app.logic import sample_logic_function

app = FastAPI()

app.include_router(api_router)

# Static and template config
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/search-ui", response_class=HTMLResponse)
async def search_ui(request: Request, query: str = Form(...)):
    # Call your actual function here instead of mock
    result = sample_logic_function() if not query else f"Received query: {query}"
    return templates.TemplateResponse("index.html", {"request": request, "result": result})
