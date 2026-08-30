import asyncio
import time

import astrbot.api.message_components as Comp
from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.provider import ProviderRequest
from astrbot.api.star import Context, Star

from .command_parser import CommandParser
from .data_formatter import DataFormatter

# 导入我们的自定义多模块组件喵
from .repo_client import RepoClient


class CountLocPlugin(Star):
    """
    AstrBot 代码行数统计分析插件。
    可以一键分析 GitHub 或 GitLab 上的公开仓库代码，支持分支选择和忽略项过滤喵！
    """

    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)
        self.config = config or {}
        self.repo_client = RepoClient(config=self.config)
        self.command_parser = CommandParser()
        # 全局统计并发信号量，最多允许同时执行 2 个仓库的统计计算喵
        self._semaphore = asyncio.Semaphore(2)
        # 用户冷却防抖记录: sender_id -> last_timestamp
        self._user_cooldown: dict[str, float] = {}
        self._cooldown_seconds = 3.0

    async def initialize(self):
        """异步初始化方法"""
        logger.info("[代码统计] 插件初始化成功喵！")

    @filter.on_llm_request()
    async def inject_code_statistics_tool_prompt(
        self, event: AstrMessageEvent, req: ProviderRequest
    ):
        """在 LLM 请求前注入工具使用提示，提升自动调用命中率喵。"""
        instruction = (
            "\n\n[CountLOC (代码统计)工具使用规范]\n"
            "- 当用户想统计某个 GitHub/GitLab 仓库的代码量、查询文件行数、或者进行代码分析等请求时，你可以调用 `query_code_statistics` 工具来获取最新的代码统计数据。\n"
            "- 该工具包含以下参数：\n"
            "  - repo_path (string, 必须): 格式为 用户名/仓库 或 组织名/仓库名（例如 DBJD-CR/astrbot_plugin_count_loc）。\n"
            "  - platform (string, 可选): 仓库托管平台，默认为 github，如果用户明确提到了 GitLab，可以传入 gitlab。\n"
            "  - branch (string, 可选): 仓库的分支名（如 main、master、dev 等），不传则使用仓库默认分支。\n"
            "  - ignored (string, 可选): 忽略的文件或文件夹路径，多个以英文逗号分隔，不填则不忽略。\n"
            "- 获得工具执行结果后，请根据得到的数据，按你的人设组织回复。\n"
        )
        req.system_prompt = req.system_prompt or ""
        if "[CountLOC" not in req.system_prompt:
            req.system_prompt += instruction

    @filter.llm_tool(name="query_code_statistics")
    async def query_code_statistics_tool(
        self,
        event: AstrMessageEvent,
        repo_path: str,
        platform: str = "github",
        branch: str | None = None,
        ignored: str | None = None,
    ) -> str:
        """获取指定 GitHub 或 GitLab 仓库的代码行数、文件数和注释行数等统计分析信息喵。

        Args:
            repo_path(string): 格式为 用户名/仓库名 的仓库路径（例如 DBJD-CR/astrbot_plugin_count_loc）。
            platform(string): 仓库托管平台，默认为 github，支持 github 或 gitlab。
            branch(string): 要查询的特定分支（可选，不填则为默认分支）。
            ignored(string): 忽略的文件或文件夹，多个用逗号分隔（可选）。
        """
        # 0. 调用 CommandParser 统一的清洗职责进行预处理喵
        repo_path = CommandParser.clean_repo_path(repo_path)

        platform = platform.lower() if platform else "github"
        if platform not in ["github", "gitlab"]:
            platform = "github"

        logger.info(
            f"[代码统计] LLM 触发了代码统计查询，目标仓库是 {repo_path}，平台是 {platform}，分支是 {branch or '默认分支'}，忽略项是 {ignored or '无忽略项'}"
        )

        # 1. 验证参数
        if not repo_path or "/" not in repo_path:
            return "统计失败，原因: 请提供正确的仓库路径格式，例如 用户名/仓库名 。"

        # 2. 发送请求获取数据（在并发限流保护下执行）
        async with self._semaphore:
            result = await self.repo_client.get_repo_loc(
                repo_path=repo_path,
                platform=platform,
                branch=branch,
                ignored=ignored,
            )

        # 3. 根据请求结果处理
        if isinstance(result, str):
            return f"统计失败，错误原因: {result}"

        # 4. 格式化统计结果并返回给大模型
        report_text = DataFormatter.format_loc_report(
            data=result,
            repo_path=repo_path,
            platform=platform,
            branch=branch,
            ignored=ignored,
        )
        return report_text

    # 注册“代码统计”指令，并提供别名：codeloc, 测代码, 统计代码, loc
    @filter.command("代码统计", alias={"codeloc", "测代码", "统计代码", "loc"})
    async def code_statistics(self, event: AstrMessageEvent):
        """分析指定 GitHub/GitLab 仓库的代码行数、文件数和注释喵。

        用法:
        /代码统计 <用户名>/<仓库名> [选项]

        选项:
        -b, --branch <分支名>   指定分支（默认 master/main）
        -i, --ignore <忽略项>   忽略的文件或文件夹，逗号分隔
        -g, --gitlab           使用 GitLab 平台（默认 GitHub）
        """
        sender_id = str(event.get_sender_id())
        now = time.time()
        last_time = self._user_cooldown.get(sender_id, 0)
        if now - last_time < self._cooldown_seconds:
            yield event.plain_result("⏳ 操作太频繁了喵，请稍等片刻再试哦！")
            return
        self._user_cooldown[sender_id] = now

        message_str = event.message_str.strip()

        # 1. 使用 CommandParser 解析用户输入
        repo_path, options, error_msg = self.command_parser.parse_args(message_str)

        if error_msg:
            # 如果有解析错误（例如用户直接打了 "/代码统计"），回复帮助提示
            yield event.plain_result(error_msg)
            return

        # 2. 友好地提示用户正在查询中
        platform_name = "GitLab" if options.get("platform") == "gitlab" else "GitHub"
        branch_info = (
            f"，分支: {options.get('branch')}" if options.get("branch") else ""
        )
        yield event.plain_result(
            f"🔍 正在为您努力测算 {platform_name} 仓库 {repo_path} {branch_info} 的代码行数，请稍候喵..."
        )

        # 3. 发送请求获取数据（在并发限流保护下执行）
        async with self._semaphore:
            result = await self.repo_client.get_repo_loc(
                repo_path=repo_path,
                platform=options.get("platform", "github"),
                branch=options.get("branch"),
                ignored=options.get("ignored"),
            )

        # 4. 根据请求结果判断与处理
        if isinstance(result, str):
            # 返回字符串代表 API 报错或者抓取失败
            yield event.plain_result(f"❌ 统计失败了喵。\n原因: {result}")
            return

        # 5. 格式化统计结果
        report_text = DataFormatter.format_loc_report(
            data=result,
            repo_path=repo_path,
            platform=options.get("platform", "github"),
            branch=options.get("branch"),
            ignored=options.get("ignored"),
        )

        # 6. 使用群合并转发消息（转发节点）回复（若平台和协议端支持），保证群聊版面整洁！
        try:
            self_id = int(event.get_self_id())
        except (ValueError, TypeError):
            self_id = 0

        try:
            # 构造群合并转发节点 Node
            node = Comp.Node(
                uin=self_id, name="代码统计", content=[Comp.Plain(report_text)]
            )
            # 发送消息链
            yield event.chain_result([node])
        except Exception as e:
            logger.warning(
                f"[代码统计] 使用转发节点发送失败，回退为普通纯文本消息发送喵。({str(e)})"
            )
            yield event.plain_result(report_text)

    async def terminate(self):
        """销毁方法"""
        await self.repo_client.close()
        logger.info("[代码统计] 插件已被安全停用喵。")
