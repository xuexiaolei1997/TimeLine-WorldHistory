import os
import glob
import asyncio
import yaml
import importlib
import uuid
from contextlib import asynccontextmanager
from fastapi import HTTPException, Request, Response, FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from core.exceptions import add_exception_handlers, AppExceptionCase
from utils.rate_limiter import rate_limit_middleware
from utils.performance import performance_monitor_middleware
import logging
from logging.config import dictConfig

from endpoints import events, periods, regions, health

logger = logging.getLogger(__name__)

# Load configuration
with open("backend/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Configure logging
os.makedirs("logs", exist_ok=True)
dictConfig(config["logging"])


def include_routers_from_directory(app: FastAPI, endpoints_root_directory: str):
    """
    自动搜索指定目录下的所有py文件，并将其中的APIRouter实例添加到FastAPI应用中。

    Args:
        endpoints_root_directory: 目录
    """
    if not os.path.isdir(endpoints_root_directory):
        print(f"错误：指定的路径 '{endpoints_root_directory}' 不是一个有效的目录。")
        return
    
    # 获取所有.py文件的路径
    py_files = glob.glob(os.path.join(endpoints_root_directory, "*.py"))
    if not py_files:
        print(f"错误：在目录 '{endpoints_root_directory}' 中没有找到任何.py文件。")
        return
    
    # 遍历每个.py文件
    for py_file in py_files:
        if "__init__" in py_file:
            continue
        # 获取文件名（不带扩展名）
        file_name = os.path.splitext(os.path.basename(py_file))[0]
        # 动态导入模块
        module = importlib.import_module(f"endpoints.{file_name}")
        
        # 检查模块中是否有APIRouter实例
        if hasattr(module, "router"):
            router: APIRouter = getattr(module, "router")
            # 将APIRouter实例添加到FastAPI应用中
            app.include_router(router)
            print(f"加载路由：/{file_name}")
        else:
            print(f"警告：模块 '{file_name}' 中没有找到APIRouter实例。")
    
    return app


class FastAPIConfig(BaseModel):
    title: str = "World History Timeline"
    version: str = "v1.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1


class FastAPIRunner:
    def __init__(self, config):
        self.config = config
        self.server_config = FastAPIConfig(**self.config['server'])
        self.cache_config = self.config.get('cache', {}).get('redis', {})
        self.app = self.create_app()

    def create_app(self):
        @asynccontextmanager
        async def fastapi_lifespan(app: FastAPI):
            logger.info('FastAPI application starting up')
            yield
            logger.info('FastAPI application shutting down')

        app = FastAPI(
            lifespan=fastapi_lifespan, 
            title=self.server_config.title, 
            version=self.server_config.version,
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json"
        )

        # 添加CORS中间件
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.get("cors", {}).get("allowed_origins", ["*"]),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # 注册中间件
        # self._register_middlewares(app)
        
        # 注册异常处理
        self._register_exception_handlers(app)
        
        # 初始化服务
        self._init_services(app)
        
        # 注册路由 - 使用自动扫描方式
        self._register_routes(app)

        return app

    def _register_middlewares(self, app: FastAPI):
        @app.middleware("http")
        async def request_id_middleware(request: Request, call_next):
            try:
                request_id = str(uuid.uuid4())
                request.state.request_id = request_id
                response = await call_next(request)
                response.headers["X-Request-ID"] = request_id
                return response
            except Exception as e:
                logger.error(f"Request ID middleware error: {str(e)}")
                return await call_next(request)

        @app.middleware("http")
        async def performance_middleware(request: Request, call_next):
            try:
                return await performance_monitor_middleware(request, call_next)
            except Exception as e:
                logger.error(f"Performance middleware error: {str(e)}")
                return await call_next(request)

        @app.middleware("http")
        async def rate_limit_handler(request: Request, call_next):
            try:
                return await rate_limit_middleware(request, call_next)
            except Exception as e:
                if isinstance(e, HTTPException):
                    raise
                logger.error(f"Rate limit middleware error: {str(e)}")
                return await call_next(request)

    def _register_exception_handlers(self, app: FastAPI):
        add_exception_handlers(app)
        
        # @app.exception_handler(AppExceptionCase)
        # async def api_exception_handler(request: Request, exc: AppExceptionCase):
        #     return JSONResponse(
        #         status_code=exc.status_code,
        #         content={
        #             "error": exc.error_code,
        #             "message": exc.message,
        #             "details": exc.details
        #         }
        #     )

    def _init_services(self, app: FastAPI):
        # 初始化缓存
        from utils.cache import CacheManager, CacheConfig
        cache_config = CacheConfig(**self.config.get("cache", {}).get("redis", {}))
        app.state.cache = CacheManager(cache_config)
        logger.info("Cache service initialized")

        # 初始化性能监控
        from utils.performance_logger import get_performance_logger
        performance_logger = get_performance_logger()
        performance_logger.cache = app.state.cache
        logger.info("Performance monitoring initialized with Redis cache")

        # 静态资源
        static_dir = os.path.join(os.path.dirname(__file__), "static")
        if os.path.exists(static_dir):
            app.mount("/static", StaticFiles(directory=static_dir), name="static")
            logger.info("Static resources mounted")

    def _register_routes(self, app: FastAPI):
        # 使用自动扫描方式注册路由
        endpoints_dir = os.path.join(os.path.dirname(__file__), "endpoints")
        include_routers_from_directory(app, endpoints_dir)

    async def run(self):
        config = uvicorn.Config(
            self.app, 
            host=self.server_config.host, 
            port=self.server_config.port,
            workers=self.server_config.workers,
            reload=True,  # 开发模式下启用热重载
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    world_history_app = FastAPIRunner(config)
    asyncio.run(world_history_app.run())
