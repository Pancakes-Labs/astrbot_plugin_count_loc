"""语言检测模块喵。

负责根据仓库文件相对路径判定其所属语言名称，供自建统计引擎使用。
与 language_colors.py 解耦：后者仅负责“语言名 -> 颜色”的展示映射，
本模块仅负责“路径 -> 语言名”的识别映射喵。
"""

from typing import ClassVar


class LanguageDetector:
    """根据文件相对路径检测语言名称喵。"""

    # 扩展名（含点、小写）-> 语言名
    EXTENSION_TO_LANGUAGE: ClassVar[dict[str, str]] = {
        # Python 系
        ".py": "Python",
        ".pyi": "Python",
        ".pyw": "Python",
        ".pyx": "Python",
        # JavaScript / TypeScript 系
        ".js": "JavaScript",
        ".mjs": "JavaScript",
        ".cjs": "JavaScript",
        ".jsx": "JSX",
        ".ts": "TypeScript",
        ".mts": "TypeScript",
        ".cts": "TypeScript",
        ".tsx": "TSX",
        # 前端
        ".html": "HTML",
        ".htm": "HTML",
        ".vue": "Vue",
        ".css": "CSS",
        ".scss": "Sass",
        ".sass": "Sass",
        ".less": "Less",
        ".styl": "Stylus",
        # JVM 系
        ".java": "Java",
        ".kt": "Kotlin",
        ".kts": "Kotlin",
        ".scala": "Scala",
        ".groovy": "Groovy",
        # C 系
        ".c": "C",
        ".h": "C",
        ".cpp": "C++",
        ".cc": "C++",
        ".cxx": "C++",
        ".hpp": "C++",
        ".hh": "C++",
        ".cs": "C#",
        # 系统级 / 主流语言
        ".go": "Go",
        ".rs": "Rust",
        ".php": "PHP",
        ".rb": "Ruby",
        ".swift": "Swift",
        ".m": "Objective-C",
        ".mm": "Objective-C",
        ".dart": "Dart",
        # 脚本 / Shell
        ".sh": "Shell",
        ".bash": "Shell",
        ".zsh": "Shell",
        ".fish": "Shell",
        ".ps1": "PowerShell",
        ".psm1": "PowerShell",
        ".bat": "Batchfile",
        ".cmd": "Batchfile",
        # 文档 / 配置
        ".md": "Markdown",
        ".markdown": "Markdown",
        ".yml": "YAML",
        ".yaml": "YAML",
        ".json": "JSON",
        ".toml": "TOML",
        ".ini": "INI",
        ".cfg": "INI",
        ".xml": "XML",
        ".svg": "SVG",
        ".txt": "Plain Text",
        ".text": "Plain Text",
        # 数据 / 查询
        ".sql": "SQL",
        ".graphql": "GraphQL",
        # 构建系统
        ".cmake": "CMake",
        ".mk": "Makefile",
        # 汇编 / 老牌
        ".asm": "Assembly",
        ".s": "Assembly",
        ".f": "Fortran",
        ".f90": "Fortran",
        ".f95": "Fortran",
        ".f03": "Fortran",
        # 函数式
        ".hs": "Haskell",
        ".lua": "Lua",
        ".pl": "Perl",
        ".pm": "Perl",
        ".r": "R",
        # Docker / 系统服务
        ".dockerfile": "Dockerfile",
        ".service": "Systemd",
    }

    # 特殊文件名（basename 全小写）-> 语言名
    FILENAME_TO_LANGUAGE: ClassVar[dict[str, str]] = {
        "dockerfile": "Dockerfile",
        "makefile": "Makefile",
        "gnumakefile": "Makefile",
        "justfile": "Makefile",
        "gemfile": "Ruby",
        "rakefile": "Ruby",
        "vagrantfile": "Ruby",
        "cmakelists.txt": "CMake",
        "license": "License",
        "license.txt": "License",
        "license.md": "License",
        "license.mit": "License",
        "readme": "Markdown",
        ".dockerignore": "Docker ignore",
        ".editorconfig": "INI",
        ".gitignore": "Plain Text",
        ".gitattributes": "Plain Text",
        ".gitmodules": "Plain Text",
        "procfile": "Plain Text",
        "pipfile": "TOML",
        "poetry.lock": "TOML",
    }

    @classmethod
    def detect(cls, rel_path: str) -> str:
        """根据仓库内相对路径判定语言名称喵。

        判定优先级：特殊文件名 -> 复合扩展名(.d.ts) -> 常规扩展名 -> 未知无扩展名回退为 Plain Text。
        """
        base = rel_path.rsplit("/", 1)[-1]
        low = base.lower()

        # 1. 特殊文件名优先
        if low in cls.FILENAME_TO_LANGUAGE:
            return cls.FILENAME_TO_LANGUAGE[low]

        # 2. 复合扩展名（.d.ts 需先于 .ts 判定）
        if low.endswith(".d.ts"):
            return "TypeScript Typings"

        # 3. 常规扩展名
        if "." in base and not base.startswith("."):
            ext = base.rsplit(".", 1)[-1].lower()
            lang = cls.EXTENSION_TO_LANGUAGE.get("." + ext)
            if lang:
                return lang
            return "Plain Text"

        # 4. 无扩展名或隐藏文件未命中特殊表：统一回退为 Plain Text 喵
        return "Plain Text"
