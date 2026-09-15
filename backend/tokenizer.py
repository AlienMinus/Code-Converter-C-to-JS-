import re

HEADER_CAPABILITIES = {
    "stdio.h": {"printf", "scanf", "puts", "getchar", "putchar"},
    "math.h": {"sqrt", "pow", "sin", "cos", "tan", "floor", "ceil", "round", "abs", "log", "exp"},
    "string.h": {"strlen", "strcpy", "strcmp", "strcat", "strncpy", "strncmp"},
    "stdlib.h": {"malloc", "calloc", "free", "abs", "rand", "srand", "atoi", "atof", "exit"},
    "ctype.h": {"toupper", "tolower", "isdigit", "isalpha", "isalnum", "isspace"},
    "stdbool.h": {"bool"},
    "limits.h": set()
}

RUNTIME_CORE = """
class __Ptr {
    constructor(getter, setter, arr = null, idx = 0) {
        this._getter = getter;
        this._setter = setter;
        this._arr = arr;
        this._idx = idx;
        return new Proxy(this, {
            get(target, prop) {
                if (prop in target) return target[prop];
                const i = Number(prop);
                if (!isNaN(i)) {
                    if (target._arr) return target._arr[target._idx + i];
                }
                if (target._getter) {
                    const obj = target._getter();
                    if (obj && typeof obj === 'object') return obj[prop];
                }
                return undefined;
            },
            set(target, prop, value) {
                const i = Number(prop);
                if (!isNaN(i)) {
                    if (target._arr) {
                        target._arr[target._idx + i] = value;
                        return true;
                    }
                }
                if (target._getter) {
                    const obj = target._getter();
                    if (obj && typeof obj === 'object') {
                        obj[prop] = value;
                        return true;
                    }
                }
                target[prop] = value;
                return true;
            }
        });
    }
    get val() {
        if (this._arr !== null) return this._arr[this._idx];
        return this._getter ? this._getter() : undefined;
    }
    set val(v) {
        if (this._arr !== null) this._arr[this._idx] = v;
        else if (this._setter) this._setter(v);
    }
}
function __ref(getter, setter) {
    return new __Ptr(getter, setter);
}
function __ref_arr(arr, idx = 0) {
    return new __Ptr(null, null, arr, idx);
}
function __ref_prop(obj, prop) {
    return new __Ptr(() => obj[prop], v => { obj[prop] = v; });
}
function __deref(p) {
    if (p && typeof p === 'object' && 'val' in p) return p.val;
    return p;
}
function __set_deref(p, v) {
    if (p && typeof p === 'object' && 'val' in p) {
        p.val = v;
        return v;
    }
    return v;
}
function __ptr_add(p, n) {
    if (p instanceof __Ptr && p._arr !== null) {
        return new __Ptr(null, null, p._arr, p._idx + n);
    }
    return p + n;
}
function __ptr_sub(p, n) {
    return __ptr_add(p, -n);
}
function __sizeof(val) {
    if (val === null || val === undefined) return 8;
    if (Array.isArray(val)) return val.length * 4;
    if (typeof val === 'number') return 4;
    if (typeof val === 'string') return val.length;
    if (typeof val === 'boolean') return 1;
    if (typeof val === 'object') return Object.keys(val).length * 4;
    return 8;
}
const NULL = null;
"""

HEADER_RUNTIMES = {
    "stdlib.h": """
const malloc = (bytes) => new Array(Math.ceil(bytes / 4) || 1).fill(0);
const calloc = (num, size) => new Array(num * size).fill(0);
const free = (ptr) => {};
const abs = Math.abs;
const rand = () => Math.floor(Math.random() * 32768);
const srand = (seed) => {};
const atoi = (str) => parseInt(str, 10) || 0;
const atof = (str) => parseFloat(str) || 0.0;
const exit = (code) => { throw new Error(`Process exited with code ${code}`); };
""",
    "string.h": """
const strlen = (s) => (typeof s === 'string' ? s.length : (Array.isArray(s) ? (s.indexOf(0) !== -1 ? s.indexOf(0) : s.length) : 0));
const strcpy = (dest, src) => {
    if (Array.isArray(dest)) {
        for (let i = 0; i < src.length; i++) dest[i] = typeof src === 'string' ? src.charCodeAt(i) : src[i];
        dest[src.length] = 0;
        return dest;
    }
    return src;
};
const strcmp = (s1, s2) => {
    const str1 = typeof s1 === 'string' ? s1 : (Array.isArray(s1) ? String.fromCharCode(...s1.filter(c => c !== 0)) : String(s1));
    const str2 = typeof s2 === 'string' ? s2 : (Array.isArray(s2) ? String.fromCharCode(...s2.filter(c => c !== 0)) : String(s2));
    return str1.localeCompare(str2);
};
const strcat = (dest, src) => {
    if (Array.isArray(dest)) {
        let start = strlen(dest);
        for (let i = 0; i < src.length; i++) dest[start + i] = typeof src === 'string' ? src.charCodeAt(i) : src[i];
        dest[start + src.length] = 0;
        return dest;
    }
    return (dest || "") + (src || "");
};
const strncpy = strcpy;
const strncmp = strcmp;
""",
    "ctype.h": """
const toupper = (c) => typeof c === 'number' ? String.fromCharCode(c).toUpperCase().charCodeAt(0) : (typeof c === 'string' ? c.toUpperCase() : c);
const tolower = (c) => typeof c === 'number' ? String.fromCharCode(c).toLowerCase().charCodeAt(0) : (typeof c === 'string' ? c.toLowerCase() : c);
const isdigit = (c) => { const ch = typeof c === 'number' ? String.fromCharCode(c) : String(c); return /\\d/.test(ch) ? 1 : 0; };
const isalpha = (c) => { const ch = typeof c === 'number' ? String.fromCharCode(c) : String(c); return /[a-zA-Z]/.test(ch) ? 1 : 0; };
const isalnum = (c) => { const ch = typeof c === 'number' ? String.fromCharCode(c) : String(c); return /[a-zA-Z0-9]/.test(ch) ? 1 : 0; };
const isspace = (c) => { const ch = typeof c === 'number' ? String.fromCharCode(c) : String(c); return /\\s/.test(ch) ? 1 : 0; };
""",
    "math.h": """
const sqrt = Math.sqrt;
const pow = Math.pow;
const sin = Math.sin;
const cos = Math.cos;
const tan = Math.tan;
const floor = Math.floor;
const ceil = Math.ceil;
const round = Math.round;
const log = Math.log;
const exp = Math.exp;
""",
    "limits.h": """
const INT_MAX = 2147483647;
const INT_MIN = -2147483648;
const CHAR_BIT = 8;
"""
}

def remove_comments(code):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " "
        return s
    pattern = re.compile(r'//.*?$|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', re.MULTILINE)
    return pattern.sub(replacer, code)

def extract_headers(code):
    return set(re.findall(r'#include\s*<([^>]+)>', code))

def remove_includes(code):
    return re.sub(r'#include\s*<.*?>', '', code)

def extract_function_calls(code):
    return set(re.findall(r'\b([a-zA-Z_]\w*)\s*\(', code))

C_KEYWORDS = {
    "if", "else", "for", "while", "do", "switch", "case", "default",
    "return", "sizeof", "break", "continue", "typedef", "struct", "enum"
}

def validate_headers(code):
    headers = extract_headers(code)
    used_functions = extract_function_calls(code)
    allowed_functions = set()
    for h in headers:
        if h not in HEADER_CAPABILITIES:
            raise SyntaxError(f"Unknown header <{h}>")
        allowed_functions |= HEADER_CAPABILITIES[h]

    # User defined functions
    user_functions = set(re.findall(
        r'\b(?:(?:unsigned|signed|const|static)\s+)*(?:void|int|float|double|char|short|long|bool|_Bool|[a-zA-Z_]\w*)(?:\s*\*+)?\s+([a-zA-Z_]\w*)\s*\(',
        code
    ))

    used_functions -= C_KEYWORDS
    used_functions -= user_functions
    used_functions.discard("main")

    illegal = used_functions - allowed_functions
    if illegal:
        raise SyntaxError(
            f"Function(s) {', '.join(sorted(illegal))} used without proper header"
        )

def get_needed_runtime(js_code, headers):
    runtime_parts = []

    # Only include pointer runtime if pointer/ref helpers are used
    pointer_symbols = {"__Ptr", "__ref", "__ref_arr", "__ref_prop", "__deref", "__set_deref", "__ptr_add", "__ptr_sub"}
    if any(re.search(rf"\b{sym}\b", js_code) for sym in pointer_symbols):
        runtime_parts.append(RUNTIME_CORE.strip())
    elif re.search(r"\b__sizeof\b", js_code):
        runtime_parts.append("""function __sizeof(val) {
    if (val === null || val === undefined) return 8;
    if (Array.isArray(val)) return val.length * 4;
    if (typeof val === 'number') return 4;
    if (typeof val === 'string') return val.length;
    if (typeof val === 'boolean') return 1;
    if (typeof val === 'object') return Object.keys(val).length * 4;
    return 8;
}""")

    if re.search(r"\bNULL\b", js_code):
        runtime_parts.append("const NULL = null;")

    # stdlib.h functions (only include if actually used)
    stdlib_funcs = {
        "malloc": "const malloc = (bytes) => new Array(Math.ceil(bytes / 4) || 1).fill(0);",
        "calloc": "const calloc = (num, size) => new Array(num * size).fill(0);",
        "free": "const free = (ptr) => {};",
        "abs": "const abs = Math.abs;",
        "rand": "const rand = () => Math.floor(Math.random() * 32768);",
        "srand": "const srand = (seed) => {};",
        "atoi": "const atoi = (str) => parseInt(str, 10) || 0;",
        "atof": "const atof = (str) => parseFloat(str) || 0.0;",
        "exit": "const exit = (code) => { throw new Error(`Process exited with code ${code}`); };"
    }
    for fn, impl in stdlib_funcs.items():
        if re.search(rf"(?<!\.)\b{fn}\b", js_code):
            runtime_parts.append(impl)

    # string.h functions (only include if actually used)
    string_funcs = {
        "strlen": "const strlen = (s) => (typeof s === 'string' ? s.length : (Array.isArray(s) ? (s.indexOf(0) !== -1 ? s.indexOf(0) : s.length) : 0));",
        "strcpy": """const strcpy = (dest, src) => {
    if (Array.isArray(dest)) {
        for (let i = 0; i < src.length; i++) dest[i] = typeof src === 'string' ? src.charCodeAt(i) : src[i];
        dest[src.length] = 0;
        return dest;
    }
    return src;
};""",
        "strcmp": """const strcmp = (s1, s2) => {
    const str1 = typeof s1 === 'string' ? s1 : (Array.isArray(s1) ? String.fromCharCode(...s1.filter(c => c !== 0)) : String(s1));
    const str2 = typeof s2 === 'string' ? s2 : (Array.isArray(s2) ? String.fromCharCode(...s2.filter(c => c !== 0)) : String(s2));
    return str1.localeCompare(str2);
};""",
        "strcat": """const strcat = (dest, src) => {
    if (Array.isArray(dest)) {
        let start = strlen(dest);
        for (let i = 0; i < src.length; i++) dest[start + i] = typeof src === 'string' ? src.charCodeAt(i) : src[i];
        dest[start + src.length] = 0;
        return dest;
    }
    return (dest || "") + (src || "");
};""",
        "strncpy": "const strncpy = strcpy;",
        "strncmp": "const strncmp = strcmp;"
    }
    for fn, impl in string_funcs.items():
        if re.search(rf"(?<!\.)\b{fn}\b", js_code):
            runtime_parts.append(impl)

    # ctype.h functions (only include if actually used)
    ctype_funcs = {
        "toupper": "const toupper = (c) => typeof c === 'number' ? String.fromCharCode(c).toUpperCase().charCodeAt(0) : (typeof c === 'string' ? c.toUpperCase() : c);",
        "tolower": "const tolower = (c) => typeof c === 'number' ? String.fromCharCode(c).toLowerCase().charCodeAt(0) : (typeof c === 'string' ? c.toLowerCase() : c);",
        "isdigit": "const isdigit = (c) => { const ch = typeof c === 'number' ? String.fromCharCode(c) : String(c); return /\\d/.test(ch) ? 1 : 0; };",
        "isalpha": "const isalpha = (c) => { const ch = typeof c === 'number' ? String.fromCharCode(c) : String(c); return /[a-zA-Z]/.test(ch) ? 1 : 0; };",
        "isalnum": "const isalnum = (c) => { const ch = typeof c === 'number' ? String.fromCharCode(c) : String(c); return /[a-zA-Z0-9]/.test(ch) ? 1 : 0; };",
        "isspace": "const isspace = (c) => { const ch = typeof c === 'number' ? String.fromCharCode(c) : String(c); return /\\s/.test(ch) ? 1 : 0; };"
    }
    for fn, impl in ctype_funcs.items():
        if re.search(rf"(?<!\.)\b{fn}\b", js_code):
            runtime_parts.append(impl)

    # math.h functions (only include if actually used)
    math_funcs = {
        "sqrt": "const sqrt = Math.sqrt;",
        "pow": "const pow = Math.pow;",
        "sin": "const sin = Math.sin;",
        "cos": "const cos = Math.cos;",
        "tan": "const tan = Math.tan;",
        "floor": "const floor = Math.floor;",
        "ceil": "const ceil = Math.ceil;",
        "round": "const round = Math.round;",
        "log": "const log = Math.log;",
        "exp": "const exp = Math.exp;"
    }
    for fn, impl in math_funcs.items():
        if fn == "log":
            if re.search(r"(?<!\.)\blog\s*\(", js_code):
                runtime_parts.append(impl)
        else:
            if re.search(rf"(?<!\.)\b{fn}\s*\(", js_code):
                runtime_parts.append(impl)

    # limits.h constants (only include if actually used)
    limits_constants = {
        "INT_MAX": "const INT_MAX = 2147483647;",
        "INT_MIN": "const INT_MIN = -2147483648;",
        "CHAR_BIT": "const CHAR_BIT = 8;"
    }
    for const_name, impl in limits_constants.items():
        if re.search(rf"\b{const_name}\b", js_code):
            runtime_parts.append(impl)

    return "\n\n".join(runtime_parts)

def inject_header_runtime(js, headers, used_functions):
    runtime = get_needed_runtime(js, headers)
    if runtime.strip():
        return runtime.strip() + "\n\n" + js
    return js

def extract_macros(code):
    return dict(re.findall(r'#define\s+(\w+)\s+(.+)', code))

def remove_macros(code):
    return re.sub(r'#define\s+\w+\s+.+', '', code)

def apply_macros(code, macros):
    for name, value in macros.items():
        code = re.sub(rf'\b{name}\b', f'({value})', code)
    return code

def parse_enum_body(body):
    entries = {}
    current_val = 0
    items = body.split(",")
    for item in items:
        item = item.strip()
        if not item:
            continue
        if "=" in item:
            k, v = item.split("=", 1)
            k = k.strip()
            v = int(v.strip())
            current_val = v
            entries[k] = current_val
        else:
            entries[item] = current_val
        current_val += 1
    return entries

def extract_all_typedefs(code):
    typedef_types = {}
    typedef_structs = {}
    typedef_enums = {}

    # 1. typedef struct [Name]? { ... } Alias;
    def struct_repl(match):
        body = match.group(1)
        alias = match.group(2)
        fields = []
        for line in body.split(";"):
            line = line.strip()
            if line:
                parts = line.split()
                fname = parts[-1].lstrip("*")
                fields.append(fname)
        typedef_structs[alias] = fields
        typedef_types[alias] = "struct"
        return ""

    code = re.sub(
        r'typedef\s+struct(?:\s+\w+)?\s*\{([^}]+)\}\s*(\w+)\s*;',
        struct_repl,
        code
    )

    # 2. typedef enum [Name]? { ... } Alias;
    def enum_repl(match):
        body = match.group(1)
        alias = match.group(2)
        entries = parse_enum_body(body)
        typedef_enums[alias] = entries
        typedef_types[alias] = "enum"
        decls = [f"const {k} = {v};" for k, v in entries.items()]
        return "\n".join(decls)

    code = re.sub(
        r'typedef\s+enum(?:\s+\w+)?\s*\{([^}]+)\}\s*(\w+)\s*;',
        enum_repl,
        code
    )

    # 3. typedef struct Name Alias;
    def struct_alias_repl(match):
        name = match.group(1)
        alias = match.group(2)
        typedef_types[alias] = f"struct {name}"
        return ""

    code = re.sub(
        r'typedef\s+struct\s+(\w+)\s+(\w+)\s*;',
        struct_alias_repl,
        code
    )

    # 4. General typedef: typedef <type> <alias>;
    def gen_repl(match):
        type_str = match.group(1).strip()
        alias = match.group(2).strip()
        typedef_types[alias] = type_str
        return ""

    code = re.sub(
        r'typedef\s+((?:(?:unsigned|signed|long\s+long|long|short|const|static)\s+)*(?:int|float|double|char|short|long|void|bool|_Bool|[a-zA-Z_]\w*)(?:\s*\*+)?)\s+([a-zA-Z_]\w*)\s*;',
        gen_repl,
        code
    )

    return typedef_types, typedef_structs, typedef_enums, code

def extract_and_convert_enums(code):
    enums = {}
    pattern = re.compile(r'enum\s+(?:(\w+)\s*)?\{([^}]+)\}(?:\s*(\w+))?\s*;')

    def replacer(match):
        name = match.group(1)
        body = match.group(2)
        var = match.group(3)
        entries = parse_enum_body(body)
        enums.update(entries)
        decls = [f"const {k} = {v};" for k, v in entries.items()]
        if var:
            decls.append(f"let {var} = 0;")
        return "\n".join(decls)

    code = pattern.sub(replacer, code)
    return enums, code

def extract_structs(code):
    structs = {}
    pattern = re.compile(r'struct\s+(\w+)\s*\{([^}]+)\}\s*;', re.DOTALL)
    for name, body in pattern.findall(code):
        fields = []
        for line in body.split(";"):
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            fname = parts[-1].lstrip("*")
            fields.append(fname)
        structs[name] = fields
    return structs

def remove_struct_definitions(code):
    return re.sub(r'struct\s+\w+\s*\{[^}]+\}\s*;', '', code, flags=re.DOTALL)

def extract_array_declarations(code):
    base_types = r"(?:(?:unsigned|signed|long\s+long|long|short|const|static)\s+)*(?:int|float|double|char|short|long|void|bool|_Bool|\w+)"
    pattern = rf'\b({base_types})\s+(\w+)\s*\[(\d*)\]\s*(?:=\s*([^;]+))?\s*;'
    matches = re.findall(pattern, code)
    arrays = {}
    for elem_type, name, size_str, init in matches:
        size = int(size_str) if size_str.strip().isdigit() else 0
        arrays[name] = (elem_type.strip(), size)
    return arrays

def replace_struct_array_declarations(code, structs):
    for struct_name, fields in structs.items():
        pattern = rf'\b(?:struct\s+)?{struct_name}\s+(\w+)\s*\[(\d+)\]\s*;'
        def repl(match):
            var = match.group(1)
            size = int(match.group(2))
            obj = "{ " + ", ".join(f"{f}: 0" for f in fields) + " }"
            return f"let {var} = Array({size}).fill(null).map(() => ({obj}));"
        code = re.sub(pattern, repl, code)
    return code

def replace_struct_declarations(code, structs):
    for struct_name, fields in structs.items():
        # Designated initializers: struct Point p = { .x = 10, .y = 20 };
        desig_pattern = rf'\b(?:struct\s+)?{struct_name}\s+(\w+)\s*=\s*\{{([^}}]*\.[^}}]+)\}}\s*;'
        def desig_repl(match):
            var = match.group(1)
            init_body = match.group(2)
            pairs = []
            for item in init_body.split(","):
                item = item.strip()
                if "=" in item:
                    k, v = item.split("=", 1)
                    k = k.strip().lstrip(".")
                    v = v.strip()
                    pairs.append(f"{k}: {v}")
            return f"let {var} = {{ {', '.join(pairs)} }};"
        code = re.sub(desig_pattern, desig_repl, code)

        # Positional initializers: struct Point p = { 10, 20 };
        pos_pattern = rf'\b(?:struct\s+)?{struct_name}\s+(\w+)\s*=\s*\{{([^}}]+)\}}\s*;'
        def pos_repl(match):
            var = match.group(1)
            vals = [v.strip() for v in match.group(2).split(",")]
            pairs = []
            for f, v in zip(fields, vals):
                pairs.append(f"{f}: {v}")
            if len(vals) < len(fields):
                for f in fields[len(vals):]:
                    pairs.append(f"{f}: 0")
            return f"let {var} = {{ {', '.join(pairs)} }};"
        code = re.sub(pos_pattern, pos_repl, code)

        # Uninitialized: struct Point p;
        uninit_pattern = rf'\b(?:struct\s+)?{struct_name}\s+(\w+)\s*;'
        def uninit_repl(match):
            var = match.group(1)
            init = ", ".join(f"{f}: 0" for f in fields)
            return f"let {var} = {{ {init} }};"
        code = re.sub(uninit_pattern, uninit_repl, code)

    return code

def replace_array_declarations(code):
    base_types = r"(?:(?:unsigned|signed|long\s+long|long|short|const|static)\s+)*(?:int|float|double|char|short|long|void|bool|_Bool|\w+)"
    pattern = rf'\b{base_types}\s+(\w+)\s*\[(\d*)\]\s*(?:=\s*([^;]+))?\s*;'
    def repl(match):
        name = match.group(1)
        size_str = match.group(2)
        init_body = match.group(3)
        if init_body:
            init_body = init_body.strip()
            if init_body.startswith("{") and init_body.endswith("}"):
                values = init_body[1:-1].strip()
                return f"let {name} = [{values}];"
            return f"let {name} = {init_body};"
        else:
            size = size_str.strip() if size_str.strip() else "0"
            return f"let {name} = Array({size}).fill(0);"
    return re.sub(pattern, repl, code)

def replace_sizeof(code, known_types=None, structs=None, array_vars=None):
    if known_types is None:
        known_types = {}
    if structs is None:
        structs = {}
    if array_vars is None:
        array_vars = {}

    TYPE_SIZES = {
        "char": 1, "unsigned char": 1, "signed char": 1,
        "short": 2, "unsigned short": 2, "signed short": 2,
        "int": 4, "unsigned int": 4, "signed int": 4, "unsigned": 4, "signed": 4,
        "float": 4,
        "double": 8, "long double": 8,
        "long": 8, "unsigned long": 8, "signed long": 8,
        "long long": 8, "unsigned long long": 8, "signed long long": 8,
        "bool": 1, "_Bool": 1, "void": 1
    }

    def get_type_size(type_name):
        type_name = type_name.strip()
        if "*" in type_name:
            return 8
        if type_name.startswith("struct "):
            sname = type_name[7:].strip()
            if sname in structs:
                return len(structs[sname]) * 4
            return 8
        if type_name in structs:
            return len(structs[type_name]) * 4
        if type_name in known_types:
            resolved = known_types[type_name]
            return get_type_size(resolved)
        if type_name in TYPE_SIZES:
            return TYPE_SIZES[type_name]
        return None

    def replacer(match):
        arg = match.group(1).strip()
        sz = get_type_size(arg)
        if sz is not None:
            return str(sz)
        if arg in array_vars:
            elem_type, count = array_vars[arg]
            elem_sz = get_type_size(elem_type) or 4
            return str(elem_sz * count)
        return f"__sizeof({arg})"

    return re.sub(r'\bsizeof\s*\(\s*([^)]+)\s*\)', replacer, code)

def replace_type_casting(code, known_types=None):
    if known_types is None:
        known_types = set()

    types_list = [
        "int", "float", "double", "char", "short", "long",
        "long long", "unsigned int", "unsigned long", "unsigned short",
        "unsigned char", "signed int", "bool", "_Bool", "void*"
    ]
    types_list.extend(known_types)
    types_list = sorted(types_list, key=len, reverse=True)
    type_pat = "|".join(re.escape(t) for t in types_list)
    full_type_pat = rf"(?:{type_pat}|\w+\s*\*+)"

    cast_pattern = re.compile(
        rf'\(\s*({full_type_pat})\s*\)\s*([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*|\[[^\]]+\])?|\d+(?:\.\d+)?|\([^)]+\))'
    )

    def replacer(match):
        cast_type = match.group(1).strip()
        expr = match.group(2).strip()

        if "*" in cast_type or cast_type in ("void*", "void *"):
            return expr
        if cast_type in ("int", "short", "long", "long long", "signed int"):
            return f"(typeof ({expr}) === 'string' ? ({expr}).charCodeAt(0) : Math.trunc({expr}))"
        if cast_type in ("unsigned int", "unsigned long", "unsigned short", "unsigned char"):
            return f"(({expr}) >>> 0)"
        if cast_type in ("float", "double"):
            return f"Number({expr})"
        if cast_type in ("char", "signed char", "unsigned char"):
            return f"(typeof ({expr}) === 'number' ? String.fromCharCode({expr}) : String({expr}))"
        if cast_type in ("bool", "_Bool"):
            return f"Boolean({expr})"
        return f"({expr})"

    return cast_pattern.sub(replacer, code)

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
        return match.group(0)
    return pattern.sub(replacer, code)

def replace_scanf(code):
    def replacer(match):
        fmt = match.group(1).strip()
        var = match.group(2).strip()
        if fmt in ("%d", "%f"):
            return f"{var} = Number(prompt());"
        if fmt == "%c":
            return f"{var} = prompt()[0];"
        if fmt == "%s":
            return f"{var} = prompt();"
        return match.group(0)
    return re.sub(r'scanf\s*\(\s*"([^"]+)"\s*,\s*&\s*(\w+)\s*\)\s*;', replacer, code)

def convert_printf_to_template(code):
    def replacer(match):
        fmt = match.group(1)
        args = match.group(2)
        if not args:
            return f"console.log(`{fmt}`);"
        arg_list = [a.strip() for a in args.split(",")]
        specs = re.findall(r"%[dfsci]", fmt)
        if len(specs) != len(arg_list):
            raise SyntaxError("printf format specifier mismatch")
        for spec, arg in zip(specs, arg_list):
            fmt = fmt.replace(spec, f"${{{arg}}}", 1)
        return f"console.log(`{fmt}`);"

    return re.sub(r'printf\s*\(\s*"([^"]*)"\s*(?:,\s*(.*?))?\s*\)\s*;', replacer, code)

def extract_pointer_variables(code, known_types=None):
    if known_types is None:
        known_types = set()
    base_types = r"(?:(?:unsigned|signed|long\s+long|long|short|const|static)\s+)*(?:int|float|double|char|short|long|void|bool|_Bool|[a-zA-Z_]\w*)"
    pattern = rf'\b(?:{base_types})\s*\*+\s*([a-zA-Z_]\w*)'
    return set(re.findall(pattern, code))

def replace_variable_declarations(code, known_types=None, array_names=None):
    if known_types is None:
        known_types = set()
    if array_names is None:
        array_names = set()

    types_list = [
        "int", "float", "double", "char", "short", "long",
        "unsigned int", "unsigned long", "unsigned short", "unsigned char",
        "long long", "unsigned long long", "unsigned", "signed int", "signed",
        "bool", "_Bool", "void"
    ]
    types_list.extend(known_types)
    types_list = sorted(types_list, key=len, reverse=True)
    type_pat = "|".join(re.escape(t) for t in types_list)
    full_type_pat = rf"(?:(?:const|static|volatile)\s+)?(?:enum\s+\w+|struct\s+\w+|{type_pat})"

    # 1. Pointer declarations: type *p = ...; or type* p;
    ptr_decl_pattern = re.compile(
        rf'\b({full_type_pat})\s*\*+\s*([a-zA-Z_]\w*)\s*(?:=\s*([^;]+))?\s*;'
    )
    def ptr_repl(match):
        type_prefix = match.group(1).strip()
        var = match.group(2).strip()
        init = match.group(3)
        kw = "const" if "const" in type_prefix else "let"
        if init:
            init = init.strip()
            if init in array_names:
                init = f"__ref_arr({init}, 0)"
            elif init == "NULL":
                init = "null"
            return f"{kw} {var} = {init};"
        else:
            return f"let {var} = null;"

    code = ptr_decl_pattern.sub(ptr_repl, code)

    # 2. General variable declarations: type a = 5, b = 10;
    var_decl_pattern = re.compile(
        rf'\b({full_type_pat})\s+([a-zA-Z_]\w*(?:\s*=\s*[^,;]+)?(?:\s*,\s*[a-zA-Z_]\w*(?:\s*=\s*[^,;]+)?)*)\s*;'
    )
    def var_repl(match):
        type_prefix = match.group(1).strip()
        decl_list = match.group(2).strip()
        kw = "const" if "const" in type_prefix else "let"
        return f"{kw} {decl_list};"

    code = var_decl_pattern.sub(var_repl, code)
    return code

def transform_pointers_and_references(code, pointer_vars, array_names):
    # 1. Arrow operator: ptr->prop -> ptr.prop
    code = re.sub(r'([a-zA-Z_]\w*)\s*->\s*([a-zA-Z_]\w*)', r'\1.\2', code)

    # 2. Address-of:
    code = re.sub(
        r'(^|[=([,?:;\s])&\s*([a-zA-Z_]\w*)\s*\[([^\]]+)\]',
        r'\1__ref_arr(\2, \3)',
        code
    )
    code = re.sub(
        r'(^|[=([,?:;\s])&\s*([a-zA-Z_]\w*)\.([a-zA-Z_]\w*)',
        r'\1__ref_prop(\2, "\3")',
        code
    )
    code = re.sub(
        r'(^|[=([,?:;\s])&\s*([a-zA-Z_]\w*)',
        r'\1__ref(() => \2, __v => \2 = __v)',
        code
    )

    # 3. Dereference write:
    code = re.sub(
        r'\*\s*\(\s*([a-zA-Z_]\w*)\s*\+\s*([^)]+)\s*\)\s*=\s*([^;]+);',
        r'__set_deref(__ptr_add(\1, \2), \3);',
        code
    )
    code = re.sub(
        r'\*\s*\(\s*([a-zA-Z_]\w*)\s*-\s*([^)]+)\s*\)\s*=\s*([^;]+);',
        r'__set_deref(__ptr_sub(\1, \2), \3);',
        code
    )
    code = re.sub(
        r'\*\s*\*\s*([a-zA-Z_]\w*)\s*=\s*([^;]+);',
        r'__set_deref(__deref(\1), \2);',
        code
    )
    # Unary * on LHS must be preceded by start of line, ;, {, }, or return
    code = re.sub(
        r'(^|[;{}\s])\*\s*([a-zA-Z_]\w*)\s*=\s*([^;]+);',
        r'\1__set_deref(\2, \3);',
        code
    )

    # 4. Dereference read:
    code = re.sub(
        r'\*\s*\(\s*([a-zA-Z_]\w*)\s*\+\s*([^)]+)\s*\)',
        r'__deref(__ptr_add(\1, \2))',
        code
    )
    code = re.sub(
        r'\*\s*\(\s*([a-zA-Z_]\w*)\s*-\s*([^)]+)\s*\)',
        r'__deref(__ptr_sub(\1, \2))',
        code
    )
    # Unary ** or * on RHS: MUST be preceded by operator or statement boundary, NOT operand!
    unary_prefix = r'(^|[=([,?:;{}!+\-*/%<>|&~]|\breturn)\s*'
    code = re.sub(
        unary_prefix + r'\*\s*\*\s*([a-zA-Z_]\w*)',
        r'\1__deref(__deref(\2))',
        code
    )
    code = re.sub(
        unary_prefix + r'\*\s*([a-zA-Z_]\w*)',
        r'\1__deref(\2)',
        code
    )

    # 5. Pointer arithmetic:
    for pv in pointer_vars:
        code = re.sub(rf'\b{pv}\s*\+\+', f'{pv} = __ptr_add({pv}, 1)', code)
        code = re.sub(rf'\+\+\s*{pv}\b', f'{pv} = __ptr_add({pv}, 1)', code)
        code = re.sub(rf'\b{pv}\s*--', f'{pv} = __ptr_sub({pv}, 1)', code)
        code = re.sub(rf'--\s*{pv}\b', f'{pv} = __ptr_sub({pv}, 1)', code)
        code = re.sub(rf'\b{pv}\s*\+=\s*([^;]+)', rf'{pv} = __ptr_add({pv}, \1)', code)
        code = re.sub(rf'\b{pv}\s*-=\s*([^;]+)', rf'{pv} = __ptr_sub({pv}, \1)', code)

    return code

def remove_param_types(param_str):
    if not param_str.strip():
        return ""
    params = param_str.split(",")
    clean = []
    for p in params:
        p = p.strip()
        m = re.search(r"([a-zA-Z_]\w*)\s*(?:\[[^\]]*\])?$", p)
        if m:
            clean.append(m.group(1))
        else:
            clean.append(p)
    return ", ".join(clean)

def extract_globals_functions_and_main(code):
    type_regex = r"(?:(?:unsigned|signed|const|static)\s+)*(?:struct\s+\w+|\w+)(?:\s*\*+)?"
    sig_pattern = re.compile(rf"\b({type_regex})\s+([a-zA-Z_]\w*)\s*\(([^)]*)\)\s*\{{", re.MULTILINE)
    functions = []
    main_body = ""
    globals_list = []
    idx = 0
    last_end = 0
    while idx < len(code):
        m = sig_pattern.search(code, idx)
        if not m:
            break
        pre_code = code[last_end:m.start()].strip()
        if pre_code:
            globals_list.append(pre_code)
        ret_type = m.group(1).strip()
        fn_name = m.group(2).strip()
        params = m.group(3).strip()
        brace_start = m.end() - 1
        brace_count = 0
        end_brace = -1
        for i in range(brace_start, len(code)):
            if code[i] == '{':
                brace_count += 1
            elif code[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_brace = i
                    break
        if end_brace == -1:
            break
        body = code[brace_start + 1:end_brace]
        if fn_name == "main":
            main_body = body
        else:
            functions.append({
                "ret_type": ret_type,
                "name": fn_name,
                "params": params,
                "body": body
            })
        idx = end_brace + 1
        last_end = idx

    after_code = code[last_end:].strip()
    if after_code:
        globals_list.append(after_code)

    return "\n\n".join(globals_list), functions, main_body

def remove_return_zero(code):
    return re.sub(r'\breturn\s+0\s*;', '', code)

def mask_c_strings(code):
    placeholders = []
    pattern = re.compile(r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')')
    def repl(m):
        idx = len(placeholders)
        placeholders.append(m.group(0))
        return f"___LEX_STR_LIT_{idx}___"
    return pattern.sub(repl, code), placeholders

def unmask_c_strings(code, placeholders):
    for idx, orig in enumerate(placeholders):
        code = code.replace(f"___LEX_STR_LIT_{idx}___", orig)
    return code

def process_block(block_code, known_types, array_names, pointer_vars, structs, typedef_types, array_vars):
    # Step A: Transform prompted and standalone scanf before pointer transforms alter &var
    block_code = replace_prompted_scanf(block_code)
    block_code = replace_scanf(block_code)

    # Step B: Protect string and char literals from subsequent code transformations
    masked_code, placeholders = mask_c_strings(block_code)

    masked_code = replace_sizeof(masked_code, typedef_types, structs, array_vars)
    masked_code = replace_type_casting(masked_code, known_types)
    masked_code = replace_variable_declarations(masked_code, known_types, array_names)
    masked_code = transform_pointers_and_references(masked_code, pointer_vars, array_names)

    # Step C: Unmask string literals
    block_code = unmask_c_strings(masked_code, placeholders)

    # Step D: Convert printf into template literals
    block_code = convert_printf_to_template(block_code)
    return block_code
