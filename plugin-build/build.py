#!/usr/bin/env python3
"""Gera o plugin do Claude Code a partir dos arquivos do DotAgents, sem alterá-los.

Uso: python3 plugin-build/build.py <pasta-de-saida>
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
OVERLAY = RAIZ / "plugin-build" / "overlay"
PASTAS = ["agents", "commands", "skills", "hooks", "memories"]
ARQUIVOS = ["license.md", "README.md"]
TEXTO = {".md", ".sh", ".json", ".mdc", ".txt"}
PLACEHOLDER = re.compile(r"\{\{[A-Z_]+\}\}")

RENDER = {
    "{{AGENTS_ROOT}}": "${CLAUDE_PLUGIN_ROOT}",
    "{{DISPATCH_MODE}}": "subagentes",
    "{{RESET_CMD}}": "/clear",
}

BOOTSTRAP_ANCORA = "Nenhuma condição atendida →"
BOOTSTRAP_CONDICAO = (
    "- **Claude Code (plugin `dotagents`):** `CLAUDE.md` na raiz contém o bloco gerido com "
    "`modo: plugin`, e `memories/` existe. Personas, skills e comandos vêm do plugin "
    "(`${CLAUDE_PLUGIN_ROOT}`), não de `.claude/`; o protocolo do Manager é injetado pelo hook "
    "`SessionStart` do plugin. Confirme via `/hooks` que os hooks do plugin `dotagents` "
    "(SessionStart, PreToolUse e UserPromptSubmit) estão registrados.\n\n"
)

BLOCO_INICIO = (
    "<!-- dotagents:begin modo: plugin — bloco gerido pelo plugin dotagents; "
    "NÃO edite manualmente. Atualize com /dotagents:setup -->"
)


def falhar(msg):
    sys.exit(f"build: {msg}")


def preparar_saida(saida):
    if saida == RAIZ or RAIZ.is_relative_to(saida):
        falhar(f"a saída não pode ser o repositório nem uma pasta acima dele: {saida}")
    if saida.exists():
        manifesto = saida / ".claude-plugin" / "plugin.json"
        vazia = not any(saida.iterdir())
        if not vazia and not (manifesto.exists() and json.loads(manifesto.read_text()).get("name") == "dotagents"):
            falhar(f"{saida} existe e não é uma saída anterior deste build")
        for item in saida.iterdir():
            if item.name == ".git":
                continue
            shutil.rmtree(item) if item.is_dir() else item.unlink()
    saida.mkdir(parents=True, exist_ok=True)


def renderizar(caminho, rel):
    texto = caminho.read_text(encoding="utf-8")
    if rel.parts[0] == "memories":
        # memories/ é copiado para o projeto, onde a variável do plugin não expande
        texto = re.sub(r"\{\{AGENTS_ROOT\}\}/skills/([\w-]+)/SKILL\.md", r"dotagents:\1", texto)
    for de, para in RENDER.items():
        texto = texto.replace(de, para)
    caminho.write_text(texto, encoding="utf-8")


def remendar_bootstrap(saida):
    arq = saida / "commands" / "dot-agent-bootstrap.md"
    texto = arq.read_text(encoding="utf-8")
    if texto.count(BOOTSTRAP_ANCORA) != 1:
        falhar(f"âncora do bootstrap não encontrada uma única vez em {arq.name}: '{BOOTSTRAP_ANCORA}'")
    arq.write_text(texto.replace(BOOTSTRAP_ANCORA, BOOTSTRAP_CONDICAO + BOOTSTRAP_ANCORA), encoding="utf-8")


def bloco_claude_md():
    """Extrai do install.sh as linhas do bloco raiz e adapta ao modo plugin."""
    install = (RAIZ / "install.sh").read_text(encoding="utf-8")
    m = re.search(r"inject_root_block\(\) \{.*?\{\n(.*?)\n\s*\} > \"\$block\"", install, re.S)
    if not m:
        falhar("bloco raiz não encontrado no install.sh (inject_root_block)")
    linhas = [BLOCO_INICIO]
    for linha in m.group(1).splitlines():
        linha = linha.strip()
        if "dotagents:begin" in linha or linha.startswith("["):
            continue
        e = re.fullmatch(r'echo "(.*)"', linha)
        if not e:
            falhar(f"linha inesperada no bloco raiz do install.sh: {linha}")
        texto = e.group(1).replace("\\`", "`").replace('\\"', '"')
        texto = texto.replace(
            "`$AGENTS_ROOT/commands/manager.md`",
            "`/dotagents:manager`, carregado no início de cada sessão pelo plugin",
        )
        if "$" in texto:
            falhar(f"variável não tratada no bloco raiz: {texto}")
        linhas.append(texto)
    if linhas[-1] != "<!-- dotagents:end -->":
        falhar("o bloco raiz do install.sh não termina em dotagents:end")
    return "\n".join(linhas) + "\n"


def versao():
    install = (RAIZ / "install.sh").read_text(encoding="utf-8")
    m = re.search(r'^DOTAGENTS_VERSION="([0-9]+\.[0-9]+\.[0-9]+)"', install, re.M)
    if not m:
        falhar("DOTAGENTS_VERSION não encontrado no install.sh")
    git = lambda *a: subprocess.check_output(["git", "-C", str(RAIZ), *a], text=True).strip()
    data = git("log", "-1", "--format=%cd", "--date=format:%Y%m%d%H%M")
    sha = git("rev-parse", "--short=7", "HEAD")
    return f"{m.group(1)}-build.{data}.g{sha}"


def main():
    if len(sys.argv) != 2:
        falhar("uso: build.py <pasta-de-saida>")
    saida = Path(sys.argv[1]).resolve()
    preparar_saida(saida)

    for pasta in PASTAS:
        shutil.copytree(RAIZ / pasta, saida / pasta)
    for arq in ARQUIVOS:
        shutil.copy2(RAIZ / arq, saida / arq)

    for caminho in saida.rglob("*"):
        if caminho.is_file() and caminho.suffix in TEXTO:
            renderizar(caminho, caminho.relative_to(saida))

    remendar_bootstrap(saida)
    restos = [
        f"{p.relative_to(saida)}: {', '.join(sorted(set(PLACEHOLDER.findall(p.read_text(encoding='utf-8')))))}"
        for p in saida.rglob("*")
        if p.is_file() and p.suffix in TEXTO and PLACEHOLDER.search(p.read_text(encoding="utf-8"))
    ]
    if restos:
        falhar("placeholder sem tradução:\n  " + "\n  ".join(restos))

    colisoes = [str(f.relative_to(OVERLAY)) for f in OVERLAY.rglob("*")
                if f.is_file() and (saida / f.relative_to(OVERLAY)).exists()]
    if colisoes:
        falhar("o original passou a ter arquivo com o mesmo caminho do overlay: " + ", ".join(colisoes))
    shutil.copytree(OVERLAY, saida, dirs_exist_ok=True)
    (saida / "scripts" / "bloco-claude.md").write_text(bloco_claude_md(), encoding="utf-8")

    for script in list((saida / "hooks").glob("*.sh")) + list((saida / "scripts").glob("*.sh")):
        script.chmod(0o755)

    manifesto = saida / ".claude-plugin" / "plugin.json"
    manifesto.parent.mkdir(exist_ok=True)
    manifesto.write_text(json.dumps({
        "name": "dotagents",
        "version": versao(),
        "description": "Squad multi-agente DotAgents (PO, Architect, Tech Lead, Developer, QA, Security, Ops) "
                       "como plugin do Claude Code. Ative por projeto com /dotagents:setup.",
        "author": {"name": "Rodrigo Celebrone; adaptação para plugin: Bruno Camara"},
        "homepage": "https://github.com/nubrao/DotAgents",
        "license": "Licença DotAgents (ver license.md)",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"plugin gerado em {saida} (versão {json.loads(manifesto.read_text())['version']})")


if __name__ == "__main__":
    main()
