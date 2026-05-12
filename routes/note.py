from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter
from models.note import Note
from config.db import conn
from schemas.note import noteEntity, notesEntity
from fastapi.templating import Jinja2Templates
import starlette.status as status
from bson import ObjectId

note = APIRouter()
templates = Jinja2Templates(directory = "templates")

@note.get("/",response_class = HTMLResponse)
async def get_notes(request: Request):
    docs = conn.notes.notes2.find({})
    newDocs = notesEntity(docs)
    return templates.TemplateResponse(
        request=request,
        name = "index.html",
        context = {"request":request, "newDocs": newDocs}
    )


@note.post("/",response_class=HTMLResponse)
async def create_note(request: Request):
    form = await request.form()
    formDict = dict(form)
    formDict["important"] = True if formDict.get("important") == "on" else False
    innserted_note = conn.notes.notes2.insert_one(formDict)
    return RedirectResponse(url = "/", status_code=status.HTTP_303_SEE_OTHER)

@note.get("/delete/{id}",response_class = HTMLResponse)
async def  delete_note(id: str):
    conn.notes.notes2.delete_one({"_id": ObjectId(id)})
    return RedirectResponse(url = "/", status_code=status.HTTP_303_SEE_OTHER)




@note.get("/edit/{id}",response_class = HTMLResponse)
async def edit_note(request: Request, id: str):
    note_found = conn.notes.notes2.find_one({"_id": ObjectId(id)})
    note_found = noteEntity(note_found)
    return templates.TemplateResponse(
        request=request,
        name = "edit.html",
        context = {
            "request":request, 
            "note": note_found
            }
        )


@note.post("/edit/{id}",response_class=HTMLResponse)
async def save_edited_note(request: Request, id:str):
    form = await request.form()
    formDict = dict(form)
    formDict["important"] = True if formDict.get("important") == "on" else False
    conn.notes.notes2.update_one({"_id": ObjectId(id)}, {"$set": formDict})
    return RedirectResponse(url = "/", status_code=status.HTTP_303_SEE_OTHER)