from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter, Request
# from models.note import Note
from config.db import conn
from utils.auth import get_current_user
from utils.greeting import get_greeting
from schemas.note import noteEntity, notesEntity
from fastapi.templating import Jinja2Templates
import starlette.status as status
from bson import ObjectId
from datetime import datetime, UTC
from bson import ObjectId

note = APIRouter()
templates = Jinja2Templates(directory = "templates")

notes_collection = conn.notes.notes






def get_note_stats(user_id: str):
    user_query = {
        "user_id": user_id
    }

    total_notes = notes_collection.count_documents(user_query)

    important_notes = notes_collection.count_documents({
        "user_id": user_id,
        "important": True
    })

    categories = list(
        notes_collection.aggregate([
            {"$match": user_query},
            {
                "$group": {
                    "_id": "$category",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ])
    )

    categories = [
        category
        for category in categories
        if category["_id"]
    ]

    return {
        "total_notes": total_notes,
        "important_notes": important_notes,
        "categories": categories
    }







def get_related_notes(note, user_id):
    query = {
        "user_id" : user_id,
        "_id": {"$ne": note["_id"]}
    }
    candidates = list(notes_collection.find(query))
    print("RELATED CANDIDATES:", len(candidates))

    current_category = note.get("category")
    current_tags = set(note.get("tags", []))

    related = []

    # Finding the related notes
    for candidate in candidates:
        score = 0

        candidate_category = candidate.get("category")
        candidate_tags = set(candidate.get("tags", []))

        if current_category and candidate_category == current_category:
            score += 3

        shared_tags = current_tags.intersection(candidate_tags)
        score += len(shared_tags) * 2

        if score > 0:
            related.append({
                "note": candidate,
                "score": score,
                "shared_tags": list(shared_tags)
            })


    related.sort(
        key=lambda item: item["score"],
        reverse=True
    )
    
    return related[:5]





#to get the notes
@note.get("/notes",response_class = HTMLResponse)
async def get_notes(
    request: Request, 
    q:str = None, 
    filter_important:bool = False,
    page:int = 1,
    error: str = None,
    category: str = None,
):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/login", status_code=302)

    per_page = 6
    skip_page = (page-1)*per_page
    query = {
        "user_id": request.session.get("user_id")
    }
    # Search
    if q:
        query["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"content": {"$regex": q, "$options": "i"}}
        ]

    # Important filter
    if filter_important:
        query["important"] =True

    # Category filter
    if category:
        query["category"] = category

    # Get filtered notes by the time created 
    results = (
        notes_collection
        .find(query)
        .sort("created_at", -1)
        .skip(skip_page)
        .limit(per_page)
        )

    # Count filtered notes
    total_notes = notes_collection.count_documents(query)

    
    has_next = page * per_page < total_notes
    
    newDocs = notesEntity(results)
    stats = get_note_stats(
        request.session.get("user_id")
    )
    user_name = request.session.get("user_name")
    first_name = user_name.split(" ")[0] if user_name else "User"
    greeting = get_greeting()


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
            "use_container": False,
            "greeting": greeting,
            "user_name": user_name,
            "first_name": first_name,
            "error": error,
            "stats": stats,
            "category": category,
            }
        )
        





        

#to create a new note
@note.post("/notes")
async def create_note(request: Request):
    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse("/login", status_code=302)

    form = await request.form()
    formDict = dict(form)

    # Basic fields
    title = formDict.get("title", "").strip()
    content = formDict.get("content", "").strip()

    # Category & Tags
    category = formDict.get("category", "").strip()
    tags_input = formDict.get("tags", "")

    tags = [
        tag.strip().lower()
        for tag in tags_input.split(",")
        if tag.strip()
    ]

    # Validation
    if not title and not content:
        return RedirectResponse(
            url="/notes?error=Please%20enter%20both%20a%20title%20and%20content",
            status_code=303
        )

    if not title:
        return RedirectResponse(
            url="/notes?error=Please%20enter%20a%20title",
            status_code=303
        )

    if not content:
        return RedirectResponse(
            url="/notes?error=Please%20enter%20a%20content",
            status_code=303
        )

    # Create the document we actually want to store
    note_data = {
        "title": title,
        "content": content,
        "important": formDict.get("important") == "on",
        "category": category or None,
        "tags": tags,
        "user_id": request.session.get("user_id"),
        "user_email": request.session.get("user"),
        "created_at": datetime.now(UTC)
    }
    notes_collection.insert_one(note_data)

    return RedirectResponse(
        url="/notes",
        status_code=status.HTTP_303_SEE_OTHER
    )







#to delete the note
@note.get("/notes/delete/{id}")
async def  delete_note(request:Request, id: str):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/login", status_code=302)

    notes_collection.delete_one({
        "_id": ObjectId(id),
        "user_id":request.session.get("user_id")
    })
    return RedirectResponse(url = "/notes", status_code=status.HTTP_303_SEE_OTHER)








#to update/edit the previously created note
@note.get("/notes/edit/{id}",response_class = HTMLResponse)
async def edit_note(request: Request, id: str):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    
    note_found = notes_collection.find_one({
        "_id": ObjectId(id),
        "user_id":request.session.get("user_id")
        })
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

@note.post("/notes/edit/{id}")
async def save_edited_note(request: Request, id:str):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/login", status_code=302)

    form = await request.form()
    formDict = dict(form)
    formDict["important"] = True if formDict.get("important") == "on" else False
    notes_collection.update_one({
        "_id": ObjectId(id),
        "user_id":request.session.get("user_id")
        },
        {"$set": formDict}
        )
    return RedirectResponse(url = "/notes", status_code=status.HTTP_303_SEE_OTHER)








#view the note on new page
@note.get("/notes/view/{id}", response_class=HTMLResponse)
async def view_note(request: Request, id: str):

    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse("/login", status_code=302)

    try:
        note_found = notes_collection.find_one({
            "_id": ObjectId(id),
            "user_id": request.session.get("user_id")
        })
    except Exception:
        return RedirectResponse("/notes", status_code=302)

    if not note_found:
        return RedirectResponse("/notes", status_code=302)

    related_notes = get_related_notes(note_found, request.session.get("user_id"))

    note_found = noteEntity(note_found)

    
    return templates.TemplateResponse(
        request=request,
        name="note.html",
        context={
            "request": request,
            "note": note_found,
            "show_navbar": True,
            "use_container": False,
            "related_notes": related_notes,
        }
    )
