# C to JavaScript Converter

This project is a web-based tool that translates C code into JavaScript and executes it in the browser. It features a Python-based backend for parsing and conversion, and a frontend utilizing the Monaco Editor for a seamless coding experience.

## Project Structure

The project is divided into two main components:

- **Backend (`/backend`)**: A Flask application that handles the transpilation logic using regex-based tokenization.
- **Frontend (`/frontend`)**: A web interface for writing C code, viewing the generated JavaScript, and seeing the execution output.

## Features

- **Syntax Translation**: Converts C variable declarations, loops, functions, and arrays to JavaScript.
- **Standard Library Support**:
  - `stdio.h`: `printf` is converted to `console.log`, `scanf` to `prompt`.
  - `math.h`: Maps functions like `sqrt`, `pow`, `sin` to JavaScript's `Math` object.
- **Structs**: Converts C structs into JavaScript objects.
- **Live Execution**: Captures console output and displays it within the application.
- **Validation**: Checks for undeclared variables and unsafe code usage before execution.

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