#!/usr/bin/env bash
# Roblox Gamesmith installer: toolchain, skill link for your agent, PATH, docs cache, then a health check.
#   ./install.sh                 everything
#   ./install.sh --no-path       don't touch your shell profile
#   ./install.sh --agent codex   link for Codex instead of Claude Code (or --agent both)
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAME="roblox-gamesmith"
AGENT="claude"
EDIT_PATH=1
while [[ $# -gt 0 ]]; do
	case "$1" in
		--no-path) EDIT_PATH=0 ;;
		--agent) AGENT="${2:?claude, codex or both}"; shift ;;
		-h|--help) sed -n 2,5p "$0"; exit 0 ;;
		*) echo "unknown option $1"; exit 1 ;;
	esac
	shift
done

say() { printf '\n\033[1m%s\033[0m\n' "$1"; }

[[ "$(uname)" == "Darwin" ]] || { echo "Roblox Gamesmith drives the macOS Roblox Studio app; macOS is required."; exit 1; }
command -v python3 >/dev/null || { echo "Python 3 is required: brew install python"; exit 1; }
command -v git >/dev/null || { echo "git is required: xcode-select --install"; exit 1; }

say "1/5 Roblox toolchain (Rokit: Rojo, Selene, StyLua, Lune)"
if ! command -v rokit >/dev/null && [[ ! -x "$HOME/.rokit/bin/rokit" ]]; then
	curl -sSf https://raw.githubusercontent.com/rojo-rbx/rokit/main/scripts/install.sh | bash
fi
export PATH="$HOME/.rokit/bin:$PATH"
for tool in rojo-rbx/rojo@7.7.1 Kampfkarren/selene@0.32.0 JohnnyMorganz/StyLua@2.6.0 lune-org/lune@0.11.1; do
	bin="$(basename "${tool%@*}" | tr '[:upper:]' '[:lower:]')"
	if command -v "$bin" >/dev/null; then echo "  $bin: $(command -v "$bin")"; else rokit add --global "$tool"; fi
done

say "2/5 uv (runs the research and docs tools with their Python packages)"
if command -v uv >/dev/null; then echo "  uv: $(command -v uv)"
else curl -LsSf https://astral.sh/uv/install.sh | sh; export PATH="$HOME/.local/bin:$PATH"; fi
python3 -c "import PIL" 2>/dev/null || python3 -m pip install --user --quiet pillow 2>/dev/null \
	|| echo "  (optional) install Pillow for contact sheets: python3 -m pip install --user pillow"

say "3/5 Link the skill for your agent"
link() {
	local dir="$1/skills"
	mkdir -p "$dir"
	if [[ -e "$dir/$NAME" && ! -L "$dir/$NAME" ]]; then
		echo "  $dir/$NAME exists and is not a link; leaving it alone"
	else
		ln -sfn "$HERE" "$dir/$NAME"
		echo "  $dir/$NAME -> $HERE"
	fi
}
case "$AGENT" in
	claude) link "$HOME/.claude" ;;
	codex) link "$HOME/.codex" ;;
	both) link "$HOME/.claude"; link "$HOME/.codex" ;;
	*) echo "--agent must be claude, codex or both"; exit 1 ;;
esac

say "4/5 Put the tools on your PATH"
LINE="export PATH=\"$HERE/tools:\$HOME/.rokit/bin:\$PATH\""
PROFILE="$HOME/.zshrc"; [[ "${SHELL:-}" == */bash ]] && PROFILE="$HOME/.bash_profile"
if [[ $EDIT_PATH -eq 1 ]]; then
	grep -qsF "$HERE/tools" "$PROFILE" || { printf '\n# Roblox Gamesmith\n%s\n' "$LINE" >> "$PROFILE"; echo "  added to $PROFILE"; }
else
	echo "  skipped; add this yourself: $LINE"
fi
export PATH="$HERE/tools:$PATH"

say "5/5 Roblox creator docs (offline copy for rbxdocs, ~35 MB text)"
"$HERE/tools/rbxdocs" sync || echo "  docs sync failed; it will retry on first use"

say "Health check"
"$HERE/tools/rbxgame" doctor || true

cat <<EOF

Next:
  1. Open Roblox Studio, open any place, and turn on "Enable Studio as MCP server"
     (Assistant panel -> ... -> Manage MCP Servers).
  2. Open a new terminal (for PATH), start your agent, and ask:
       "Make me a Roblox game where you <your idea>. Use the roblox-gamesmith skill."
  3. Or try the example: cd "$HERE/examples/lily-pad-leap" && rbxgame open
EOF
