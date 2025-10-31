# VS Code Python UV Project Template

This template provides a complete VS Code setup for Python projects using uv package manager with the following features:

## Features

- ✅ Git auto-sync for work/* branches
- ✅ Auto-commit and push on VS Code close
- ✅ Virtual environment management with uv
- ✅ OneDrive-safe virtual environment location
- ✅ Automatic virtual environment activation
- ✅ Custom tasks and keybindings

## Quick Setup

### 1. Copy Template Files

Copy the following files from this template to your new project:

```
.vscode/
├── settings-template.json     → settings.json
├── tasks-template.json       → tasks.json  
├── keybindings-template.json → keybindings.json
├── setup-venv-template.ps1   → setup-venv.ps1
└── auto-commit-template.ps1  → auto-commit.ps1
```

### 2. Configure Project Settings

Edit the copied files and replace the following placeholders:

- `{{PROJECT_NAME}}` - Your project name (e.g., "MyProject")
- `{{PYTHON_VERSION}}` - Python version (e.g., "cp312", "cp311")
- `{{VENV_BASE_PATH}}` - Base path for virtual environments (e.g., "D:/Users/yourname/PythonVenvs")

### 3. Project Structure

Your project should have:
- `pyproject.toml` - Python project configuration
- `uv.lock` - uv lock file
- `.gitignore` - Including `.venv/` and other Python ignores

### 4. Run Setup

```powershell
# Create virtual environment
.vscode\setup-venv.ps1 -Action create

# Check status
.vscode\setup-venv.ps1 -Action info
```

## Configuration Details

### Git Auto-sync Settings
- Automatic fetch every 3 minutes
- Auto-pull before branch checkout  
- Smart commit and auto-push for work/* branches
- No confirmation dialogs for sync operations

### Python Environment Settings
- Virtual environments stored outside OneDrive
- Automatic activation in VS Code terminals
- uv-based package management
- Development dependencies included

### VS Code Integration
- Custom tasks for common operations
- Keyboard shortcuts for quick access
- Command palette integration
- Proper Python interpreter detection

## Available Commands

### Git Operations
- `Ctrl+Shift+G, Ctrl+Shift+S` - Sync with remote
- `Ctrl+Shift+G, Ctrl+Shift+P` - Push to remote
- `Ctrl+Alt+W` - Auto-commit and push (work/* branches)

### Python Environment
- `Ctrl+Shift+P, Ctrl+Shift+A` - Activate virtual environment
- Command Palette: "Python: Setup Virtual Environment"
- Command Palette: "Python: Show Virtual Environment Info"

### Tasks (Ctrl+Shift+P → "Tasks: Run Task")
- Git: Sync with remote
- Git: Push to remote
- Git: Work branch auto commit and push
- Python: Setup Virtual Environment
- Python: Show Virtual Environment Info
- Python: Activate Virtual Environment

## Customization

### Change Virtual Environment Location
Edit in `settings.json`:
```json
"python.defaultInterpreterPath": "{{VENV_BASE_PATH}}/{{PROJECT_NAME}}/{{PYTHON_VERSION}}/Scripts/python.exe",
"python.venvPath": "{{VENV_BASE_PATH}}",
"python.venvFolders": ["{{VENV_BASE_PATH}}"]
```

### Modify Auto-commit Behavior
Edit `auto-commit.ps1`:
- Change branch pattern (currently `work/*`)
- Modify commit message format
- Adjust error handling

### Add Custom Tasks
Add to `tasks.json`:
```json
{
    "label": "Your Custom Task",
    "type": "shell",
    "command": "your-command",
    "group": "build"
}
```

## Troubleshooting

### Common Issues
1. **PowerShell Execution Policy**: Run `Set-ExecutionPolicy RemoteSigned`
2. **Remote Not Found**: Check git remote configuration
3. **Virtual Environment Not Activated**: Restart VS Code or run activation task
4. **uv Not Found**: Install uv package manager

### Debug Commands
```powershell
# Check virtual environment
.vscode\setup-venv.ps1 -Action info

# Check git remotes
git remote -v

# Test auto-commit (dry run)
.vscode\auto-commit.ps1 -Action status
```

## Template Files

The following template files are available:
- `settings-template.json` - VS Code workspace settings
- `tasks-template.json` - Custom tasks definition
- `keybindings-template.json` - Keyboard shortcuts
- `setup-venv-template.ps1` - Virtual environment management
- `auto-commit-template.ps1` - Git auto-commit functionality

Each template file contains placeholders that should be replaced with your project-specific values.