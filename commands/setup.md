---
description: Ativa a squad DotAgents no projeto atual pelo plugin — cria memories/, docs/todo|done|adr e o bloco gerido do CLAUDE.md. Rode uma vez por repositório.
---

Na raiz do projeto, rode e mostre a saída:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/setup-projeto.sh"
```

- **Terminou bem:** oriente a reiniciar a sessão do Claude Code — o protocolo do Manager entra pelo hook
  de início de sessão — e, depois, rodar `/dotagents:dot-agent-bootstrap` para preencher `memories/`.
- **Recusou por instalação antiga** (`install.sh`): explique a migração que o script imprimiu. Não apague
  nada por conta própria.
