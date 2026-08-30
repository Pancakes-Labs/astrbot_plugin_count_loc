"""代码统计请求客户端门面（Facade）喵。

保留与旧版 CodeTabs API 客户端完全一致的外部接口（get_repo_loc / close），
内部实际委托给自建统计引擎 LocEngine 完成统计，从而实现：
- 上层 main.py 零改动
- 对第三方统计 API 的彻底解耦（不再依赖任何统计外包服务）
"""

import asyncio
import time

from astrbot.api import logger

from .loc_engine import LocEngine, LocError


class RepoClient:
    """代码统计客户端门面喵。

    对外接口与原 CodeTabs 客户端保持一致：
    - get_repo_loc(repo_path, platform, branch, ignored) -> list[dict] | str
    - close()
    """

    def __init__(self, config: dict | None = None):
        """初始化客户端喵。

        参数:
            config: AstrBot 插件配置字典。
        """
        self._config = config or {}
        # 委托给自建统计引擎（惰性初始化，与调用时 event loop 绑定）
        self._engine: LocEngine | None = None
        # 简单 TTL 内存缓存: key -> (timestamp, data)
        self._cache: dict[tuple, tuple[float, list[dict[str, str | int]]]] = {}
        self._cache_ttl = 600  # 缓存 10 分钟

    def _get_engine(self) -> LocEngine:
        """惰性获取自建统计引擎实例喵。"""
        if self._engine is None:
            # 从 AstrBot 配置中读取 token 和限制参数
            self._engine = LocEngine(
                github_token=self._config.get("github_token", ""),
                gitlab_token=self._config.get("gitlab_token", ""),
                max_archive_mb=self._config.get("max_archive_mb", 100),
            )
        return self._engine

    async def close(self):
        """关闭底层引擎，释放连接池与缓存资源喵。"""
        self._cache.clear()
        if self._engine:
            await self._engine.close()
            self._engine = None

    def _clean_expired_cache(self, now: float):
        """清理已过期的缓存项喵。"""
        expired_keys = [
            k for k, (ts, _) in self._cache.items() if now - ts > self._cache_ttl
        ]
        for k in expired_keys:
            self._cache.pop(k, None)

    async def get_repo_loc(
        self,
        repo_path: str,
        platform: str = "github",
        branch: str | None = None,
        ignored: list[str] | str | None = None,
    ) -> list[dict[str, str | int]] | str:
        """异步统计仓库代码行数，支持 TTL 内存缓存喵。

        参数:
            repo_path: 仓库路径，如 "username/reponame"（GitLab 支持多级子组）。
            platform: 平台，"github" 或 "gitlab"。
            branch: 分支名称；缺省时自动查询默认分支。
            ignored: 忽略的文件/文件夹列表（支持列表或逗号分隔的字符串）。

        返回:
            List[Dict]: 语言统计数据列表，最后一项通常为 Total。
            str: 面向用户的可读错误信息（调用失败时）。
        """
        # 归一化缓存 key
        now = time.time()
        self._clean_expired_cache(now)

        norm_ignored = (
            ",".join(sorted(LocEngine._normalize_ignored(ignored))) if ignored else ""
        )
        cache_key = (
            platform.lower(),
            repo_path.lower(),
            (branch or "").lower(),
            norm_ignored,
        )

        if cache_key in self._cache:
            ts, cached_data = self._cache[cache_key]
            if now - ts <= self._cache_ttl:
                logger.info(f"[代码统计] 仓库命中缓存喵: {repo_path} ({platform})")
                return cached_data

        logger.info(
            f"[代码统计] 开始统计: 平台为 {platform}，仓库为 {repo_path}，"
            f"分支为 {branch or '默认分支'}，忽略：{ignored or '无'}"
        )

        engine = self._get_engine()

        try:
            result = await engine.get_repo_loc(
                repo_path=repo_path,
                platform=platform,
                branch=branch,
                ignored=ignored,
            )
            # 仅在成功获取数据列表时写入缓存
            if isinstance(result, list):
                self._cache[cache_key] = (now, result)
            return result
        except LocError as e:
            # 业务错误：message 本身即为面向用户的提示语
            logger.error(f"[代码统计] 统计失败: {str(e)}")
            return str(e)
        except asyncio.CancelledError:
            # 显式重新抛出 CancelledError，避免协程取消被静默吞没喵
            raise
        except Exception as e:  # noqa: BLE001
            logger.error(f"[代码统计] 未知异常: {str(e)}")
            return f"发生未知错误喵: {str(e)}"
