while True:
 
    def obter_base_equipamentos():
        # Base de dados exigida pelo enunciado
        return {
            "1": {"nome": "Geladeira", "cômodo": "Cozinha", "potencia": 250},
            "2": {"nome": "Chuveiro Elétrico", "ccômodo": "Banho", "potencia": 5500},
            "3": {"nome": "Ar Condicionado", "cômodo": "Climatização", "potencia": 1200},
            "4": {"nome": "Televisão", "categoria": "Entretenimento", "potencia": 100},
            "5": {"nome": "Lâmpada LED", "categoria": "Iluminação", "potencia": 10},
            "6": {"nome": "Micro-ondas", "categoria": "Cozinha", "potencia": 1200},
            "7": {"nome": "Notebook", "categoria": "Escritório", "potencia": 65}
        }
 
    def exibir_menu(base_dados):
        print("\n--- EQUIPAMENTOS DISPONÍVEIS ---")
        for chave, info in base_dados.items():
            print(f"[{chave}] {info['nome']} ({info['potencia']}W)")
 
    def executar_sistema():
        base_dados = obter_base_equipamentos()
       
        print("=== CADASTRO DO IMÓVEL ===")
        imovel = input("Digite o nome/identificação do imóvel: ")
       
        # 1. Usuário escolhe a quantidade de cômodos
        qtd_comodos = int(input("\nQuantos cômodos tem na casa? "))
       
        total_consumo_casa = 0
        relatorio_itens = []
 
        # Loop para percorrer cada cômodo escolhido pelo usuário
        for i in range(qtd_comodos):
            nome_comodo = input(f"\nDigite o nome do cômodo {i+1} (ex: Sala, Cozinha, Quarto): ")
           
            # 2. Usuário escolhe quantos equipamentos tem NESTE cômodo específico
            qtd_equipamentos = int(input(f"Quantos equipamentos tem no(a) {nome_comodo}? "))
 
            # Loop para cadastrar o que tem dentro do cômodo
            for j in range(qtd_equipamentos):
                print(f"\n-> Escolhendo o item {j+1} do(a) {nome_comodo}:")
                exibir_menu(base_dados)
               
                opcao = input("Selecione o número do equipamento: ")
               
                if opcao in base_dados:
                    equip = base_dados[opcao]
                   
                    # Usuário define as quantidades e tempo de uso do aparelho escolhido
                    qtd = int(input(f"Quantas unidades de '{equip['nome']}' tem nesse cômodo? "))
                    horas = float(input(f"Quantas horas por dia cada um fica ligado? "))
                   
                    # Cálculo do consumo mensal (Watts * Qtd * Horas * 30 dias / 1000)
                    consumo_mes = (equip['potencia'] * qtd * horas * 30) / 1000
                    total_consumo_casa += consumo_mes
                   
                    # Guarda as escolhas do usuário para o relatório
                    relatorio_itens.append({
                        "comodo": nome_comodo,
                        "nome": equip['nome'],
                        "qtd": qtd,
                        "consumo": consumo_mes
                    })
                else:
                    print("Opção inválida! Item desconsiderado.")
 
        # --- RELATÓRIO FINAL ---
        print(f"\n==================================================")
        print(f"RESUMO DE CONSUMO - {imovel.upper()}")
        print(f"==================================================")
        print(f"{'Cômodo':<15} | {'Equipamento':<18} | {'Qtd':<4} | {'Consumo Mensal'}")
        print("-" * 60)
       
        for item in relatorio_itens:
            print(f"{item['comodo']:<15} | {item['nome']:<18} | {item['qtd']:<4} | {item['consumo']:.2f} kWh/mês")
           
        print("-" * 60)
        print(f"CONSUMO TOTAL DA RESIDÊNCIA: {total_consumo_casa:.2f} kWh/mês")
        print(f"==================================================")
 
    if __name__ == "__main__":
        executar_sistema()
 
        cadastro = int(input("Deseja cadastrar outro imóvel? Qualquer número = Sim / 2 = Não" ))
 
        if cadastro == 2:
            print("Muito obrigado, finalizando sistema...")
            break