**MIRAVEC**  

· Grupo 1 · CESAR School

## 1. Pergunta de Negócio, Público e Critério de Sucesso

### Pergunta de negócio que o grupo quer responder

Como transformar automaticamente os dados semanais de Ovitrampas (OVTs) e Estações Disseminadoras de Larvicida (EDLS) da GEVACZ, atualmente analisados de forma manual em planilhas Excel,em informação operacional que indique, de forma rápida e sem precisar de manutenção manual, quais regiões exigem intervenção prioritária no combate ao Aedes aegypti.

### Público e uso pretendido da resposta

O público-alvo principal são os agentes e gestores da GEVACZ (Gerência de Vigilância Ambiental e Controle de Zoonoses) do Recife, que precisam decidir semanalmente onde alocar recursos de controle vetorial, como a instalação de novas EDLS ou inspeção emergencial de focos. O relatório gerado pela pipeline serve como matéria prima para essa tomada de decisão, eliminando a etapa de análise manual em Excel.

### Critério de sucesso do projeto

- A pipeline processa os arquivos Excel de entrada e gera o relatório de KPIs.
- O relatório HTML gerado apresenta corretamente o ranking de zonas por nível de risco (Crítico, Alto, Médio, Baixo) e as recomendações de intervenção da semana.
- O código está versionado no GitHub com histórico de commits organizado e README explicativo.
- O produto é demonstrado ao vivo para o professor com dados reais ou simulados, mostrando a geração automática do relatório a partir do upload de uma planilha.

## 2. Levantamento dos Dados — API IBGE SIDRA

### Agregados e variáveis do IBGE explorados

O grupo realizou integração com a API pública do IBGE SIDRA (Sistema IBGE de Recuperação Automática), disponível em servicodados.ibge.gov.br. Foram explorados os seguintes recursos:

**Agregado:** 4093 — Notificações de doenças de notificação compulsória (inclui dengue)

**Variável:** 4099 — Número de casos confirmados

**Localidade:** N3[26] — Estado de Pernambuco (nível estadual, código 26)

**Período:** 2012T1 a 2026T2 (série trimestral completa desde 2012)

A função montar_periodos() do código gera automaticamente a sequência de trimestres no formato aceito pela API (ex.: 201201|201202|...|202602), e a função consultar_agregado() monta a URL de requisição com suporte a filtros de classificação e localidade.

### Granularidade disponível

**Geográfica:** Nível estadual (N3) Pernambuco como unidade de análise. A API permite refinar para nível municipal (N6) em consultas futuras.

**Temporal:** Trimestral, quatro períodos por ano (T1 a T4). A série cobre 14 anos de histórico, de 2012 a 2026, totalizando aproximadamente 58 trimestres.

### Problemas de qualidade identificados

- Valores ausentes: alguns períodos mais recentes (2025–2026) podem retornar valores nulos ou com preenchimento parcial, pois os dados de notificação compulsória têm defasagem de publicação.
- Cobertura incompleta: a granularidade estadual agrega todos os municípios de Pernambuco, o que dilui variações locais relevantes para o projeto, como diferenças entre bairros do Recife.
- Inconsistências de formato: a API retorna os valores como strings, é necessário converter para numérico antes de qualquer cálculo, tratando os casos em que o valor é '...' (dado não disponível) ou '-' (zero).
- Limitação de classificações: o agregado 4093 agrega múltiplas doenças. É necessário aplicar o filtro de classificação correto para isolar apenas os casos de dengue.

## 3. Tratamentos Necessários

Com base na exploração inicial da API e nas características do projeto, os seguintes tratamentos serão aplicados nos dados brutos antes de alimentar a pipeline:

- Conversão de tipos: todos os valores de contagem de casos serão convertidos de string para inteiro, com tratamento de exceção para os tokens especiais '...', '-' e valores em branco.
- Filtragem de doença: aplicar o filtro de classificação para restringir os resultados apenas a dengue, excluindo outras doenças de notificação presentes no agregado.
- Tratamento de nulos: períodos sem dado disponível receberão o valor 0 ou serão excluídos da análise de tendência, dependendo da posição na série temporal.
- Agregação temporal: os dados trimestrais serão convertidos para uma série anual quando necessário para visualização de tendências de longo prazo.
- Junção com dados da GEVACZ: os dados do IBGE (contexto epidemiológico de Pernambuco) serão utilizados como dado de referência externo para contextualizar os índices das OVTs e EDLS locais.

## 4. Formato Final dos Dados

Após o processamento, os dados devem assumir o seguinte esquema de tabela para alimentar a pipeline de análise:

| **Coluna** | **Tipo** | **Descrição** |
| --- | --- | --- |
| periodo | string | Trimestre no formato YYYYTT (ex: 202301) |
| ano | inteiro | Ano de referência (ex: 2023) |
| trimestre | inteiro | Trimestre de referência (1 a 4) |
| casos_dengue | inteiro | Número de casos confirmados de dengue em PE |
| localidade | string | Nome da localidade (ex: Pernambuco) |
| fonte | string | Origem do dado (ex: IBGE SIDRA – Agregado 4093) |

## 5. Critérios para Dados Considerados "Prontos"

Os dados serão considerados prontos para alimentar a pipeline quando atenderem a todos os critérios abaixo:

- Ausência de valores nulos na coluna casos_dengue — toda linha deve ter um número inteiro válido (mínimo: 0).
- Cobertura temporal contínua: nenhum trimestre faltando dentro do intervalo definido para análise.
- Tipos corretos: colunas numéricas como inteiro, colunas textuais como string — verificado via validação automática no início da pipeline.
- Formato de período padronizado: todos no formato YYYYTT sem variação.
- Arquivo salvo como .xlsx ou .csv na pasta dados/ do repositório, com nome padronizado (ibge_dengue_pe.xlsx).

## 6. Recorrência da Pipeline e Versionamento

### Como a pipeline roda de forma recorrente

A pipeline foi projetada para ser executada manualmente toda semana, após a coleta de dados das OVTs e EDLS pela GEVACZ. O fluxo de execução é:

- O operador coloca os arquivos Excel atualizados (ovts.xlsx e edls.xlsx) na pasta dados/ do projeto.
- Executa o comando python main.py no terminal dentro da pasta do projeto.
- A pipeline lê os arquivos, processa os dados, calcula os scores de risco e gera o relatório HTML automaticamente na pasta saida/.
- O relatório abre automaticamente no navegador, pronto para ser usado na tomada de decisão semanal.

Em versões futuras do projeto, a recorrência poderá ser automatizada via GitHub Actions, que executaria a pipeline toda semana em uma data e hora programadas, sem necessidade de intervenção manual.

### Como o código será versionado

O código está hospedado no GitHub no repositório do Grupo 1. O fluxo de versionamento adotado pelo grupo é:

- Cada funcionalidade nova ou correção é feita em um branch separado e integrada via Pull Request ao branch main.
- As mensagens de commit seguem o padrão: feat: para novas funcionalidades, fix: para correções e docs: para atualizações de documentação.
- Este documento fica dentro do diretório docs/ do repositório, conforme especificado pelo professor.
- O arquivo requirements.txt na raiz do repositório lista todas as dependências (pandas, openpyxl, requests) para garantir que qualquer membro do grupo consiga rodar o projeto com um único comando: pip install -r requirements.txt.
