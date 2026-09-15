import re

JS_KEYWORDS = {
    "function", "return", "let", "const", "var",
    "if", "else", "for", "while", "do",
    "switch", "case", "default", "break", "continue",
    "new", "typeof", "instanceof", "this", "class",
    "get", "set", "constructor", "true", "false",
    "null", "undefined", "try", "catch", "finally", "throw",
    "in", "of"
}

JS_BUILTINS = {
    "console", "log", "Math", "prompt", "Array",
    "Number", "String", "Boolean", "Object", "Proxy",
    "parseInt", "parseFloat", "isNaN", "isFinite",
    "Error", "Date", "JSON", "RegExp", "NaN", "Infinity",
    "trunc", "sqrt", "pow", "sin", "cos", "tan", "floor", "ceil", "round",
    "abs", "min", "max", "random", "fromCharCode", "charCodeAt"
}

RUNTIME_HELPERS = {
    "__Ptr", "__ref", "__ref_arr", "__ref_prop",
    "__deref", "__set_deref", "__ptr_add", "__ptr_sub",
    "__sizeof", "NULL", "__v",
    # stdlib.h
    "malloc", "calloc", "free", "rand", "srand", "atoi", "atof", "exit",
    # string.h
    "strlen", "strcpy", "strcmp", "strcat", "strncpy", "strncmp",
    # ctype.h
    "toupper", "tolower", "isdigit", "isalpha", "isalnum", "isspace",
    # stdbool.h
    "bool"
}


def strip_strings_and_comments(code):
    # Remove single line comments
    code = re.sub(r"//.*", "", code)
    # Remove multi-line comments
    code = re.sub(r"/\*[\s\S]*?\*/", "", code)

    # Process template literals: keep ${...} content, strip plain text
    def clean_template(match):
        content = match.group(1)
        # Extract expressions inside ${...}
        exprs = re.findall(r"\$\{([^}]+)\}", content)
        return " " + " ".join(exprs) + " "

    code = re.sub(r"`([\s\S]*?)`", clean_template, code)

    # Remove double-quoted and single-quoted strings
    code = re.sub(r'"(?:\\.|[^"\\])*"', '""', code)
    code = re.sub(r"'(?:\\.|[^'\\])*'", "''", code)

    return code


def extract_js_declared_vars(code):
    declared = set()

    # match: let a = 1, b = 2; or const x = 5; or var y;
    decl_blocks = re.findall(r"\b(?:let|const|var)\s+([^;]+);", code)
    for block in decl_blocks:
        # Split on commas that are not inside parentheses/braces
        items = re.split(r",(?![^(]*\))", block)
        for item in items:
            item = item.strip()
            # item could be: a = 5 or *p or a
            m = re.match(r"([a-zA-Z_]\w*)", item)
            if m:
                declared.add(m.group(1))

    # match: for (let i = 0; ...)
    for_decls = re.findall(r"\bfor\s*\(\s*(?:let|var|const)\s+([a-zA-Z_]\w*)", code)
    for v in for_decls:
        declared.add(v)

    return declared


def extract_function_names(code):
    return set(re.findall(r"\bfunction\s+(\w+)", code))


def extract_function_params(code):
    params = set()
    matches = re.findall(r"\bfunction\s+\w*\s*\(([^)]*)\)", code)
    for m in matches:
        for p in m.split(","):
            p = p.strip()
            # Could be arrow function param or simple param
            name_m = re.search(r"\b([a-zA-Z_]\w*)\b", p)
            if name_m:
                params.add(name_m.group(1))
    return params


def find_variable_usages(code):
    # Strip strings and comments first
    clean_code = strip_strings_and_comments(code)

    # Remove object property access like .prop so prop isn't seen as a variable
    clean_code = re.sub(r"\.\s*[a-zA-Z_]\w*", "", clean_code)

    # Remove object literal keys like { prop: 0 } or { x: 10 }
    clean_code = re.sub(r"\b[a-zA-Z_]\w*\s*:", "", clean_code)

    # Remove arrow function parameter lists like ((a, b) => ...) or (v => ...)
    clean_code = re.sub(r"\([^)]*\)\s*=>", "", clean_code)
    clean_code = re.sub(r"\b[a-zA-Z_]\w*\s*=>", "", clean_code)

    # Find all identifier tokens
    tokens = re.findall(r"\b[a-zA-Z_]\w*\b", clean_code)
    return set(tokens)


def detect_undeclared_variables(code, declared_vars):
    used_vars = find_variable_usages(code)

    function_names = extract_function_names(code)
    function_params = extract_function_params(code)
    js_declared = extract_js_declared_vars(code)

    allowed = (
        declared_vars |
        js_declared |
        function_names |
        function_params |
        JS_KEYWORDS |
        JS_BUILTINS |
        RUNTIME_HELPERS
    )

    undeclared = used_vars - allowed
    return undeclared
