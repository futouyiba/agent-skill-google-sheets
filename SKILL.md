---
name: gsheets
description: 操作用户的 Google Sheets（谷歌表格）：查找、读取、写入、更新表格数据。当用户提到 Google Sheets / 谷歌表格 / 在线表格，要读表、写表、查表、分析表格数据、把结果写进表格时使用。基于 gsheets MCP 服务器（服务账号方案）。
---

# Google Sheets 操作

前提：已按仓库 README 配置好 `gsheets` MCP 服务器（服务账号方案）。工具名为 `mcp__gsheets__*`（list_spreadsheets、list_sheets、get_sheet_data、update_cells 等）。

## 标准流程

1. **找表**：`list_spreadsheets` 列出服务账号可见的表格。找不到目标表 → 见下方"权限模型"。
2. **看结构**：`list_sheets`（传 spreadsheet id）列出工作表 tab。
3. **读数据**：`get_sheet_data` 读指定工作表，可传 A1 范围（如 `A1:F20`）。
4. **写数据**：`update_cells` 等写入；写之前先读目标区域确认现有内容，避免覆盖。

## 权限模型（重要）

服务账号只能看到**共享给它**的表，其余一律 403。服务账号邮箱的获取方式：

- 从 MCP 配置里的凭证文件读：`GOOGLE_APPLICATION_CREDENTIALS` 指向的 JSON 中 `client_email` 字段（形如 `xxx@yyy.iam.gserviceaccount.com`）；
- 或直接问用户。

**症状**：`list_spreadsheets` 为空 / 调用返回 403 PERMISSION_DENIED
**处理**：让用户把表格共享给该邮箱（需要写入给**编辑者**权限）。共享后立即可见，无需重启会话。

## 故障排查

| 症状 | 原因与处理 |
|---|---|
| 工具调用超时 | 服务器需要访问 googleapis.com。若用户在受限网络（如中国大陆），需按 README 部署代理补丁：`proxy-patch/sitecustomize.py` + MCP 配置中的 `PYTHONPATH` 与 `--with pysocks`，并确认代理可用 |
| gsheets 工具没加载 | 跑 `claude mcp list` 检查；配置在 `~/.claude.json` 的 `mcpServers.gsheets`；按 README 重新注册 |
| 401 / invalid_grant | 服务账号密钥失效或被删：按 README 在 Google Cloud 重新生成密钥并更新路径 |

## 注意

- 写操作（改值、插行列）执行前先向用户确认目标表和区域。
- 大表先 `list_sheets` + 小范围读探明结构，不要整表拉取。
