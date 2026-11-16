# 给 httplib2 强制走本地代理的启动补丁（代理端口可用环境变量覆盖）
#
# 背景：mcp-google-sheets 的 googleapiclient 链路使用 httplib2，
# 而 httplib2 不读取 HTTP(S)_PROXY 环境变量，代理支持又依赖 PySocks。
# 在受限网络（如无法直连 googleapis.com）下，所有 MCP 工具调用都会超时。
#
# 用法：把本目录加入 MCP 命令的环境变量 PYTHONPATH，
# 并在 uvx 参数中加 --with pysocks。详见仓库 README。
import os

_PROXY_HOST = os.environ.get("GSHEETS_PROXY_HOST", "127.0.0.1")
_PROXY_PORT = int(os.environ.get("GSHEETS_PROXY_PORT", "7897"))

try:
    import httplib2

    _proxy = httplib2.ProxyInfo(
        httplib2.socks.PROXY_TYPE_HTTP, _PROXY_HOST, _PROXY_PORT
    )
    _orig_init = httplib2.Http.__init__

    def _patched_init(self, *args, **kwargs):
        _orig_init(self, *args, **kwargs)
        if getattr(self, "proxy_info", None) is None:
            self.proxy_info = _proxy

    if getattr(httplib2.Http.__init__, "_proxy_patched", False) is False:
        _patched_init._proxy_patched = True
        httplib2.Http.__init__ = _patched_init
except Exception:
    pass
