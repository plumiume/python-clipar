# Sphinx Documentation Build Script
# Usage: uv run python build_docs.py

import subprocess
import sys
from pathlib import Path

def main():
    """Build Sphinx documentation."""
    sphinx_dir = Path(__file__).parent
    source_dir = sphinx_dir / "source"
    build_dir = sphinx_dir.parent / "docs" / "html"
    
    # Ensure build directory exists
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Run sphinx-build
    cmd = [
        "sphinx-build",
        "-b", "html",
        "-d", str(build_dir / ".doctrees"),
        str(source_dir),
        str(build_dir)
    ]
    
    print(f"Building documentation...")
    print(f"Source: {source_dir}")
    print(f"Output: {build_dir}")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print(f"\nDocumentation built successfully!")
        print(f"Open: {build_dir / 'index.html'}")
    else:
        print(f"\nBuild failed with exit code {result.returncode}")
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()
