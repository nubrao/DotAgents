---
description: Ativa a squad DotAgents pelo plugin num repositório ou numa pasta acima de vários repositórios — cria memories/, docs/todo|done|adr e o bloco gerido do CLAUDE.md.
---

## 1. Perguntar onde ativar

Descubra a raiz do git do diretório atual (`git rev-parse --show-toplevel`; fora de um repositório,
use o diretório atual) e a pasta acima dela. Pergunte com `AskUserQuestion`, mostrando os caminhos
absolutos nas opções:

- **Neste repositório** — `<raiz do git>`: memória e tasks só deste repositório.
- **Na pasta acima dos repositórios** — `<pasta acima>`: uma ativação vale para todos os repositórios
  dentro dela, com `memories/` e `docs/todo/` compartilhados.

Outro caminho entra pelo campo livre da pergunta. Se um repositório abaixo tiver ativação própria, a
dele vale para ele — a mais próxima vence.

## 2. Ativar

Rode e mostre a saída:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/setup-projeto.sh" "<pasta escolhida>"
```

- **Terminou bem:** oriente a reiniciar a sessão do Claude Code — o protocolo do Manager entra pelo hook
  de início de sessão — e, depois, rodar `/dotagents:dot-agent-bootstrap` para preencher `memories/`.
  Com a squad ativa, edição de código exige task ativa em `<pasta escolhida>/docs/todo/`.
- **Recusou por instalação antiga** (`install.sh`): explique a migração que o script imprimiu. Não apague
  nada por conta própria.
