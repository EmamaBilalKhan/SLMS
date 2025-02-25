from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from config.db import connectdb
from routes.auth_route import router as auth_router
from routes.course_route import router as course_router
from routes.admin_route import router as admin_router
from routes.progress_route import router as progress_router
from routes.assignments_route import router as assignment_router

app = FastAPI()
connectdb()

app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:3000"], allow_methods=["*"],
    allow_headers=["*"], allow_credentials=True)

@app.middleware("http")
async def auth_middleware(request:Request,call_next):
    path = request.url.path
    print("cookies: ",request.cookies)
    print("path: ",path)
    return await call_next(request)


@app.get("/")
def root():
    response = JSONResponse(
        status_code=200,
        content={"message": "Welcome to the API"},
    )
    return response

app.include_router(auth_router)
app.include_router(course_router)
app.include_router(assignment_router)
app.include_router(admin_router)
app.include_router(progress_router)



