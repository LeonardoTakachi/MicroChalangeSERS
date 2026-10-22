# Sistema de Dimensionamento Energético Residencial
 
Projeto desenvolvido em Python para dimensionamento energético residencial. O sistema permite cadastrar um imóvel, seus cômodos e equipamentos, calcular o consumo mensal de energia, dimensionar um sistema solar fotovoltaico (com ou sem baterias) e gerar uma proposta com orçamento, economia estimada e payback simples.
 
A partir da Sprint 4, o sistema conta com uma **interface web em Flask** que integra todo o fluxo, da residência cadastrada até a proposta ao cliente.

---

## Integrantes
 
- Daniel Vieira Santos - RM 573326
- Gustavo Bitencourt Lopes - RM 568885
- Giovane Salazar Fioravante - RM 570396
- Leonardo Basile Takachi - RM 569066

---

## Links
Interface: https://microchalangesers.onrender.com/

Kanban:
 
- CP4 e CP5: https://trello.com/b/fr7tB7n4/cp5-sers
- CP6: https://trello.com/b/S19KeIjw/cp6-sers

Video (Youtube): https://youtu.be/4nIQ_oryxPw

---
 
## Objetivo
 
O objetivo do projeto é organizar as informações de consumo de uma residência e, a partir delas, dimensionar a geração solar fotovoltaica de forma estruturada, usando datasets de equipamentos reais.
 
O sistema calcula:
 
- o consumo mensal de cada equipamento e o consumo total da residência;
- o custo mensal estimado de energia elétrica;
- a potência fotovoltaica necessária e a quantidade de módulos;
- a compatibilidade do inversor com o arranjo fotovoltaico;
- a geração estimada e o percentual do consumo atendido;
- o armazenamento necessário para uma autonomia desejada;
- o orçamento, a economia estimada e o payback simples.

---
  
## Funcionalidades
 
### CP4 e CP5:
 
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
- Exibição de relatório final com os dados cadastrados;
- Cálculo do custo mensal individual de cada equipamento;
- Remoção de equipamentos com confirmação e atualização do consumo;
- Ranking dos equipamentos por consumo;
- Identificação dos equipamentos de maior consumo;
- Recomendações de economia com simulação de redução de uso;
- Resumo do dimensionamento da residência;
- Catálogo de equipamentos fotovoltaicos por datasets;
- Validação da estrutura, quantidade, tipos, unidades, preços e fontes dos datasets.
  
### CP6
 
- Residências cadastradas salvas em JSON e reutilizadas, sem novo cadastro;
- Recurso solar com HSP (fonte registrada) e PR (justificativa obrigatória);
- Cálculo da potência fotovoltaica necessária (kWp) e da quantidade de módulos;
- Seleção de módulo e inversor nos datasets, com verificação de tensão, corrente, strings e razão DC/AC;
- Ranking das combinações por custo, excesso de potência e razão DC/AC, não apenas pelo menor preço;
- Estimativa de geração diária e mensal e percentual do consumo atendido;
- Distinção entre energia gerada e energia efetivamente compensada;
- Cenários com e sem baterias, com dimensionamento por autonomia;
- Orçamento item a item com preços lidos dos datasets;
- Comparação dos cenários, economia mensal e anual e payback simples;
- Proposta consolidada, com salvamento do projeto, reabertura e exportação em HTML;
- Validações com mensagens claras e tabela de diagnóstico quando nenhuma combinação é compatível;
- Interface web integrada, sem necessidade de editar código, datasets ou fazer cálculos externos.

---

## Cálculos utilizados
 
### Consumo mensal
 
```text
Consumo (kWh/mês) = Potência (W) × Quantidade × Horas/dia × 30 / 1000
```
 
### Custo mensal estimado
 
```text
Custo mensal (R$) = Consumo total (kWh/mês) × Valor do kWh
```
 
### Demanda e potência fotovoltaica
 
```text
E_dia  = E_mês / 30
P_FV   = E_dia / (HSP × PR)                 [kWp]
N_mod  = teto[(P_FV × 1000) / P_mod]
P_inst = (N_mod × P_mod) / 1000             [kWp]
```
 
### Inversor
 
```text
R_DC/AC = P_FV_instalada / P_inversor
```
 
Verificações realizadas para cada combinação de módulo e inversor:
 
- potência FV dentro do máximo aceito pelo inversor;
- `Voc` corrigido para 10 °C comparado com a tensão CC máxima, e `Vmp` dentro da faixa do MPPT;
- divisão dos módulos em strings dentro do tamanho mínimo e máximo da série e do número de entradas MPPT;
- `Isc` acima do limite do MPPT é sempre recusada. `Imp` até 10% acima do limite gera apenas aviso;
- razão DC/AC acima de 1,5 é recusada. Entre 0,3 e 0,8 o inversor passa com aviso de inversor folgado.
Quando apenas o arranjo de strings falha, o sistema pode somar até 6 módulos. O ajuste aparece na proposta como "calculado X, ajustado para Y".
 
### Geração e atendimento
 
```text
E_gerada,dia = P_inst × HSP × PR
E_gerada,mês = E_gerada,dia × 30
Atendimento (%) = E_gerada,mês / E_consumida,mês × 100
E_compensada = min(E_gerada,mês ; E_consumida,mês − custo de disponibilidade)
```
 
O custo de disponibilidade vem da fase do inversor (monofásico 30 kWh, bifásico 50 kWh, trifásico 100 kWh) e pode ser alterado na tela.
 
### Baterias
 
```text
E_aut = (E_dia / 24) × horas_autonomia × fração_da_carga
C_bat = E_aut / (DoD × η_bat)
N_bat = teto(C_bat / C_unidade)
```
 
No cenário com baterias, o inversor precisa ser híbrido e a bateria precisa ser compatível com ele. Opções acima do máximo de módulos em paralelo são descartadas.
 
### Orçamento, economia e payback
 
```text
Custo_item       = quantidade × preço_unitário
Custo_total      = soma dos Custo_item
Economia_mensal  = E_compensada × tarifa
Economia_anual   = Economia_mensal × 12
Payback simples  = Investimento / Economia_anual
```
 
Como a bateria não aumenta a energia compensada, a economia é a mesma nos dois cenários. A bateria aumenta o investimento e o payback, e o benefício é a autonomia em caso de queda de energia.

---
 
## Product Backlog
 
O desenvolvimento foi organizado a partir dos itens definidos no Product Backlog.
 
### CP4 e CP5
 
- PB01 - Imóvel;
- PB02 - Cômodo;
- PB04 - Consumo;
- PB06 - Relatório / Consumo Total;
- PB09 - Custo;
- PB10 – Custo por equipamento;
- PB11 - Resumo-Dimensionamento;
- PB14 – Identificação dos Equipamentos de Maior Consumo;
- PB18 – Recomendação de Economia;
- PB19 – Base de Equipamentos.
  
### CP6 (Product Backlog Final)
 
| PB | Descrição |
|---|---|
| PB01 | Recuperação da residência |
| PB02 | Recuperação da demanda energética |
| PB03 | Recurso solar (HSP e PR) |
| PB04 | Cálculo da potência fotovoltaica necessária |
| PB05 | Consulta ao dataset de módulos fotovoltaicos |
| PB06 | Dimensionamento dos módulos |
| PB07 | Seleção do inversor |
| PB08 | Estimativa da geração fotovoltaica |
| PB09 | Comparação geração × consumo |
| PB10 | Opção de sistema com ou sem baterias |
| PB11 | Dimensionamento das baterias |
| PB12 | Dataset de baterias |
| PB13 | Geração automática do orçamento |
| PB14 | Comparação dos cenários |
| PB15 | Estimativa de economia |
| PB16 | Payback simples |
| PB17 | Tela ou relatório consolidado |
| PB18 | Validação dos dados |
| PB19 | Interface integrada |
| PB20 | Persistência do projeto (desejável) |
| PB21 | Exportação da proposta (desejável) |
 
As Tasks correspondentes também estão identificadas no código por meio de comentários, facilitando a relação entre implementação e backlog. A numeração dos PBs da Sprint 3 é independente da numeração das Sprints 1 e 2.

---
  
## Interface web
 
O fluxo da aplicação segue as etapas abaixo:
 
| Etapa | Tela | O que acontece |
|---|---|---|
| 1 | Residência | Escolher uma residência cadastrada ou cadastrar uma nova |
| 2 | Recurso solar | Informar HSP (com fonte), PR (com justificativa), tarifa e custo de disponibilidade |
| 3 | Sistema FV | Ver o ranking de combinações módulo + inversor e escolher uma |
| 4 | Baterias | Definir autonomia e escolher a bateria |
| 5 | Proposta | Ver orçamento, comparativo, economia, payback e conclusão; salvar e baixar em HTML |
| - | Projetos salvos | Reabrir e baixar propostas anteriores |

---
 
## Estrutura do repositório
 
```text
MicroChalangeSERS/
├── CP4-5
│   ├── ficha_produto_backlog.pdf
│   ├── micro_challenge.py
├── CP6
│   ├── datasets
│       ├── baterias.csv
│       ├── inversores.csv
│       └── modulos.csv
│   ├── templates
│       ├── _macros.html
│       ├── base.html
│       ├── baterias.html
│       ├── projetos.html
│       ├── proposta.html
│       ├── residencia.html
│       ├── sistema.html
│       └── solar.html
│   ├── app.py
│   ├── micro_challenge.py
│   └── requirements.txt
├── datasets
│   ├── baterias.csv
│   ├── inversores.csv
│   └── modulos.csv
├── ficha_produto_backlog.pdf
├── Product_Backlog_Dimensionamento_Energetico_Residencial.pdf
└── README.md
```
 
- `micro_challenge.py`: motor de cálculo, validações, persistência e relatório. Também funciona sozinho, no terminal.
- `app.py`: rotas da interface web em Flask.
- `datasets/`: equipamentos e preços, separados da lógica de cálculo. Para atualizar um preço ou incluir um equipamento, basta editar o CSV.

---

## Tecnologias utilizadas
 
- Python 3
- Flask e Jinja2
- HTML e CSS
- CSV e JSON
- Git
- GitHub
- Trello

---

## Limitações
 
- O payback é simples: não considera juros, reajuste tarifário, degradação dos módulos, bandeiras tarifárias nem Fio B. Não é previsão financeira exata.
- HSP e PR são informados pelo usuário e devem ter fonte e justificativa (por exemplo, CRESESB/SunData).
- A economia assume compensação de créditos de energia.
- O orçamento cobre apenas módulos, inversor e baterias, sem instalação, projeto, proteções, cabeamento ou impostos.
- Os preços e as especificações dos datasets devem ser conferidos nas fontes registradas em cada CSV.

---
  
## Solução de problemas
 
| Problema | Causa provável | Solução |
|---|---|---|
| `TemplateNotFound` | A pasta `templates/` não está ao lado do `app.py` | Mantenha os arquivos `.html` dentro de `templates/` |
| "Não foi possível carregar os datasets" | CSVs ausentes ou fora do padrão | Confira a pasta `datasets/` e rode a opção 2 do terminal |
| "Nenhuma combinação compatível..." | Residência pequena para os inversores cadastrados ou dado trocado no CSV | Consulte a tabela de diagnóstico na tela do Sistema FV |

 ---
