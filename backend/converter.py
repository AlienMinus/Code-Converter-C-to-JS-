from tokenizer import *
from validator import detect_undeclared_variables

def convert_c_to_js(c_code):

    validate_headers(c_code)
    headers = extract_headers(c_code)

    # ---- MACROS ----
    macros = extract_macros(c_code)
    code = remove_macros(c_code)
    code = apply_macros(code, macros)

    # ---- TYPEDEF STRUCTS ----
    typedef_structs = extract_typedef_structs(code)
    code = remove_typedef_structs(code)

    # ---- STRUCTS ----
    structs = extract_structs(code)
    code = remove_struct_definitions(code)
    structs.update(typedef_structs)

    # ---- STRUCT ARRAYS (NEW) ----
    code = replace_struct_array_declarations(code, structs)

    # ---- NORMAL ARRAYS (NEW) ----
    code = replace_array_declarations(code)

    # ---- STRUCT VARIABLES ----
    code = replace_struct_declarations(code, structs)

    # ---- PREPROCESS ----
    code = remove_includes(code)

    declared_vars = collect_declared_variables(code)

    functions = extract_non_main_functions(code)
    functions = convert_function_syntax(functions)

    main_body = extract_main_body(code)
    main_body = remove_return_zero(main_body)

    js = functions + "\n\n" + main_body

    js = replace_prompted_scanf(js)
    js = replace_scanf(js)
    js = convert_printf_to_template(js)
    js = replace_variable_declarations(js)

    used_functions = extract_function_calls(code)
    js = inject_header_runtime(js, headers, used_functions)

    undeclared = detect_undeclared_variables(js, declared_vars)

    return {
        "js": js.strip(),
        "structs": structs,
        "macros": macros,
        "undeclared": list(undeclared)
    }
