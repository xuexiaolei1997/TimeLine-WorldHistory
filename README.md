# 世界历史时间线 - 3D地球可视化

![项目截图](public/textures/earth.jpg)

一个交互式的3D地球时间线应用，展示世界各地的文明演变历史。

## 功能特性

- 🌍 3D地球模型，可旋转缩放查看
- 📅 垂直时间线控制，浏览不同历史时期
- 🏛️ 显示特定时期的重要历史事件标记
- 🔍 点击标记查看事件详细信息
- 🖼️ 支持展示事件相关图片和资料

## 技术栈

- React.js
- Three.js (3D渲染)
- React-Three-Fiber (Three.js React封装)
- Drei (Three.js辅助组件)
- Date-fns (日期处理)

## 安装运行

1. 克隆仓库
```bash
git clone https://github.com/xuexiaolei1997/TimeLine-WorldHistory.git
cd timeline-worldhistory
```

2. 安装依赖
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

## 项目结构

```
public/          # 静态资源
  textures/      # 3D纹理贴图
src/
  components/    # React组件
    Earth3D/     # 3D地球组件
    Timeline/    # 时间线组件
  utils/         # 工具函数
  App.js         # 主应用
  index.js       # 入口文件
```

## 贡献指南

欢迎提交Pull Request或Issue报告问题。

## 许可证

MIT
