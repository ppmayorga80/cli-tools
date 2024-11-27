import pyperclip
import re


def simple_latex_eq_compiler(content: str):
    patterns = [
        (r'\\begin{aligned}', r'\\end{aligned}'),
        (r'\\begin{aligned\*}', r'\\end{aligned\*}'),
        (r'\\begin{align}', r'\\end{align'),
        (r'\\begin{align\*}', r'\\end{align\*}'),
    ]
    changes = 0
    for start_pattern, end_pattern in patterns:
        for rl in re.finditer(start_pattern, content):
            a, b = rl.span()
            if not content[a - 1:].startswith("$") and not content[a - 2:].startswith("$$"):
                n1 = content.count('$$', 0, a)
                n2 = content.count('$', 0, a)
                assert n1 % 2 == n2 % 2 == 0, f"$ or $$ does not match before position {a}: {start_pattern}"

                normal_end_pattern = end_pattern.replace(r'\*',r'*').encode('utf-8').decode('unicode_escape')
                c = content.find(normal_end_pattern, b)
                d = c + len(normal_end_pattern)
                eqn = content[a:d]

                new_content = content[:a] + f"$${eqn}$$" + content[d:]
                content = new_content
                changes += 1
    if changes > 0:
        return simple_latex_eq_compiler(content)

    return content


def fix_math_latex_expressions(text: str) -> str:
    text = text.replace("\(", "$")
    text = text.replace("\)", "$")
    text = text.replace("\[", "$$")
    text = text.replace("\]", "$$")
    return text


def fix_latex_list_to_md(text: str) -> str:
    text = text.replace("\item", "\n+ ")
    return text


def remove_quotes(text: str) -> str:
    if text.startswith('"'):
        text = text[1:]
        return remove_quotes(text)
    if text.endswith('"'):
        text = text[:-1]
        return remove_quotes(text)
    return text


def fix_md_from_clipboard() -> str or None:
    content = pyperclip.paste()
    if content is None:
        return

    new_content = content
    new_content = remove_quotes(new_content)
    new_content = fix_math_latex_expressions(new_content)
    new_content = fix_latex_list_to_md(new_content)
    new_content = simple_latex_eq_compiler(new_content)

    pyperclip.copy(new_content)


if __name__ == '__main__':
    fix_md_from_clipboard()
