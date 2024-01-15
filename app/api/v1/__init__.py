from app.api.v1.analyze import router as analyze_router
from app.api.v1.share import router as share_router
from app.api.v1.root import router as root_router

routers = [analyze_router, share_router, root_router]
