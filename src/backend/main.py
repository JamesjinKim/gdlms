from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 각 모듈의 웹 서버 라우터 임포트
from AGV.agv_server import router as agv_router
from gas_cabinet.gas_web_server import router as gas_router
from stocker.stocker_web_server import router as stocker_router

app = FastAPI(title="Integrated Equipment Control System")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vue.js Vite는 기본적으로 5173 포트를 사용 #개발 서버 vueCLI => vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 각 모듈의 라우터를 메인 앱에 포함
app.include_router(
    agv_router,
    prefix="/agv",
    tags=["AGV Control"]
)

app.include_router(
    gas_router,
    prefix="/gas",
    tags=["Gas Cabinet Control"]
)

app.include_router(
    stocker_router,
    prefix="/stocker",
    tags=["Stocker Control"]
)

@app.get("/")
async def root():
    return {
        "service": "Equipment Control System",
        "version": "1.0",
        "available_endpoints": {
            "agv": "/agv",
            "gas_cabinet": "/gas",
            "stocker": "/stocker"
        }
    }

@app.get("/status")
async def get_system_status():
    return {
        "agv_status": "running",
        "gas_cabinet_status": "running",
        "stocker_status": "running"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)