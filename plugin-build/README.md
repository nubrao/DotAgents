# Plugin do Claude Code gerado a partir do DotAgents

Este fork mantém os arquivos do DotAgents **sem edição**. O plugin é gerado por `build.py` e publicado
na branch `plugin`, que é a fonte do marketplace.

```
main (espelho do original + plugin-build/ + .github/)  ──build.py──▶  branch plugin
```

## O que o build faz

1. Copia `agents/`, `commands/`, `skills/`, `hooks/`, `memories/`, `license.md` e `README.md`.
2. Troca os placeholders do instalador: `{{AGENTS_ROOT}}` → `${CLAUDE_PLUGIN_ROOT}`, que o Claude Code
   expande em comando, skill e agente; `{{DISPATCH_MODE}}` → `subagentes`; `{{RESET_CMD}}` → `/clear`.
   Em `memories/`, que vai para o projeto, a referência a uma skill vira `dotagents:<skill>`.
3. Acrescenta à verificação de integridade do `dot-agent-bootstrap` a condição do modo plugin.
4. Sobrepõe `overlay/`: o `hooks.json`, o `dotagents-guard.sh`, o `/dotagents:setup` e o script dele.
5. Extrai o bloco raiz do `install.sh` para `scripts/bloco-claude.md`, adaptado ao modo plugin.
6. Escreve `.claude-plugin/plugin.json` com a versão do `install.sh` mais data e commit da `main`.

**O build falha, de propósito,** quando o original muda algo de que ele depende: placeholder novo,
âncora do bootstrap, formato do bloco raiz, ou arquivo com o mesmo caminho de um do `overlay/`. A falha
aparece na Action, antes de chegar ao plugin.

## Hooks

`/dotagents:setup` pergunta onde ativar a squad: no repositório ou numa pasta acima de vários
repositórios. `dotagents-guard.sh` procura o bloco `dotagents:begin` no `CLAUDE.md` do projeto e, se não
achar, nas pastas acima dele; a ativação mais próxima vence e a pasta dela é a raiz da squad, passada
ao gate e ao remind do original. Sem ativação, não faz nada; em projeto instalado pelo `install.sh`
também não, para não duplicar os hooks dele. No início da
sessão, manda ler o protocolo do Manager pelo caminho do plugin — o arquivo inteiro passa do limite de
saída de um hook.

## Atualização

A Action `sincronizar-e-gerar` roda a cada 6 horas, à mão, e a cada push em `plugin-build/`:

1. traz a `main` do original pela API `merge-upstream`;
2. gera o plugin;
3. se a saída mudou, abre PR na branch `plugin` e fecha o PR anterior dela.

Nada chega a quem instalou sem o merge desse PR. Se o sync falhar — conflito, ou mudança do original
em `.github/workflows/`, que o token da Action não pode escrever —, sincronizar pelo botão "Sync fork".

## Rodar localmente

```bash
python3 plugin-build/build.py /tmp/dotagents-plugin
claude plugin validate /tmp/dotagents-plugin
claude --plugin-dir /tmp/dotagents-plugin
```

Atribuição das modificações, exigida pela licença: `overlay/MODIFICACOES.md`.
