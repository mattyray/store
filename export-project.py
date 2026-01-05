#!/usr/bin/env python3
"""
Export project source code to a single markdown file for Claude.
Run from project root: python export-project.py
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Files to include (relative to project root)
INCLUDE_PATTERNS = [
    # Backend - Django apps
    "backend/apps/catalog/models.py",
    "backend/apps/catalog/views.py",
    "backend/apps/catalog/serializers.py",
    "backend/apps/catalog/urls.py",
    "backend/apps/catalog/admin.py",
    "backend/apps/orders/models.py",
    "backend/apps/orders/views.py",
    "backend/apps/orders/serializers.py",
    "backend/apps/orders/urls.py",
    "backend/apps/orders/admin.py",
    "backend/apps/orders/emails.py",
    "backend/apps/payments/views.py",
    "backend/apps/payments/urls.py",
    "backend/apps/core/models.py",
    "backend/apps/core/views.py",
    "backend/apps/core/urls.py",
    "backend/apps/core/admin.py",
    # Backend - Config
    "backend/config/settings/base.py",
    "backend/config/settings/development.py",
    "backend/config/settings/production.py",
    "backend/config/urls.py",
    # Backend - Root files
    "backend/requirements.txt",
    "backend/Dockerfile",
    "backend/.env.example",
    # Frontend - App pages
    "frontend/src/app/layout.tsx",
    "frontend/src/app/page.tsx",
    "frontend/src/app/photos/page.tsx",
    "frontend/src/app/photos/[slug]/page.tsx",
    "frontend/src/app/collections/page.tsx",
    "frontend/src/app/collections/[slug]/page.tsx",
    "frontend/src/app/book/page.tsx",
    "frontend/src/app/book/[slug]/page.tsx",
    "frontend/src/app/cart/page.tsx",
    "frontend/src/app/gift-cards/page.tsx",
    "frontend/src/app/track-order/page.tsx",
    "frontend/src/app/order/success/page.tsx",
    "frontend/src/app/about/page.tsx",
    "frontend/src/app/contact/page.tsx",
    # Frontend - Components
    "frontend/src/components/Header.tsx",
    "frontend/src/components/Footer.tsx",
    "frontend/src/components/PhotoCard.tsx",
    # Frontend - Lib & Types
    "frontend/src/lib/api.ts",
    "frontend/src/types/index.ts",
    # Frontend - Config
    "frontend/package.json",
    "frontend/tailwind.config.ts",
    "frontend/next.config.ts",
    "frontend/Dockerfile",
    # Root
    "docker-compose.yml",
]

# Language mapping for syntax highlighting
LANG_MAP = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".js": "javascript",
    ".jsx": "jsx",
    ".json": "json",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".md": "markdown",
    ".txt": "text",
    ".env": "bash",
    "Dockerfile": "dockerfile",
}


def get_language(filepath: str) -> str:
    """Get syntax highlighting language for a file."""
    name = Path(filepath).name
    if name == "Dockerfile":
        return "dockerfile"
    ext = Path(filepath).suffix
    return LANG_MAP.get(ext, "text")


def generate_tree(files: list[str]) -> str:
    """Generate a simple tree view of included files."""
    tree_lines = ["```"]
    tree_lines.append("store/")

    # Group by directory
    dirs = {}
    for f in sorted(files):
        parts = f.split("/")
        if len(parts) == 1:
            dirs.setdefault(".", []).append(parts[0])
        else:
            top = parts[0]
            rest = "/".join(parts[1:])
            dirs.setdefault(top, []).append(rest)

    for top_dir in sorted(dirs.keys()):
        if top_dir == ".":
            for f in dirs[top_dir]:
                tree_lines.append(f"├── {f}")
        else:
            tree_lines.append(f"├── {top_dir}/")
            for f in sorted(dirs[top_dir]):
                tree_lines.append(f"│   ├── {f}")

    tree_lines.append("```")
    return "\n".join(tree_lines)


def export_project():
    """Export all project files to a single markdown file."""
    output_lines = []

    # Header
    output_lines.append("# Photography Store - Project Export")
    output_lines.append("")
    output_lines.append("Django + Next.js e-commerce store for fine art photography prints.")
    output_lines.append("")
    output_lines.append("**Stack:** Django 5 + DRF (backend), Next.js 16 + Tailwind (frontend), PostgreSQL, Stripe, Docker")
    output_lines.append("")

    # Collect existing files
    existing_files = []
    for pattern in INCLUDE_PATTERNS:
        filepath = PROJECT_ROOT / pattern
        if filepath.exists():
            existing_files.append(pattern)

    # File tree
    output_lines.append("## Project Structure")
    output_lines.append("")
    output_lines.append(generate_tree(existing_files))
    output_lines.append("")

    # File contents
    output_lines.append("---")
    output_lines.append("")
    output_lines.append("## Source Files")
    output_lines.append("")

    for pattern in existing_files:
        filepath = PROJECT_ROOT / pattern
        lang = get_language(pattern)

        output_lines.append(f"### {pattern}")
        output_lines.append("")
        output_lines.append(f"```{lang}")

        try:
            content = filepath.read_text()
            output_lines.append(content.rstrip())
        except Exception as e:
            output_lines.append(f"# Error reading file: {e}")

        output_lines.append("```")
        output_lines.append("")

    # Write output
    output_path = PROJECT_ROOT / "project-export.md"
    output_path.write_text("\n".join(output_lines))

    print(f"Exported {len(existing_files)} files to {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    export_project()
