# 世界历史时间线 - 3D地球可视化

![项目截图](public/textures/earth.jpg)

一个全栈的3D地球时间线应用，展示世界各地的文明演变历史，包含前后端系统和管理功能。

## 功能特性

### 前端功能
- 🌍 3D地球模型，可旋转缩放查看
- 📅 垂直时间线控制，浏览不同历史时期
- 🏛️ 显示特定时期的重要历史事件标记
- 🔍 点击标记查看事件详细信息
- 🖼️ 支持展示事件相关图片和资料
- 🌐 多语言支持（中英文切换）
- 📊 系统健康状态监控面板

### 后端功能
- 🚀 RESTful API 提供历史数据
- 🔒 管理员认证和权限控制
- 📝 管理员后台管理历史事件、时期和地区
- ⚡ 性能监控和日志记录
- 🔄 数据缓存和限流保护

## 技术栈

### 前端
- React.js
- Three.js (3D渲染)
- React-Three-Fiber (Three.js React封装)
- Drei (Three.js辅助组件)
- Date-fns (日期处理)
- i18next (国际化)

### 后端
- Python 3
- Flask (Web框架)
- MongoDB (数据库)
- PyMongo (MongoDB驱动)
- Marshmallow (数据序列化)
- Gunicorn (生产服务器)

## 安装运行

### 前端
1. 克隆仓库
```bash
git clone https://github.com/xuexiaolei1997/TimeLine-WorldHistory.git
cd timeline-worldhistory
```

2. 安装前端依赖
```bash
npm install
```

3. 下载纹理文件
- 将earth.jpg放入`public/textures/`目录

4. 启动开发服务器
```bash
npm start
```

5. 访问应用
打开浏览器访问 [http://localhost:3000](http://localhost:3000)

### 后端
1. 安装Python依赖
```bash
cd backend
pip install -r requirements.txt
```

2. 配置MongoDB
- 安装MongoDB并启动服务
- 修改`backend/config.yaml`中的数据库连接配置

3. 导入初始数据
```bash
python backend/utils/data_importer.py
```

4. 启动后端服务
```bash
python backend/run.py
```

## 项目结构

```
public/          # 静态资源
  textures/      # 3D纹理贴图
  mock-data/     # 模拟数据
src/             # 前端代码
  components/    # React组件
    Earth3D/     # 3D地球组件
    Timeline/    # 时间线组件
    Admin/       # 管理后台组件
  locales/       # 多语言文件
  utils/         # 工具函数
backend/         # 后端代码
  endpoints/     # API端点
  services/      # 业务逻辑
  schemas/       # 数据模型
  utils/         # 工具函数
  static/        # 静态文件
docs/            # 文档
  db/            # 数据库示例数据
```

## 数据库配置

1. 安装MongoDB
2. 创建数据库`timeline`
3. 创建集合: `events`, `periods`, `regions`
4. 修改`backend/config.yaml`中的连接配置:
```yaml
database:
  host: localhost
  port: 27017
  name: timeline
```

## API文档

API文档可通过Swagger UI访问：
[http://localhost:5000/api/docs](http://localhost:5000/api/docs)

主要API端点：
- `/api/events` - 历史事件
- `/api/periods` - 历史时期
- `/api/regions` - 地理区域
- `/api/health` - 系统健康状态

## 环境变量

前端环境变量配置在`.env`文件：
```
REACT_APP_API_URL=http://localhost:5000/api
```

## 测试运行

运行前端测试：
```bash
npm test
```

运行后端测试：
```bash
cd backend
pytest
```

## 贡献指南

1. Fork仓库
2. 创建特性分支 (`git checkout -b feature/your-feature`)
3. 提交更改 (`git commit -am 'Add some feature'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 创建Pull Request

提交代码前请确保：
- 通过所有测试
- 更新相关文档
- 遵循现有代码风格

## 许可证

MIT
