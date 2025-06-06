from fastapi import Request, APIRouter, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.core.agent import run_agent  
import json
import os
from pydantic import BaseModel

router = APIRouter()

# @router.get("/sample")
# async def sample_endpoint():
#     result = sample_logic_function()
#     return {"result": result}
templates = Jinja2Templates(directory="app/templates")

# def mock_process_query(query: str):
#     return {"message": f"Received query: {query}"}

class QueryRequest(BaseModel):
    query: str

# @router.post("/search")
# def search_endpoint(request: QueryRequest):
#     try:
#         response = run_agent(request.query)
#         return response
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@router.post("/search-ui", response_class=HTMLResponse)
async def search_ui(request: Request, query: str = Form(...)):
    try:
        # Run your full business logic agent
        result = run_agent(query)

        # Generate docx and determine path
        filename = f"{query[:30].replace(' ', '_')}.docx"
        filepath = os.path.join("static", "reports", filename)

        # Save docx (assuming your run_agent saves it already)
        # OR call your docx function here explicitly if needed
        # json_to_docx(result, query, filepath)

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
