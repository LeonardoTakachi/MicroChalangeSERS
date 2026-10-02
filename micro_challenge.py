from datetime import datetime
import csv
import os
import math

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
    """PB19 - T06: carrega os três datasets integrados ao sistema."""
    return {
        "modulos": carregar_dataset("modulos"),
        "inversores": carregar_dataset("inversores"),
        "baterias": carregar_dataset("baterias"),
    }


def validar_quantidade_datasets(datasets):
    """PB19 - T03: confere a quantidade mínima exigida."""
    minimo = {"modulos": 10, "inversores": 8, "baterias": 6}
    erros = []
    for nome, minimo_exigido in minimo.items():
        qtd = len(datasets.get(nome, []))
        if qtd < minimo_exigido:
            erros.append(f"{nome}: {qtd} encontrados; mínimo = {minimo_exigido}.")
    return erros


def validar_registros_pb19(datasets):
    """PB19 - T04/T05: valida tipos, unidades, preços e rastreabilidade."""
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
    """Executa T03-T05 e informa se os datasets podem ser usados pelo sistema."""
    try:
        datasets = listar_datasets_pb19()
    except (FileNotFoundError, ValueError, KeyError) as erro:
        print(f"\nPB19 - erro ao carregar datasets: {erro}")
        return False

    erros = validar_quantidade_datasets(datasets)
    erros_registros, avisos = validar_registros_pb19(datasets)
    erros.extend(erros_registros)

    print("\n" + "=" * 85)
    print("VALIDAÇÃO DOS DATASETS - PB19")
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
    print("\nT05 - CONFERÊNCIA MANUAL NECESSÁRIA:")
    print("O código verifica rastreabilidade e consistência, mas a existência")
    print("do produto deve ser confirmada na fonte/datasheet registrado no CSV.")
    print("=" * 85)
    return True


def dimensionar_sistema_pb19(consumo_mensal_kwh, horas_sol_pico=4.5):
    # PB19 - T07: pré-dimensionamento e verificação de compatibilidade
    if consumo_mensal_kwh <= 0 or horas_sol_pico <= 0:
        raise ValueError("Consumo e horas de sol pico devem ser maiores que zero.")

    datasets = listar_datasets_pb19()
    energia_diaria = consumo_mensal_kwh / 30
    potencia_necessaria_w = (energia_diaria / horas_sol_pico) * 1000
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
    print("CATÁLOGO DE EQUIPAMENTOS - PB19")
    print("=" * 85)
    ids = {"modulos": "id_modulo", "inversores": "id_inversor", "baterias": "id_bateria"}
    for nome, registros in datasets.items():
        print(f"\n{nome.upper()} ({len(registros)} registros)")
        for item in registros:
            print(f"- {item[ids[nome]]} | {item['fabricante']} {item['modelo']} | R$ {item['preco_brl']:.2f}")


def executar_pb19():
    # Menu do PB19 sem alterar o fluxo residencial existente.
    while True:
        print("\n=== PB19 - EQUIPAMENTOS FOTOVOLTAICOS ===")
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


if __name__ == "__main__":
    while True:
        print("\n=== SISTEMA ===")
        print("1 - Dimensionamento residencial")
        print("2 - Gestão de Equipamentos Fotovoltaicos")
        print("0 - Sair")
        escolha = input("Escolha: ").strip()
        if escolha == "1":
            executar_sistema()
        elif escolha == "2":
            executar_pb19()
        elif escolha == "0":
            print("Muito obrigado, finalizando sistema...")
            break
        else:
            print("Opção inválida.")
