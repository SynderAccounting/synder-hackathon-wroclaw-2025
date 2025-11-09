import uvicorn
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from starlette.middleware.cors import CORSMiddleware

from routers.orders_router import orders_router
from routers.suppliers_router import supplier_router
from routers.image_router import image_router
from routers.shopify_router import shopify_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(shopify_router, prefix="/shopify", tags=["shopify"])
app.include_router(image_router)
app.include_router(supplier_router, prefix="/suppliers", tags=["suppliers"])
app.include_router(orders_router, prefix="/orders", tags=["orders"])

mcp = FastApiMCP(app)

mcp.mount_http()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
