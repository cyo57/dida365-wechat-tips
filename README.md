# Dida365 滴答清单微信推送客户端

一个使用 Python + httpx 开发的滴答清单本地客户端，能够获取今天和未来七天的未完成任务，并通过企业微信机器人推送。

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目或下载文件
# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入您的真实配置
```

### 2. 本地授权（必须执行一次）

**重要**：首次运行必须在本地完成 OAuth 授权，因为 Docker 容器无法处理交互式输入。

```bash
# 本地运行程序完成授权
python main.py
```

按照提示：
1. 复制显示的授权 URL 到浏览器
2. 完成授权后，复制重定向 URL 中的 `code`
3. 将 `code` 输入程序

完成后，`data/token_cache` 文件会被创建，存储 access_token。

### 3. 运行方式

#### 方式一：Docker 运行（推荐）

```bash
# 构建并运行
docker-compose up --build

# 后台运行
docker-compose up -d
```

#### 方式二：本地运行

```bash
pip install -r requirements.txt
python main.py
```

## 📁 项目结构

```
├── main.py              # 主程序入口
├── config.py            # 配置管理
├── dida_client.py       # 滴答清单API客户端
├── wechat_bot.py        # 微信机器人客户端
├── requirements.txt     # Python依赖
├── .env.example         # 环境变量模板
├── Dockerfile          # Docker容器配置
├── docker-compose.yml  # Docker编排配置
└── data/               # 数据目录（token缓存）
```

## 🔧 配置说明

### .env 文件配置

```env
# 滴答清单开发者中心的 Client ID
CLIENT_ID = "your_dida365_client_id_here"

# 滴答清单开发者中心的 Client Secret  
CLIENT_SECRET = "your_dida365_client_secret_here"

# 企业微信机器人的 Webhook Key
WECHAT_BOT_KEY = "your_wechat_bot_key_here"

# OAuth 2.0 授权回调地址
REDIRECT_URI = "https://your_domain.com/callback"
```

## 🎯 功能特性

- ✅ OAuth 2.0 认证系统（有效期约6个月）
- ✅ **智能授权提醒**：token过期时自动通过微信通知
- ✅ 智能任务筛选：今天 + 未来7天未完成任务
- ✅ 美观输出格式：使用表情符号区分任务类型
- ✅ 微信机器人推送：纯文本格式
- ✅ Docker 容器化部署
- ✅ Token 自动缓存

## 📱 输出示例

```
📅 今日计划 (11-13)：
    ⭐ 17:00 周报
    ⏰ 17:30 超融合&SCP场景使用实验（PT2）
    ⏰ 18:30 HOL自由平台
    ⏰ 21:30 PT1-aDesk普通办公场景

🗓️ 未来七天：
    🛎 11-14 (周五) 超融合集群部署
```

## ⏰ 定时推送设置

### 使用 Cron 定时执行（推荐）

#### 1. 使用提供的执行脚本

项目已提供 `run_dida365.sh` 脚本，请直接使用：

```bash
# 给脚本执行权限（如果还没有）
chmod +x run_dida365.sh

# 编辑脚本，修改项目路径
nano run_dida365.sh
# 修改 PROJECT_DIR 为您的实际项目路径
```

#### 2. 设置 Cron 定时任务

```bash
# 编辑 crontab
crontab -e

# 添加以下定时任务（根据需要选择）：

# 每天上午9点推送
0 9 * * * /path/to/run_dida365.sh

# 工作日每天上午9点推送（周一到周五）
0 9 * * 1-5 /path/to/run_dida365.sh

# 每天上午9点和下午6点推送
0 9,18 * * * /path/to/run_dida365.sh

# 每周一上午9点推送（本周计划）
0 9 * * 1 /path/to/run_dida365.sh
```

#### 3. 常用时间配置示例

| 时间 | Cron 表达式 | 说明 |
|------|-------------|------|
| 每天9点 | `0 9 * * *` | 每日日报 |
| 工作日9点 | `0 9 * * 1-5` | 工作日提醒 |
| 每天9点和18点 | `0 9,18 * * *` | 早晚提醒 |
| 每周一9点 | `0 9 * * 1` | 周计划 |
| 每15分钟 | `*/15 * * * *` | 测试用 |

#### 4. Docker 容器配置优化

为了确保 cron 执行成功，请确认 `docker-compose.yml` 中的配置：

```yaml
restart: never  # 执行完自动退出，不重启
```

#### 5. 日志查看

```bash
# 查看 cron 执行日志
tail -f /var/log/syslog | grep CRON

# 或查看 Docker 容器日志
docker-compose logs dida365-client
```

### 验证定时任务

```bash
# 查看当前的 cron 任务
crontab -l

# 手动测试脚本
/path/to/run_dida365.sh
```

## 🐛 常见问题

### Q: Docker 运行时如何输入授权 code？
**A**: 如上所述，必须先在本地运行一次完成授权，然后将缓存的 token 迁移到 Docker 环境。

### Q: Token 过期了怎么办？
**A**: 删除 `data/token_cache` 文件，重新在本地运行一次授权流程。

### Q: 如何确保定时任务正常运行？
**A**: 
1. 确认脚本有执行权限：`chmod +x run_dida365.sh`
2. 检查脚本路径是否正确
3. 查看 cron 日志确认执行情况
4. 确保 Docker 服务正常运行