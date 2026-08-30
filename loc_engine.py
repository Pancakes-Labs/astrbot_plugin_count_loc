"""自建代码统计引擎喵。

不依赖任何第三方统计 API：直接从 GitHub / GitLab 官方归档地址下载仓库
压缩包，在内存中解压并逐文件、逐行统计 代码 / 注释 / 空白行 数，
最终输出与旧版 CodeTabs 兼容的数据结构，供上层格式化模块直接复用喵。
"""

import asyncio
import io
import os
import tarfile
import time
import zipfile
from urllib.parse import quote

import httpx

from astrbot.api import logger

from .comment_rules import count_lines
from .language_detector import LanguageDetector


class LocError(Exception):
    """自建统计引擎的业务错误，message 可直接面向用户展示喵。"""


def _decode_content(data: bytes) -> str | None:
    """将文件字节解码为文本；检测到二进制特征（NUL 字节）时返回 None 喵。"""
    if b"\x00" in data[:8192]:
        return None
    return data.decode("utf-8", errors="replace")


class LocEngine:
    """自建代码统计引擎。

    职责链：解析默认分支 -> 下载归档 -> 解压过滤 -> 逐行统计聚合。
    """

    # GitHub 官方接口
    GITHUB_API = "https://api.github.com/repos/{owner}/{repo}"
    GITHUB_ARCHIVE = (
        "https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{branch}"
    )
    # GitLab 官方接口
    GITLAB_API = "https://gitlab.com/api/v4/projects/{encoded_path}"
    GITLAB_ARCHIVE = (
        "https://gitlab.com/{full_path}/-/archive/{branch}/{basename}-{branch}.tar.gz"
    )

    def __init__(
        self,
        github_token: str = "",
        gitlab_token: str = "",
        max_archive_mb: int = 100,
        max_content_mb: int = 300,
        max_files: int = 50000,
        timeout: float = 60.0,
    ):
        """初始化引擎。

        参数:
            github_token: GitHub Personal Access Token（可选），提升 API 限额。
            gitlab_token: GitLab Personal Access Token（可选），提升 API 限额。
            max_archive_mb: 仓库归档压缩包的最大体积（MB），超限拒绝统计。
            max_content_mb: 单个文本文件的最大体积（MB），超限跳过该文件。
            max_files: 单个仓库允许解压统计的最大文件数上限。
            timeout: HTTP 请求超时时间（秒）。
        """
        # Token 配置：AstrBot 插件配置优先，回退到环境变量
        self.github_token = (
            github_token.strip()
            if github_token
            else os.environ.get("GITHUB_TOKEN", "").strip()
        )
        self.gitlab_token = (
            gitlab_token.strip()
            if gitlab_token
            else os.environ.get("GITLAB_TOKEN", "").strip()
        )
        self.max_archive_mb = max_archive_mb
        self.max_content_mb = max_content_mb
        self.max_archive_bytes = max_archive_mb * 1024 * 1024
        self.max_content_bytes = max_content_mb * 1024 * 1024
        self.max_files = max_files
        self.timeout = timeout
        # 归档下载缓存与默认分支缓存 (TTL 10分钟，归档缓存最多保留 2 个条目防内存占用)
        self._cache_ttl = 600
        self._max_archive_cache_entries = 2
        self._branch_cache: dict[str, tuple[float, str]] = {}
        self._archive_cache: dict[str, tuple[float, bytes]] = {}
        # 惰性初始化 AsyncClient，绑定调用时的 event loop 喵
        self.client: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------
    # HTTP 客户端管理
    # ------------------------------------------------------------------
    def _get_client(self) -> httpx.AsyncClient:
        """获取当前异步客户端实例（惰性创建）喵。"""
        if self.client is None or getattr(self.client, "is_closed", True):
            self.client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)
        return self.client

    async def close(self):
        """关闭客户端，释放连接池与内存缓存资源喵。"""
        self._branch_cache.clear()
        self._archive_cache.clear()
        if self.client and not getattr(self.client, "is_closed", False):
            try:
                await self.client.aclose()
            except Exception as e:  # noqa: BLE001
                logger.error(f"[代码统计] 释放资源时发生异常喵: {str(e)}")

    def _github_headers(self) -> dict[str, str]:
        """若配置了 GitHub Token 则携带鉴权头，提升 API 限额喵。"""
        if self.github_token:
            return {"Authorization": f"Bearer {self.github_token}"}
        return {}

    def _gitlab_headers(self) -> dict[str, str]:
        """若配置了 GitLab Token 则携带鉴权头，提升 API 限额喵。"""
        if self.gitlab_token:
            return {"PRIVATE-TOKEN": self.gitlab_token}
        return {}

    @staticmethod
    def _normalize_ignored(
        ignored: list[str] | str | None,
    ) -> list[str]:
        """将忽略项统一归一化为去空白后的字符串列表喵。"""
        if not ignored:
            return []
        raw_items = ignored.split(",") if isinstance(ignored, str) else ignored
        return [
            item.strip().strip("/")
            for item in raw_items
            if isinstance(item, str) and item.strip()
        ]

    @staticmethod
    def _parse_repo_path(repo_path: str) -> tuple[str, ...]:
        """将仓库路径按 / 拆分为多级子路径（兼容 GitLab 嵌套组）喵。"""
        normalized = repo_path.strip().strip("/")
        parts = [p for p in normalized.split("/") if p]
        if len(parts) < 2:
            raise LocError("请提供正确的仓库路径格式，例如 用户名/仓库名 喵！")
        return tuple(parts)

    # ------------------------------------------------------------------
    # 默认分支解析
    # ------------------------------------------------------------------
    async def _fetch_default_branch(
        self,
        cache_key: str,
        api_url: str,
        headers: dict[str, str],
        platform_name: str,
        is_private_fn,
    ) -> str:
        """通用的默认分支解析抽象方法，集成缓存、鉴权、错误处理与私有仓库拦截喵。"""
        now = time.time()
        if cache_key in self._branch_cache:
            ts, cached_branch = self._branch_cache[cache_key]
            if now - ts <= self._cache_ttl:
                return cached_branch

        client = self._get_client()
        logger.info(f"[代码统计] 正在查询 {platform_name} 默认分支: {api_url}")
        try:
            response = await client.get(api_url, headers=headers)
        except httpx.RequestError as e:
            raise LocError(
                f"网络连接异常，无法访问 {platform_name} API 喵。错误详情: {str(e)}"
            ) from e

        if response.status_code == 404:
            raise LocError("未找到该仓库，请检查路径是否正确，且仓库必须是公开的喵！")
        if response.status_code == 403:
            hint = "，或在插件配置中填写 Token 以提升配额！" if not headers else ""
            raise LocError(f"{platform_name} API 访问频率受限{hint}喵。可稍后再试。")
        response.raise_for_status()

        try:
            data = response.json()
        except ValueError as e:
            raise LocError(f"{platform_name} API 响应解析失败，请稍后再试喵！") from e

        if is_private_fn(data):
            raise LocError("本插件仅支持统计公开 (Public) 仓库喵！")

        branch = data.get("default_branch")
        if not branch:
            raise LocError(f"无法从 {platform_name} API 获取仓库的默认分支喵。")
        self._branch_cache[cache_key] = (now, branch)
        return branch

    async def _resolve_default_branch_github(self, owner: str, repo: str) -> str:
        """通过 GitHub API 查询仓库默认分支喵。"""
        return await self._fetch_default_branch(
            cache_key=f"github:{owner}/{repo}".lower(),
            api_url=self.GITHUB_API.format(owner=owner, repo=repo),
            headers=self._github_headers(),
            platform_name="GitHub",
            is_private_fn=lambda data: data.get("private") is True,
        )

    async def _resolve_default_branch_gitlab(self, full_path: str) -> str:
        """通过 GitLab API 查询仓库默认分支喵。"""
        encoded = quote(full_path, safe="")
        return await self._fetch_default_branch(
            cache_key=f"gitlab:{full_path}".lower(),
            api_url=self.GITLAB_API.format(encoded_path=encoded),
            headers=self._gitlab_headers(),
            platform_name="GitLab",
            is_private_fn=lambda data: bool(
                data.get("visibility") and data.get("visibility") != "public"
            ),
        )

    # ------------------------------------------------------------------
    # 归档下载与解压
    # ------------------------------------------------------------------
    async def _download_archive(
        self, url: str, headers: dict[str, str] | None = None
    ) -> bytes:
        """流式下载仓库归档压缩包字节流，支持归档内存缓存与实时体积熔断喵。"""
        now = time.time()
        # 清理过期缓存
        expired_keys = [
            k
            for k, (ts, _) in self._archive_cache.items()
            if now - ts > self._cache_ttl
        ]
        for k in expired_keys:
            self._archive_cache.pop(k, None)

        if url in self._archive_cache:
            ts, cached_bytes = self._archive_cache[url]
            if now - ts <= self._cache_ttl:
                size_mb = len(cached_bytes) / (1024 * 1024)
                logger.info(
                    f"[代码统计] 命中归档包内存缓存喵: {url} ({size_mb:.2f} MB)"
                )
                return cached_bytes

        client = self._get_client()
        logger.info(f"[代码统计] 正在流式下载仓库归档: {url}")
        req_headers = headers or {}
        try:
            async with client.stream("GET", url, headers=req_headers) as response:
                if response.status_code == 404:
                    raise LocError(
                        "未找到该仓库或分支，请检查仓库名、分支名是否正确，且仓库必须公开喵！"
                    )
                if response.status_code == 403:
                    raise LocError(
                        "访问仓库归档受限（HTTP 403），可能触发了速率限制或需要权限喵！"
                    )
                response.raise_for_status()

                chunks = []
                downloaded = 0
                async for chunk in response.aiter_bytes():
                    downloaded += len(chunk)
                    if downloaded > self.max_archive_bytes:
                        size_mb = downloaded / (1024 * 1024)
                        raise LocError(
                            f"仓库归档过大（已超过 {size_mb:.1f} MB），"
                            f"达到 {self.max_archive_mb} MB 统计上限，已提前终止下载喵！"
                        )
                    chunks.append(chunk)

                content = b"".join(chunks)
        except httpx.RequestError as e:
            raise LocError(
                f"网络连接异常，无法下载仓库归档喵。错误详情: {str(e)}"
            ) from e

        size_mb = len(content) / (1024 * 1024)
        logger.info(f"[代码统计] 归档下载完成，共 {size_mb:.2f} MB，开始解压统计喵。")
        # 控制归档缓存最大条目数
        if len(self._archive_cache) >= self._max_archive_cache_entries:
            oldest_key = min(
                self._archive_cache.keys(), key=lambda k: self._archive_cache[k][0]
            )
            self._archive_cache.pop(oldest_key, None)
        self._archive_cache[url] = (now, content)
        return content

    def _should_ignore(self, rel_path: str, ignored: list[str]) -> bool:
        """判断相对路径是否命中忽略规则（精确路径或任意层级目录匹配）喵。"""
        if not ignored:
            return False
        parts = rel_path.split("/")
        for ig in ignored:
            if ig == rel_path:
                return True
            # 忽略项作为目录名，匹配路径中任意层级（如 venv、node_modules）
            if ig in parts:
                return True
            # 忽略项是路径前缀（如 docs -> docs/xx）
            if rel_path.startswith(ig + "/"):
                return True
        return False

    @staticmethod
    def _strip_top_dir(path: str) -> str:
        """剥离 GitHub/GitLab 归档固有的顶层目录（如 repo-main/）喵。"""
        parts = path.split("/", 1)
        return parts[1] if len(parts) > 1 else ""

    def _is_effective_member(self, rel_path: str, ignored: list[str]) -> bool:
        """过滤有效统计成员（排除空路径、系统隐藏垃圾与用户忽略项）喵。"""
        if not rel_path:
            return False
        if rel_path.startswith("__MACOSX/") or rel_path.endswith(".DS_Store"):
            return False
        if self._should_ignore(rel_path, ignored):
            return False
        return True

    def _iter_zip_members(self, data: bytes):
        """流式迭代 zip 归档中的有效文件成员喵。"""
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                for info in zf.infolist():
                    if info.is_dir():
                        continue
                    rel_path = self._strip_top_dir(info.filename.replace("\\", "/"))
                    yield rel_path, info.file_size, lambda inf=info: zf.read(inf)
        except zipfile.BadZipFile as e:
            raise LocError("仓库归档不是有效的 zip 格式，统计失败喵！") from e

    def _iter_tar_members(self, data: bytes):
        """流式迭代 tar.gz 归档中的有效文件成员喵。"""
        try:
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as tf:
                for member in tf.getmembers():
                    if member.isdir() or member.islnk() or member.issym():
                        continue
                    rel_path = self._strip_top_dir(member.name.replace("\\", "/"))

                    def read_tar_member(m=member) -> bytes:
                        fobj = tf.extractfile(m)
                        if fobj is None:
                            return b""
                        return fobj.read()

                    yield rel_path, member.size, read_tar_member
        except tarfile.TarError as e:
            raise LocError("仓库归档不是有效的 tar 格式，统计失败喵！") from e

    def _process_archive_stream(
        self, member_iterator, ignored: list[str]
    ) -> dict[str, dict]:
        """通用的归档流解压统计驱动，统一处理过滤、计数熔断、体积预检与聚合喵。"""
        totals: dict[str, dict] = {}
        processed_files = 0
        for rel_path, file_size, read_func in member_iterator:
            if not self._is_effective_member(rel_path, ignored):
                continue

            processed_files += 1
            if processed_files > self.max_files:
                logger.warning(
                    f"[代码统计] 仓库包含文件数超过安全上限 {self.max_files}，终止后续文件解压喵！"
                )
                break

            if file_size > self.max_content_bytes:
                logger.warning(
                    f"[代码统计] 文件超过 {self.max_content_mb} MB 限制，已跳过解压: "
                    f"{rel_path} ({file_size / 1024 / 1024:.1f} MB)"
                )
                continue

            try:
                content = read_func()
            except Exception:  # noqa: BLE001
                logger.warning(f"[代码统计] 文件解压失败，已跳过: {rel_path}")
                continue
            self._count_file(rel_path, content, totals)
        return totals

    def _process_zip(self, data: bytes, ignored: list[str]) -> dict[str, dict]:
        """解压并统计 zip 归档（GitHub codeload）喵。"""
        return self._process_archive_stream(self._iter_zip_members(data), ignored)

    def _process_tar(self, data: bytes, ignored: list[str]) -> dict[str, dict]:
        """解压并统计 tar.gz 归档（GitLab archive）喵。"""
        return self._process_archive_stream(self._iter_tar_members(data), ignored)

    # ------------------------------------------------------------------
    # 单文件计数与聚合
    # ------------------------------------------------------------------
    def _count_file(
        self, rel_path: str, content: bytes, totals: dict[str, dict]
    ) -> None:
        """对单个文件计数并聚合到 totals 字典喵。"""
        if len(content) > self.max_content_bytes:
            logger.warning(
                f"[代码统计] 文件超过 {self.max_content_mb} MB 限制，已跳过: "
                f"{rel_path} ({len(content) / 1024 / 1024:.1f} MB)"
            )
            return

        text = _decode_content(content)
        if text is None:
            return

        language = LanguageDetector.detect(rel_path)
        code, comments, blanks, _total = count_lines(text, language)

        entry = totals.get(language)
        if entry is None:
            entry = {
                "language": language,
                "files": 0,
                "code": 0,
                "comments": 0,
                "blanks": 0,
            }
            totals[language] = entry
        entry["files"] += 1
        entry["code"] += code
        entry["comments"] += comments
        entry["blanks"] += blanks

    @staticmethod
    def _to_codetabs(totals: dict[str, dict]) -> list[dict]:
        """将内部聚合结果转换为与 CodeTabs 兼容的扁平列表结构喵。"""
        items = sorted(totals.values(), key=lambda x: x["code"], reverse=True)
        data = []
        for entry in items:
            code = entry["code"]
            comments = entry["comments"]
            blanks = entry["blanks"]
            data.append(
                {
                    "language": entry["language"],
                    "files": entry["files"],
                    "linesOfCode": code,
                    "comments": comments,
                    "blanks": blanks,
                    "lines": code + comments + blanks,
                }
            )

        tot_files = sum(e["files"] for e in data)
        tot_code = sum(e["linesOfCode"] for e in data)
        tot_comments = sum(e["comments"] for e in data)
        tot_blanks = sum(e["blanks"] for e in data)
        data.append(
            {
                "language": "Total",
                "files": tot_files,
                "lines": tot_code + tot_comments + tot_blanks,
                "blanks": tot_blanks,
                "comments": tot_comments,
                "linesOfCode": tot_code,
            }
        )
        return data

    # ------------------------------------------------------------------
    # 对外主入口
    # ------------------------------------------------------------------
    async def get_repo_loc(
        self,
        repo_path: str,
        platform: str = "github",
        branch: str | None = None,
        ignored: list[str] | str | None = None,
    ) -> list[dict[str, int | str]]:
        """统计指定仓库的代码行数，返回与 CodeTabs 兼容的数据列表喵。

        参数:
            repo_path: 仓库路径，如 "username/reponame"（GitLab 支持多级组）。
            platform: "github" 或 "gitlab"。
            branch: 指定分支；缺省时自动查询仓库默认分支。
            ignored: 忽略的文件/目录（列表或逗号分隔字符串）。

        返回:
            扁平语言统计列表，最后一项为 Total。
            失败时抛出 LocError（message 可直接面向用户展示）。
        """
        if platform not in ("github", "gitlab"):
            platform = "github"

        parts = self._parse_repo_path(repo_path)
        ignore_list = self._normalize_ignored(ignored)

        if platform == "github":
            if len(parts) != 2:
                raise LocError("GitHub 仓库路径格式应为 用户名/仓库名 喵！")
            owner, repo = parts[0], parts[1]
            if not branch:
                branch = await self._resolve_default_branch_github(owner, repo)
            archive_url = self.GITHUB_ARCHIVE.format(
                owner=owner, repo=repo, branch=quote(branch)
            )
            data = await self._download_archive(
                archive_url, headers=self._github_headers()
            )
            # 使用 asyncio.to_thread 将 CPU 密集解压与文本统计移出主事件循环喵
            totals = await asyncio.to_thread(self._process_zip, data, ignore_list)
        else:
            full_path = "/".join(parts)
            if not branch:
                branch = await self._resolve_default_branch_gitlab(full_path)
            basename = parts[-1]
            # ref 段转义所有斜杠，文件名段将斜杠转换为中划线
            ref_encoded = quote(branch, safe="")
            basename_encoded = quote(basename, safe="")
            name_branch = quote(branch.replace("/", "-"), safe="")
            archive_url = (
                f"https://gitlab.com/{full_path}/-/archive/{ref_encoded}/"
                f"{basename_encoded}-{name_branch}.tar.gz"
            )
            data = await self._download_archive(
                archive_url, headers=self._gitlab_headers()
            )
            # 使用 asyncio.to_thread 将 CPU 密集解压与文本统计移出主事件循环喵
            totals = await asyncio.to_thread(self._process_tar, data, ignore_list)

        return self._to_codetabs(totals)
