#!/bin/sh
# Encaminha os hooks do DotAgents só em projeto ativado pelo plugin (/dotagents:setup).
# Uso: dotagents-guard.sh <gate|remind|session> [claude]
MODO="$1"
ALVO="${2:-claude}"
IN=$(cat 2>/dev/null) || IN=""
ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
DIR=$(cd "$(dirname "$0")" && pwd)
PLUGIN="${CLAUDE_PLUGIN_ROOT:-$(dirname "$DIR")}"

# Projeto instalado pelo install.sh já registra os próprios hooks.
[ -f "$ROOT/.claude/hooks/dotagents-gate.sh" ] && exit 0
# Projeto sem a squad: nada a fazer.
grep -qs 'dotagents:begin' "$ROOT/CLAUDE.md" || exit 0

case "$MODO" in
  gate)
    printf '%s' "$IN" | exec "$DIR/dotagents-gate.sh" "$ALVO"
    ;;
  remind)
    # o remind do original aponta para a instalação em .claude/; no plugin o protocolo fica no plugin
    printf '%s' "$IN" | "$DIR/dotagents-remind.sh" "$ALVO" | R="$PLUGIN" perl -pe 's/\.claude\/commands\/manager\.md/$ENV{R}\/commands\/manager.md/g'
    ;;
  session)
    # o protocolo inteiro passa do limite de saída do hook; a sessão recebe a diretiva e o caminho
    cat <<EOT
# Protocolo da squad DotAgents (plugin dotagents)
Este projeto usa a squad DotAgents. Antes da primeira ação desta sessão, leia por inteiro o protocolo
do Manager em \`$PLUGIN/commands/manager.md\` (também disponível como /dotagents:manager) e siga-o em
toda demanda. Personas em \`$PLUGIN/agents/\`, skills em \`$PLUGIN/skills/\`.
EOT
    ;;
esac
exit 0
