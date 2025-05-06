import os
import glob
import asyncio
import yaml
import importlib
import uuid
from contextlib import asynccontextmanager
from fastapi import Request, Response
from pydantic import BaseModel
import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from core.exceptions import add_exception_handlers
import logging
from logging.config import dictConfig

logger = logging.getLogger(__name__)


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
        """
        初始化FastAPI应用
        """

        

        # 配置日志
        dictConfig({
            'version': 1,
            'formatters': {
                'default': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'default',
                    'stream': 'ext://sys.stdout',
                },
            },
            'root': {
                'level': 'INFO',
                'handlers': ['console'],
            },
        })

        @asynccontextmanager
        async def fastapi_lifespan(app: FastAPI):
            logger.info('FastAPI application starting up')
            yield
            logger.info('FastAPI application shutting down')

        app = FastAPI(lifespan=fastapi_lifespan, title=self.server_config.title, version=self.server_config.version)

        # 添加请求ID中间件
        @app.middleware("http")
        async def request_id_middleware(request: Request, call_next):
            request_id = str(uuid.uuid4())
            request.state.request_id = request_id
            
            # 设置日志上下文
            logger = logging.getLogger(__name__)
            logger = logging.LoggerAdapter(logger, {'request_id': request_id})
            
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response

        # 开启CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # 全局异常处理
        add_exception_handlers(app)

        # 初始化缓存
        from utils.cache import CacheManager, CacheConfig
        cache_config = CacheConfig(**self.config.get("cache", {}).get("redis", {}))
        app.state.cache = CacheManager(cache_config)
        logger.info("Cache service initialized")

        # 静态资源
        logger.info("Loading static resources...")
        static_dir = os.path.join(os.path.dirname(__file__), "static")
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

        # 注册路由
        endpoints_root_directory = os.path.join(os.path.dirname(__file__), "endpoints")
        app = include_routers_from_directory(app, endpoints_root_directory)

        return app
    
    async def run(self):
        config = uvicorn.Config(self.app, 
                                host=self.server_config.host, 
                                port=self.server_config.port,
                                workers=self.server_config.workers)
        server = uvicorn.Server(config)
        await server.serve()

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    world_history_app = FastAPIRunner(config)
    asyncio.run(world_history_app.run())
