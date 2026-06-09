from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.init_db import init_database
from app.routers import admin, auth, jobs, options, reports

app = FastAPI(title='Gang Gang Cross-border IP API')

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r'^http://(localhost|127\.0\.0\.1):\d+$',
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(options.router)
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(reports.router)
app.include_router(admin.router)


@app.on_event('startup')
def startup():
    init_database()


@app.get('/health')
def health():
    return {'ok': True}
