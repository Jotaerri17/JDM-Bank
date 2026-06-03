# 🏦 JDM Bank - Sistema Bancário & Plataforma de Investimentos

O **JDM Bank** é um sistema bancário baseado em terminal desenvolvido em Python, integrado a um banco de dados relacional PostgreSQL hospedado na nuvem (Neon DB). Além das operações tradicionais de conta corrente, o projeto conta com um ecossistema completo de investimentos com cotações e taxas capturadas em tempo real via APIs externas.

---

## 🎯 Resumo do Projeto

O objetivo do projeto é simular o funcionamento interno de uma instituição financeira digital diretamente no terminal. O fluxo de dados conecta o usuário autenticado à sua carteira de ativos e ao seu extrato consolidado, persistindo todas as movimentações financeiras de forma segura no banco de dados.

### Principais Funcionalidades:
* **Autenticação Segura:** Cadastro de novos clientes com validação de maioridade e login via CPF e Senha.
* **Conta Corrente:** Realização de depósitos imediatos e transferências financeiras entre contas utilizando o e-mail cadastrado como chave principal.
* **Plataforma de Investimentos:**
  * **CDB Pós-Fixado:** Aplicações com rendimento atrelado à Taxa Selic Meta atualizada.
  * **Fundos Imobiliários (FII):** Simulação de investimentos em renda variável com foco em proventos ponderados (Dividend Yield).
  * **Bitcoin (BTC):** Compra e venda de frações de criptoativo baseadas no preço de mercado em tempo real.
* **Painel de Resgate/Venda:** Módulo inteligente que calcula lucros ou prejuízos antes da liquidação, comparando a cotação histórica da compra com o valor de mercado atualizado.

---

## 📚 Bibliotecas Utilizadas e Suas Funções

O projeto foi construído utilizando um conjunto de bibliotecas nativas e externas do Python para garantir performance, segurança e conectividade:

1. **`psycopg2`**
   * *O que faz:* É o adaptador de banco de dados PostgreSQL para o Python.
   * *Função no projeto:* Permite que o código execute comandos SQL (`Queries`, `Inserts`, `Updates`, `Deletes`) e gerencie transações (`commit`/`rollback`) diretamente na nuvem do Neon DB.
2. **`requests`**
   * *O que faz:* Envia requisições HTTP/HTTPS para servidores externos de forma simples.
   * *Função no projeto:* Utilizada para consumir dados externos (APIs) de finanças e economia, trazendo os preços do Bitcoin e as taxas do governo para dentro do sistema bancário.
3. **`python-dotenv`**
   * *O que faz:* Carrega variáveis de ambiente de um arquivo `.env` para o escopo do código.
   * *Função no projeto:* Garante a segurança das credenciais e strings de conexão com o banco de dados, evitando que senhas e URLs sensíveis do Neon DB fiquem expostas no código fonte.
4. **`datetime`** *(Nativa)*
   * *O que faz:* Manipulação e formatação de datas e horários.
   * *Função no projeto:* Registra o momento exato das movimentações e calcula o intervalo em dias entre a aplicação e o resgate para computar os juros compostos da renda fixa.
5. **`os` & `sys`** *(Nativas)*
   * *O que fazem:* Interação com o sistema operacional e controle do interpretador Python.
   * *Função no projeto:* Gerenciamento de caminhos de arquivos e encerramento limpo do terminal.

---

## 🌐 APIs Integradas

Para eliminar dados fictícios na área de investimentos, o sistema integra-se a duas grandes fontes de dados financeiras:

* **API do Banco Central do Brasil (SGS - Sistema Gerenciador de Séries Temporais):**
  * *Endpoint consumido:* Série `432` (Taxa Selic Meta definida pelo COPOM).
  * *Aplicação:* Captura o percentual oficial de juros da economia brasileira em tempo real no momento em que o usuário investe em CDB, travando a rentabilidade do ativo.
* **AwesomeAPI / Binance API:**
  * *Endpoint consumido:* Par de moedas `BTC-BRL`.
  * *Aplicação:* Coleta o preço *bid* (compra) do Bitcoin em Reais. Permite calcular a quantidade fracionada exata de cripto que o usuário adquire com seu saldo corrente e recalcular o valor de venda com base na oscilação de mercado.

---

## 🏗️ Estrutura do Banco de Dados (PostgreSQL)

O banco é composto por 4 tabelas altamente amarradas através de chaves estrangeiras (`FOREIGN KEY`):

* `usuarios`: Guarda os dados cadastrais (Nome, CPF, Senha, E-mail, Telefone) e o saldo atual da conta corrente.
* `movimentacoes`: O extrato consolidado do usuário, salvando o tipo de operação (DEPOSITO, TRANSFERENCIA, INVESTIMENTO, RESGATE) e o valor movimentado.
* `tipos_investimento`: Catálogo fixo de produtos financeiros disponíveis no banco.
* `investimentos_usuarios`: A carteira individual do cliente, vinculando o ID do usuário ao produto adquirido, o valor investido, a taxa/cotação travada no dia da compra e o carimbo de data.

---

## 🚀 Como Executar o Projeto

1. Certifique-se de que possui as dependências instaladas no seu ambiente virtual:
   ```bash
   pip install psycopg2-binary requests python-dotenv