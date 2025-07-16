# Smart Holiday Booking Assistant

## 项目结构

- `client/` — 前端（Next.js + Tailwind + Firebase Auth）
- `server/` — 后端（FastAPI + MongoDB/Firestore 预留）

## 快速开始

### 1. 前端
```bash
cd client
npm install
npm run dev
```
访问：http://localhost:3000

### 2. 后端
```bash
cd server
source ../server/bin/activate  # 激活虚拟环境
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
访问：http://localhost:8000

### 3. 数据库
- MongoDB: 默认连接 `mongodb://localhost:27017`，可在 `server/app/main.py` 修改
- Firestore: 预留配置，需安装 Google Cloud SDK 并配置凭证

### 4. 认证
- 前端集成 Firebase Authentication（Email/Google 登录）
- 后端可根据需要校验 Firebase Token

## CORS
- 已配置允许 `localhost:3000` 和 `localhost:8000` 互通

---

如需详细开发文档，请分别查看 `client/README.md` 和 `server/README.md`。 