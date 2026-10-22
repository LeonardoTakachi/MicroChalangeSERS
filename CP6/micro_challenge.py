from datetime import datetime
import csv
import os
import math
import json
import re
import unicodedata
from html import escape

def obter_base_equipamentos():
    # Base de dados exigida pelo enunciado
    return {
        "1": {"nome": "Geladeira", "categoria": "Cozinha", "potencia": 250},
        "2": {"nome": "Chuveiro Elétrico", "categoria": "Banho", "potencia": 5500},
        "3": {"nome": "Ar Condicionado", "categoria": "Climatização", "potencia": 1200},
        "4": {"nome": "Televisão", "categoria": "Entretenimento", "potencia": 100},
        "5": {"nome": "Lâmpada LED", "categoria": "Iluminação", "potencia": 10},
        "6": {"nome": "Micro-ondas", "categoria": "Cozinha", "potencia": 1200},
        "7": {"nome": "Notebook", "categoria": "Escritório", "potencia": 65}
    }


# PB19 - T01: estrutura e campos dos três datasets
# (módulos, inversores e baterias). Os dados dos produtos entram em T02/T03.
PASTA_DATASETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datasets")


def _campo(nome, tipo, obrigatorio=True, valores=None):
    # tipos: texto, inteiro, numero, booleano (0/1), enum, data (AAAA-MM-DD), url
    return {
        "nome": nome,
        "tipo": tipo,
        "obrigatorio": obrigatorio,
        "valores": valores
    }


def _campos_comerciais():
    # Campos comuns aos três datasets: certificação, preço e fontes rastreáveis
    return [
        _campo("selo_inmetro", "booleano"),
        _campo("preco_brl", "numero"),
        _campo("data_preco", "data"),
        _campo("fonte_preco", "url"),
        _campo("fonte_especificacao", "url")
    ]


def obter_estrutura_datasets():
    modulos = [
        _campo("id_modulo", "texto"),
        _campo("fabricante", "texto"),
        _campo("modelo", "texto"),
        _campo("tecnologia_celula", "enum", valores=[
            "monocristalino_perc", "monocristalino_topcon",
            "monocristalino_hjt", "policristalino", "outro"
        ]),
        _campo("num_celulas", "inteiro"),
        _campo("potencia_pico_wp", "numero"),
        _campo("eficiencia_modulo_pct", "numero"),
        _campo("vmp_v", "numero"),
        _campo("imp_a", "numero"),
        _campo("voc_v", "numero"),
        _campo("isc_a", "numero"),
        _campo("coef_temp_pmax_pct_c", "numero"),
        _campo("coef_temp_voc_pct_c", "numero"),
        _campo("coef_temp_isc_pct_c", "numero", obrigatorio=False),
        _campo("comprimento_mm", "numero"),
        _campo("largura_mm", "numero"),
        _campo("espessura_mm", "numero"),
        _campo("peso_kg", "numero"),
        _campo("garantia_produto_anos", "inteiro"),
        _campo("garantia_desempenho_anos", "inteiro")
    ] + _campos_comerciais() + [
        _campo("observacoes", "texto", obrigatorio=False)
    ]

    inversores = [
        _campo("id_inversor", "texto"),
        _campo("fabricante", "texto"),
        _campo("modelo", "texto"),
        _campo("tipo", "enum", valores=["string", "micro", "hibrido"]),
        _campo("fase", "enum", valores=["monofasico", "bifasico", "trifasico"]),
        _campo("tensao_saida_v", "numero"),
        _campo("potencia_nominal_ca_w", "numero"),
        _campo("potencia_max_ca_w", "numero"),
        _campo("potencia_max_fv_wp", "numero"),
        _campo("tensao_cc_max_v", "numero"),
        _campo("tensao_mppt_min_v", "numero"),
        _campo("tensao_mppt_max_v", "numero"),
        _campo("tensao_partida_v", "numero", obrigatorio=False),
        _campo("num_mppt", "inteiro"),
        _campo("strings_por_mppt", "inteiro"),
        _campo("corrente_max_mppt_a", "numero"),
        _campo("corrente_curto_max_mppt_a", "numero"),
        _campo("eficiencia_max_pct", "numero"),
        _campo("aceita_bateria", "booleano"),
        # Campos de bateria ficam vazios quando aceita_bateria = 0
        _campo("bateria_tensao_min_v", "numero", obrigatorio=False),
        _campo("bateria_tensao_max_v", "numero", obrigatorio=False),
        _campo("bateria_corrente_max_carga_a", "numero", obrigatorio=False),
        _campo("bateria_corrente_max_descarga_a", "numero", obrigatorio=False),
        _campo("bateria_comunicacao", "enum", obrigatorio=False,
               valores=["can", "rs485", "outro"]),
        _campo("peso_kg", "numero", obrigatorio=False),
        _campo("garantia_anos", "inteiro")
    ] + _campos_comerciais() + [
        _campo("observacoes", "texto", obrigatorio=False)
    ]

    baterias = [
        _campo("id_bateria", "texto"),
        _campo("fabricante", "texto"),
        _campo("modelo", "texto"),
        _campo("quimica", "enum", valores=[
            "lifepo4", "litio_nmc", "chumbo_acido", "outro"
        ]),
        _campo("acoplamento", "enum", valores=["cc", "ca"]),
        _campo("tensao_nominal_v", "numero"),
        _campo("tensao_min_v", "numero"),
        _campo("tensao_max_v", "numero"),
        _campo("capacidade_nominal_kwh", "numero"),
        _campo("capacidade_util_kwh", "numero"),
        _campo("profundidade_descarga_pct", "numero"),
        _campo("potencia_continua_w", "numero"),
        _campo("potencia_pico_w", "numero"),
        _campo("corrente_max_carga_a", "numero"),
        _campo("corrente_max_descarga_a", "numero"),
        _campo("eficiencia_ciclo_pct", "numero"),
        _campo("ciclos_vida", "inteiro"),
        _campo("comunicacao", "enum", valores=["can", "rs485", "outro"]),
        _campo("modular", "booleano"),
        _campo("modulos_max_paralelo", "inteiro"),
        _campo("peso_kg", "numero", obrigatorio=False),
        _campo("garantia_anos", "inteiro")
    ] + _campos_comerciais() + [
        _campo("inversores_compativeis", "texto"),
        _campo("observacoes", "texto", obrigatorio=False)
    ]

    return {
        "modulos": {"arquivo": "modulos.csv", "campos": modulos},
        "inversores": {"arquivo": "inversores.csv", "campos": inversores},
        "baterias": {"arquivo": "baterias.csv", "campos": baterias}
    }


def _converter_valor(campo, texto, numero_linha):
    nome = campo["nome"]
    texto = texto.strip()

    if texto == "":
        if campo["obrigatorio"]:
            raise ValueError(
                f"Linha {numero_linha}: o campo '{nome}' é obrigatório."
            )
        return None

    try:
        if campo["tipo"] == "inteiro":
            return int(texto)

        if campo["tipo"] == "numero":
            return float(texto)

        if campo["tipo"] == "booleano":
            if texto not in ("0", "1"):
                raise ValueError
            return int(texto)

        if campo["tipo"] == "data":
            datetime.strptime(texto, "%Y-%m-%d")
            return texto

        if campo["tipo"] == "url":
            if not texto.lower().startswith(("http://", "https://")):
                raise ValueError
            return texto

        if campo["tipo"] == "enum":
            if texto not in campo["valores"]:
                raise ValueError
            return texto

    except ValueError:
        raise ValueError(
            f"Linha {numero_linha}: valor inválido '{texto}' "
            f"para o campo '{nome}' (tipo {campo['tipo']})."
        )

    return texto


# Lê um dataset conferindo se as colunas seguem a estrutura definida
def carregar_dataset(nome, pasta=PASTA_DATASETS):
    estrutura = obter_estrutura_datasets()

    if nome not in estrutura:
        raise ValueError(f"Dataset desconhecido: '{nome}'.")

    campos = estrutura[nome]["campos"]
    esperado = [c["nome"] for c in campos]
    caminho = os.path.join(pasta, estrutura[nome]["arquivo"])

    with open(caminho, newline="", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)

        if leitor.fieldnames != esperado:
            raise ValueError(
                f"As colunas de '{estrutura[nome]['arquivo']}' "
                "não seguem a estrutura definida."
            )

        registros = []
        for numero_linha, linha in enumerate(leitor, start=2):
            registros.append({
                c["nome"]: _converter_valor(c, linha[c["nome"]] or "", numero_linha)
                for c in campos
            })

    return registros



# PB19 - T02 a T08: catálogo de equipamentos fotovoltaicos
def listar_datasets_pb19():
    # PB19 - T06: carrega os três datasets integrados ao sistema.
    return {
        "modulos": carregar_dataset("modulos"),
        "inversores": carregar_dataset("inversores"),
        "baterias": carregar_dataset("baterias"),
    }


def validar_quantidade_datasets(datasets):
    # PB19 - T03: confere a quantidade mínima exigida.
    minimo = {"modulos": 10, "inversores": 8, "baterias": 6}
    erros = []
    for nome, minimo_exigido in minimo.items():
        qtd = len(datasets.get(nome, []))
        if qtd < minimo_exigido:
            erros.append(f"{nome}: {qtd} encontrados; mínimo = {minimo_exigido}.")
    return erros


def validar_registros_pb19(datasets):
    # PB19 - T04/T05: valida tipos, unidades, preços e rastreabilidade.
    erros = []
    avisos = []
    ids_campos = {"modulos": "id_modulo", "inversores": "id_inversor", "baterias": "id_bateria"}

    for nome, registros in datasets.items():
        ids = set()
        for numero, item in enumerate(registros, start=1):
            id_campo = ids_campos[nome]
            ident = item[id_campo]
            if ident in ids:
                erros.append(f"{nome}, registro {numero}: ID duplicado '{ident}'.")
            ids.add(ident)

            if item["preco_brl"] <= 0:
                erros.append(f"{nome}, {ident}: preço deve ser maior que zero.")
            if item["data_preco"] > datetime.now().strftime("%Y-%m-%d"):
                erros.append(f"{nome}, {ident}: data_preco está no futuro.")
            if not item["fonte_preco"] or not item["fonte_especificacao"]:
                erros.append(f"{nome}, {ident}: fontes são obrigatórias.")

            if nome == "modulos":
                if item["potencia_pico_wp"] <= 0 or item["voc_v"] <= 0 or item["vmp_v"] <= 0:
                    erros.append(f"{nome}, {ident}: potência/tensões inválidas.")
            elif nome == "inversores":
                if item["potencia_nominal_ca_w"] <= 0:
                    erros.append(f"{nome}, {ident}: potência nominal inválida.")
                if item["tensao_mppt_max_v"] > item["tensao_cc_max_v"]:
                    erros.append(f"{nome}, {ident}: MPPT máximo supera Vcc máximo.")
            else:
                if item["capacidade_nominal_kwh"] <= 0:
                    erros.append(f"{nome}, {ident}: capacidade inválida.")
                if item["capacidade_util_kwh"] > item["capacidade_nominal_kwh"]:
                    erros.append(f"{nome}, {ident}: capacidade útil supera nominal.")

            # A validação automática comprova rastreabilidade mínima.
            # A confirmação de que o modelo realmente existe deve ser feita
            # conferindo o datasheet/fonte indicada (T05).
            avisos.append(f"{nome}, {ident}: conferir manualmente fabricante/modelo na fonte.")
    return erros, avisos


def validar_pb19():
    # Executa T03-T05 e informa se os datasets podem ser usados pelo sistema.
    try:
        datasets = listar_datasets_pb19()
    except (FileNotFoundError, ValueError, KeyError) as erro:
        print(f"\nErro ao carregar datasets: {erro}")
        return False

    erros = validar_quantidade_datasets(datasets)
    erros_registros, avisos = validar_registros_pb19(datasets)
    erros.extend(erros_registros)

    print("\n" + "=" * 85)
    print("VALIDAÇÃO DOS DATASETS")
    print("=" * 85)
    for nome, registros in datasets.items():
        print(f"{nome.capitalize():<12}: {len(registros)} registros")

    if erros:
        print("\nERROS:")
        for erro in erros:
            print(f"- {erro}")
        print("=" * 85)
        return False

    print("\nEstrutura, quantidade, tipos, unidades e fontes obrigatórias: OK.")
    print("\nCONFERÊNCIA MANUAL NECESSÁRIA:")
    print("O código verifica rastreabilidade e consistência, mas a existência")
    print("do produto deve ser confirmada na fonte/datasheet registrado no CSV.")
    print("=" * 85)
    return True


def dimensionar_sistema_pb19(consumo_mensal_kwh, horas_sol_pico=4.5, pr=0.75):
    # PB19 - T07: pré-dimensionamento e verificação de compatibilidade
    if consumo_mensal_kwh <= 0 or horas_sol_pico <= 0:
        raise ValueError("Consumo e horas de sol pico devem ser maiores que zero.")
    if not 0 < pr <= 1:
        raise ValueError("O PR deve estar entre 0 e 1.")

    datasets = listar_datasets_pb19()
    energia_diaria = consumo_mensal_kwh / 30
    potencia_necessaria_w = (energia_diaria / (horas_sol_pico * pr)) * 1000  # P_FV = E_dia/(HSP x PR)
    candidatos = []

    for modulo in datasets["modulos"]:
        qtd = math.ceil(potencia_necessaria_w / modulo["potencia_pico_wp"])
        potencia_fv = qtd * modulo["potencia_pico_wp"]

        for inversor in datasets["inversores"]:
            if potencia_fv > inversor["potencia_max_fv_wp"]:
                continue
            max_serie = math.floor(inversor["tensao_cc_max_v"] / modulo["voc_v"])
            min_serie = max(1, math.ceil(inversor["tensao_mppt_min_v"] / modulo["vmp_v"]))
            if min_serie > max_serie:
                continue
            if modulo["isc_a"] > inversor["corrente_curto_max_mppt_a"]:
                continue

            candidatos.append({
                "modulo": modulo,
                "inversor": inversor,
                "qtd_modulos": qtd,
                "potencia_fv_wp": potencia_fv,
                "modulos_serie_min": min_serie,
                "modulos_serie_max": max_serie,
                "baterias_compativeis": [],
            })

    candidatos.sort(key=lambda x: (x["potencia_fv_wp"] - potencia_necessaria_w, x["qtd_modulos"]))

    for opcao in candidatos[:5]:
        inversor = opcao["inversor"]
        if not inversor["aceita_bateria"]:
            continue
        tokens = [t.strip().lower() for t in inversor["modelo"].split(";")]
        tokens += [inversor["fabricante"].lower()]
        for bateria in datasets["baterias"]:
            compat = bateria["inversores_compativeis"].lower()
            if any(t and t in compat for t in tokens):
                opcao["baterias_compativeis"].append(bateria)

    return {
        "energia_diaria_kwh": energia_diaria,
        "potencia_fv_necessaria_kw": potencia_necessaria_w / 1000,
        "opcoes": candidatos[:5],
    }


def calcular_orcamento_pb19(opcao, quantidade_baterias=0):
    # PB19 - T08: calcula o orçamento dos equipamentos selecionados.
    if quantidade_baterias < 0:
        raise ValueError("Quantidade de baterias não pode ser negativa.")
    modulo = opcao["modulo"]
    inversor = opcao["inversor"]
    bateria = None
    if quantidade_baterias:
        if not opcao["baterias_compativeis"]:
            raise ValueError("Não há bateria compatível cadastrada para este inversor.")
        bateria = opcao["baterias_compativeis"][0]

    subtotal_modulos = opcao["qtd_modulos"] * modulo["preco_brl"]
    subtotal_inversor = inversor["preco_brl"]
    subtotal_bateria = quantidade_baterias * bateria["preco_brl"] if bateria else 0
    total = subtotal_modulos + subtotal_inversor + subtotal_bateria

    return {
        "modulos": {"modelo": modulo["modelo"], "quantidade": opcao["qtd_modulos"], "subtotal": subtotal_modulos},
        "inversor": {"modelo": inversor["modelo"], "quantidade": 1, "subtotal": subtotal_inversor},
        "bateria": {"modelo": bateria["modelo"] if bateria else None, "quantidade": quantidade_baterias, "subtotal": subtotal_bateria},
        "total": total,
    }


def exibir_catalogo_pb19():
    # PB19 - T06: exibe os produtos vindos dos CSVs.
    datasets = listar_datasets_pb19()
    print("\n" + "=" * 85)
    print("CATÁLOGO DE EQUIPAMENTOS")
    print("=" * 85)
    ids = {"modulos": "id_modulo", "inversores": "id_inversor", "baterias": "id_bateria"}
    for nome, registros in datasets.items():
        print(f"\n{nome.upper()} ({len(registros)} registros)")
        for item in registros:
            print(f"- {item[ids[nome]]} | {item['fabricante']} {item['modelo']} | R$ {item['preco_brl']:.2f}")


def executar_pb19():
    # Menu do PB19 sem alterar o fluxo residencial existente.
    while True:
        print("\n=== EQUIPAMENTOS FOTOVOLTAICOS ===")
        print("1 - Validar datasets (T03-T05)")
        print("2 - Exibir catálogo (T06)")
        print("3 - Dimensionar e verificar compatibilidade (T07)")
        print("4 - Dimensionar + orçamento (T07-T08)")
        print("0 - Voltar")
        opcao = input("Escolha: ").strip()

        if opcao == "1":
            validar_pb19()
        elif opcao == "2":
            try:
                exibir_catalogo_pb19()
            except (FileNotFoundError, ValueError) as erro:
                print(f"Erro: {erro}")
        elif opcao in ("3", "4"):
            try:
                consumo = float(input("Consumo mensal (kWh): ").replace(",", "."))
                resultado = dimensionar_sistema_pb19(consumo)
                print(f"\nPotência FV estimada: {resultado['potencia_fv_necessaria_kw']:.2f} kWp")
                if not resultado["opcoes"]:
                    print("Nenhuma combinação compatível foi encontrada.")
                    continue
                for i, item in enumerate(resultado["opcoes"], 1):
                    print(f"\n[{i}] {item['modulo']['modelo']} + {item['inversor']['modelo']}")
                    print(f"    Módulos: {item['qtd_modulos']}")
                    print(f"    Série possível: {item['modulos_serie_min']} a {item['modulos_serie_max']} módulos")
                    print(f"    Baterias compatíveis: {len(item['baterias_compativeis'])}")
                    if opcao == "4":
                        orc = calcular_orcamento_pb19(item)
                        print(f"    Orçamento sem bateria: R$ {orc['total']:.2f}")
            except (ValueError, FileNotFoundError) as erro:
                print(f"Erro: {erro}")
        elif opcao == "0":
            return
        else:
            print("Opção inválida.")

def exibir_menu(base_dados):
    print("\n--- EQUIPAMENTOS DISPONÍVEIS ---")

    for chave, info in base_dados.items():
        print(f"[{chave}] {info['nome']} ({info['potencia']}W)")


# PB09 - T01 e T02
def obter_valor_kwh():
    while True:
        try:
            valor = float(
                input("\nDigite o valor do kWh da sua conta de luz (R$): ")
                .replace(",", ".")
            )

            if valor <= 0:
                print("Erro: o valor do kWh deve ser maior que zero.")
            else:
                return valor

        except ValueError:
            print("Erro: digite um valor monetário válido.")


# PB11 - T01 a T05
def remover_equipamento(imovel, relatorio_itens):
    # PB11 - T01: listar os equipamentos cadastrados na residência
    print("\n--- EQUIPAMENTOS CADASTRADOS ---")

    for numero, item in enumerate(relatorio_itens, start=1):
        print(
            f"[{numero}] {item['comodo']} - {item['nome']} "
            f"(qtd: {item['qtd']}, {item['consumo']:.2f} kWh/mês)"
        )

    # PB11 - T02: selecionar o equipamento que será removido
    while True:
        try:
            escolha = int(
                input(
                    "Digite o número do equipamento a remover "
                    "(0 para cancelar): "
                )
            )

            if escolha == 0:
                print("Remoção cancelada.")
                return False

            if 1 <= escolha <= len(relatorio_itens):
                break

            print(
                "Opção inválida! Digite um número entre "
                f"1 e {len(relatorio_itens)}."
            )

        except ValueError:
            print("Valor inválido! Digite um número inteiro.")

    item = relatorio_itens[escolha - 1]

    # PB11 - T03: solicitar confirmação da remoção
    confirmacao = input(
        f"Confirma a remoção de '{item['nome']}' "
        f"do(a) {item['comodo']}? (s/n): "
    ).strip().lower()

    if confirmacao != "s":
        print("Remoção cancelada.")
        return False

    # PB11 - T04: remover o equipamento selecionado
    del relatorio_itens[escolha - 1]

    # PB11 - T05: atualizar os dados armazenados (equipamentos do cômodo)
    for comodo in imovel["comodos"]:
        comodo["equipamentos"] = [
            e for e in comodo["equipamentos"] if e is not item
        ]

    print(f"'{item['nome']}' removido com sucesso.")
    return True


# PB14 - T03: comparar o consumo mensal de dois equipamentos
def consome_mais(equip_a, equip_b):
    return equip_a["consumo"] > equip_b["consumo"]


# PB14 - T04: ordenar os equipamentos do maior para o menor consumo
# (insertion sort, usando a comparação do T03)
def ordenar_por_consumo(equipamentos):
    ordenados = equipamentos.copy()

    for i in range(1, len(ordenados)):
        atual = ordenados[i]
        j = i - 1

        while j >= 0 and consome_mais(atual, ordenados[j]):
            ordenados[j + 1] = ordenados[j]
            j -= 1

        ordenados[j + 1] = atual

    return ordenados


# PB14 - T01 a T05 e T07
def exibir_ranking_consumo(imovel, qtd_destaque=3):
    # PB14 - T01: recuperar os equipamentos e seus consumos mensais
    # PB14 - T02: associar cada equipamento ao seu respectivo cômodo
    equipamentos = []

    for comodo in imovel["comodos"]:
        for equip in comodo["equipamentos"]:
            equipamentos.append({
                "comodo": comodo["nome"],
                "nome": equip["nome"],
                "consumo": equip["consumo"]
            })

    print("\n" + "=" * 85)
    print("RANKING DE CONSUMO DOS EQUIPAMENTOS (maior -> menor)")
    print("=" * 85)

    if not equipamentos:
        print("Nenhum equipamento cadastrado.")
        print("=" * 85)
        return

    # PB14 - T03 e T04: comparar e ordenar pelo consumo
    ranking = ordenar_por_consumo(equipamentos)

    # PB14 - T05: identificar os equipamentos com maior consumo
    qtd_destaque = min(qtd_destaque, len(ranking))
    maiores = ranking[:qtd_destaque]

    consumo_total = sum(e["consumo"] for e in ranking)

    print(
        f"{'':<3} {'Pos':>4} | "
        f"{'Cômodo':<15} | "
        f"{'Equipamento':<18} | "
        f"{'Consumo Mensal':<18} | "
        f"{'% do total'}"
    )
    print("-" * 85)

    for posicao, equip in enumerate(ranking, start=1):
        percentual = (
            equip["consumo"] / consumo_total * 100
            if consumo_total > 0 else 0
        )

        # PB14 - T07: destacar os equipamentos de maior consumo
        marcador = ">>>" if posicao <= qtd_destaque else ""

        print(
            f"{marcador:<3} {posicao:>3}º | "
            f"{equip['comodo']:<15} | "
            f"{equip['nome']:<18} | "
            f"{equip['consumo']:>10.2f} kWh/mês | "
            f"{percentual:>6.1f}%"
        )

    print("-" * 85)

    # PB14 - T07: resumo dos maiores consumidores
    consumo_maiores = sum(e["consumo"] for e in maiores)
    percentual_maiores = (
        consumo_maiores / consumo_total * 100
        if consumo_total > 0 else 0
    )

    print(f">>> MAIORES CONSUMIDORES (top {qtd_destaque}):")
    for equip in maiores:
        print(
            f"    - {equip['nome']} ({equip['comodo']}): "
            f"{equip['consumo']:.2f} kWh/mês"
        )
    print(
        f"    Juntos representam {percentual_maiores:.1f}% "
        f"do consumo total da residência."
    )
    print("=" * 85)


# PB18 - T04: regra para destacar os maiores consumidores
# Um equipamento é considerado "grande consumidor" quando representa
# pelo menos 20% do consumo total da residência. Se nenhum atingir
# esse limite, o equipamento de maior consumo é destacado.
PERCENTUAL_MINIMO_DESTAQUE = 20

# Percentual de redução do tempo de uso usado na simulação de economia
REDUCAO_SIMULADA = 20


# PB18 - T05: estrutura para a apresentação das recomendações
RECOMENDACOES = {
    "Geladeira": "Evite abrir a porta com frequência e verifique a borracha de vedação.",
    "Chuveiro Elétrico": "Reduza o tempo de banho e use a posição 'verão' em dias quentes.",
    "Ar Condicionado": "Mantenha portas e janelas fechadas e regule a temperatura em 23 °C.",
    "Televisão": "Desligue da tomada em vez de deixar em stand-by.",
    "Lâmpada LED": "Aproveite a luz natural e apague as luzes de cômodos vazios.",
    "Micro-ondas": "Planeje o uso para aquecer mais itens de uma vez.",
    "Notebook": "Ative o modo de economia de energia e desligue quando não estiver em uso."
}

RECOMENDACAO_PADRAO = "Reduza o tempo de uso diário sempre que possível."


# PB18 - T01 a T07
def exibir_recomendacoes_economia(relatorio_itens, valor_kwh):
    print("\n" + "=" * 85)
    print("RECOMENDAÇÕES DE ECONOMIA")
    print("=" * 85)

    if not relatorio_itens:
        print("Nenhum equipamento cadastrado.")
        print("=" * 85)
        return

    # PB18 - T01: recuperar os consumos mensais calculados
    # (cópia dos dados, sem alterar os itens originais - T07)
    equipamentos = []
    for item in relatorio_itens:
        equipamentos.append({
            "comodo": item["comodo"],
            "nome": item["nome"],
            "consumo": item["consumo"]
        })

    consumo_total = sum(e["consumo"] for e in equipamentos)

    # PB18 - T02: comparar o consumo dos equipamentos cadastrados
    # (reaproveita a comparação e a ordenação do PB14)
    ordenados = ordenar_por_consumo(equipamentos)

    # PB18 - T03: identificar os que mais contribuem para o consumo total
    # PB18 - T04: aplicar a regra de destaque
    oportunidades = []
    for equip in ordenados:
        percentual = (
            equip["consumo"] / consumo_total * 100
            if consumo_total > 0 else 0
        )

        if percentual >= PERCENTUAL_MINIMO_DESTAQUE:
            oportunidades.append((equip, percentual))

    if not oportunidades:
        maior = ordenados[0]
        percentual = (
            maior["consumo"] / consumo_total * 100
            if consumo_total > 0 else 0
        )
        oportunidades.append((maior, percentual))

    print(
        f"Critério: equipamentos com {PERCENTUAL_MINIMO_DESTAQUE}% ou mais "
        f"do consumo total da residência."
    )
    print("-" * 85)

    # PB18 - T06: exibir os equipamentos identificados como oportunidades
    for numero, (equip, percentual) in enumerate(oportunidades, start=1):
        # Simulação: economia ao reduzir o tempo de uso em 20%.
        # Calculada em variáveis separadas, sem mudar o consumo (T07).
        economia_kwh = equip["consumo"] * REDUCAO_SIMULADA / 100
        economia_reais = economia_kwh * valor_kwh

        dica = RECOMENDACOES.get(equip["nome"], RECOMENDACAO_PADRAO)

        print(f"{numero}. {equip['nome']} ({equip['comodo']})")
        print(
            f"   Consumo atual: {equip['consumo']:.2f} kWh/mês "
            f"({percentual:.1f}% do total)"
        )
        print(f"   Recomendação: {dica}")
        print(
            f"   Reduzindo {REDUCAO_SIMULADA}% do tempo de uso, economia estimada de "
            f"{economia_kwh:.2f} kWh/mês (R$ {economia_reais:.2f})"
        )
        print()

    # PB18 - T07: deixar claro que os valores calculados não foram alterados
    print(
        "* As recomendações são apenas sugestões. "
        "Os valores de consumo calculados não foram alterados."
    )
    print("=" * 85)


# Resumo do dimensionamento (extra, fora da ficha)
def exibir_resumo(imovel, relatorio_itens, consumo_total, valor_kwh, custo_total):
    # contar a quantidade de cômodos
    qtd_comodos = len(imovel["comodos"])

    # somar as unidades de todos os equipamentos
    total_unidades = sum(item["qtd"] for item in relatorio_itens)

    # formatar e exibir o resumo
    print("\n" + "=" * 85)
    print("RESUMO DO DIMENSIONAMENTO")
    print("=" * 85)

    # nome do imóvel
    print(f"Imóvel: {imovel['nome']}")
    print(f"Quantidade de cômodos: {qtd_comodos}")
    print(f"Quantidade de equipamentos: {total_unidades}")

    # consumo total e custo mensal estimado
    print(f"Consumo total: {consumo_total:.2f} kWh/mês")
    print(f"Valor do kWh: R$ {valor_kwh:.2f}")
    print(f"Custo mensal estimado: R$ {custo_total:.2f}")
    print("=" * 85)


def executar_sistema():
    base_dados = obter_base_equipamentos()

    print("\n=== CADASTRO DO IMÓVEL ===")

    # PB01 - T01 e T03
    nome_imovel = input(
        "Digite o nome/identificação do imóvel: "
    ).strip()

    # PB01 - T04
    while nome_imovel == "":
        print(
            "O nome do imóvel não pode ser vazio. "
            "Por favor, digite novamente."
        )

        nome_imovel = input(
            "Digite o nome/identificação do imóvel: "
        ).strip()

    # PB01 - T02
    imovel = {
        "nome": nome_imovel,
        "comodos": []
    }

    # Quantidade de cômodos
    while True:
        try:
            qtd_comodos = int(
                input("\nQuantos cômodos tem na casa? ")
            )

            if qtd_comodos <= 0:
                print("A quantidade de cômodos deve ser maior que zero.")
            else:
                break

        except ValueError:
            print("Valor inválido! Digite um número inteiro.")

    total_consumo_casa = 0
    relatorio_itens = []

    # PB02 - T05
    for i in range(qtd_comodos):

        # PB02 - T02
        nome_comodo = input(
            f"\nDigite o nome do cômodo {i + 1} "
            "(ex: Sala, Cozinha, Quarto): "
        ).strip()

        # PB02 - T03
        while nome_comodo == "":
            print(
                "O nome do cômodo não pode ser vazio. "
                "Por favor, digite novamente."
            )

            nome_comodo = input(
                f"Digite o nome do cômodo {i + 1}: "
            ).strip()

        # PB02 - T01
        comodo = {
            "nome": nome_comodo,
            "equipamentos": []
        }

        # PB02 - T04
        imovel["comodos"].append(comodo)

        # Quantidade de equipamentos
        while True:
            try:
                qtd_equipamentos = int(
                    input(
                        f"Quantos equipamentos tem no(a) "
                        f"{nome_comodo}? "
                    )
                )

                if qtd_equipamentos <= 0:
                    print(
                        "A quantidade de equipamentos deve "
                        "ser maior que zero."
                    )
                else:
                    break

            except ValueError:
                print("Valor inválido! Digite um número inteiro.")

        for j in range(qtd_equipamentos):
            print(
                f"\n-> Escolhendo o item {j + 1} "
                f"do(a) {nome_comodo}:"
            )

            while True:
                exibir_menu(base_dados)

                opcao = input(
                    "Selecione o número do equipamento: "
                ).strip()

                if opcao in base_dados:
                    equip = base_dados[opcao]
                    break

                print(
                    "Opção inválida! "
                    "Selecione um equipamento da lista."
                )

            # PB04 - T01 e T02
            # Dados necessários:
            # potência, quantidade e horas de uso diário

            # PB04 - T03 e T04
            while True:
                try:
                    qtd = int(
                        input(
                            f"Quantas unidades de "
                            f"'{equip['nome']}' tem nesse cômodo? "
                        )
                    )

                    if qtd <= 0:
                        print(
                            "A quantidade não pode ser zero "
                            "ou negativa."
                        )
                    else:
                        break

                except ValueError:
                    print(
                        "Valor inválido! "
                        "Digite um número inteiro."
                    )

            # PB04 - T03 e T04
            while True:
                try:
                    horas = float(
                        input(
                            "Quantas horas por dia cada um "
                            "fica ligado? "
                        ).replace(",", ".")
                    )

                    if horas <= 0:
                        print(
                            "As horas não podem ser zero "
                            "ou negativas."
                        )
                    else:
                        break

                except ValueError:
                    print("Valor inválido! Digite um número.")

            # PB04 - T05
            consumo_mes = (
                equip["potencia"]
                * qtd
                * horas
                * 30
            ) / 1000

            # PB06 - T01, T02 e T03
            total_consumo_casa += consumo_mes

            item = {
                "comodo": nome_comodo,
                "nome": equip["nome"],
                "potencia": equip["potencia"],
                "qtd": qtd,
                "horas": horas,
                "consumo": consumo_mes
            }

            comodo["equipamentos"].append(item)
            relatorio_itens.append(item)

    # PB11 - T01 a T05
    while relatorio_itens:
        resposta = input(
            "\nDeseja remover algum equipamento? (s/n): "
        ).strip().lower()

        if resposta != "s":
            break

        remover_equipamento(imovel, relatorio_itens)

    # PB11 - T06
    total_consumo_casa = sum(item["consumo"] for item in relatorio_itens)

    # PB09 - T01 e T02
    valor_kwh = obter_valor_kwh()

    # PB09 - T03
    consumo_total = total_consumo_casa

    # PB09 - T04
    custo_total = consumo_total * valor_kwh

    # PB10 - T01 a T04
    # Recuperar os itens e calcular o custo usando a tarifa informada.
    for item in relatorio_itens:
        item["custo"] = item["consumo"] * valor_kwh

    print("\n" + "=" * 85)
    print(f"RESUMO DE CONSUMO - {imovel['nome'].upper()}")
    print("=" * 85)

    print(
        f"{'Cômodo':<15} | "
        f"{'Equipamento':<18} | "
        f"{'Qtd':<4} | "
        f"{'Consumo Mensal':<18} | "
        f"{'Custo Mensal'}"
    )

    print("-" * 85)

    # PB11 - T07
    if not relatorio_itens:
        print("Nenhum equipamento cadastrado.")

    # PB04 - T06 / PB10 - T05 e T06
    for item in relatorio_itens:
        print(
            f"{item['comodo']:<15} | "
            f"{item['nome']:<18} | "
            f"{item['qtd']:<4} | "
            f"{item['consumo']:>10.2f} kWh/mês | "
            f"R$ {item['custo']:.2f}"
        )

    print("-" * 85)

    # PB06 - T04 e T05
    print(
        f"CONSUMO TOTAL DA RESIDÊNCIA: "
        f"{total_consumo_casa:.2f} kWh/mês"
    )

    # PB09 - T05 e T06
    print(f"VALOR DO kWh: R$ {valor_kwh:.2f}")

    print(
        f"CUSTO MENSAL ESTIMADO: "
        f"R$ {custo_total:.2f}"
    )

    print("=" * 85)

    # PB14 - T01 a T05 e T07
    exibir_ranking_consumo(imovel)

    # PB18 - T01 a T07
    exibir_recomendacoes_economia(relatorio_itens, valor_kwh)

    # Resumo do dimensionamento (extra, fora da ficha)
    exibir_resumo(imovel, relatorio_itens, consumo_total, valor_kwh, custo_total)

    # PB01 (Sprint 3): guarda a residência para reutilizar no dimensionamento FV
    try:
        salvar_residencia(imovel, valor_kwh)
        print("\nResidência salva. Use a opção 3 do menu para gerar a proposta solar.")
    except (OSError, ValueError) as erro:
        print(f"\nNão foi possível salvar a residência: {erro}")


# ======================================================================
# SPRINT 3 - DIMENSIONAMENTO FOTOVOLTAICO COMPLETO
# Cobre PB01 a PB18, PB20 e PB21 do Product Backlog Final.
# Os equipamentos e preços vêm SEMPRE dos CSVs (pasta datasets/).
# ======================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_DADOS = os.path.join(BASE_DIR, "dados")
PASTA_RESIDENCIAS = os.path.join(PASTA_DADOS, "residencias")  # PB01
PASTA_PROJETOS = os.path.join(PASTA_DADOS, "projetos")        # PB20

DIAS_MES = 30                 # mesma convenção usada no consumo (Sprints 1-2)
HSP_PADRAO = 4.5              # valor inicial editável; a fonte deve ser informada
PR_PADRAO = 0.75              # valor inicial editável; a justificativa é obrigatória
PR_JUSTIFICATIVA_PADRAO = (
    "Valor típico para sistemas residenciais (perdas por temperatura, "
    "sujeira, cabeamento, inversor e sombreamento), em geral entre 0,70 e 0,80."
)
FONTE_HSP_PADRAO = "CRESESB - SunData (informe a localidade e o plano utilizado)"
TEMP_MIN_C = 10               # temperatura mínima para corrigir o Voc (frio aumenta Voc)
DC_AC_MIN, DC_AC_MAX, DC_AC_IDEAL = 0.8, 1.5, 1.15
# Custo de disponibilidade (kWh/mês) cobrado mesmo com compensação total
CUSTO_DISPONIBILIDADE_KWH = {"monofasico": 30, "bifasico": 50, "trifasico": 100}


class ErroValidacao(ValueError):
    """Erro de dado de entrada, com mensagem pronta para o usuário (PB18)."""


# ----------------------------------------------------------------------
# PB18 - Validações
# ----------------------------------------------------------------------
def validar_positivo(valor, nome, unidade=""):
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        raise ErroValidacao(f"{nome}: informe um número válido.")
    if math.isnan(numero) or math.isinf(numero):
        raise ErroValidacao(f"{nome}: informe um número válido.")
    if numero <= 0:
        sufixo = f" ({unidade})" if unidade else ""
        raise ErroValidacao(f"{nome} deve ser maior que zero{sufixo}.")
    return numero


def validar_texto(valor, nome):
    if valor is None or not str(valor).strip():
        raise ErroValidacao(f"{nome}: campo obrigatório.")
    return str(valor).strip()


def validar_parametros_solares(hsp, pr):
    hsp = validar_positivo(hsp, "Horas de Sol Pico (HSP)", "h/dia")
    if hsp > 12:
        raise ErroValidacao("HSP acima de 12 h/dia não é plausível. Confira a fonte.")
    pr = validar_positivo(pr, "Fator global de desempenho (PR)")
    if pr > 1:
        raise ErroValidacao("O PR deve estar entre 0 e 1 (exemplo: 0,75).")
    return hsp, pr


def validar_premissas(premissas):
    hsp, pr = validar_parametros_solares(premissas.get("hsp"), premissas.get("pr"))
    disponibilidade = premissas.get("disponibilidade_kwh")
    if disponibilidade is not None:
        disponibilidade = float(disponibilidade)
        if disponibilidade < 0:
            raise ErroValidacao("O custo de disponibilidade não pode ser negativo.")
    return {
        "hsp": hsp,
        "fonte_hsp": validar_texto(premissas.get("fonte_hsp"), "Fonte da HSP"),
        "pr": pr,
        "justificativa_pr": validar_texto(
            premissas.get("justificativa_pr"), "Justificativa do PR"
        ),
        "tarifa_kwh": validar_positivo(
            premissas.get("tarifa_kwh"), "Tarifa de energia", "R$/kWh"
        ),
        "disponibilidade_kwh": disponibilidade,  # None = automático (fase do inversor)
    }


# ----------------------------------------------------------------------
# Formatação (padrão brasileiro)
# ----------------------------------------------------------------------
def brl(valor):
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def num(valor, casas=2):
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


# ----------------------------------------------------------------------
# PB01 - Residências cadastradas (persistência em JSON)
# ----------------------------------------------------------------------
def _slug(texto):
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", texto.lower()).strip("_") or "sem_nome"


def calcular_consumo_item(potencia_w, qtd, horas):
    potencia_w = validar_positivo(potencia_w, "Potência do equipamento", "W")
    qtd = validar_positivo(qtd, "Quantidade")
    if qtd != int(qtd):
        raise ErroValidacao("A quantidade deve ser um número inteiro.")
    horas = validar_positivo(horas, "Horas de uso por dia", "h")
    if horas > 24:
        raise ErroValidacao("As horas de uso por dia não podem passar de 24.")
    return potencia_w * int(qtd) * horas * DIAS_MES / 1000


def salvar_residencia(imovel, valor_kwh):
    nome = validar_texto(imovel.get("nome"), "Nome da residência")
    valor_kwh = validar_positivo(valor_kwh, "Tarifa de energia", "R$/kWh")
    comodos = []
    for comodo in imovel.get("comodos", []):
        equipamentos = []
        for e in comodo.get("equipamentos", []):
            calcular_consumo_item(e["potencia"], e["qtd"], e["horas"])  # valida
            equipamentos.append({
                "nome": e["nome"], "potencia": e["potencia"],
                "qtd": int(e["qtd"]), "horas": e["horas"],
            })
        if equipamentos:
            comodos.append({"nome": comodo["nome"], "equipamentos": equipamentos})
    if not comodos:
        raise ErroValidacao("A residência precisa ter ao menos um equipamento para ser salva.")

    dados = {
        "nome": nome,
        "tarifa_kwh": valor_kwh,
        "comodos": comodos,
        "salvo_em": datetime.now().isoformat(timespec="seconds"),
    }
    os.makedirs(PASTA_RESIDENCIAS, exist_ok=True)
    with open(os.path.join(PASTA_RESIDENCIAS, _slug(nome) + ".json"),
              "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)
    return dados


def listar_residencias():
    if not os.path.isdir(PASTA_RESIDENCIAS):
        return []
    nomes = []
    for arq in sorted(os.listdir(PASTA_RESIDENCIAS)):
        if arq.endswith(".json"):
            try:
                with open(os.path.join(PASTA_RESIDENCIAS, arq), encoding="utf-8") as f:
                    nomes.append(json.load(f)["nome"])
            except (OSError, ValueError, KeyError):
                continue
    return nomes


def carregar_residencia(nome):
    caminho = os.path.join(PASTA_RESIDENCIAS, _slug(nome) + ".json")
    try:
        with open(caminho, encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        raise ErroValidacao(f"Residência '{nome}' não encontrada.")
    except ValueError:
        raise ErroValidacao(f"O arquivo da residência '{nome}' está corrompido.")


# ----------------------------------------------------------------------
# PB02 - Demanda energética
# ----------------------------------------------------------------------
def calcular_demanda(residencia):
    itens = []
    for comodo in residencia.get("comodos", []):
        for e in comodo.get("equipamentos", []):
            consumo = calcular_consumo_item(e["potencia"], e["qtd"], e["horas"])
            itens.append({
                "comodo": comodo["nome"], "nome": e["nome"],
                "potencia_w": e["potencia"], "qtd": e["qtd"],
                "horas": e["horas"], "consumo_kwh_mes": consumo,
            })
    if not itens:
        raise ErroValidacao("A residência não possui equipamentos cadastrados.")

    e_mes = sum(i["consumo_kwh_mes"] for i in itens)
    potencia_w = sum(i["potencia_w"] * i["qtd"] for i in itens)
    return {
        "residencia": residencia["nome"],
        "itens": itens,
        "e_mes_kwh": e_mes,
        "e_dia_kwh": e_mes / DIAS_MES,           # E_dia = E_mes / 30
        "potencia_instalada_w": potencia_w,
        "potencia_instalada_kw": potencia_w / 1000,
    }


# ----------------------------------------------------------------------
# PB04 / PB06 - Potência FV necessária e quantidade de módulos
# ----------------------------------------------------------------------
def calcular_potencia_fv_kw(e_dia_kwh, hsp, pr):
    # P_FV = E_dia / (HSP x PR)
    e_dia_kwh = validar_positivo(e_dia_kwh, "Consumo diário", "kWh")
    hsp, pr = validar_parametros_solares(hsp, pr)
    return e_dia_kwh / (hsp * pr)


def dimensionar_modulos(p_fv_kw, modulo):
    # N_mod = teto[(P_FV x 1000) / P_mod];  P_inst = N_mod x P_mod / 1000
    p_mod = validar_positivo(modulo["potencia_pico_wp"], "Potência do módulo", "Wp")
    n_mod = math.ceil(round(p_fv_kw * 1000 / p_mod, 6))
    return n_mod, n_mod * p_mod / 1000


# ----------------------------------------------------------------------
# PB07 - Compatibilidade do inversor com o arranjo
# ----------------------------------------------------------------------
def avaliar_inversor(modulo, qtd_modulos, inversor, temp_min_c=TEMP_MIN_C):
    motivos, avisos = [], []
    p_wp = qtd_modulos * modulo["potencia_pico_wp"]
    p_ca = inversor["potencia_nominal_ca_w"]
    if not p_ca or p_ca <= 0:
        return {"compativel": False, "motivos": ["Potência CA do inversor inválida."],
                "avisos": [], "razao_dc_ac": None, "arranjo": None}

    razao = p_wp / p_ca  # R_DC/AC = P_FV_instalada / P_inversor
    if p_wp > inversor["potencia_max_fv_wp"]:
        motivos.append("Potência FV acima do limite do inversor.")
    if razao > DC_AC_MAX:
        motivos.append("Razão DC/AC acima do aceitável (inversor subdimensionado).")
    elif razao < DC_AC_MIN:
        motivos.append("Razão DC/AC abaixo do aceitável (inversor superdimensionado).")

    # Tensão de circuito aberto corrigida para a temperatura mínima
    fator_frio = 1 + modulo["coef_temp_voc_pct_c"] / 100 * (temp_min_c - 25)
    voc_frio = modulo["voc_v"] * fator_frio
    max_serie = min(
        math.floor(round(inversor["tensao_cc_max_v"] / voc_frio, 9)),
        math.floor(round(inversor["tensao_mppt_max_v"] / modulo["vmp_v"], 9)),
    )
    min_serie = max(1, math.ceil(round(inversor["tensao_mppt_min_v"] / modulo["vmp_v"], 9)))

    arranjo = None
    if min_serie > max_serie:
        motivos.append("Tensões do módulo incompatíveis com a faixa do inversor.")
    else:
        entradas = inversor["num_mppt"] * inversor["strings_por_mppt"]
        for strings in range(1, entradas + 1):
            base, resto = divmod(qtd_modulos, strings)
            if base < 1:
                break
            comprimentos = {base} if resto == 0 else {base, base + 1}
            if min(comprimentos) < min_serie or max(comprimentos) > max_serie:
                continue
            if resto != 0 and strings > inversor["num_mppt"]:
                continue  # strings de tamanhos diferentes exigem MPPTs distintos
            por_mppt = math.ceil(strings / inversor["num_mppt"])
            if modulo["imp_a"] * por_mppt > inversor["corrente_max_mppt_a"]:
                continue
            if modulo["isc_a"] * por_mppt > inversor["corrente_curto_max_mppt_a"]:
                continue
            if resto == 0:
                descricao = f"{strings} string(s) de {base} módulos"
            else:
                descricao = (f"{strings - resto} string(s) de {base} e "
                             f"{resto} de {base + 1} módulos (MPPTs distintos)")
            arranjo = {"strings": strings, "strings_por_mppt": por_mppt,
                       "descricao": descricao}
            break
        if arranjo is None:
            motivos.append("Não há arranjo de strings que atenda tensão e corrente do inversor.")

    if inversor["tensao_cc_max_v"] and arranjo:
        avisos.append(f"Voc corrigido para {temp_min_c} °C usado na verificação de tensão máxima.")
    return {"compativel": not motivos, "motivos": motivos, "avisos": avisos,
            "razao_dc_ac": razao, "arranjo": arranjo}


def baterias_compativeis_com(inversor, baterias):
    if not inversor["aceita_bateria"]:
        return []
    tokens = [t.strip().lower() for t in inversor["modelo"].split(";") if t.strip()]
    fabricante = inversor["fabricante"].lower()
    v_min, v_max = inversor.get("bateria_tensao_min_v"), inversor.get("bateria_tensao_max_v")
    compativeis = []
    for bateria in baterias:
        texto = (bateria["inversores_compativeis"] or "").lower()
        if not (any(t in texto for t in tokens) or fabricante in texto):
            continue
        if v_min is not None and v_max is not None:
            if not v_min <= bateria["tensao_nominal_v"] <= v_max:
                continue
        compativeis.append(bateria)
    return compativeis


def _normalizar(valores):
    menor, maior = min(valores), max(valores)
    if maior - menor <= 1e-12:
        return [0.0] * len(valores)
    return [(v - menor) / (maior - menor) for v in valores]


def selecionar_equipamentos_fv(p_fv_kw, datasets, exigir_bateria=False, top=5):
    """Combina módulo + inversor compatíveis e ordena por um score que NÃO usa
    só o preço: 40% custo, 30% excesso de potência FV e 30% distância da
    razão DC/AC ideal (PB07)."""
    candidatos, rejeicoes = [], {}
    for modulo in datasets["modulos"]:
        qtd, p_inst = dimensionar_modulos(p_fv_kw, modulo)
        for inversor in datasets["inversores"]:
            if exigir_bateria and not inversor["aceita_bateria"]:
                rejeicoes["Inversor não aceita bateria."] = rejeicoes.get(
                    "Inversor não aceita bateria.", 0) + 1
                continue
            aval = avaliar_inversor(modulo, qtd, inversor)
            if not aval["compativel"]:
                for motivo in aval["motivos"]:
                    rejeicoes[motivo] = rejeicoes.get(motivo, 0) + 1
                continue
            baterias = baterias_compativeis_com(inversor, datasets["baterias"])
            if exigir_bateria and not baterias:
                rejeicoes["Sem bateria compatível cadastrada."] = rejeicoes.get(
                    "Sem bateria compatível cadastrada.", 0) + 1
                continue
            candidatos.append({
                "modulo": modulo, "inversor": inversor, "qtd_modulos": qtd,
                "potencia_instalada_kwp": p_inst,
                "razao_dc_ac": aval["razao_dc_ac"], "arranjo": aval["arranjo"],
                "avisos": aval["avisos"],
                "custo_fv": qtd * modulo["preco_brl"] + inversor["preco_brl"],
                "baterias_compativeis": baterias,
            })

    if not candidatos:
        principais = sorted(rejeicoes.items(), key=lambda x: -x[1])[:3]
        detalhe = " ".join(f"{m}" for m, _ in principais)
        raise ErroValidacao(
            "Nenhuma combinação compatível de módulo e inversor foi encontrada "
            "nos datasets para esta potência. " + detalhe
        )

    custo_n = _normalizar([c["custo_fv"] for c in candidatos])
    excesso_n = _normalizar([c["potencia_instalada_kwp"] - p_fv_kw for c in candidatos])
    razao_n = _normalizar([abs(c["razao_dc_ac"] - DC_AC_IDEAL) for c in candidatos])
    for c, a, b, d in zip(candidatos, custo_n, excesso_n, razao_n):
        c["score"] = 0.4 * a + 0.3 * b + 0.3 * d
    candidatos.sort(key=lambda c: (c["score"], c["custo_fv"]))
    return candidatos[:top]


# ----------------------------------------------------------------------
# PB08 / PB09 - Geração e comparação com o consumo
# ----------------------------------------------------------------------
def estimar_geracao(p_inst_kwp, hsp, pr):
    dia = p_inst_kwp * hsp * pr          # E_gerada,dia = P_inst x HSP x PR
    return {"dia_kwh": dia, "mes_kwh": dia * DIAS_MES}


def comparar_geracao_consumo(gerada_mes, consumo_mes, disponibilidade_kwh=0):
    consumo_mes = validar_positivo(consumo_mes, "Consumo mensal", "kWh")
    atendimento = gerada_mes / consumo_mes * 100  # (E_gerada / E_consumida) x 100
    compensavel = max(consumo_mes - disponibilidade_kwh, 0)
    compensada = min(gerada_mes, compensavel)
    return {
        "consumo_mes_kwh": consumo_mes,
        "gerada_mes_kwh": gerada_mes,
        "atendimento_pct": atendimento,
        "disponibilidade_kwh": disponibilidade_kwh,
        "compensada_mes_kwh": compensada,
        "excedente_mes_kwh": max(gerada_mes - compensada, 0),
        "compensada_pct": compensada / consumo_mes * 100,
    }


# ----------------------------------------------------------------------
# PB11 / PB12 - Baterias
# ----------------------------------------------------------------------
def dimensionar_bateria(e_dia_kwh, autonomia_h, fracao_critica_pct, bateria):
    autonomia_h = validar_positivo(autonomia_h, "Autonomia desejada", "h")
    fracao_critica_pct = validar_positivo(fracao_critica_pct, "Parcela da carga atendida", "%")
    if fracao_critica_pct > 100:
        raise ErroValidacao("A parcela da carga atendida pelas baterias não pode passar de 100%.")

    dod = bateria["profundidade_descarga_pct"] / 100
    eta = bateria["eficiencia_ciclo_pct"] / 100
    c_unidade = bateria["capacidade_nominal_kwh"]
    if dod <= 0 or eta <= 0 or c_unidade <= 0:
        raise ErroValidacao(
            f"Bateria {bateria['modelo']}: DoD, eficiência ou capacidade inválidos no dataset."
        )

    carga_kw = e_dia_kwh / 24 * fracao_critica_pct / 100
    e_aut = carga_kw * autonomia_h                      # energia necessária (kWh)
    c_bat = e_aut / (dod * eta)                         # C_bat = E_aut / (DoD x eta)
    n_bat = max(1, math.ceil(round(c_bat / c_unidade, 6)))  # N_bat = teto(C_bat / C_un)
    cap_total = n_bat * c_unidade
    cap_util = cap_total * dod * eta

    avisos, viavel = [], True
    limite = bateria.get("modulos_max_paralelo")
    if limite and n_bat > limite:
        viavel = False
        avisos.append(f"Quantidade ({n_bat}) acima do máximo em paralelo ({limite}).")
    if n_bat * bateria["potencia_continua_w"] < carga_kw * 1000:
        avisos.append("Potência contínua das baterias menor que a carga média atendida.")
    return {
        "bateria": bateria, "autonomia_h": autonomia_h,
        "fracao_critica_pct": fracao_critica_pct,
        "energia_necessaria_kwh": e_aut, "capacidade_calculada_kwh": c_bat,
        "quantidade": n_bat, "capacidade_unitaria_kwh": c_unidade,
        "capacidade_ah_unitaria": c_unidade * 1000 / bateria["tensao_nominal_v"],
        "capacidade_total_kwh": cap_total, "capacidade_util_kwh": cap_util,
        "autonomia_obtida_h": cap_util / carga_kw if carga_kw > 0 else 0,
        "custo_total": n_bat * bateria["preco_brl"],
        "avisos": avisos, "viavel": viavel,
    }


def listar_opcoes_bateria(candidato, e_dia_kwh, autonomia_h, fracao_critica_pct):
    opcoes = [dimensionar_bateria(e_dia_kwh, autonomia_h, fracao_critica_pct, b)
              for b in candidato["baterias_compativeis"]]
    viaveis = sorted((o for o in opcoes if o["viavel"]), key=lambda o: o["custo_total"])
    if not viaveis:
        raise ErroValidacao(
            "Nenhuma bateria compatível atende a autonomia pedida. "
            "Reduza a autonomia ou a parcela da carga atendida."
        )
    return viaveis


# ----------------------------------------------------------------------
# PB13 / PB15 / PB16 - Orçamento, economia e payback simples
# ----------------------------------------------------------------------
def montar_orcamento(modulo, qtd_modulos, inversor, bateria=None, qtd_baterias=0):
    if qtd_modulos <= 0 or (bateria and qtd_baterias <= 0):
        raise ErroValidacao("Quantidades do orçamento devem ser maiores que zero.")
    itens = [
        {"equipamento": "Módulo fotovoltaico",
         "modelo": f"{modulo['fabricante']} {modulo['modelo']}",
         "quantidade": qtd_modulos, "preco_unitario": modulo["preco_brl"]},
        {"equipamento": "Inversor",
         "modelo": f"{inversor['fabricante']} {inversor['modelo']}",
         "quantidade": 1, "preco_unitario": inversor["preco_brl"]},
    ]
    if bateria:
        itens.append({"equipamento": "Bateria",
                      "modelo": f"{bateria['fabricante']} {bateria['modelo']}",
                      "quantidade": qtd_baterias, "preco_unitario": bateria["preco_brl"]})
    for item in itens:
        item["subtotal"] = item["quantidade"] * item["preco_unitario"]  # Custo_item
    return {"itens": itens, "total": sum(i["subtotal"] for i in itens)}  # Custo_total


def calcular_economia(compensada_mes_kwh, tarifa_kwh):
    tarifa_kwh = validar_positivo(tarifa_kwh, "Tarifa de energia", "R$/kWh")
    mensal = compensada_mes_kwh * tarifa_kwh  # Economia_mensal = E_compensada x tarifa
    return {"tarifa_kwh": tarifa_kwh, "compensada_mes_kwh": compensada_mes_kwh,
            "mensal": mensal, "anual": mensal * 12}


def calcular_payback_simples(investimento, economia_anual):
    if economia_anual <= 0:
        raise ErroValidacao("Economia anual nula: não é possível calcular o payback.")
    anos = investimento / economia_anual  # Payback = Investimento / Economia_anual
    return {"anos": anos, "meses": anos * 12}


# ----------------------------------------------------------------------
# Cenários (PB10 / PB14) e proposta (PB17)
# ----------------------------------------------------------------------
def calcular_cenario(demanda, premissas, opcao, bateria_dim=None):
    modulo, inversor = opcao["modulo"], opcao["inversor"]
    geracao = estimar_geracao(opcao["potencia_instalada_kwp"],
                              premissas["hsp"], premissas["pr"])
    disponibilidade = premissas["disponibilidade_kwh"]
    if disponibilidade is None:
        disponibilidade = CUSTO_DISPONIBILIDADE_KWH.get(inversor["fase"], 0)
    atendimento = comparar_geracao_consumo(
        geracao["mes_kwh"], demanda["e_mes_kwh"], disponibilidade)

    orcamento = montar_orcamento(
        modulo, opcao["qtd_modulos"], inversor,
        bateria_dim["bateria"] if bateria_dim else None,
        bateria_dim["quantidade"] if bateria_dim else 0)
    economia = calcular_economia(atendimento["compensada_mes_kwh"], premissas["tarifa_kwh"])
    try:
        payback, aviso_payback = calcular_payback_simples(
            orcamento["total"], economia["anual"]), None
    except ErroValidacao as erro:
        payback, aviso_payback = None, str(erro)

    return {
        "tipo": "com_bateria" if bateria_dim else "sem_bateria",
        "modulo": modulo, "inversor": inversor,
        "qtd_modulos": opcao["qtd_modulos"],
        "potencia_instalada_kwp": opcao["potencia_instalada_kwp"],
        "razao_dc_ac": opcao["razao_dc_ac"], "arranjo": opcao["arranjo"],
        "avisos": opcao["avisos"], "geracao": geracao,
        "atendimento": atendimento, "bateria": bateria_dim,
        "orcamento": orcamento, "economia": economia,
        "payback": payback, "aviso_payback": aviso_payback,
    }


def _payback_texto(cenario):
    if cenario["payback"]:
        return f"{num(cenario['payback']['anos'], 1)} anos (payback simples, estimativa)"
    return cenario["aviso_payback"] or "—"


def resumo_cenario_linhas(c):
    """Linhas (rótulo, valor) usadas no terminal, na web e no HTML."""
    m, i, a, e = c["modulo"], c["inversor"], c["atendimento"], c["economia"]
    linhas = [
        ("Módulo", f"{m['fabricante']} {m['modelo']} ({num(m['potencia_pico_wp'], 0)} Wp)"),
        ("Quantidade de módulos", str(c["qtd_modulos"])),
        ("Potência instalada", f"{num(c['potencia_instalada_kwp'], 2)} kWp"),
        ("Inversor", f"{i['fabricante']} {i['modelo']} "
                     f"({num(i['potencia_nominal_ca_w'] / 1000, 1)} kW CA)"),
        ("Razão DC/AC", num(c["razao_dc_ac"], 2)),
        ("Arranjo", c["arranjo"]["descricao"] if c["arranjo"] else "—"),
        ("Geração estimada",
         f"{num(c['geracao']['dia_kwh'], 1)} kWh/dia | {num(c['geracao']['mes_kwh'], 0)} kWh/mês"),
        ("Consumo mensal", f"{num(a['consumo_mes_kwh'], 0)} kWh/mês"),
        ("Atendimento do consumo", f"{num(a['atendimento_pct'], 1)}%"),
        ("Energia compensada",
         f"{num(a['compensada_mes_kwh'], 0)} kWh/mês "
         f"(custo de disponibilidade: {num(a['disponibilidade_kwh'], 0)} kWh)"),
        ("Excedente gerado (não compensado no mês)", f"{num(a['excedente_mes_kwh'], 0)} kWh/mês"),
    ]
    b = c["bateria"]
    if b:
        bat = b["bateria"]
        linhas += [
            ("Bateria", f"{bat['fabricante']} {bat['modelo']} ({bat['quimica']})"),
            ("Quantidade de baterias", str(b["quantidade"])),
            ("Autonomia considerada", f"{num(b['autonomia_h'], 1)} h "
                                      f"({num(b['fracao_critica_pct'], 0)}% da carga)"),
            ("Energia necessária / capacidade calculada",
             f"{num(b['energia_necessaria_kwh'], 2)} kWh / {num(b['capacidade_calculada_kwh'], 2)} kWh"),
            ("Capacidade instalada",
             f"{num(b['capacidade_total_kwh'], 2)} kWh nominais | "
             f"{num(b['capacidade_util_kwh'], 2)} kWh úteis"),
            ("Autonomia obtida", f"{num(b['autonomia_obtida_h'], 1)} h"),
        ]
    linhas += [
        ("Tarifa utilizada", f"{brl(e['tarifa_kwh'])}/kWh"),
        ("Economia estimada",
         f"{brl(e['mensal'])}/mês | {brl(e['anual'])}/ano"),
        ("Investimento (equipamentos)", brl(c["orcamento"]["total"])),
        ("Payback", _payback_texto(c)),
    ]
    return linhas


def orcamento_linhas(c):
    return [[i["equipamento"], i["modelo"], str(i["quantidade"]),
             brl(i["preco_unitario"]), brl(i["subtotal"])]
            for i in c["orcamento"]["itens"]] + [["TOTAL", "", "", "", brl(c["orcamento"]["total"])]]


def comparar_cenarios(sem, com):
    def v(c, f):
        return f(c) if c else "—"
    return [
        ["Potência FV instalada", num(sem["potencia_instalada_kwp"], 2) + " kWp",
         v(com, lambda c: num(c["potencia_instalada_kwp"], 2) + " kWp")],
        ["Módulos", f"{sem['qtd_modulos']} x {sem['modulo']['modelo']}",
         v(com, lambda c: f"{c['qtd_modulos']} x {c['modulo']['modelo']}")],
        ["Inversor", sem["inversor"]["modelo"], v(com, lambda c: c["inversor"]["modelo"])],
        ["Geração mensal", num(sem["geracao"]["mes_kwh"], 0) + " kWh",
         v(com, lambda c: num(c["geracao"]["mes_kwh"], 0) + " kWh")],
        ["Atendimento", num(sem["atendimento"]["atendimento_pct"], 1) + "%",
         v(com, lambda c: num(c["atendimento"]["atendimento_pct"], 1) + "%")],
        ["Armazenamento", "Não possui",
         v(com, lambda c: f"{c['bateria']['quantidade']} x {c['bateria']['bateria']['modelo']} "
                          f"({num(c['bateria']['capacidade_util_kwh'], 1)} kWh úteis)")],
        ["Autonomia", "—", v(com, lambda c: num(c["bateria"]["autonomia_obtida_h"], 1) + " h")],
        ["Investimento", brl(sem["orcamento"]["total"]),
         v(com, lambda c: brl(c["orcamento"]["total"]))],
        ["Economia anual", brl(sem["economia"]["anual"]),
         v(com, lambda c: brl(c["economia"]["anual"]))],
        ["Payback simples", _payback_texto(sem), v(com, _payback_texto)],
    ]


def gerar_conclusao(sem, com):
    """Resposta à questão final, usando apenas números calculados (seção 9 do PDF)."""
    if com is None:
        return ("Não foi possível montar o cenário com baterias com os equipamentos "
                "cadastrados; a análise considera apenas o sistema sem armazenamento.")
    extra = com["orcamento"]["total"] - sem["orcamento"]["total"]
    pct = extra / sem["orcamento"]["total"] * 100
    texto = (
        f"Sem baterias o investimento é {brl(sem['orcamento']['total'])}, com economia de "
        f"{brl(sem['economia']['anual'])}/ano e {_payback_texto(sem)}. Com baterias o investimento "
        f"vai a {brl(com['orcamento']['total'])} ({brl(extra)} a mais, {num(pct, 0)}%), com "
        f"{_payback_texto(com)} e autonomia de {num(com['bateria']['autonomia_obtida_h'], 1)} h "
        f"({num(com['bateria']['capacidade_util_kwh'], 1)} kWh úteis). "
        "No modelo de compensação adotado, a bateria não aumenta a energia compensada; "
        "ela compra segurança de fornecimento, não economia. "
    )
    if sem["payback"] and com["payback"] and com["payback"]["anos"] > sem["payback"]["anos"]:
        texto += ("Pelo critério financeiro, a solução sem baterias é a mais vantajosa para esta "
                  "residência; as baterias só se justificam se houver necessidade real de backup "
                  "durante quedas de energia.")
    else:
        texto += "Avalie se a autonomia obtida justifica o investimento adicional."
    return texto


def gerar_proposta(residencia, premissas, demanda, p_fv_kw, sem, com=None):
    return {
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "residencia": residencia["nome"],
        "demanda": demanda, "premissas": premissas,
        "p_fv_necessaria_kw": p_fv_kw,
        "sem_bateria": sem, "com_bateria": com,
        "comparativo": comparar_cenarios(sem, com),
        "conclusao": gerar_conclusao(sem, com),
    }


def formatar_proposta_texto(prop):
    d, p = prop["demanda"], prop["premissas"]
    linhas = ["=" * 85, f"PROPOSTA FOTOVOLTAICA - {prop['residencia'].upper()}", "=" * 85,
              f"Consumo: {num(d['e_mes_kwh'], 1)} kWh/mês | {num(d['e_dia_kwh'], 2)} kWh/dia",
              f"Potência instalada de cargas: {num(d['potencia_instalada_kw'], 2)} kW",
              f"HSP: {num(p['hsp'], 2)} h/dia (fonte: {p['fonte_hsp']})",
              f"PR: {num(p['pr'], 2)} ({p['justificativa_pr']})",
              f"Potência FV necessária: {num(prop['p_fv_necessaria_kw'], 2)} kWp"]
    for chave, titulo in (("sem_bateria", "CENÁRIO SEM BATERIAS"),
                          ("com_bateria", "CENÁRIO COM BATERIAS")):
        c = prop[chave]
        if not c:
            continue
        linhas += ["", "-" * 85, titulo, "-" * 85]
        linhas += [f"{r}: {v}" for r, v in resumo_cenario_linhas(c)]
        linhas.append("Orçamento:")
        linhas += ["  " + " | ".join(x for x in l if x) for l in orcamento_linhas(c)]
    linhas += ["", "-" * 85, "COMPARATIVO", "-" * 85]
    linhas += [f"{r[0]:<22} | {r[1]:<32} | {r[2]}" for r in prop["comparativo"]]
    linhas += ["", "CONCLUSÃO:", prop["conclusao"], "",
               "* Valores estimados. O payback é simples (sem juros, reajuste tarifário,",
               "  degradação dos módulos, bandeiras ou Fio B) e não é previsão financeira exata.",
               "=" * 85]
    return "\n".join(linhas)


def _tabela_html(cabecalho, linhas):
    topo = "".join("<th>" + escape(str(c)) + "</th>" for c in cabecalho)
    corpo = "".join(
        "<tr>" + "".join("<td>" + escape(str(c)) + "</td>" for c in l) + "</tr>"
        for l in linhas)
    return f"<table><thead><tr>{topo}</tr></thead><tbody>{corpo}</tbody></table>"


def gerar_proposta_html(prop):
    """PB21 - página final para entregar ao cliente."""
    d, p = prop["demanda"], prop["premissas"]
    partes = [
        "<!DOCTYPE html><html lang='pt-BR'><head><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1'>",
        f"<title>Proposta FV - {escape(prop['residencia'])}</title><style>",
        "body{font-family:Arial,sans-serif;max-width:900px;margin:24px auto;padding:0 16px;color:#222}",
        "h1{color:#b45309}h2{border-bottom:2px solid #f59e0b;padding-bottom:4px;margin-top:32px}",
        "table{border-collapse:collapse;width:100%;margin:8px 0}",
        "th,td{border:1px solid #ddd;padding:6px 10px;text-align:left;font-size:14px}",
        "th{background:#fef3c7}.nota{font-size:12px;color:#666}",
        "</style></head><body>",
        f"<h1>Proposta de Energia Solar</h1><p>Residência: <b>{escape(prop['residencia'])}</b> "
        f"| Gerada em {escape(prop['gerado_em'])}</p>",
        "<h2>Consumo e premissas</h2>",
        _tabela_html(["Item", "Valor"], [
            ["Consumo mensal / diário", f"{num(d['e_mes_kwh'], 1)} kWh / {num(d['e_dia_kwh'], 2)} kWh"],
            ["Potência instalada das cargas", f"{num(d['potencia_instalada_kw'], 2)} kW"],
            ["HSP", f"{num(p['hsp'], 2)} h/dia - fonte: {p['fonte_hsp']}"],
            ["PR", f"{num(p['pr'], 2)} - {p['justificativa_pr']}"],
            ["Potência FV necessária", f"{num(prop['p_fv_necessaria_kw'], 2)} kWp"],
        ]),
    ]
    for chave, titulo in (("sem_bateria", "Cenário sem baterias"),
                          ("com_bateria", "Cenário com baterias")):
        c = prop[chave]
        if not c:
            continue
        partes.append(f"<h2>{titulo}</h2>")
        partes.append(_tabela_html(["Item", "Resultado"], resumo_cenario_linhas(c)))
        partes.append("<h3>Orçamento</h3>")
        partes.append(_tabela_html(
            ["Equipamento", "Fabricante/modelo", "Qtd", "Preço unit.", "Subtotal"],
            orcamento_linhas(c)))
    partes += [
        "<h2>Comparativo</h2>",
        _tabela_html(["Critério", "Sem baterias", "Com baterias"], prop["comparativo"]),
        f"<h2>Conclusão</h2><p>{escape(prop['conclusao'])}</p>",
        "<p class='nota'>Valores estimados. O payback é simples (sem juros, reajuste "
        "tarifário, degradação dos módulos, bandeiras tarifárias ou Fio B) e não "
        "constitui previsão financeira exata.</p></body></html>",
    ]
    return "".join(partes)


# ----------------------------------------------------------------------
# PB20 - Persistência do projeto
# ----------------------------------------------------------------------
def salvar_projeto(prop):
    os.makedirs(PASTA_PROJETOS, exist_ok=True)
    nome = f"{_slug(prop['residencia'])}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(os.path.join(PASTA_PROJETOS, nome + ".json"), "w", encoding="utf-8") as f:
        json.dump(prop, f, ensure_ascii=False, indent=2)
    return nome


def listar_projetos():
    if not os.path.isdir(PASTA_PROJETOS):
        return []
    return sorted((a[:-5] for a in os.listdir(PASTA_PROJETOS) if a.endswith(".json")),
                  reverse=True)


def carregar_projeto(nome):
    try:
        with open(os.path.join(PASTA_PROJETOS, nome + ".json"), encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise ErroValidacao(f"Projeto '{nome}' não encontrado.")
    except ValueError:
        raise ErroValidacao(f"O projeto '{nome}' está corrompido.")


def exportar_proposta_html(prop, caminho=None):
    caminho = caminho or os.path.join(
        PASTA_DADOS, f"proposta_{_slug(prop['residencia'])}.html")
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(gerar_proposta_html(prop))
    return caminho


# ----------------------------------------------------------------------
# Fluxo completo no terminal (a interface principal é o app.py)
# ----------------------------------------------------------------------
def _ler_float(mensagem, padrao=None):
    while True:
        texto = input(mensagem).strip().replace(",", ".")
        if texto == "" and padrao is not None:
            return padrao
        try:
            return float(texto)
        except ValueError:
            print("Digite um número válido.")


def _ler_escolha(mensagem, quantidade, padrao=1):
    while True:
        texto = input(mensagem).strip()
        if texto == "":
            return padrao - 1
        if texto.isdigit() and 1 <= int(texto) <= quantidade:
            return int(texto) - 1
        print(f"Escolha um número entre 1 e {quantidade}.")


def executar_proposta_cli():
    try:
        nomes = listar_residencias()
        if not nomes:
            print("\nNenhuma residência cadastrada. Use a opção 1 do menu primeiro.")
            return
        print("\n=== PROPOSTA FOTOVOLTAICA ===")
        for n, nome in enumerate(nomes, 1):
            print(f"[{n}] {nome}")
        residencia = carregar_residencia(nomes[_ler_escolha("Residência: ", len(nomes))])
        demanda = calcular_demanda(residencia)
        print(f"\nConsumo: {num(demanda['e_mes_kwh'], 1)} kWh/mês | "
              f"{num(demanda['e_dia_kwh'], 2)} kWh/dia | "
              f"Potência instalada: {num(demanda['potencia_instalada_kw'], 2)} kW")

        premissas = validar_premissas({
            "hsp": _ler_float(f"HSP em h/dia [{HSP_PADRAO}]: ", HSP_PADRAO),
            "fonte_hsp": input(f"Fonte da HSP [{FONTE_HSP_PADRAO}]: ").strip() or FONTE_HSP_PADRAO,
            "pr": _ler_float(f"PR (0 a 1) [{PR_PADRAO}]: ", PR_PADRAO),
            "justificativa_pr": input("Justificativa do PR [padrão]: ").strip() or PR_JUSTIFICATIVA_PADRAO,
            "tarifa_kwh": _ler_float(f"Tarifa R$/kWh [{residencia['tarifa_kwh']}]: ",
                                     residencia["tarifa_kwh"]),
            "disponibilidade_kwh": None,
        })
        p_fv = calcular_potencia_fv_kw(demanda["e_dia_kwh"], premissas["hsp"], premissas["pr"])
        print(f"Potência FV necessária: {num(p_fv, 2)} kWp")

        datasets = listar_datasets_pb19()
        opcoes = selecionar_equipamentos_fv(p_fv, datasets)
        print("\nOpções sem baterias (melhor primeiro):")
        for n, o in enumerate(opcoes, 1):
            print(f"[{n}] {o['qtd_modulos']}x {o['modulo']['modelo']} + {o['inversor']['modelo']} | "
                  f"{num(o['potencia_instalada_kwp'], 2)} kWp | DC/AC {num(o['razao_dc_ac'], 2)} | "
                  f"{brl(o['custo_fv'])}")
        sem = calcular_cenario(demanda, premissas, opcoes[_ler_escolha("Escolha [1]: ", len(opcoes))])

        com = None
        if input("\nComparar com sistema com baterias? (s/n): ").strip().lower() == "s":
            autonomia = _ler_float("Autonomia desejada em horas [12]: ", 12)
            fracao = _ler_float("Parcela da carga atendida pelas baterias em % [100]: ", 100)
            try:
                opcoes_b = selecionar_equipamentos_fv(p_fv, datasets, exigir_bateria=True)
                base = opcoes_b[0]
                baterias = listar_opcoes_bateria(base, demanda["e_dia_kwh"], autonomia, fracao)
                print("\nBaterias compatíveis:")
                for n, b in enumerate(baterias, 1):
                    print(f"[{n}] {b['quantidade']}x {b['bateria']['modelo']} | "
                          f"{num(b['capacidade_total_kwh'], 1)} kWh | {brl(b['custo_total'])}")
                escolhida = baterias[_ler_escolha("Escolha [1]: ", len(baterias))]
                com = calcular_cenario(demanda, premissas, base, escolhida)
            except ErroValidacao as erro:
                print(f"Cenário com baterias indisponível: {erro}")

        proposta = gerar_proposta(residencia, premissas, demanda, p_fv, sem, com)
        print("\n" + formatar_proposta_texto(proposta))
        if input("\nSalvar projeto e exportar proposta em HTML? (s/n): ").strip().lower() == "s":
            print(f"Projeto salvo: {salvar_projeto(proposta)}")
            print(f"Proposta exportada em: {exportar_proposta_html(proposta)}")
    except (ErroValidacao, FileNotFoundError, ValueError) as erro:
        print(f"\nNão foi possível concluir: {erro}")


if __name__ == "__main__":
    while True:
        print("\n=== SISTEMA ===")
        print("1 - Dimensionamento residencial")
        print("2 - Gestão de Equipamentos Fotovoltaicos")
        print("3 - Proposta fotovoltaica completa (Sprint 3)")
        print("0 - Sair")
        escolha = input("Escolha: ").strip()
        if escolha == "1":
            executar_sistema()
        elif escolha == "2":
            executar_pb19()
        elif escolha == "3":
            executar_proposta_cli()
        elif escolha == "0":
            print("Muito obrigado, finalizando sistema...")
            break
        else:
            print("Opção inválida.")
