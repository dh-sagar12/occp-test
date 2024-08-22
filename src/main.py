from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from src.auth.router import router as auth_router
from src.auth.router import public_router as auth_public_router
from src.vehicles.router import router as vehicle_router
from src.machine.router import router as machine_router
from src.ocpp.router import router as ocpp_router

from src.utils.auth_bearer import JWTBearer

app = FastAPI(
    title='OCCP Backend DOCS',
    version='1.0',
    servers=[{'url': 'http://localhost:8000'}]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # 信頼するオリジンのリスト
    allow_credentials=True,   # クッキーをサポートするかどうか
    allow_methods=["*"],      # 全てのHTTPメソッドを許可する
    allow_headers=["*"],      # 全てのHTTPヘッダーを許可する
)


app.include_router(auth_router)
app.include_router(auth_public_router)
app.include_router(ocpp_router)
app.include_router(vehicle_router, dependencies=[Depends(JWTBearer())])
app.include_router(machine_router, dependencies=[Depends(JWTBearer())])
