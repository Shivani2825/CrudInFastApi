from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi_login.exceptions import InvalidCredentialsException
from fastapi import APIRouter, Request, Form,status,Depends
from .models import User
from user.pydantic_models import *
from fastapi_login import LoginManager
from passlib.context import CryptContext
import typing

router=APIRouter()
SECRET = 'your-secret-key'
manager = LoginManager(SECRET, token_url='/auth/token')
templates = Jinja2Templates(directory="user/templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def flash(request: Request, message: typing.Any, category: str = "") -> None:
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append({"message": message, "category": category})


def get_flashed_messages(request: Request):
    print(request.session)
    return request.session.pop("_messages") if "_messages" in request.session else []

templates= Jinja2Templates(directory="user/templates")
templates.env.globals['get_flashed_messages'] = get_flashed_messages

@router.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request, })

@router.get("/login/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request, })


@router.get("/home/", response_class=HTMLResponse)
async def read_item(request: Request):
   
    return templates.TemplateResponse("home.html", {
       
        "request": request, })
import uuid

@router.get("/delete/{id}")
async def delete(request:Request,id:uuid.UUID):
    user=await User.get(id=id).delete()
    return RedirectResponse("/table/")


@router.get("/table/", response_class=HTMLResponse)
async def read_item(request: Request):
    user=await User.all()
    return templates.TemplateResponse("table.html", {
         "user":user,
        "request": request, })



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_hash_password(password):
    return pwd_context.hash(password)

@router.post('/add/',)
async def create_user(request:Request, email:str=Form(...),
                        name:str=Form(...),
                        password:str=Form(...)):
  
    user_obj=await User.create(name=name,email=email,
                                password=get_hash_password(password))
    print(user_obj)
    flash(request, "Added Successful", "success")
    return templates.TemplateResponse("login.html", {
        "request": request, })

@manager.user_loader()
async def load_user(email:str):
    if await User.exists(email=email):
        user=await User.get(email=email)
        return user

@router.post('/ulogin/')
async def login(request:Request,email: str = Form(...)
                , password: str = Form(...)):

    email = email
   
    user = await load_user(email)
    
    if not User:
        flash(request, "Invalid Username", "danger")
        return templates.TemplateResponse("login.html",{'request':request})
    elif not verify_password(password,user.password):
        flash(request, "Password incorect", "danger")
        return templates.TemplateResponse("login.html",{'request':request})

    else:
        # request.session['id']=user.id
        request.session['name']=user.name  
        flash(request, "Login Successful", "success")
        return templates.TemplateResponse("home.html",{'request':request})

@router.get('/update/{id}', response_class=HTMLResponse)
async def update_user(request:Request,id:uuid.UUID):
    print(id)
    user = await User.get(id=id)
    return templates.TemplateResponse("update.html",{'request':request,"user":user})

@router.post("/update_user/{id}")
async def update(request:Request,id:uuid.UUID, email:str=Form(...),
                                name:str=Form(...)):
            await User.filter(id=id).update(name=name,email=email)                       

            return templates.TemplateResponse("table.html",{'request':request})

    
