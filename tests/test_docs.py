"""The docs are the product: every path they mention must exist, and every reference must be reachable."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = [p for p in ROOT.rglob("*.md") if "examples" not in p.parts and ".git" not in p.parts]
PATH_RE = re.compile(r"`((?:references|workflows|templates|tools|examples|tests)/[\w./-]+?)`")
LINK_RE = re.compile(r"\]\((?!https?://|#|mailto:)([^)#\s]+)")


class Docs(unittest.TestCase):
    def test_mentioned_paths_exist(self):
        missing = []
        for doc in DOCS:
            text = doc.read_text()
            for m in PATH_RE.finditer(text):
                path = m.group(1).rstrip(".,")
                if "<" in path or "*" in path:
                    continue
                if not (ROOT / path).exists() and not (doc.parent / path).exists():
                    missing.append(f"{doc.relative_to(ROOT)}: {path}")
            for m in LINK_RE.finditer(text):
                target = m.group(1)
                if not (doc.parent / target).exists() and not (ROOT / target).exists():
                    missing.append(f"{doc.relative_to(ROOT)}: link {target}")
        self.assertEqual(missing, [], "paths mentioned in docs that don't exist")

    def test_every_reference_is_routed(self):
        skill = (ROOT / "SKILL.md").read_text()
        routed = set(re.findall(r"references/([\w-]+\.md)", skill))
        linked = set()
        for doc in DOCS:
            linked |= set(re.findall(r"([\w-]+\.md)", doc.read_text()))
        orphans = [p.name for p in (ROOT / "references").glob("*.md") if p.name not in routed and p.name not in linked]
        self.assertEqual(orphans, [], "references nothing points to")
        unrouted = [p.name for p in (ROOT / "references").glob("*.md") if p.name not in routed]
        self.assertEqual(unrouted, [], "references missing from the SKILL.md routing table")

    def test_skill_front_matter(self):
        head = (ROOT / "SKILL.md").read_text().split("---")[1]
        self.assertIn("name: roblox-gamesmith", head)
        self.assertIn("description:", head)
        self.assertLess(len(head), 1200, "keep the description short: agents read it to decide relevance")

    def test_tools_are_executable(self):
        for name in ("rbxgame", "studio", "rbxdocs", "rbx-research", "yt-research", "devforum", "rbxcloud"):
            p = ROOT / "tools" / name
            self.assertTrue(p.exists(), name)
            self.assertTrue(p.stat().st_mode & 0o111, f"{name} is not executable")


if __name__ == "__main__":
    unittest.main()
