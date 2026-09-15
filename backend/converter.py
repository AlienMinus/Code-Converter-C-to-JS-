from tokenizer import *
from validator import detect_undeclared_variables
import re

def convert_c_to_js(c_code):
    # Step 1: Comments cleanup
    code = remove_comments(c_code)

    # Step 2: Validate and extract included headers
    validate_headers(code)
    headers = extract_headers(code)

    # Step 3: Extract and apply preprocessor macros
    macros = extract_macros(code)
    code = remove_macros(code)
    code = apply_macros(code, macros)

    # Step 4: Extract all typedef aliases (primitives, pointers, structs, enums)
    typedef_types, typedef_structs, typedef_enums, code = extract_all_typedefs(code)

    # Step 5: Extract and convert enum definitions
    enums, code = extract_and_convert_enums(code)

    # Step 6: Extract struct definitions
    structs = extract_structs(code)
    code = remove_struct_definitions(code)
    structs.update(typedef_structs)

    known_types = set(typedef_types.keys()) | set(structs.keys()) | set(enums.keys())

    # Step 7: Handle struct and primitive arrays
    array_vars = extract_array_declarations(code)
    code = replace_struct_array_declarations(code, structs)
    code = replace_array_declarations(code)
    array_names = set(array_vars.keys())

    # Step 8: Handle struct variable declarations (designated, positional, and uninitialized)
    code = replace_struct_declarations(code, structs)

    # Step 9: Extract pointer variable names
    pointer_vars = extract_pointer_variables(code, known_types)

    # Step 10: Remove #include directives
    code = remove_includes(code)

    # Step 11: Extract top-level globals, user functions, and main function
    global_code, functions_list, main_body = extract_globals_functions_and_main(code)

    import textwrap

    processed_globals = process_block(
        global_code, known_types, array_names, pointer_vars, structs, typedef_types, array_vars
    )
    processed_globals = textwrap.dedent(processed_globals).strip()

    # Step 12: Process each non-main user function body and signature
    fn_strings = []
    for fn in functions_list:
        clean_p = remove_param_types(fn["params"])
        fn_pointer_vars = set(pointer_vars)
        for p in fn["params"].split(","):
            if "*" in p:
                m = re.search(r"([a-zA-Z_]\w*)\s*$", p.strip())
                if m:
                    fn_pointer_vars.add(m.group(1))

        processed_body = process_block(
            fn["body"], known_types, array_names, fn_pointer_vars, structs, typedef_types, array_vars
        )
        dedented_body = textwrap.dedent(processed_body).strip()
        indented_body = textwrap.indent(dedented_body, "    ")
        fn_strings.append(f"function {fn['name']}({clean_p}) {{\n{indented_body}\n}}")

    # Step 13: Process main body
    main_body = remove_return_zero(main_body)
    processed_main = process_block(
        main_body, known_types, array_names, pointer_vars, structs, typedef_types, array_vars
    )
    processed_main = textwrap.dedent(processed_main).strip()

    parts = []
    if processed_globals.strip():
        parts.append(processed_globals.strip())
    if fn_strings:
        parts.append("\n\n".join(fn_strings))
    if processed_main.strip():
        parts.append(processed_main.strip())

    user_js = "\n\n".join(parts)

    # Step 14: Check undeclared variables in user code
    undeclared = detect_undeclared_variables(user_js, set())

    # Step 15: Determine only the needed runtime machinery (tree-shaken)
    runtime = get_needed_runtime(user_js, headers).strip()
    full_js = (runtime + "\n\n" + user_js).strip() if runtime else user_js

    return {
        "js": user_js,                # Clean, human-readable transpiled code for display!
        "runtime": runtime,           # Tree-shaken runtime helpers (if needed)
        "full_js": full_js,           # Self-contained executable JavaScript
        "structs": structs,
        "macros": macros,
        "undeclared": list(undeclared)
    }
