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
                print(
                    "A quantidade de cômodos deve ser maior que zero."
                )
            else:
                break

        except ValueError:
            print(
                "Valor inválido! Digite um número inteiro."
            )

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
                print(
                    "Valor inválido! Digite um número inteiro."
                )

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
                    print(
                        "Valor inválido! Digite um número."
                    )

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

    # PB09 - T01 e T02
    valor_kwh = obter_valor_kwh()

    # PB09 - T03
    consumo_total = total_consumo_casa

    # PB09 - T04
    custo_total = consumo_total * valor_kwh

    print("\n==================================================")
    print(
        f"RESUMO DE CONSUMO - "
        f"{imovel['nome'].upper()}"
    )
    print("==================================================")

    print(
        f"{'Cômodo':<15} | "
        f"{'Equipamento':<18} | "
        f"{'Qtd':<4} | "
        f"{'Consumo Mensal'}"
    )

    print("-" * 70)

    # PB04 - T06
    for item in relatorio_itens:
        print(
            f"{item['comodo']:<15} | "
            f"{item['nome']:<18} | "
            f"{item['qtd']:<4} | "
            f"{item['consumo']:.2f} kWh/mês"
        )

    print("-" * 70)

    # PB06 - T04 e T05
    print(
        f"CONSUMO TOTAL DA RESIDÊNCIA: "
        f"{total_consumo_casa:.2f} kWh/mês"
    )

    # PB09 - T05 e T06
    print(
        f"VALOR DO kWh: "
        f"R$ {valor_kwh:.2f}"
    )

    print(
        f"CUSTO MENSAL ESTIMADO: "
        f"R$ {custo_total:.2f}"
    )

    print("==================================================")


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
                print(
                    "Valor inválido! Digite um número."
                )

        if cadastro == 2:
            print(
                "Muito obrigado, finalizando sistema..."
            )
            break


