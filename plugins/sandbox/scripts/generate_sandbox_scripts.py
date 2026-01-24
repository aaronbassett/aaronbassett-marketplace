#!/usr/bin/env python3
"""
Generate sandbox management scripts (up.sh, shell.sh, run.sh, stop.sh).

Usage:
    python3 generate_sandbox_scripts.py \
        --name myproject \
        --location /path/to/sandbox \
        --ports 3000,3001,3002 \
        --output /path/to/sandbox/sandbox/

Creates four bash scripts for managing the sandbox container.
"""

import argparse
from pathlib import Path


def generate_up_script(project_name: str, location: str, ports: str) -> str:
    """Generate up.sh script."""
    return f"""#!/usr/bin/env bash
# Start the {project_name} sandbox

set -e

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_NAME="{project_name}"

echo "Building sandbox container..."
docker build -t "sandbox-$PROJECT_NAME" "$PROJECT_DIR"

echo "Starting sandbox..."
docker run -d \\
    --name "sandbox-$PROJECT_NAME" \\
    -v "$PROJECT_DIR/workspace:/workspace" \\
    -v "$PROJECT_DIR/.docker-cache/cargo:/root/.cargo" \\
    -v "$PROJECT_DIR/.docker-cache/npm:/root/.npm" \\
    -v "$PROJECT_DIR/.docker-cache/pip:/root/.cache/pip" \\
    -v "$PROJECT_DIR/.docker-cache/claude:/root/.claude" \\
    -p {ports} \\
    --env-file "$PROJECT_DIR/.env" \\
    "sandbox-$PROJECT_NAME"

echo ""
echo "Sandbox is starting..."
echo "Waiting for container to be ready..."
sleep 2

if docker ps | grep -q "sandbox-$PROJECT_NAME"; then
    echo ""
    echo "✅ Sandbox is running!"
    echo ""
    echo "Access the sandbox:"
    echo "  Interactive shell: ./sandbox/shell.sh"
    echo "  Run commands: ./sandbox/run.sh <command>"
    echo "  Stop sandbox: ./sandbox/stop.sh"
    echo ""
    echo "Edit files in: $PROJECT_DIR/workspace/"
else
    echo ""
    echo "❌ Failed to start sandbox"
    echo "Check logs: docker logs sandbox-$PROJECT_NAME"
    exit 1
fi
"""


def generate_shell_script(project_name: str) -> str:
    """Generate shell.sh script."""
    return f"""#!/usr/bin/env bash
# Open interactive shell in {project_name} sandbox

set -e

PROJECT_NAME="{project_name}"

if ! docker ps | grep -q "sandbox-$PROJECT_NAME"; then
    echo "❌ Sandbox is not running"
    echo "Start it with: ./sandbox/up.sh"
    exit 1
fi

echo "Entering sandbox shell..."
echo "(Type 'exit' to leave the sandbox)"
echo ""

docker exec -it "sandbox-$PROJECT_NAME" /bin/zsh
"""


def generate_run_script(project_name: str) -> str:
    """Generate run.sh script."""
    return f"""#!/usr/bin/env bash
# Run command in {project_name} sandbox

set -e

PROJECT_NAME="{project_name}"

if ! docker ps | grep -q "sandbox-$PROJECT_NAME"; then
    echo "❌ Sandbox is not running"
    echo "Start it with: ./sandbox/up.sh"
    exit 1
fi

if [ $# -eq 0 ]; then
    echo "Usage: ./sandbox/run.sh <command>"
    echo ""
    echo "Examples:"
    echo "  ./sandbox/run.sh cargo test"
    echo "  ./sandbox/run.sh npm run dev"
    echo "  ./sandbox/run.sh python -m pytest"
    exit 1
fi

docker exec "sandbox-$PROJECT_NAME" "$@"
"""


def generate_stop_script(project_name: str, location: str) -> str:
    """Generate stop.sh script."""
    return f"""#!/usr/bin/env bash
# Stop the {project_name} sandbox

set -e

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_NAME="{project_name}"

if ! docker ps -a | grep -q "sandbox-$PROJECT_NAME"; then
    echo "Sandbox container not found"
    exit 0
fi

echo "Fixing workspace file permissions..."
docker exec "sandbox-$PROJECT_NAME" chown -R $(id -u):$(id -g) /workspace || true

echo "Stopping sandbox..."
docker stop "sandbox-$PROJECT_NAME"

echo "Removing container..."
docker rm "sandbox-$PROJECT_NAME"

echo "✅ Sandbox stopped"
echo ""
echo "Workspace files preserved in: $PROJECT_DIR/workspace/"
echo "Docker caches preserved in: $PROJECT_DIR/.docker-cache/"
echo ""
echo "To start again: ./sandbox/up.sh"
"""


def main():
    parser = argparse.ArgumentParser(description="Generate sandbox management scripts")
    parser.add_argument("--name", required=True, help="Project name")
    parser.add_argument("--location", required=True, help="Sandbox directory path")
    parser.add_argument(
        "--ports",
        default="3000-3999:3000-3999",
        help="Port mapping (default: 3000-3999:3000-3999)",
    )
    parser.add_argument("--output", required=True, help="Output directory for scripts")

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    scripts = {
        "up.sh": generate_up_script(args.name, args.location, args.ports),
        "shell.sh": generate_shell_script(args.name),
        "run.sh": generate_run_script(args.name),
        "stop.sh": generate_stop_script(args.name, args.location),
    }

    for filename, content in scripts.items():
        script_path = output_dir / filename
        script_path.write_text(content)
        script_path.chmod(0o755)  # Make executable
        print(f"Created: {script_path}")

    print(f"\\n✅ Generated {len(scripts)} management scripts in {output_dir}")


if __name__ == "__main__":
    main()
