/**
 * LexCodex C -> JavaScript Studio Frontend Script
 */

let cEditor, jsEditor, outputEditor;
let editorReady = false;
const STORAGE_KEY = "lexcodex_c_code_v1";
let saveTimeout = null;

// ================= PRESET C CODES =================
const PRESETS = {
  scanf_basic: `#include <stdio.h>

int main() {
    int n;
    printf("Enter Your Number: ");
    scanf("%d", &n);
    printf("Your number is %d\\n", n);
    return 0;
}`,

  pointer_swap: `#include <stdio.h>

// Pass-by-reference pointer swap function
void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

int main() {
    int x = 10, y = 20;
    printf("Before swap: x = %d, y = %d\\n", x, y);

    swap(&x, &y);

    printf("After swap:  x = %d, y = %d\\n", x, y);
    return 0;
}`,

  pointer_array: `#include <stdio.h>

int main() {
    int arr[5] = {10, 20, 30, 40, 50};
    int *p = arr;

    printf("First element: *p = %d\\n", *p);

    p++;
    printf("Second element after p++: *p = %d\\n", *p);

    *(p + 2) = 999;
    printf("4th element modified via *(p+2): arr[3] = %d\\n", arr[3]);

    return 0;
}`,

  struct_arrow: `#include <stdio.h>

struct Point {
    int x;
    int y;
};

int main() {
    // Initialized struct
    struct Point pt = { .x = 10, .y = 20 };
    struct Point *ptr = &pt;

    printf("Initial point: (%d, %d)\\n", pt.x, pt.y);

    // Member mutation via arrow operator
    ptr->x = 55;
    ptr->y = 88;

    printf("Modified point via ptr->: (%d, %d)\\n", pt.x, pt.y);
    return 0;
}`,

  sizeof_casting: `#include <stdio.h>

struct Rect {
    int width;
    int height;
};

int main() {
    int arr[10];

    // Compile-time sizeof resolution
    printf("--- SIZEOF SIZES ---\\n");
    printf("sizeof(int):        %d bytes\\n", sizeof(int));
    printf("sizeof(double):     %d bytes\\n", sizeof(double));
    printf("sizeof(int*):       %d bytes\\n", sizeof(int*));
    printf("sizeof(arr):        %d bytes\\n", sizeof(arr));
    printf("sizeof(struct Rect): %d bytes\\n", sizeof(struct Rect));

    // C explicit type casting
    float pi = 3.999;
    int truncated = (int)pi;
    char letter = (char)65;

    printf("\\n--- TYPE CASTING ---\\n");
    printf("(int)3.999  = %d\\n", truncated);
    printf("(char)65    = %c\\n", letter);

    return 0;
}`,

  typedef_enums: `#include <stdio.h>

typedef int integer;
typedef int* IntPtr;

typedef struct {
    int id;
    int score;
} Player;

enum GameState {
    IDLE,
    PLAYING = 5,
    GAME_OVER
};

int main() {
    integer score = 100;
    IntPtr ptr = &score;
    *ptr = 250;

    Player p1 = {1, 95};
    enum GameState state = PLAYING;

    printf("Score: %d\\n", score);
    printf("Player ID: %d, Score: %d\\n", p1.id, p1.score);
    printf("Game State: %d\\n", state);

    return 0;
}`,

  stdlib_strings: `#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

int main() {
    // Dynamic memory allocation simulation
    int *buffer = (int*)malloc(3 * sizeof(int));
    buffer[0] = 42;
    printf("Dynamic buffer[0]: %d\\n", buffer[0]);
    free(buffer);

    // string.h
    char greeting[20] = "Hello";
    printf("Length of '%s': %d\\n", greeting, strlen(greeting));

    // ctype.h & math.h
    printf("toupper('c'): %c\\n", toupper('c'));
    printf("isdigit('5'): %d\\n", isdigit('5'));
    printf("abs(-42):     %d\\n", abs(-42));

    return 0;
}`,

  control_flow: `#include <stdio.h>

int main() {
    int choice = 2;
    switch (choice) {
        case 1:
            printf("Selected Option 1\\n");
            break;
        case 2:
            printf("Selected Option 2\\n");
            break;
        default:
            printf("Unknown Option\\n");
            break;
    }

    int i = 0;
    printf("Do-While loop: ");
    do {
        printf("%d ", i);
        i++;
    } while (i < 4);
    printf("\\n");

    return 0;
}`
};

// ================= MONACO LOADER =================
require.config({
  paths: {
    vs: "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs"
  }
});

require(["vs/editor/editor.main"], function () {
  // Determine initial code: from localStorage or default
  const savedCode = localStorage.getItem(STORAGE_KEY);
  const initialCode = savedCode || PRESETS.scanf_basic;

  // 1. C EDITOR
  cEditor = monaco.editor.create(document.getElementById("cEditor"), {
    value: initialCode,
    language: "c",
    theme: "vs-dark",
    automaticLayout: true,
    fontSize: 13,
    fontFamily: "'Fira Code', Consolas, monospace",
    minimap: { enabled: false },
    lineNumbers: "on",
    scrollBeyondLastLine: false,
    tabSize: 4
  });

  // Auto-save debounced
  cEditor.onDidChangeModelContent(() => {
    setSaveStatus("Saving...");
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(() => {
      localStorage.setItem(STORAGE_KEY, cEditor.getValue());
      setSaveStatus("Saved");
    }, 600);
  });

  // Ctrl+Enter inside C editor
  cEditor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
    convert();
  });

  // 2. JS EDITOR
  jsEditor = monaco.editor.create(document.getElementById("jsEditor"), {
    value: "// Generated JavaScript will appear here after conversion\n",
    language: "javascript",
    theme: "vs-dark",
    readOnly: true,
    automaticLayout: true,
    fontSize: 13,
    fontFamily: "'Fira Code', Consolas, monospace",
    minimap: { enabled: false },
    scrollBeyondLastLine: false
  });

  // 3. OUTPUT EDITOR
  outputEditor = monaco.editor.create(document.getElementById("outputEditor"), {
    value: "> Output will appear here...\n",
    language: "plaintext",
    theme: "vs-dark",
    readOnly: true,
    minimap: { enabled: false },
    lineNumbers: "off",
    wordWrap: "on",
    fontSize: 13,
    fontFamily: "'Fira Code', Consolas, monospace",
    automaticLayout: true,
    scrollBeyondLastLine: false
  });

  editorReady = true;
  const btn = document.getElementById("runBtn");
  if (btn) btn.disabled = false;
});

// Global Keyboard Shortcut: Ctrl+Enter and Ctrl+L
window.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    convert();
  } else if ((e.ctrlKey || e.metaKey) && (e.key === "l" || e.key === "L")) {
    e.preventDefault();
    clearOutput();
  }
});

// ================= CONVERT & RUN =================
function convert() {
  if (!editorReady) {
    showToast("Editor is still initializing...");
    return;
  }

  const runBtn = document.getElementById("runBtn");
  const undeclaredBadge = document.getElementById("undeclaredBadge");
  const timingBadge = document.getElementById("timingBadge");

  runBtn.disabled = true;
  timingBadge.textContent = "Transpiling...";
  timingBadge.style.color = "#fbbf24";
  undeclaredBadge.style.display = "none";
  outputEditor.setValue("> Transpiling C code...\n");

  const cCode = cEditor.getValue();
  const startTime = performance.now();

  fetch("/convert", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code: cCode })
  })
    .then((res) => res.json())
    .then((data) => {
      const transpileTime = Math.round(performance.now() - startTime);

      if (data.error) {
        outputEditor.setValue("> Compile Error:\n" + data.error);
        timingBadge.textContent = "Compile Error";
        timingBadge.style.color = "#f43f5e";
        runBtn.disabled = false;
        return;
      }

      const jsCode = data.js || data.result;
      jsEditor.setValue(jsCode);

      // Undeclared variable warnings
      if (data.undeclared && data.undeclared.length > 0) {
        undeclaredBadge.style.display = "inline-block";
        undeclaredBadge.textContent = "⚠️ Undeclared: " + data.undeclared.join(", ");
      } else {
        undeclaredBadge.style.display = "none";
      }

      // Execute JavaScript
      runJS(jsCode, transpileTime);
      runBtn.disabled = false;
    })
    .catch((err) => {
      outputEditor.setValue("> Network / Server Error:\n" + err.message);
      timingBadge.textContent = "Server Error";
      timingBadge.style.color = "#f43f5e";
      runBtn.disabled = false;
    });
}

// ================= JS EXECUTION ENGINE =================
function runJS(code, transpileMs = 0) {
  let output = [];
  const timingBadge = document.getElementById("timingBadge");
  const execStart = performance.now();

  const consoleBackup = console.log;
  console.log = (...args) => {
    output.push(args.join(" "));
    outputEditor.setValue(output.join("\n"));
  };

  try {
    new Function(code)();
    const execMs = Math.max(1, Math.round(performance.now() - execStart));
    timingBadge.textContent = `⚡ Transpile: ${transpileMs}ms • Run: ${execMs}ms`;
    timingBadge.style.color = "#10b981";

    if (output.length === 0) {
      outputEditor.setValue("> Program exited successfully with no output.\n");
    }
  } catch (err) {
    output.push("> Runtime Error: " + err.message);
    outputEditor.setValue(output.join("\n"));
    timingBadge.textContent = "Runtime Error";
    timingBadge.style.color = "#f43f5e";
  }

  console.log = consoleBackup;
}

// ================= ACTIONS & HELPERS =================
function onPresetChange(presetKey) {
  if (!PRESETS[presetKey] || !editorReady) return;
  const newCode = PRESETS[presetKey];
  cEditor.setValue(newCode);
  localStorage.setItem(STORAGE_KEY, newCode);
  setSaveStatus("Saved");
  showToast(`Loaded Preset: ${presetKey.replace(/_/g, ' ')}`);
}

function resetCurrentPreset() {
  const select = document.getElementById("presetSelect");
  if (select && PRESETS[select.value]) {
    cEditor.setValue(PRESETS[select.value]);
    localStorage.setItem(STORAGE_KEY, PRESETS[select.value]);
    setSaveStatus("Reset");
    showToast("Reset to preset default");
  }
}

function clearOutput() {
  if (outputEditor) {
    outputEditor.setValue("");
    const timingBadge = document.getElementById("timingBadge");
    timingBadge.textContent = "Ready";
    timingBadge.style.color = "#94a3b8";
    showToast("Output cleared");
  }
}

function copyCode(type) {
  let text = "";
  if (type === "c" && cEditor) text = cEditor.getValue();
  else if (type === "js" && jsEditor) text = jsEditor.getValue();
  else if (type === "output" && outputEditor) text = outputEditor.getValue();

  if (!text) {
    showToast("Nothing to copy!");
    return;
  }

  navigator.clipboard.writeText(text).then(
    () => showToast(`Copied ${type.toUpperCase()} to clipboard!`),
    () => showToast("Failed to copy.")
  );
}

function changeTheme(theme) {
  if (window.monaco) {
    monaco.editor.setTheme(theme);
    showToast(`Theme set to ${theme}`);
  }
}

function setSaveStatus(text) {
  const el = document.getElementById("saveStatus");
  if (el) el.textContent = text;
}

function showToast(msg) {
  const toast = document.getElementById("toast");
  if (!toast) return;
  toast.textContent = msg;
  toast.classList.add("show");
  setTimeout(() => {
    toast.classList.remove("show");
  }, 2200);
}
