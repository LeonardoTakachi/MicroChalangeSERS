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

    # Resumo do dimensionamento (extra, fora da ficha)
    exibir_resumo(imovel, relatorio_itens, consumo_total, valor_kwh, custo_total)


if __name__ == "__main__":
    while True:
        executar_sistema()

        while True:
            try:
                cadastro = int(
                    input(
                        "\nDeseja cadastrar outro imóvel? "
                        "Qualquer número = Sim / 2 = Não: "
                    )
                )
                break

            except ValueError:
                print("Valor inválido! Digite um número.")

        if cadastro == 2:
            print("Muito obrigado, finalizando sistema...")
            break
