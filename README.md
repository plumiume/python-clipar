# Clipar

**Clipar** is a modern Python library that simplifies command-line interface (CLI) creation using type annotations and decorators. It provides an intuitive way to build robust CLI applications with minimal boilerplate code.

## Features

- 🎯 **Type-driven**: Use Python type annotations to define CLI arguments
- 🎨 **Decorator-based**: Simple `@namespace` and `@group` decorators
- 🔧 **Auto-parsing**: Automatic argument parsing based on type hints
- 📦 **Nested Groups**: Support for nested argument groups
- 🚀 **Easy Integration**: Drop-in replacement for argparse workflows
- ✅ **Type Safe**: Full type checking support with mypy/pylance

## Installation

```bash
pip install git+https://github.com/plumiume/argparse-class-namespace.git
```

## Quick Start

### Basic Usage

```python
from clipar import namespace

@namespace
class Config:
    input_file: str           # positional argument
    output_file: str = "out.txt"  # optional argument with default
    verbose: bool = False     # boolean flag
    workers: int = 1          # integer option

if __name__ == "__main__":
    config = Config.parse_args()
    print(f"Processing {config.input_file} with {config.workers} workers")
```

**Command line usage:**
```bash
python app.py data.csv --output-file results.json --verbose --workers 4
```

### Argument Types

Clipar automatically determines argument types based on Python type annotations:

| Type Annotation | CLI Behavior | Example |
|-----------------|--------------|---------|
| `name: str` | Positional argument | `app.py input.txt` |
| `name: str = "default"` | Optional argument | `--name value` |
| `flag: bool = False` | Boolean flag | `--flag` |
| `count: int = 1` | Integer option | `--count 5` |
| `rate: float = 1.0` | Float option | `--rate 2.5` |

### Nested Groups

Organize related arguments using the `@group` decorator:

```python
from clipar import namespace, group

@group
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    username: str = "admin"
    password: str = "secret"

@group
class LoggingConfig:
    level: str = "INFO"
    file: str = "app.log"
    format: str = "%(asctime)s - %(levelname)s - %(message)s"

@namespace
class AppConfig:
    app_name: str = "MyApp"
    version: str = "1.0.0"
    debug: bool = False
    database = DatabaseConfig
    logging = LoggingConfig

# Usage
config = AppConfig.parse_args([
    "--app-name", "ProductionApp",
    "--debug",
    "--database-host", "prod-db.example.com",
    "--database-port", "3306",
    "--logging-level", "DEBUG"
])

print(f"App: {config.app_name}")
print(f"Database: {config.database.host}:{config.database.port}")
print(f"Log level: {config.logging.level}")
```

## Advanced Features

### Custom Parser Options

Configure the underlying ArgumentParser:

```python
from clipar import namespace

@namespace
class Config:
    input_file: str
    verbose: bool = False

# With custom parser options
config = Config.parse_args(
    args=["--help"],  # Custom arguments
    # Additional ArgumentParser options can be configured
)
```

### Error Handling

Clipar provides clear error messages for invalid arguments:

```python
try:
    config = Config.parse_args()
except SystemExit as e:
    # Handle argument parsing errors
    if e.code != 0:
        print("Invalid arguments provided")
```

### Help Generation

Automatic help generation based on your class structure:

```bash
python app.py --help
```

Output:
```
usage: app.py [-h] [--output-file OUTPUT_FILE] [--verbose] [--workers WORKERS] input_file

positional arguments:
  input_file            

optional arguments:
  -h, --help            show this help message and exit
  --output-file OUTPUT_FILE
  --verbose             
  --workers WORKERS     
```

### Adding Help Messages

Clipar supports adding help messages for arguments using string literals placed after variable declarations:

```python
from clipar import namespace

@namespace
class Config:
    input_file: str
    "Path to the input data file (required)"
    
    output_dir: str = "./output"
    "Directory where processed files will be saved"
    
    workers: int = 4
    "Number of parallel workers for processing"
    
    verbose: bool = False
    "Enable verbose logging output"
    
    dry_run: bool = False
    "Show what would be done without actually executing"

# Command line usage:
config = Config.parse_args(['data.txt', '--workers', '8', '--verbose'])
```

**Help output:**
```
usage: app.py [-h] [--output-dir OUTPUT_DIR] [--workers WORKERS] [--verbose] [--dry-run] input_file

positional arguments:
  input_file            Path to the input data file (required)

options:
  -h, --help            show this help message and exit
  --output-dir OUTPUT_DIR
                        Directory where processed files will be saved
  --workers WORKERS     Number of parallel workers for processing
  --verbose             Enable verbose logging output
  --dry-run             Show what would be done without actually executing
```

**Help messages in groups:**
