# Modificações sobre o DotAgents

DotAgents — Copyright (c) 2026 Rodrigo Celebrone. Licença em [`license.md`](license.md), mantida na
íntegra.

Esta é uma redistribuição modificada, feita a partir do fork `nubrao/DotAgents`, que empacota o
framework como plugin do Claude Code.

**Autor das modificações:** Bruno Camara
**Data:** 2026-11-16

## O que foi modificado

Os arquivos do framework não são editados no fork. O plugin é gerado por `plugin-build/build.py`, que
copia os arquivos e aplica as mudanças abaixo na saída:

- **Placeholders do instalador** — `{{AGENTS_ROOT}}` vira `${CLAUDE_PLUGIN_ROOT}`, que o Claude Code
  expande para a pasta do plugin; `{{DISPATCH_MODE}}` vira `subagentes`; `{{RESET_CMD}}` vira `/clear`.
  Em `memories/`, que é copiado para o projeto, a referência a uma skill vira o nome dela no plugin
  (`dotagents:<skill>`).
- **`commands/dot-agent-bootstrap.md`** — a verificação de integridade ganha a condição do modo plugin.
- **Hooks** — registrados pelo `hooks/hooks.json` do plugin, através de `hooks/dotagents-guard.sh`, que só
  os ativa em projeto preparado com `/dotagents:setup` e não duplica os de uma instalação feita pelo
  `install.sh`. No lugar do import `@.claude/commands/manager.md` do `CLAUDE.md`, o hook
  `SessionStart` manda ler o protocolo do Manager pelo caminho do plugin — o arquivo inteiro passa do
  limite de saída de um hook. O lembrete do `remind` aponta para o mesmo caminho.
- **Arquivos novos** — `commands/setup.md` (`/dotagents:setup`), `scripts/setup-projeto.sh`,
  `scripts/bloco-claude.md` (extraído do bloco raiz do `install.sh`, adaptado ao modo plugin) e este
  arquivo.
