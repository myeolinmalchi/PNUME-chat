from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

##CORS
origins = [
    "http://localhost:3000",
]

##CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Test api"}

@app.get("/items")
async def root():
    return {"message": "this is items page"}