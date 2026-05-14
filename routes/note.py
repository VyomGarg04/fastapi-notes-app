from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter
# from models.note import Note
from config.db import conn
from schemas.note import noteEntity, notesEntity
from fastapi.templating import Jinja2Templates
import starlette.status as status
from bson import ObjectId
from datetime import datetime, UTC

note = APIRouter()
templates = Jinja2Templates(directory = "templates")

notes_collection = conn.notes.notes


#to get the notes
@note.get("/",response_class = HTMLResponse)
async def get_notes(request: Request, q:str = None, filter_important:bool = False,page:int = 1):
    per_page = 6
    skip_page = (page-1)*per_page
    query ={}
    if q:
        query["title"] = {"$regex": q, "$options": "i"}
    if filter_important:
        query["important"] =True
    #sorting the results by the time created 
    results = notes_collection.find(query).sort("created_at", -1).skip(skip_page).limit(per_page)
    
    total_notes = notes_collection.count_documents(query)
    has_next = page * per_page < total_notes
    
    newDocs = notesEntity(results)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context = {
            "request":request,
            "newDocs": newDocs,
            "q":q, 
            "filter_important":filter_important,
            "page":page,
            "has_next":has_next,
            "show_navbar":True,
            "use_container": True
            }
    )
        
        

#to create a new note
@note.post("/")
async def create_note(request: Request):
    form = await request.form()
    formDict = dict(form)
    formDict["important"] = formDict.get("important") == "on"
    formDict["created_at"] = datetime.now(UTC)
    inserted_note = notes_collection.insert_one(formDict)
    return RedirectResponse(url = "/", status_code=status.HTTP_303_SEE_OTHER)

#to delete the note
@note.get("/delete/{id}")
async def  delete_note(id: str):
    notes_collection.delete_one({"_id": ObjectId(id)})
    return RedirectResponse(url = "/", status_code=status.HTTP_303_SEE_OTHER)



#to update/edit the previously created note
@note.get("/edit/{id}",response_class = HTMLResponse)
async def edit_note(request: Request, id: str):
    note_found = notes_collection.find_one({"_id": ObjectId(id)})
    note_found = noteEntity(note_found)
    return templates.TemplateResponse(
        request=request,
        name = "edit.html",
        context = {
            "request":request, 
            "note": note_found,
            "show_navbar":True,
            "use_container": True
            }
        )

@note.post("/edit/{id}")
async def save_edited_note(request: Request, id:str):
    form = await request.form()
    formDict = dict(form)
    formDict["important"] = True if formDict.get("important") == "on" else False
    notes_collection.update_one({"_id": ObjectId(id)}, {"$set": formDict})
    return RedirectResponse(url = "/", status_code=status.HTTP_303_SEE_OTHER)



