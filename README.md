# MicroChalangeSERS

Projeto desenvolvido em Python para dimensionamento energético residencial. O sistema permite cadastrar um imóvel, seus cômodos e equipamentos, calcular o consumo mensal de energia e estimar o custo mensal da residência com base no valor do kWh informado pelo usuário.

## Objetivo

O objetivo do projeto é organizar as informações de consumo de uma residência e realizar o cálculo mensal de energia de forma simples e estruturada.

O sistema calcula:

- o consumo mensal de cada equipamento;
- o consumo total mensal da residência;
- o custo mensal estimado de energia elétrica.

## Funcionalidades

- Cadastro e identificação do imóvel;
- Cadastro de múltiplos cômodos;
- Associação dos cômodos ao imóvel;
- Seleção de equipamentos a partir de uma base predefinida;
- Cadastro da quantidade de equipamentos;
- Cadastro das horas de uso diário;
- Validação de entradas numéricas;
- Rejeição de valores negativos ou iguais a zero;
- Cálculo do consumo mensal em kWh/mês;
- Cálculo do consumo total da residência;
- Entrada do valor do kWh;
- Cálculo do custo mensal estimado;
- Exibição de relatório final com os dados cadastrados.

## Cálculos utilizados

### Consumo mensal

```text
Consumo (kWh/mês) = Potência (W) × Quantidade × Horas/dia × 30 / 1000
```

### Custo mensal estimado

```text
Custo mensal (R$) = Consumo total (kWh/mês) × Valor do kWh
```

## Product Backlog

O desenvolvimento foi organizado a partir dos itens definidos no Product Backlog:

- PB01 - Imóvel;
- PB02 - Cômodo;
- PB04 - Consumo;
- PB06 - Relatório / Consumo Total;
- PB09 - Custo.

As Tasks correspondentes também estão identificadas no código por meio de comentários, facilitando a relação entre implementação e backlog.

## Kanban

O acompanhamento das atividades foi realizado por meio de um quadro Kanban no Trello:

[https://trello.com/b/fr7tB7n4/cp4-sers](https://trello.com/invite/b/6a9b655dfa817f09831ab595/ATTI2ab191a7edfa9e2a702690beb3710a150FE35865/cp5-sers)

## Estrutura do repositório

```text
MicroChalangeSERS/
├── micro_challenge.py
├── ficha_produto_backlog.pdf
├── Product_Backlog_Dimensionamento_Energetico_Residencial.pdf
└── README.md
```

## Tecnologias utilizadas

- Python 3
- Git
- GitHub
- Trello

O projeto utiliza apenas recursos nativos do Python e não depende de bibliotecas externas.

## Como executar

Clone o repositório:

```bash
git clone https://github.com/LeonardoTakachi/MicroChalangeSERS.git
```

Acesse a pasta do projeto:

```bash
cd MicroChalangeSERS
```

Execute o programa:

```bash
python micro_challenge.py
```

Caso necessário, utilize:

```bash
python3 micro_challenge.py
```

## Integrantes

- Daniel Vieira Santos - RM 573326
- Gustavo Bitencourt Lopes - RM 568885
- Giovane Salazar Fioravante - RM 570396
- Leonardo Basile Takachi - RM 569066
