# MicroChalangeSERS

Sistema em Python para **dimensionamento energético residencial**, desenvolvido para cadastrar imóveis, cômodos e equipamentos, calcular o consumo mensal de energia e estimar o custo mensal da residência.

## 🎯 Objetivo

O projeto tem como objetivo permitir que o usuário informe os equipamentos existentes em uma residência, a quantidade de unidades e o tempo médio de uso diário para calcular:

- consumo mensal de cada equipamento;
- consumo total mensal do imóvel;
- custo mensal estimado de energia elétrica.

## ⚙️ Funcionalidades

- Cadastro e identificação do imóvel;
- Cadastro de múltiplos cômodos;
- Associação dos cômodos ao imóvel;
- Seleção de equipamentos a partir de uma base predefinida;
- Cadastro da quantidade de equipamentos;
- Cadastro das horas de uso diário;
- Validação de entradas numéricas;
- Rejeição de valores negativos ou iguais a zero;
- Cálculo do consumo mensal em `kWh/mês`;
- Cálculo do consumo total da residência;
- Entrada do valor do kWh da conta de energia;
- Estimativa do custo mensal em reais (`R$`);
- Relatório final com os equipamentos cadastrados e seus respectivos consumos;
- Possibilidade de cadastrar mais de um imóvel durante a execução.

## 🧮 Cálculos utilizados

### Consumo mensal

O consumo mensal de cada equipamento é calculado pela fórmula:

```text
Consumo (kWh/mês) = Potência (W) × Quantidade × Horas/dia × 30 / 1000
```

### Custo mensal estimado

```text
Custo mensal (R$) = Consumo total (kWh/mês) × Valor do kWh
```

## 🗂️ Product Backlog

O desenvolvimento foi organizado com base nos seguintes itens do Product Backlog:

- **PB01 — Imóvel:** cadastro e validação da identificação do imóvel;
- **PB02 — Cômodo:** cadastro, validação e associação de múltiplos cômodos;
- **PB04 — Consumo:** entrada dos dados e cálculo do consumo mensal;
- **PB06 — Relatório / Consumo Total:** soma e apresentação do consumo total;
- **PB09 — Custo:** cálculo e apresentação do custo mensal estimado.

As Tasks do backlog também estão identificadas diretamente no código por comentários como:

```python
# PB01 - T02
# PB02 - T04
# PB04 - T05
# PB06 - T03
# PB09 - T04
```

## 📋 Kanban / Trello

O planejamento e acompanhamento das Tasks do projeto foram realizados por meio de um quadro Kanban no Trello.

🔗 **Trello — CP4 SERS:**  
https://trello.com/b/fr7tB7n4/cp4-sers

## 🗃️ Estrutura do repositório

```text
MicroChalangeSERS/
├── micro_challenge.py
├── ficha_produto_backlog.pdf
├── Product_Backlog_Dimensionamento_Energetico_Residencial.pdf
└── README.md
```

## 🛠️ Tecnologias utilizadas

- Python 3
- Git
- GitHub
- Trello

O projeto utiliza apenas recursos nativos do Python e não necessita de bibliotecas externas.

## ▶️ Como executar

### 1. Clone o repositório

```bash
git clone https://github.com/LeonardoTakachi/MicroChalangeSERS.git
```

### 2. Entre na pasta do projeto

```bash
cd MicroChalangeSERS
```

### 3. Execute o programa

```bash
python micro_challenge.py
```

Em alguns ambientes, pode ser necessário utilizar:

```bash
python3 micro_challenge.py
```

## 💡 Exemplo de funcionamento

Durante a execução, o sistema solicita informações como:

```text
Nome do imóvel: Casa Principal
Quantidade de cômodos: 2
Nome do cômodo: Sala
Equipamento: Televisão
Quantidade: 2
Horas de uso por dia: 5
Valor do kWh: R$ 0,95
```

Ao final, o programa apresenta um relatório com o consumo mensal dos equipamentos, o consumo total da residência e o custo mensal estimado.

## 📌 Status

Projeto desenvolvido e organizado de acordo com as Tasks definidas no Product Backlog e acompanhadas pelo quadro Kanban do Trello.
