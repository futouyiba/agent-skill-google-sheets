# Agent Skill: Google Sheets（服务账号方案）

[English version](README_EN.md)

一个可移植的 Agent Skill 包，让任何支持 [Agent Skills](https://www.anthropic.com/news/skills) 标准的 AI 客户端（Claude Code、Claude Desktop、以及兼容该格式的第三方 agent 客户端）安全地读写你的 Google Sheets。

## 为什么是"本地服务器 + 共享邮箱"这个模式？

接入 Google Sheets 给 AI 客户端，通常有三条路，前两条对个人用户都是堵的：

| 路线 | 门槛 | 结论 |
|---|---|---|
| ① Google 官方远程 MCP（`sheetsmcp.googleapis.com`） | 要求背后的 GCP 项目加入 **Workspace Developer Preview 计划**，而该计划的申请表单**不接受个人 Gmail**——必须是 Workspace 公司/组织邮箱 | 个人用户被挡 |
| ② claude.ai 官方连接器（自定义 Connector） | 需要 Claude Pro/Max/Team/Enterprise 订阅；OAuth 回调走 claude.ai 后端，第三方 API token / 自建中转用户不可用 | 非官方订阅用户被挡 |
| ③ 本仓库的方案：**本地 MCP 服务器 + 服务账号** | 只要一个免费的 Google Cloud 项目 | ✅ 人人可用 |

本方案用 [mcp-google-sheets](https://github.com/xing5/mcp-google-sheets) 在本地跑 MCP 服务器，通过 **Google Cloud 服务账号**（一种程序身份，不是人的账号）直连 Sheets API 正式版：

- **不依赖任何订阅、任何预览资格**——走的是 GA 正式版 API，长期稳定；
- **权限边界清晰**：服务账号只能看到**显式共享给它**的表，你的其他文件它一概不可见。代价只是每张表首次使用前共享一次（跟共享给同事一样点一下）。

> 如果你有 Workspace 公司邮箱，推荐直接走官方远程 MCP（①），以你自己账号的身份访问全部表格、无需逐张共享——步骤见文末附录。

## 目录

- `SKILL.md` — 技能本体（放进你的 skills 目录）
- `proxy-patch/sitecustomize.py` — 受限网络（无法直连 googleapis.com）所需的代理补丁，可选

## 接入步骤

### 第 1 步：Google Cloud 侧（约 10 分钟，全在浏览器）

1. 打开 [Google Cloud Console](https://console.cloud.google.com)，新建一个项目（如 `sheets-mcp`）。
2. 启用 **Google Sheets API** 和 **Google Drive API**（菜单 → API 和服务 → 启用）。
3. 创建服务账号：IAM 和管理 → 服务账号 → 创建（无需授予权限）。
4. 为服务账号创建 **JSON 密钥**并下载，保存到如 `~/.config/mcp-google-sheets/service-account.json`。
5. 记下 JSON 里的 `client_email`（形如 `xxx@yyy.iam.gserviceaccount.com`）——**每张要用的表格都要共享给这个邮箱**（编辑者权限）。

### 第 2 步：注册 MCP 服务器（Claude Code / 兼容客户端）

网络可直接访问 googleapis.com：

```bash
claude mcp add gsheets -s user \
  -e GOOGLE_APPLICATION_CREDENTIALS=~/.config/mcp-google-sheets/service-account.json \
  -- uvx --with 'mcp<2' mcp-google-sheets
```

受限网络（如中国大陆，走本地代理 127.0.0.1:7897）：把本仓库的 `proxy-patch/` 放到 `~/.config/mcp-google-sheets/bootstrap/`，再执行：

```bash
claude mcp add gsheets -s user \
  -e GOOGLE_APPLICATION_CREDENTIALS=~/.config/mcp-google-sheets/service-account.json \
  -e PYTHONPATH=~/.config/mcp-google-sheets/bootstrap \
  -- uvx --with 'mcp<2' --with pysocks mcp-google-sheets
```

说明：

- `--with 'mcp<2'` 必须保留：mcp-google-sheets 尚不兼容 mcp 2.x（FastMCP 已改名）。
- `--with pysocks` + `PYTHONPATH` 指向补丁：httplib2 无视代理环境变量，补丁在启动时强制挂 ProxyInfo。代理地址可用 `GSHEETS_PROXY_HOST` / `GSHEETS_PROXY_PORT` 环境变量覆盖（默认 127.0.0.1:7897）。
- 依赖 [uv](https://docs.astral.sh/uv/)（`uvx`）。首次启动会自动下载依赖。

### 第 3 步：安装技能

把 `SKILL.md` 所在目录复制到你的客户端技能目录，例如 Claude Code：

```bash
mkdir -p ~/.claude/skills/gsheets   # 或项目的 .claude/skills/gsheets
cp SKILL.md ~/.claude/skills/gsheets/
```

新开会话即生效。之后直接说"读一下我的 xx 表格"。

## 安全须知

- **`service-account.json` 是密钥，绝不要提交到仓库或分享给他人。** 本仓库不应包含任何密钥文件。
- 服务账号只能看到显式共享给它的表——权限边界清晰，但记得共享时给的是"编辑者"还是"查看者"要按需选择。
- 密钥泄露/过期：在 Google Cloud 删除该密钥重新生成即可。

## 附：有 Workspace 账号时的更优解（官方远程 MCP）

1. 按官方文档 [Configure the Sheets MCP server](https://developers.google.com/workspace/sheets/api/guides/configure-mcp-server) 建 OAuth 客户端（重定向 URI 加 `http://localhost:7777/callback`），并让项目加入 Workspace Developer Preview 计划（需公司邮箱）。
2. `claude mcp add -s user --transport http --client-id <你的客户端ID> --callback-port 7777 gsheets https://sheetsmcp.googleapis.com/mcp/v1`
3. `claude mcp login gsheets`（受限网络需先 export 代理环境变量）。

官方方案以你自己的 Google 账号身份访问全部表格，无需逐张共享。

## License

MIT
