let cEditor, jsEditor, outputEditor;
let editorReady = false;

// ===== MONACO LOADER =====
require.config({
  paths: {
    vs: "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs"
  }
});

require(["vs/editor/editor.main"], function () {

  // ----- C EDITOR -----
  cEditor = monaco.editor.create(document.getElementById("cEditor"), {
    value: `#include <stdio.h>

int main(){
    int n;
    printf("Enter Your Number: ");
    scanf("%d", &n);
    printf("Number is %d", n);
}`,
    language: "c",
    theme: "vs-dark",
    automaticLayout: true
  });

  // ----- JS EDITOR -----
  jsEditor = monaco.editor.create(document.getElementById("jsEditor"), {
    value: "",
    language: "javascript",
    theme: "vs-dark",
    readOnly: true,
    automaticLayout: true
  });

  // ----- OUTPUT -----
  outputEditor = monaco.editor.create(document.getElementById("outputEditor"), {
    value: "",
    language: "plaintext",
    theme: "vs-dark",
    readOnly: true,
    minimap: { enabled: false },
    lineNumbers: "off",
    wordWrap: "on"
  });

  editorReady = true;
  const btn = document.getElementById("runBtn");
  if (btn) btn.disabled = false;
});

// ===== CONVERT BUTTON =====
function convert() {
  if (!editorReady) {
    alert("Editor still loading...");
    return;
  }

  outputEditor.setValue("");

  const cCode = cEditor.getValue();

  fetch("https://code-converter-c-to-js.onrender.com/convert", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code: cCode })
  })
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        outputEditor.setValue("> Compile Error:\n" + data.error);
        return;
      }

      const jsCode = data.js || data.result;
      jsEditor.setValue(jsCode);
      runJS(jsCode);
    })
    .catch(err => {
      outputEditor.setValue("> Error: " + err.message);
    });
}

// ===== JS EXECUTION ENGINE =====
function runJS(code) {
  let output = [];

  const consoleBackup = console.log;
  console.log = (...args) => {
    output.push("> " + args.join(" "));
    outputEditor.setValue(output.join("\n"));
  };

  try {
    // prompt() works synchronously
    new Function(code)();
  } catch (err) {
    output.push("> Runtime Error: " + err.message);
    outputEditor.setValue(output.join("\n"));
  }

  console.log = consoleBackup;
}
