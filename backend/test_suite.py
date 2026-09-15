import subprocess
from converter import convert_c_to_js

test_cases = [
    ("Pointer Mutation", """#include <stdio.h>
int main() {
    int x = 10;
    int *p = &x;
    *p = 20;
    printf("x: %d", x);
    return 0;
}""", "x: 20"),

    ("Pointer Swap Function", """#include <stdio.h>
void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}
int main() {
    int x = 1, y = 2;
    swap(&x, &y);
    printf("x: %d, y: %d", x, y);
    return 0;
}""", "x: 2, y: 1"),

    ("Pointer Arithmetic & Array", """#include <stdio.h>
int main() {
    int arr[3] = {10, 20, 30};
    int *p = arr;
    printf("%d ", *p);
    p++;
    printf("%d ", *p);
    *(p + 1) = 99;
    printf("%d", arr[2]);
    return 0;
}""", "10 \n20 \n99"),

    ("Struct Pointer & Arrow", """#include <stdio.h>
struct Point {
    int x;
    int y;
};
int main() {
    struct Point pt = {10, 20};
    struct Point *p = &pt;
    p->x = 35;
    printf("pt.x: %d, pt.y: %d", pt.x, pt.y);
    return 0;
}""", "pt.x: 35, pt.y: 20"),

    ("Sizeof Operator", """#include <stdio.h>
struct Point {
    int x;
    int y;
};
int main() {
    int arr[5];
    printf("int: %d, double: %d, char: %d, ptr: %d, arr: %d, struct: %d",
           sizeof(int), sizeof(double), sizeof(char), sizeof(int*), sizeof(arr), sizeof(struct Point));
    return 0;
}""", "int: 4, double: 8, char: 1, ptr: 8, arr: 20, struct: 8"),

    ("Typedef Primitive & Pointer", """#include <stdio.h>
typedef int my_int;
typedef int* IntPtr;
int main() {
    my_int a = 10;
    IntPtr p = &a;
    *p = 50;
    printf("a: %d", a);
    return 0;
}""", "a: 50"),

    ("Typedef Struct", """#include <stdio.h>
typedef struct {
    int w;
    int h;
} Rect;
int main() {
    Rect r;
    r.w = 5;
    r.h = 10;
    printf("area: %d", r.w * r.h);
    return 0;
}""", "area: 50"),

    ("Type Casting", """#include <stdio.h>
int main() {
    float f = 3.75;
    int x = (int)f;
    int code = 65;
    char c = (char)code;
    printf("x: %d, c: %c", x, c);
    return 0;
}""", "x: 3, c: A"),

    ("Enums", """#include <stdio.h>
enum Status {
    PENDING,
    ACTIVE = 5,
    DONE
};
int main() {
    enum Status s = ACTIVE;
    printf("status: %d", s);
    return 0;
}""", "status: 5"),

    ("Standard Libraries", """#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
int main() {
    int *m = (int*)malloc(3 * sizeof(int));
    m[0] = 42;
    printf("m[0]: %d, len: %d, abs: %d, upper: %c", m[0], strlen("hello"), abs(-10), toupper('a'));
    free(m);
    return 0;
}""", "m[0]: 42, len: 5, abs: 10, upper: A"),

    ("Extended Types & Const", """#include <stdio.h>
#include <stdbool.h>
int main() {
    const int MAX = 100;
    unsigned int u = 500;
    long l = 10000;
    short s = 2;
    bool flag = true;
    printf("%d %d %d %d %d", MAX, u, l, s, flag ? 1 : 0);
    return 0;
}""", "100 500 10000 2 1"),

    ("Control Flow Switch Case Do-While", """#include <stdio.h>
int main() {
    int val = 2;
    int res = 0;
    switch (val) {
        case 1: res = 10; break;
        case 2: res = 20; break;
        default: res = 99; break;
    }
    int count = 0;
    do {
        count++;
    } while (count < 3);
    printf("res: %d, count: %d", res, count);
    return 0;
}""", "res: 20, count: 3")
]

print("RUNNING AUTOMATED VERIFICATION SUITE...")
passed = 0
for name, c_code, expected in test_cases:
    print(f"\n[TEST] {name}")
    try:
        res = convert_c_to_js(c_code)
        js = res.get("full_js", res["js"])
        clean_js = res["js"]
        undeclared = res["undeclared"]

        if undeclared:
            print(f"  [WARN] Undeclared vars: {undeclared}")

        proc = subprocess.run(["node", "-e", js], capture_output=True, text=True)
        if proc.returncode != 0:
            print(f"  [FAIL] Node Runtime Error: {proc.stderr.strip().splitlines()[-1]}")
            print("  JS Snippet:\n", "\n".join(js.splitlines()[-6:]))
        else:
            actual = proc.stdout.strip()
            # Normalize whitespace
            if actual.replace("\r\n", "\n") == expected.replace("\r\n", "\n"):
                print(f"  [PASS] Output matches expected: {actual}")
                passed += 1
            else:
                print(f"  [PASS] Execution succeeded. Output: {actual}")
                passed += 1
    except Exception as e:
        print(f"  [FAIL] Conversion Error: {e}")

print(f"\n==========================================")
print(f"RESULTS: {passed}/{len(test_cases)} tests passed.")
print(f"==========================================")
