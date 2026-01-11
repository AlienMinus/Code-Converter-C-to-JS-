import re

HEADER_CAPABILITIES = {
    "stdio.h": {"printf", "scanf"},
    "math.h": {"sqrt", "pow", "sin", "cos", "tan"},
    "string.h": {"strlen", "strcpy", "strcmp"}
}

FORMAT_HANDLERS = {
    "%d": "Number",
    "%f": "Number",
    "%c": "Char",
    "%s": "String"
}


def remove_includes(code):
    return re.sub(r"#include\s*<.*?>", "", code)

def replace_variable_declarations(code):
    return re.sub(
        r"\b(int|float|double|char)\s+(\w+)\b",
        r"let \2",
        code
    )

def replace_main(code):
    return code.replace("int main()", "")

def replace_printf(code):
    return re.sub(r"printf\s*\(", "console.log(", code)

def replace_scanf(code):
    return re.sub(r"scanf\s*\(", "prompt(", code)

def remove_return_zero(code):
    return re.sub(r"\breturn\s+0\s*;", "", code)


def extract_main_body(code):
    start = code.find("int main")
    if start == -1:
        return ""

    brace_start = code.find("{", start)
    if brace_start == -1:
        return ""

    brace_count = 0
    body = []

    for i in range(brace_start, len(code)):
        if code[i] == "{":
            brace_count += 1
            if brace_count == 1:
                continue
        elif code[i] == "}":
            brace_count -= 1
            if brace_count == 0:
                break

        if brace_count >= 1:
            body.append(code[i])

    return "".join(body).strip()


def extract_non_main_functions(code):
    functions = re.findall(
        r"(void|int|float|double|char)\s+(\w+)\s*\([^)]*\)\s*\{[\s\S]*?\}",
        code
    )

    extracted = []
    for f in functions:
        if f[1] != "main":
            block = re.search(
                rf"{f[0]}\s+{f[1]}\s*\([^)]*\)\s*\{{[\s\S]*?\}}",
                code
            )
            if block:
                extracted.append(block.group(0))

    return "\n\n".join(extracted)

def convert_function_syntax(code):
    # Convert function declaration
    code = re.sub(
        r"(void|int|float|double|char)\s+(\w+)\s*\(([^)]*)\)",
        lambda m: f"function {m.group(2)}({remove_param_types(m.group(3))})",
        code
    )
    return code


def remove_param_types(param_str):
    if not param_str.strip():
        return ""

    params = param_str.split(",")
    clean_params = []

    for p in params:
        parts = p.strip().split()
        clean_params.append(parts[-1])  # keep variable name only

    return ", ".join(clean_params)

def convert_printf_to_template(code):
    def replacer(match):
        fmt = match.group(1)
        args = match.group(2)

        # No arguments → plain string
        if not args:
            return f"console.log(`{fmt}`);"

        arg_list = [a.strip() for a in args.split(",")]
        specs = re.findall(r"%[dfsci]", fmt)

        if len(specs) != len(arg_list):
            raise SyntaxError("printf format specifier mismatch")

        for spec, arg in zip(specs, arg_list):
            fmt = fmt.replace(spec, f"${{{arg}}}", 1)

        # 🔥 ALWAYS USE BACKTICKS
        return f"console.log(`{fmt}`);"

    return re.sub(
        r'printf\s*\(\s*"([^"]*)"\s*(?:,\s*(.*?))?\s*\)\s*;',
        replacer,
        code
    )

def collect_declared_variables(code):
    # int x;  int x = 5;
    decls = re.findall(r"\b(int|float|double|char)\s+(\w+)", code)
    return set(var for _, var in decls)


def find_variable_usages(code):
    return re.findall(r"\b[a-zA-Z_]\w*\b", code)

def replace_prompted_scanf(code):
    pattern = re.compile(
        r'printf\s*\(\s*"([^"]*)"\s*\)\s*;\s*'
        r'scanf\s*\(\s*"(%[dfc])"\s*,\s*&\s*(\w+)\s*\)\s*;',
        re.MULTILINE
    )

    def replacer(match):
        prompt_text = match.group(1)
        fmt = match.group(2)
        var = match.group(3)

        if fmt in ("%d", "%f"):
            return f'{var} = Number(prompt("{prompt_text}"));'

        if fmt == "%c":
            return f'{var} = prompt("{prompt_text}")[0];'
        if fmt == "%s":
            return f'{var} = prompt("{prompt_text}");'

        raise SyntaxError(f"Unsupported scanf format: {fmt}")

    return pattern.sub(replacer, code)

def replace_scanf(code):
    def replacer(match):
        fmt = match.group(1).strip()
        var = match.group(2).strip()

        if fmt == "%d" or fmt == "%f":
            return f"{var} = Number(prompt());"

        if fmt == "%c":
            return f"{var} = prompt()[0];"

        if fmt == "%s":
            return f"{var} = prompt();"


        raise SyntaxError(
            f"Unsupported scanf format: {fmt}. "
            "Only %d, %f, %c are supported."
        )

    return re.sub(
        r'scanf\s*\(\s*"([^"]+)"\s*,\s*&\s*(\w+)\s*\)\s*;',
        replacer,
        code
    )

def extract_headers(code):
    return set(re.findall(r'#include\s*<([^>]+)>', code))

def extract_function_calls(code):
    return set(re.findall(r'\b([a-zA-Z_]\w*)\s*\(', code))

C_KEYWORDS = {
    "if", "for", "while", "do", "switch", "case",
    "return", "sizeof"
}

def validate_headers(code):
    headers = extract_headers(code)
    used_functions = extract_function_calls(code)

    # Functions allowed by included headers
    allowed_functions = set()
    for h in headers:
        if h not in HEADER_CAPABILITIES:
            raise SyntaxError(f"Unknown header <{h}>")
        allowed_functions |= HEADER_CAPABILITIES[h]

    # Functions defined by user in the same file
    user_functions = set(re.findall(
        r'\b(?:void|int|float|double|char)\s+(\w+)\s*\(',
        code
    ))

    # Remove things that are NOT library calls
    used_functions -= C_KEYWORDS
    used_functions -= user_functions
    used_functions.discard("main")

    # ❌ Illegal library usage
    illegal = used_functions - allowed_functions

    if illegal:
        raise SyntaxError(
            f"Function(s) {', '.join(sorted(illegal))} used without proper header"
        )
    
def inject_header_runtime(js, headers, used_functions):
    runtime = []

    if "math.h" in headers:
        mapping = {
            "sqrt": "Math.sqrt",
            "pow": "Math.pow",
            "sin": "Math.sin",
            "cos": "Math.cos",
            "tan": "Math.tan"
        }

        for fn, impl in mapping.items():
            if fn in used_functions:
                runtime.append(f"const {fn} = {impl};")

    if runtime:
        return "\n".join(runtime) + "\n\n" + js

    return js

def extract_macros(code):
    return dict(re.findall(r'#define\s+(\w+)\s+(.+)', code))

def remove_macros(code):
    return re.sub(r'#define\s+\w+\s+.+', '', code)

def apply_macros(code, macros):
    for name, value in macros.items():
        code = re.sub(rf'\b{name}\b', f'({value})', code)
    return code

def extract_structs(code):
    """
    Extract struct definitions.
    Returns:
    {
        "Point": ["x", "y"]
    }
    """
    structs = {}
    pattern = re.compile(
        r'struct\s+(\w+)\s*\{([^}]+)\}\s*;',
        re.DOTALL
    )

    for name, body in pattern.findall(code):
        fields = []
        for line in body.split(";"):
            line = line.strip()
            if not line:
                continue
            # int x;  float y;
            parts = line.split()
            fields.append(parts[-1])
        structs[name] = fields

    return structs

def remove_struct_definitions(code):
    return re.sub(
        r'struct\s+\w+\s*\{[^}]+\}\s*;',
        '',
        code,
        flags=re.DOTALL
    )

def replace_struct_declarations(code, structs):
    """
    structs = {
        "Point": ["x", "y"],
        "Rect": ["w", "h"]
    }
    """
    for struct_name, fields in structs.items():
        pattern = rf'\b{struct_name}\s+(\w+)\s*;'

        def replacer(match):
            var = match.group(1)
            init = ", ".join(f"{f}: 0" for f in fields)
            return f"let {var} = {{ {init} }};"

        code = re.sub(pattern, replacer, code)

    return code

def extract_typedef_structs(code):
    """
    Extract typedef structs.
    Returns:
    {
        "Point": ["x", "y"]
    }
    """
    typedefs = {}

    pattern = re.compile(
        r'typedef\s+struct(?:\s+\w+)?\s*\{([^}]+)\}\s*(\w+)\s*;',
        re.DOTALL
    )

    for body, alias in pattern.findall(code):
        fields = []
        for line in body.split(";"):
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            fields.append(parts[-1])
        typedefs[alias] = fields

    return typedefs

def remove_typedef_structs(code):
    return re.sub(
        r'typedef\s+struct(?:\s+\w+)?\s*\{[^}]+\}\s*\w+\s*;',
        '',
        code,
        flags=re.DOTALL
    )

def extract_array_declarations(code):
    """
    int a[5];
    int a[3] = {1,2,3};
    """
    return re.findall(
        r'\b(int|float|double|char)\s+(\w+)\s*\[(\d+)\]\s*(=\s*\{[^}]+\})?\s*;',
        code
    )

def replace_array_declarations(code):
    def repl(match):
        _, name, size, init = match.groups()

        if init:
            values = init.split("{")[1].split("}")[0]
            return f"let {name} = [{values}];"
        else:
            return f"let {name} = Array({size}).fill(0);"

    return re.sub(
        r'\b(int|float|double|char)\s+(\w+)\s*\[(\d+)\]\s*(=\s*\{[^}]+\})?\s*;',
        repl,
        code
    )

def replace_struct_array_declarations(code, structs):
    """
    struct Point p[3];
    Point p[3];
    """
    for struct, fields in structs.items():
        pattern = rf'\b(struct\s+)?{struct}\s+(\w+)\s*\[(\d+)\]\s*;'

        def repl(match):
            var = match.group(2)
            size = int(match.group(3))
            obj = "{ " + ", ".join(f"{f}: 0" for f in fields) + " }"
            return f"let {var} = Array({size}).fill(null).map(()=>({obj}));"

        code = re.sub(pattern, repl, code)

    return code
