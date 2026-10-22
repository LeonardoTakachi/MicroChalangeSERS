"""Interface web (Flask) do Sistema de Dimensionamento Energético Residencial.

Executar:  python app.py      (abre em http://127.0.0.1:5000)
Todos os cálculos vêm do micro_challenge.py e todos os equipamentos/preços
vêm dos CSVs em datasets/. Nada é calculado ou digitado fora do sistema.
"""
import os
import re

from flask import (Flask, Response, abort, flash, redirect, render_template,
                   request, session, url_for)

import micro_challenge as mc

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "troque-esta-chave-em-producao")
app.jinja_env.globals.update(num=mc.num, brl=mc.brl, resumo=mc.resumo_cenario_linhas,
                             orcamento=mc.orcamento_linhas)

DISPONIBILIDADES = {
    "auto": "Automático (pela fase do inversor)", "0": "Nenhum (0 kWh)",
    "30": "Monofásico (30 kWh)", "50": "Bifásico (50 kWh)", "100": "Trifásico (100 kWh)",
}


# ----------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------
def _numero(texto, nome):
    try:
        return float(str(texto).strip().replace(",", "."))
    except ValueError:
        raise mc.ErroValidacao(f"{nome}: informe um número válido.")


def _datasets():
    # Lê os CSVs a cada uso: atualizar equipamentos/preços não exige reiniciar.
    try:
        return mc.listar_datasets_pb19()
    except (FileNotFoundError, ValueError, KeyError) as erro:
        raise mc.ErroValidacao(f"Não foi possível carregar os datasets: {erro}")


def _solar_padrao(residencia):
    return {"hsp": str(mc.HSP_PADRAO), "fonte_hsp": mc.FONTE_HSP_PADRAO,
            "pr": str(mc.PR_PADRAO), "justificativa_pr": mc.PR_JUSTIFICATIVA_PADRAO,
            "tarifa": str(residencia["tarifa_kwh"]), "disp": "auto"}


def _validar_solar(s):
    disp = None if s.get("disp", "auto") == "auto" else float(s["disp"])
    return mc.validar_premissas({
        "hsp": _numero(s["hsp"], "Horas de Sol Pico (HSP)"),
        "fonte_hsp": s["fonte_hsp"],
        "pr": _numero(s["pr"], "Fator de desempenho (PR)"),
        "justificativa_pr": s["justificativa_pr"],
        "tarifa_kwh": _numero(s["tarifa"], "Tarifa de energia"),
        "disponibilidade_kwh": disp,
    })


def _preparar():
    """Reúne residência, demanda, premissas e P_FV. Retorna (ctx, destino, msg)."""
    nome = session.get("residencia")
    if not nome:
        return None, "residencia", "Selecione ou cadastre uma residência."
    try:
        residencia = mc.carregar_residencia(nome)
        demanda = mc.calcular_demanda(residencia)
    except mc.ErroValidacao as erro:
        session.pop("residencia", None)
        return None, "residencia", str(erro)
    if "solar" not in session:
        return None, "solar", "Informe o recurso solar (HSP e PR)."
    try:
        premissas = _validar_solar(session["solar"])
        p_fv = mc.calcular_potencia_fv_kw(demanda["e_dia_kwh"], premissas["hsp"], premissas["pr"])
    except mc.ErroValidacao as erro:
        return None, "solar", str(erro)
    return {"residencia": residencia, "demanda": demanda,
            "premissas": premissas, "p_fv": p_fv}, None, None


def _chave(opcao):
    return f"{opcao['modulo']['id_modulo']}|{opcao['inversor']['id_inversor']}"


def _escolher(ranking, chave):
    return next((o for o in ranking if _chave(o) == chave), ranking[0])


def _cenario_sem(ctx):
    ranking = mc.selecionar_equipamentos_fv(ctx["p_fv"], _datasets())
    escolhida = _escolher(ranking, session.get("sel_sem", ""))
    return ranking, escolhida, mc.calcular_cenario(ctx["demanda"], ctx["premissas"], escolhida)


def _cenario_com(ctx):
    bat = session.get("bat") or {}
    if not bat.get("usar"):
        return None, None
    autonomia = _numero(bat.get("autonomia", "12"), "Autonomia desejada")
    fracao = _numero(bat.get("fracao", "100"), "Parcela da carga atendida")
    bases = mc.selecionar_equipamentos_fv(ctx["p_fv"], _datasets(), exigir_bateria=True)
    base = _escolher(bases, bat.get("base", ""))
    opcoes = mc.listar_opcoes_bateria(base, ctx["demanda"]["e_dia_kwh"], autonomia, fracao)
    escolhida = next((o for o in opcoes if o["bateria"]["id_bateria"] == bat.get("bateria")),
                     opcoes[0])
    cenario = mc.calcular_cenario(ctx["demanda"], ctx["premissas"], base, escolhida)
    return cenario, {"bases": bases, "base": base, "opcoes": opcoes, "escolhida": escolhida}


def _proposta_atual(ctx):
    avisos = []
    _, _, sem = _cenario_sem(ctx)
    try:
        com, _ = _cenario_com(ctx)
    except mc.ErroValidacao as erro:
        com = None
        avisos.append(f"Cenário com baterias indisponível: {erro}")
    prop = mc.gerar_proposta(ctx["residencia"], ctx["premissas"], ctx["demanda"],
                             ctx["p_fv"], sem, com)
    return prop, avisos


def _exigir_contexto():
    ctx, destino, msg = _preparar()
    if ctx is None:
        flash(msg, "erro")
    return ctx, destino


def _resposta_html(prop):
    nome = f"proposta_{mc._slug(prop['residencia'])}.html"
    return Response(mc.gerar_proposta_html(prop), mimetype="text/html",
                    headers={"Content-Disposition": f'attachment; filename="{nome}"'})


# ----------------------------------------------------------------------
# 1. Residência (PB01 / PB02)
# ----------------------------------------------------------------------
def _linhas_do_form():
    f = request.form
    return list(zip(f.getlist("comodo"), f.getlist("equip"), f.getlist("qtd"), f.getlist("horas")))


@app.route("/", methods=["GET", "POST"])
def residencia():
    base = mc.obter_base_equipamentos()
    linhas = []
    if request.method == "POST":
        try:
            if request.form.get("acao") == "selecionar":
                mc.carregar_residencia(request.form.get("nome", ""))
                nome = request.form["nome"]
            else:
                linhas = _linhas_do_form()
                comodos = {}
                for comodo, equip, qtd, horas in linhas:
                    if not comodo.strip() and not horas.strip():
                        continue  # linha em branco
                    mc.validar_texto(comodo, "Nome do cômodo")
                    if equip not in base:
                        raise mc.ErroValidacao("Escolha um equipamento da lista.")
                    qtd_n, horas_n = _numero(qtd, "Quantidade"), _numero(horas, "Horas por dia")
                    mc.calcular_consumo_item(base[equip]["potencia"], qtd_n, horas_n)
                    comodos.setdefault(comodo.strip(), []).append({
                        "nome": base[equip]["nome"], "potencia": base[equip]["potencia"],
                        "qtd": int(qtd_n), "horas": horas_n})
                imovel = {"nome": request.form.get("nome_novo", ""),
                          "comodos": [{"nome": n, "equipamentos": e} for n, e in comodos.items()]}
                nome = mc.salvar_residencia(
                    imovel, _numero(request.form.get("tarifa", ""), "Tarifa de energia"))["nome"]
            session["residencia"] = nome
            for chave in ("solar", "sel_sem", "bat"):
                session.pop(chave, None)
            return redirect(url_for("solar"))
        except mc.ErroValidacao as erro:
            flash(str(erro), "erro")

    demanda, atual = None, session.get("residencia")
    if atual:
        try:
            demanda = mc.calcular_demanda(mc.carregar_residencia(atual))
        except mc.ErroValidacao:
            atual = None
    return render_template("residencia.html", nomes=mc.listar_residencias(), atual=atual,
                           demanda=demanda, base=base, linhas=linhas, etapa=1)


# ----------------------------------------------------------------------
# 2. Recurso solar (PB03 / PB04)
# ----------------------------------------------------------------------
@app.route("/solar", methods=["GET", "POST"])
def solar():
    nome = session.get("residencia")
    if not nome:
        flash("Selecione ou cadastre uma residência.", "erro")
        return redirect(url_for("residencia"))
    try:
        res = mc.carregar_residencia(nome)
        demanda = mc.calcular_demanda(res)
    except mc.ErroValidacao as erro:
        session.pop("residencia", None)
        flash(str(erro), "erro")
        return redirect(url_for("residencia"))

    if request.method == "POST":
        campos = ("hsp", "fonte_hsp", "pr", "justificativa_pr", "tarifa", "disp")
        session["solar"] = {c: request.form.get(c, "").strip() for c in campos}
        if session["solar"]["disp"] not in DISPONIBILIDADES:
            session["solar"]["disp"] = "auto"
        try:
            _validar_solar(session["solar"])
            return redirect(url_for("sistema"))
        except mc.ErroValidacao:
            return redirect(url_for("solar"))

    valores = session.get("solar") or _solar_padrao(res)
    p_fv, erro = None, None
    try:
        premissas = _validar_solar(valores)
        p_fv = mc.calcular_potencia_fv_kw(demanda["e_dia_kwh"], premissas["hsp"], premissas["pr"])
    except mc.ErroValidacao as e:
        erro = str(e) if "solar" in session else None
    return render_template("solar.html", demanda=demanda, v=valores, p_fv=p_fv, erro=erro,
                           disponibilidades=DISPONIBILIDADES, etapa=2)


# ----------------------------------------------------------------------
# 3. Sistema FV sem baterias (PB05 a PB09)
# ----------------------------------------------------------------------
@app.route("/sistema", methods=["GET", "POST"])
def sistema():
    if request.method == "POST":
        session["sel_sem"] = request.form.get("escolha", "")
        return redirect(url_for("sistema"))
    ctx, destino = _exigir_contexto()
    if ctx is None:
        return redirect(url_for(destino))
    ranking = escolhida = cenario = erro = None
    try:
        ranking, escolhida, cenario = _cenario_sem(ctx)
    except mc.ErroValidacao as e:
        erro = str(e)
    return render_template("sistema.html", ctx=ctx, ranking=ranking, escolhida=escolhida,
                           cenario=cenario, erro=erro, chave=_chave, etapa=3)


# ----------------------------------------------------------------------
# 4. Baterias (PB10 a PB12)
# ----------------------------------------------------------------------
@app.route("/baterias", methods=["GET", "POST"])
def baterias():
    if request.method == "POST":
        f = request.form
        session["bat"] = {"usar": "usar" in f, "autonomia": f.get("autonomia", "12").strip(),
                          "fracao": f.get("fracao", "100").strip(),
                          "base": f.get("base", ""), "bateria": f.get("bateria", "")}
        return redirect(url_for("baterias"))
    ctx, destino = _exigir_contexto()
    if ctx is None:
        return redirect(url_for(destino))
    bat = session.get("bat") or {"usar": True, "autonomia": "12", "fracao": "100"}
    if "bat" not in session:
        session["bat"] = bat
    cenario = detalhes = erro = None
    try:
        cenario, detalhes = _cenario_com(ctx)
    except mc.ErroValidacao as e:
        erro = str(e)
    return render_template("baterias.html", ctx=ctx, bat=bat, cenario=cenario,
                           detalhes=detalhes, erro=erro, chave=_chave, etapa=4)


# ----------------------------------------------------------------------
# 5. Proposta (PB13 a PB17, PB20, PB21)
# ----------------------------------------------------------------------
@app.route("/proposta", methods=["GET", "POST"])
def proposta():
    ctx, destino = _exigir_contexto()
    if ctx is None:
        return redirect(url_for(destino))
    try:
        prop, avisos = _proposta_atual(ctx)
    except mc.ErroValidacao as erro:
        flash(str(erro), "erro")
        return redirect(url_for("sistema"))
    if request.method == "POST":
        try:
            flash(f"Projeto salvo: {mc.salvar_projeto(prop)}", "ok")
        except OSError as erro:
            flash(f"Não foi possível salvar: {erro}", "erro")
        return redirect(url_for("proposta"))
    for aviso in avisos:
        flash(aviso, "aviso")
    return render_template("proposta.html", prop=prop, atual=True, etapa=5)


@app.route("/proposta/baixar")
def baixar_proposta():
    ctx, destino = _exigir_contexto()
    if ctx is None:
        return redirect(url_for(destino))
    try:
        return _resposta_html(_proposta_atual(ctx)[0])
    except mc.ErroValidacao as erro:
        flash(str(erro), "erro")
        return redirect(url_for("sistema"))


# ----------------------------------------------------------------------
# Projetos salvos (PB20)
# ----------------------------------------------------------------------
def _projeto_ou_404(nome):
    if not re.fullmatch(r"[a-z0-9_]+", nome):
        abort(404)
    try:
        return mc.carregar_projeto(nome)
    except mc.ErroValidacao:
        abort(404)


@app.route("/projetos")
def projetos():
    return render_template("projetos.html", projetos=mc.listar_projetos(), etapa=6)


@app.route("/projetos/<nome>")
def ver_projeto(nome):
    return render_template("proposta.html", prop=_projeto_ou_404(nome), atual=False,
                           nome_projeto=nome, etapa=6)


@app.route("/projetos/<nome>/baixar")
def baixar_projeto(nome):
    return _resposta_html(_projeto_ou_404(nome))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
