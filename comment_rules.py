"""各语言注释语法规则与逐行计数实现喵。

负责将文件文本按语言拆分为：代码行 / 注释行 / 空白行 / 总行数。
采用启发式规则，覆盖常见语言的 单行注释 与 块注释 语法。
注释识别为统计口径的近似实现，不保证与编译器解析完全一致喵。
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CommentSyntax:
    """某语言的注释语法定义。

    line:  单行注释起始标记元组（匹配去除首尾空白后行首）。
    block: 块注释 (起始标记, 结束标记) 元组列表，支持跨行。
    """

    line: tuple[str, ...] = ()
    block: tuple[tuple[str, str], ...] = ()


# 语言名 -> 注释语法规则
COMMENT_SYNTAX: dict[str, CommentSyntax] = {
    "Python": CommentSyntax(line=("#",), block=(('"""', '"""'), ("'''", "'''"))),
    "JavaScript": CommentSyntax(line=("//",), block=(("/*", "*/"),)),
    "TypeScript": CommentSyntax(line=("//",), block=(("/*", "*/"),)),
    "TypeScript Typings": CommentSyntax(line=("//",), block=(("/*", "*/"),)),
    "JSX": CommentSyntax(line=("//",), block=(("/*", "*/"),)),
    "TSX": CommentSyntax(line=("//",), block=(("/*", "*/"),)),
    "Java": CommentSyntax(line=("//",), block=(("/*", "*/"),)),
    "C": CommentSyntax(line=("//",), block=(("/*", "*/"),)),
    "C++": CommentSyntax(line=("//",), block=(("/*", "*/"),)),
    "C#": CommentSyntax(line=("//",), block=(("/*", "*/"),)),
    "Go": CommentSyntax(line=("//",), block=(("/*", "*/"),)),
    "Rust": CommentSyntax(line=("//",), block=(("/*", "*/"),)),
    "PHP": CommentSyntax(line=("//", "#"), block=(("/*", "*/"),)),
    "Swift": CommentSyntax(line=("//",), block=(("/*", "*/"),)),
    "Kotlin": CommentSyntax(line=("//",), block=(("/*", "*/"),)),
    "Dart": CommentSyntax(line=("//",), block=(("/*", "*/"),)),
    "Objective-C": CommentSyntax(line=("//",), block=(("/*", "*/"),)),
    "Scala": CommentSyntax(line=("//",), block=(("/*", "*/"),)),
    "Groovy": CommentSyntax(line=("//",), block=(("/*", "*/"),)),
    "Sass": CommentSyntax(line=("//",), block=(("/*", "*/"),)),
    "Less": CommentSyntax(line=("//",), block=(("/*", "*/"),)),
    "Stylus": CommentSyntax(line=("//",), block=(("/*", "*/"),)),
    "Shell": CommentSyntax(line=("#",)),
    "Ruby": CommentSyntax(line=("#",), block=(("=begin", "=end"),)),
    "Lua": CommentSyntax(line=("--",), block=(("--[[", "]]"),)),
    "Haskell": CommentSyntax(line=("--",), block=(("{-", "-}"),)),
    "Perl": CommentSyntax(line=("#",)),
    "R": CommentSyntax(line=("#",)),
    "SQL": CommentSyntax(line=("--",), block=(("/*", "*/"),)),
    "GraphQL": CommentSyntax(line=("#",)),
    "Fortran": CommentSyntax(line=("!",)),
    "Assembly": CommentSyntax(line=(";",)),
    "YAML": CommentSyntax(line=("#",)),
    "TOML": CommentSyntax(line=("#",)),
    "INI": CommentSyntax(line=("#", ";")),
    "CMake": CommentSyntax(line=("#",)),
    "Makefile": CommentSyntax(line=("#",)),
    "Dockerfile": CommentSyntax(line=("#",)),
    "Systemd": CommentSyntax(line=("#", ";")),
    "Batchfile": CommentSyntax(
        line=(
            "REM ",
            "rem ",
            "::",
            "echo off > nul",
        )
    ),
    "PowerShell": CommentSyntax(line=("#",), block=(("<#", "#>"),)),
    "HTML": CommentSyntax(block=(("<!--", "-->"),)),
    "XML": CommentSyntax(block=(("<!--", "-->"),)),
    "SVG": CommentSyntax(block=(("<!--", "-->"),)),
    "Vue": CommentSyntax(line=("//",), block=(("/*", "*/"), ("<!--", "-->"))),
    "CSS": CommentSyntax(block=(("/*", "*/"),)),
}


def _is_line_comment(line: str, markers: tuple[str, ...]) -> bool:
    """判断去除首尾空白后的行是否整行为单行注释喵。"""
    return any(line.startswith(m) for m in markers)


def _find_block_start(
    line: str, pairs: tuple[tuple[str, str], ...]
) -> tuple[int | None, int, str, str]:
    """在行内查找首个块注释起点喵。

    返回 (start_idx, end_idx, start_marker, end_marker)；
    start_idx 为 None 表示未命中；end_idx 为 -1 表示该行未闭合块。
    """
    best_idx: int | None = None
    best_end: int = -1
    best_start = ""
    best_end_marker = ""
    for start, end in pairs:
        idx = line.find(start)
        if idx == -1:
            continue
        if best_idx is None or idx < best_idx:
            best_idx = idx
            best_end = line.find(end, idx + len(start))
            best_start = start
            best_end_marker = end
    return best_idx, best_end, best_start, best_end_marker


def count_lines(content: str, language: str) -> tuple[int, int, int, int]:
    """统计文本的 (代码行, 注释行, 空白行, 总行数) 喵。

    启发式注释识别规则：
    - 空白行：去除首尾空白后为空字符串。
    - 单行注释：行首（去除前导空白）以指定标记开头。
    - 块注释：跨行状态机；支持单行内多段闭合与跨行状态流转。
    - 包含有效代码字符即优先判定为代码行，纯注释内容判定为注释行。
    """
    syntax = COMMENT_SYNTAX.get(language)
    if syntax is None:
        line_markers: tuple[str, ...] = ()
        block_pairs: tuple[tuple[str, str], ...] = ()
    else:
        line_markers = syntax.line
        block_pairs = syntax.block

    code = 0
    comments = 0
    blanks = 0
    total = 0

    in_block = False
    block_end = ""

    for raw_line in content.splitlines():
        total += 1
        line = raw_line.strip()

        if not line:
            blanks += 1
            continue

        if in_block:
            end_idx = line.find(block_end)
            if end_idx == -1:
                # 仍在块注释内且该行未闭合
                comments += 1
                continue

            # 块注释在该行闭合，提取闭合后的剩余内容继续解析
            in_block = False
            remaining = line[end_idx + len(block_end) :].strip()
            # 该行包含了注释部分
            has_comment = True
            has_code = False

            # 检查闭合后的尾部内容
            if remaining:
                if _is_line_comment(remaining, line_markers):
                    pass
                elif block_pairs:
                    # 尾部可能开启了新的块注释或包含代码
                    b_start_idx, b_end_idx, _, b_end = _find_block_start(
                        remaining, block_pairs
                    )
                    if b_start_idx is not None:
                        if b_start_idx > 0:
                            has_code = True
                        if b_end_idx == -1:
                            in_block = True
                            block_end = b_end
                    else:
                        has_code = True
                else:
                    has_code = True

            if has_code:
                code += 1
            elif has_comment:
                comments += 1
            continue

        # 1. 纯单行注释判断
        if _is_line_comment(line, line_markers):
            comments += 1
            continue

        # 2. 块注释起始扫描（支持行内多次嵌套或行首/行中块注释）
        if block_pairs:
            start_idx, end_idx, start, end = _find_block_start(line, block_pairs)
            if start_idx is not None:
                has_code = start_idx > 0  # 块注释前存在代码字符
                curr_line = line
                curr_start_idx = start_idx
                curr_end_idx = end_idx
                curr_end_marker = end

                while curr_start_idx is not None:
                    if curr_end_idx != -1:
                        # 块在当前行内闭合
                        after_text = curr_line[
                            curr_end_idx + len(curr_end_marker) :
                        ].strip()
                        if not after_text:
                            break
                        if _is_line_comment(after_text, line_markers):
                            break
                        # 检查后续是否还有下一个块注释
                        next_s_idx, next_e_idx, _, next_end = _find_block_start(
                            after_text, block_pairs
                        )
                        if next_s_idx is not None:
                            if next_s_idx > 0:
                                has_code = True
                            curr_line = after_text
                            curr_start_idx = next_s_idx
                            curr_end_idx = next_e_idx
                            curr_end_marker = next_end
                        else:
                            has_code = True
                            break
                    else:
                        # 块未闭合，跨行进入块状态
                        in_block = True
                        block_end = curr_end_marker
                        break

                if has_code:
                    code += 1
                else:
                    comments += 1
                continue

        # 3. 纯代码行
        code += 1

    return code, comments, blanks, total
