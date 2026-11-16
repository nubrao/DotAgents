#!/bin/sh
# Encaminha os hooks do DotAgents só onde a squad foi ativada pelo plugin (/dotagents:setup).
# A ativação vale para a pasta dela e tudo abaixo; a mais próxima do projeto vence.
# Uso: dotagents-guard.sh <gate|remind|session> [claude]
MODO="$1"
ALVO="${2:-claude}"
IN=$(cat 2>/dev/null) || IN=""
PROJETO="${CLAUDE_PROJECT_DIR:-$PWD}"
DIR=$(cd "$(dirname "$0")" && pwd)
PLUGIN="${CLAUDE_PLUGIN_ROOT:-$(dirname "$DIR")}"

# Projeto instalado pelo install.sh já registra os próprios hooks.
[ -f "$PROJETO/.claude/hooks/dotagents-gate.sh" ] && exit 0

RAIZ=""
d="$PROJETO"
while :; do
  if grep -qs 'dotagents:begin' "$d/CLAUDE.md"; then RAIZ="$d"; break; fi
  [ "$d" = "/" ] && break
  d=$(dirname "$d")
done
# Sem ativação no projeto nem acima dele: nada a fazer.
[ -z "$RAIZ" ] && exit 0

# Gate e remind do original procuram docs/todo/ na raiz recebida; caminhos relativos viram absolutos.
absoluto() { R="$RAIZ" perl -pe 's/(?<![\/\w])docs\/todo\//$ENV{R}\/docs\/todo\//g'; }

case "$MODO" in
  gate)
    printf '%s' "$IN" | CLAUDE_PROJECT_DIR="$RAIZ" "$DIR/dotagents-gate.sh" "$ALVO" | absoluto
    ;;
  remind)
    # o remind do original aponta para a instalação em .claude/; no plugin o protocolo fica no plugin
    printf '%s' "$IN" | CLAUDE_PROJECT_DIR="$RAIZ" "$DIR/dotagents-remind.sh" "$ALVO" \
      | R="$PLUGIN" perl -pe 's/\.claude\/commands\/manager\.md/$ENV{R}\/commands\/manager.md/g'
    ;;
  session)
    # o protocolo inteiro passa do limite de saída do hook; a sessão recebe a diretiva e os caminhos
    cat <<EOT
# Protocolo da squad DotAgents (plugin dotagents)
Este projeto usa a squad DotAgents. Antes da primeira ação desta sessão, leia por inteiro o protocolo
do Manager em \`$PLUGIN/commands/manager.md\` (também disponível como /dotagents:manager) e siga-o em
toda demanda. Personas em \`$PLUGIN/agents/\`, skills em \`$PLUGIN/skills/\`.
A raiz da squad é \`$RAIZ\`: todo caminho \`memories/\` e \`docs/\` do protocolo é relativo a ela.
EOT
    ;;
esac
exit 0
