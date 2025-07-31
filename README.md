# AWD FlagCat 🚩🐱

一款美观、易用的AWD（攻防模式）自动化攻击平台，由我和我的AI程序员R456共同开发。

![App Screenshot](URL_TO_YOUR_SCREENSHOT) ## ✨ 功能特性

- **现代化UI**：基于Tauri+Vue3构建，支持一键切换浅色/暗黑主题。
- **集成化布局**：多栏目分体式布局，便于实时观察攻击日志和调整配置。
- **双攻击模式**：
    - **脚本攻击**：支持上传、选择并动态执行自定义的Python攻击脚本。
    - **可视化配置**：无需编写代码，通过表单即可配置HTTP GET/POST攻击。
- **灵活的目标配置**：支持`IP:端口`或`域名:端口`格式，可为每个目标指定不同端口。
- **可配置的提交**：自由设定Flag的提交API地址和认证Token。
- **实时反馈**：通过WebSocket实现所有操作日志的实时显示。
- **独立打包**：可打包成独立的便携版应用，无需安装开发环境。

## 🚀 如何运行

1.  **后端**: `cd awd_platform` 然后 `pip install -r requirements.txt`，最后 `uvicorn main:app --reload`
2.  **前端**: `cd awd_frontend` 然后 `pnpm install`，最后 `pnpm tauri dev`

## 🛠️ 如何构建

```bash
# 1. 打包Python后端
pyinstaller --noconsole --onefile --name awd_backend awd_platform/main.py

# 2. 修改tauri.conf.json以包含sidecar (详见我们之前的对话)

# 3. 构建Tauri应用
pnpm tauri build
## 📜 许可证
本项目采用 MIT License 开源。