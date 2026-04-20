import re
import shutil
from pathlib import Path

SRC = Path(r"C:\Users\chris\.claude-mem\graphify-corpus")
DST = Path(r"C:\Users\chris\Desktop\claude-mem-obsidian-full")


def slugify(value: str) -> str:
    value = (value or "unknown").strip()
    value = re.sub(r"[^A-Za-z0-9._ -]+", "_", value)
    value = value.replace(" ", "_")
    value = re.sub(r"_+", "_", value)
    return value[:120] or "unknown"


def parse_frontmatter(text: str) -> dict:
    meta = {}
    if not text.startswith("---\n"):
        return meta

    lines = text.splitlines()
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return meta

    for line in lines[1:end_idx]:
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        meta[key.strip()] = val.strip()

    return meta


def append_related_block(content: str, type_name: str, project: str, session: str) -> str:
    if "## Related" in content:
        return content

    type_slug = slugify(type_name)
    proj_slug = slugify(project)
    sess_slug = slugify(session)

    block = (
        "\n\n## Related\n"
        f"- [[_hubs/types/{type_slug}|Type: {type_name or 'unknown'}]]\n"
        f"- [[_hubs/projects/{proj_slug}|Project: {project or 'unknown'}]]\n"
        f"- [[_hubs/sessions/{sess_slug}|Session]]\n"
    )

    return content.rstrip() + block + "\n"


def write_hub(path: Path, title: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = f"# {title}\n\n{body}\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    if not SRC.exists():
        raise FileNotFoundError(f"Source not found: {SRC}")

    if DST.exists():
        shutil.rmtree(DST)
    DST.mkdir(parents=True, exist_ok=True)

    copied_files = 0
    for folder in ["observations", "prompts", "summaries", "sessions"]:
        src_dir = SRC / folder
        dst_dir = DST / folder
        if src_dir.exists():
            shutil.copytree(src_dir, dst_dir)
            copied_files += len(list(dst_dir.glob("*.md")))

    projects = set()
    types = set()
    sessions = set()

    md_files = list(DST.rglob("*.md"))
    updated = 0

    for file_path in md_files:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        meta = parse_frontmatter(content)

        type_name = meta.get("type") or meta.get("source_type") or "unknown"
        project = meta.get("project") or "unknown"
        session = (
            meta.get("session_id")
            or meta.get("memory_session_id")
            or meta.get("content_session_id")
            or "unknown"
        )

        projects.add(project)
        types.add(type_name)
        sessions.add(session)

        new_content = append_related_block(content, type_name, project, session)
        if new_content != content:
            file_path.write_text(new_content, encoding="utf-8")
            updated += 1

    write_hub(
        DST / "Home.md",
        "Claude-Mem Full Corpus Vault",
        "\n".join(
            [
                f"- Total markdown files: **{len(md_files)}**",
                f"- Projects: **{len(projects)}**",
                f"- Types: **{len(types)}**",
                f"- Sessions: **{len(sessions)}**",
                "",
                "Open Graph View in Obsidian to explore the full connected corpus.",
                "",
                "Quick links:",
                "- [[_hubs/Types Index]]",
                "- [[_hubs/Projects Index]]",
                "- [[_hubs/Sessions Index]]",
            ]
        ),
    )

    types_index_lines = ["# Types Index", ""]
    for t in sorted(types):
        slug = slugify(t)
        types_index_lines.append(f"- [[_hubs/types/{slug}|{t}]]")
        write_hub(
            DST / "_hubs" / "types" / f"{slug}.md",
            f"Type: {t}",
            "Backlinks panel shows all notes connected to this type.",
        )
    write_hub(DST / "_hubs" / "Types Index.md", "Types Index", "\n".join(types_index_lines[2:]))

    projects_index_lines = ["# Projects Index", ""]
    for p in sorted(projects):
        slug = slugify(p)
        projects_index_lines.append(f"- [[_hubs/projects/{slug}|{p}]]")
        write_hub(
            DST / "_hubs" / "projects" / f"{slug}.md",
            f"Project: {p}",
            "Backlinks panel shows all notes connected to this project.",
        )
    write_hub(DST / "_hubs" / "Projects Index.md", "Projects Index", "\n".join(projects_index_lines[2:]))

    sessions_index_lines = ["# Sessions Index", ""]
    for s in sorted(sessions):
        slug = slugify(s)
        sessions_index_lines.append(f"- [[_hubs/sessions/{slug}|{s}]]")
        write_hub(
            DST / "_hubs" / "sessions" / f"{slug}.md",
            f"Session: {s}",
            "Backlinks panel shows all notes connected to this session.",
        )
    write_hub(DST / "_hubs" / "Sessions Index.md", "Sessions Index", "\n".join(sessions_index_lines[2:]))

    print(f"Vault created: {DST}")
    print(f"Copied files: {copied_files}")
    print(f"Markdown files processed: {len(md_files)}")
    print(f"Files updated with links: {updated}")
    print(f"Projects: {len(projects)}, Types: {len(types)}, Sessions: {len(sessions)}")


if __name__ == "__main__":
    main()
