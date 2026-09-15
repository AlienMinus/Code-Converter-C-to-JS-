# C to JavaScript Converter

This project is a web-based tool that translates C code into JavaScript and executes it in the browser. It features a Python-based backend for parsing and conversion, and a frontend utilizing the Monaco Editor for a seamless coding experience.

## Project Structure

The project is divided into two main components:

- **Backend (`/backend`)**: A Flask application that handles the transpilation logic using regex-based tokenization.
- **Frontend (`/frontend`)**: A web interface for writing C code, viewing the generated JavaScript, and seeing the execution output.

## Features

- **Syntax Translation**: Converts C variable declarations, loops, functions, and arrays to JavaScript.
- **Pointers & Memory Referencing**:
  - Full pointer support: `int *p = &x;`, `*p = 20;`, pass-by-reference in functions (e.g. `swap(&a, &b)`).
  - Pointer arithmetic: `p++`, `p--`, `*(p + i)`.
  - Arrow operator on struct pointers: `ptr->field` or `(*ptr).field`.
  - Array-pointer decay and null pointers (`NULL`).
- **`sizeof` Operator**: Compile-time resolution for types (`sizeof(int)` == 4, `sizeof(double)` == 8, `sizeof(pointer)` == 8), arrays (`sizeof(arr)` == length * size), structs, and runtime dynamic fallback.
- **`typedef` System**: Full typedef support for primitives (`typedef int my_int;`), pointers (`typedef int* IntPtr;`), structs (`typedef struct { ... } Point;`), and enums.
- **Type Casting**: C-style explicit casts like `(int)f`, `(float)x`, `(char)code`, `(bool)val`, and pointer casts `(void*)ptr`.
- **Extended Types & Modifiers**: `short`, `long`, `long long`, `unsigned`, `signed`, `bool`, `_Bool`, `const`.
- **Enums**: `enum Color { RED, GREEN = 2, BLUE };` translated to JavaScript constants.
- **Standard Library Support**:
  - `stdio.h`: `printf` to `console.log`, `scanf` to `prompt`.
  - `stdlib.h`: `malloc`, `calloc`, `free`, `abs`, `rand`, `srand`, `atoi`, `atof`, `exit`.
  - `string.h`: `strlen`, `strcpy`, `strcmp`, `strcat`, `strncpy`, `strncmp`.
  - `ctype.h`: `toupper`, `tolower`, `isdigit`, `isalpha`, `isalnum`, `isspace`.
  - `math.h`: `sqrt`, `pow`, `sin`, `cos`, `tan`, `floor`, `ceil`, `round`, `log`, `exp`.
  - `stdbool.h`: `bool`, `true`, `false`.
  - `limits.h`: `INT_MAX`, `INT_MIN`, `CHAR_BIT`.
- **Structs**: Converts C structs (including positional and designated initializers) into JavaScript objects.
- **Live Execution**: Captures console output and displays it within the application.
- **Validation**: Smart validation detecting undeclared variables without false positives on strings, template literals, or property accesses.

## Prerequisites

- **Python 3.x**
- **pip** (Python package installer)

## Installation & Setup

### 1. Backend Setup

Navigate to the `backend` directory and install the required dependencies:

```bash
cd backend
pip install flask flask-cors waitress
```

### 2. Run the Server

Start the backend server:

```bash
python app.py
```

The server will start on `http://127.0.0.1:5000`.

### 3. Access the Application

Open your web browser and navigate to:

```
http://127.0.0.1:5000
```

## Usage

1. **Write C Code**: Enter your C code in the left-hand editor pane.
2. **Convert & Run**: Click the "Convert & Run" button in the toolbar.
3. **View Results**:
   - The generated JavaScript code appears in the middle pane.
   - The execution output (or errors) appears in the right-hand pane.

## Technologies Used

- **Backend**: Python, Flask, Waitress
- **Frontend**: HTML5, JavaScript, Monaco Editor (VS Code editor core)