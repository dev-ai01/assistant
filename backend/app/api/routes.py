from fastapi import Request, APIRouter, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.core.agent import run_agent  
import json
import os
from pydantic import BaseModel

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

class QueryRequest(BaseModel):
    query: str

@router.post("/search-ui", response_class=HTMLResponse)
async def search_ui(request: Request, query: str = Form(...)):
    try:
        # Run your full business logic agent
        result = run_agent(query)

        # Generate docx and determine path
        filename = f"{query[:30].replace(' ', '_')}.docx"
        filepath = os.path.join("static", "reports", filename)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "result": json.dumps(result, indent=2),
            "docx_link": f"/static/reports/{filename}.docx"
        })
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "result": f"Error: {str(e)}",
            "docx_link": None
        })
