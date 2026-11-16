#!/bin/bash
# Ativa a squad DotAgents no projeto pelo plugin: memories/, docs/ e o bloco gerido do CLAUDE.md.
# Idempotente: arquivo existente em memories/ é preservado e o bloco é substituído no lugar.
set -eu
PLUGIN="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "${1:-$PWD}"

if [ -f .claude/hooks/dotagents-gate.sh ] || [ -f .claude/agents/techlead.md ]; then
  echo "Este projeto já tem o DotAgents instalado pelo install.sh (.claude/hooks ou .claude/agents)."
  echo "Para migrar para o plugin: remova do .claude/ as pastas agents, skills, commands e hooks do"
  echo "DotAgents e as entradas dotagents-gate/dotagents-remind do .claude/settings.json; depois rode"
  echo "/dotagents:setup de novo. memories/ e docs/ são preservados."
  exit 2
fi

echo "memories/ (só o que falta):"
(cd "$PLUGIN/memories" && find . -type f) | sed 's|^\./||' | while IFS= read -r rel; do
  [ -f "memories/$rel" ] && continue
  mkdir -p "memories/$(dirname "$rel")"
  cp "$PLUGIN/memories/$rel" "memories/$rel"
  echo "  + memories/$rel"
done

mkdir -p docs/todo docs/done docs/adr
echo "docs/todo, docs/done e docs/adr: ok"

BLOCO="$PLUGIN/scripts/bloco-claude.md"
if [ -f CLAUDE.md ] && grep -q 'dotagents:begin' CLAUDE.md; then
  awk -v bloco="$BLOCO" '
    /<!-- dotagents:begin/ { while ((getline l < bloco) > 0) print l; pular=1; next }
    /<!-- dotagents:end/   { pular=0; next }
    !pular { print }' CLAUDE.md > CLAUDE.md.tmp && mv CLAUDE.md.tmp CLAUDE.md
  echo "CLAUDE.md: bloco do DotAgents atualizado"
elif [ -f CLAUDE.md ]; then
  { cat "$BLOCO"; echo; cat CLAUDE.md; } > CLAUDE.md.tmp && mv CLAUDE.md.tmp CLAUDE.md
  echo "CLAUDE.md: bloco do DotAgents inserido no topo"
else
  cp "$BLOCO" CLAUDE.md
  echo "CLAUDE.md: criado com o bloco do DotAgents"
fi

echo
echo "Pronto. Reinicie a sessão do Claude Code e rode /dotagents:dot-agent-bootstrap."
