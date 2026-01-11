from tokenizer import find_variable_usages
import re

JS_KEYWORDS = {
    "function", "return", "let", "const", "var",
    "if", "else", "for", "while", "do",
    "switch", "case", "break", "continue"
}

JS_BUILTINS = {
    "console", "log", "Math", "prompt"
}


def extract_function_names(code):
    return set(re.findall(r"function\s+(\w+)", code))


def extract_function_params(code):
    params = set()
    matches = re.findall(r"function\s+\w+\s*\(([^)]*)\)", code)
    for m in matches:
        for p in m.split(","):
            if p.strip():
                params.add(p.strip())
    return params


def detect_undeclared_variables(code, declared_vars):
    used_vars = set(find_variable_usages(code))

    function_names = extract_function_names(code)
    function_params = extract_function_params(code)

    allowed = (
        declared_vars |
        function_names |
        function_params |
        JS_KEYWORDS |
        JS_BUILTINS
    )

    undeclared = used_vars - allowed
    return undeclared
