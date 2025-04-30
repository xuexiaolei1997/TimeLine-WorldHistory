# Backend 改进说明

## 文件结构变更

```
backend/
├── api/               # 新增API主文件目录
│   └── main.py        # 从根目录移动至此
├── utils/             # 新增工具类目录
│   ├── decorators.py  # 异常处理装饰器
│   └── database.py    # 数据库管理工具
```

## 新增功能说明

### 1. 异常处理装饰器 (`decorators.py`)

```python
from utils.decorators import handle_app_exceptions

@router.get("/{id}")
@handle_app_exceptions  # 自动处理AppExceptionCase异常
def get_item(id: int, db: Session = Depends(get_db)):
    return repo.get(id)
```

### 2. 数据库管理工具 (`database.py`)

主要功能：
- 连接池管理 (pool_size=10, max_overflow=20)
- 连接健康检查 (pool_pre_ping=True)
- 统一会话管理

使用方式：
```python
from utils.database import db_manager

# 获取数据库会话
db: Session = Depends(db_manager.get_db)

# 检查数据库连接
if not db_manager.check_connection():
    raise Exception("Database connection failed")
```

## 代码改进对比

### 改进前
```python
try:
    return repo.get(id)
except AppExceptionCase as e:
    raise HTTPException(status_code=e.status_code, detail=e.context)
```

### 改进后
```python
@handle_app_exceptions
def get_item(id: int):
    return repo.get(id)
```

## 注意事项

1. 所有数据库依赖应改为使用`db_manager.get_db`
2. 需要异常处理的端点添加`@handle_app_exceptions`装饰器
3. 旧`database.py`已备份为`database_old.py`
