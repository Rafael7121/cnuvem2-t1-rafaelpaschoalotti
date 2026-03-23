"""
================================================================
main.py — Aplicacao principal (ponto de entrada)
================================================================
Aluno: Rafael Paschoalotti
Disciplina: Computacao em Nuvem II (ISW035)

Este e o arquivo principal da aplicacao. Ele apresenta um menu
interativo no terminal que permite ao usuario executar as quatro
operacoes exigidas pela atividade:

  1. Upload de arquivo para o Azure Blob Storage
  2. Exclusao de arquivo do Azure Blob Storage
  3. Listagem de arquivos no Azure Blob Storage
  4. Consulta de dados no Azure Database for MySQL

O codigo utiliza os modulos storage_ops e database_ops para
separar responsabilidades (cada modulo cuida de um servico).

Execucao:
  python src/main.py

Pre-requisitos:
  - Arquivo .env configurado com credenciais validas
  - Dependencias instaladas (pip install -r requirements.txt)
  - Servidor MySQL acessivel (firewall liberado para seu IP)
  - Container no Blob Storage criado
================================================================
"""

# --- Imports do sistema ---

# 'sys' e usado para encerrar o programa de forma limpa com sys.exit()
import sys

# 'os' e usado para verificar existencia de arquivos (os.path.exists)
import os

# --- Imports de terceiros ---

# 'tabulate' formata listas/dicionarios como tabelas no terminal.
# Exemplo de saida:
#   | id | nome           | preco   |
#   |----|----------------|---------|
#   | 1  | Notebook Gamer | 5499.90 |
from tabulate import tabulate

# --- Imports dos modulos locais do projeto ---

# Importa as funcoes de operacao com Azure Blob Storage
# (upload, delete, listagem) definidas no modulo storage_ops.py
from storage_ops import upload_arquivo, deletar_arquivo, listar_arquivos

# Importa a funcao de consulta ao MySQL
# definida no modulo database_ops.py
from database_ops import consultar_produtos


def exibir_menu():
    """
    Exibe o menu principal no terminal com as opcoes disponiveis.

    Nao recebe parametros nem retorna valores — apenas imprime na tela.
    O menu e exibido repetidamente pelo loop principal em main().
    """
    print("\n" + "=" * 60)
    print("  ATIVIDADE 4.1 — ARMAZENAMENTO EM NUVEM")
    print("  Computacao em Nuvem II (ISW035) — FATEC Jahu")
    print("  Aluno: Rafael Paschoalotti")
    print("=" * 60)
    print("  [1] Upload de arquivo para o Blob Storage")
    print("  [2] Excluir arquivo do Blob Storage")
    print("  [3] Listar arquivos no Blob Storage")
    print("  [4] Consultar dados no MySQL")
    print("  [0] Sair")
    print("=" * 60)


def opcao_upload():
    """
    Trata a opcao 1 do menu: upload de arquivo para o Blob Storage.

    Fluxo:
      1. Solicita ao usuario o caminho do arquivo no disco local.
      2. Verifica se o arquivo existe (os.path.exists).
      3. Chama upload_arquivo() do modulo storage_ops.
      4. Exibe mensagem de sucesso ou erro.

    Tratamento de erros:
      - FileNotFoundError: arquivo nao encontrado no caminho informado
      - Exception generica: qualquer outro erro (rede, permissao Azure, etc.)
    """
    print("\n--- UPLOAD DE ARQUIVO ---")

    # Solicita o caminho do arquivo. strip() remove espacos em branco
    # acidentais no inicio e fim da entrada do usuario.
    caminho = input("Caminho do arquivo local: ").strip()

    # Verifica se o arquivo existe antes de tentar enviar,
    # evitando uma chamada desnecessaria ao Azure.
    if not os.path.exists(caminho):
        print("ERRO: Arquivo '{}' nao encontrado no disco local.".format(caminho))
        return

    try:
        # Chama a funcao de upload que envia o arquivo para o Azure.
        # Retorna o nome do blob criado no container.
        nome_blob = upload_arquivo(caminho)
        print("SUCESSO: Arquivo '{}' enviado para o container.".format(nome_blob))

    except Exception as erro:
        # Captura qualquer excecao e exibe a mensagem de erro.
        # Isso inclui erros de rede, autenticacao, permissao, etc.
        print("ERRO ao fazer upload: {}".format(erro))


def opcao_deletar():
    """
    Trata a opcao 2 do menu: exclusao de arquivo do Blob Storage.

    Fluxo:
      1. Solicita ao usuario o nome exato do blob a ser excluido.
      2. Pede confirmacao antes de deletar (operacao irreversivel).
      3. Chama deletar_arquivo() do modulo storage_ops.
      4. Exibe mensagem de sucesso ou erro.

    Tratamento de erros:
      - Exception: blob nao encontrado, erro de rede, etc.
    """
    print("\n--- EXCLUSAO DE ARQUIVO ---")

    # Solicita o nome do blob (deve ser o nome exato como aparece na listagem)
    nome = input("Nome do arquivo (blob) a excluir: ").strip()

    # Validacao simples: nome nao pode estar vazio
    if not nome:
        print("ERRO: Nome do arquivo nao pode ser vazio.")
        return

    # Confirmacao de seguranca — exclusao e permanente
    # (a menos que soft-delete esteja habilitado na Storage Account)
    confirmacao = input("Tem certeza que deseja excluir '{}'? (s/n): ".format(nome)).strip().lower()

    if confirmacao != "s":
        print("Operacao cancelada pelo usuario.")
        return

    try:
        # Chama a funcao de exclusao
        deletar_arquivo(nome)
        print("SUCESSO: Arquivo '{}' excluido do container.".format(nome))

    except Exception as erro:
        # Trata erros como blob nao encontrado (404) ou falha de rede
        print("ERRO ao excluir arquivo: {}".format(erro))


def opcao_listar():
    """
    Trata a opcao 3 do menu: listagem de arquivos no Blob Storage.

    Fluxo:
      1. Chama listar_arquivos() que retorna lista de dicionarios.
      2. Se a lista estiver vazia, informa que o container esta vazio.
      3. Caso contrario, formata os dados como tabela usando tabulate.

    Tratamento de erros:
      - Exception: falha de conexao, container nao encontrado, etc.
    """
    print("\n--- LISTAGEM DE ARQUIVOS ---")

    try:
        # Obtem a lista de blobs do container
        arquivos = listar_arquivos()

        # Verifica se ha arquivos no container
        if not arquivos:
            print("INFO: O container esta vazio — nenhum arquivo encontrado.")
            return

        # Exibe a quantidade total de arquivos encontrados
        print("{} arquivo(s) encontrado(s):\n".format(len(arquivos)))

        # tabulate() formata a lista de dicionarios como uma tabela ASCII.
        # - headers="keys": usa as chaves dos dicionarios como cabecalho
        # - tablefmt="grid": formato com bordas e linhas divisorias
        print(tabulate(arquivos, headers="keys", tablefmt="grid"))

    except Exception as erro:
        print("ERRO ao listar arquivos: {}".format(erro))


def opcao_consultar_mysql():
    """
    Trata a opcao 4 do menu: consulta ao banco de dados MySQL.

    Fluxo:
      1. Chama consultar_produtos() que conecta ao MySQL e retorna os registros.
      2. Se nao houver registros, informa que a tabela esta vazia.
      3. Caso contrario, formata como tabela usando tabulate.

    Tratamento de erros:
      - Exception: falha de conexao, tabela nao encontrada, etc.
    """
    print("\n--- CONSULTA AO MYSQL ---")

    try:
        # Chama a funcao que conecta ao MySQL e executa SELECT * FROM produtos
        produtos = consultar_produtos()

        # Verifica se ha registros na tabela
        if not produtos:
            print("INFO: A tabela 'produtos' esta vazia — nenhum registro encontrado.")
            return

        # Exibe a quantidade de registros retornados
        print("{} registro(s) encontrado(s):\n".format(len(produtos)))

        # Formata e exibe como tabela.
        # Cada item de 'produtos' e um dicionario como:
        #   {'id': 1, 'nome': 'Notebook Gamer', 'preco': Decimal('5499.90'), ...}
        print(tabulate(produtos, headers="keys", tablefmt="grid"))

    except Exception as erro:
        print("ERRO ao consultar MySQL: {}".format(erro))


def main():
    """
    Funcao principal — ponto de entrada da aplicacao.

    Implementa um loop infinito que:
      1. Exibe o menu de opcoes.
      2. Le a escolha do usuario.
      3. Direciona para a funcao correspondente.
      4. Repete ate o usuario escolher '0' (sair).

    O loop usa if/elif (ao inves de match/case) para compatibilidade
    com Python 3.8 e 3.9 (match/case exige 3.10+).
    """
    print("\nIniciando aplicacao de integracao com Azure...")
    print("Certifique-se de que o arquivo .env esta configurado.\n")

    # Loop principal — mantem o programa rodando ate o usuario encerrar
    while True:
        # Exibe as opcoes disponiveis
        exibir_menu()

        # Le a opcao digitada pelo usuario
        # strip() remove espacos/quebras de linha acidentais
        opcao = input("\n  Escolha uma opcao: ").strip()

        # Direciona para a funcao correspondente com base na opcao
        if opcao == "1":
            opcao_upload()
        elif opcao == "2":
            opcao_deletar()
        elif opcao == "3":
            opcao_listar()
        elif opcao == "4":
            opcao_consultar_mysql()
        elif opcao == "0":
            # Encerra o programa de forma limpa
            print("\nEncerrando aplicacao. Ate a proxima!")
            sys.exit(0)
        else:
            # Opcao nao reconhecida — informa e volta ao menu
            print("Opcao invalida. Digite um numero de 0 a 4.")


# --- Ponto de entrada ---
# Este bloco garante que main() so e executada quando o arquivo e rodado
# diretamente (python src/main.py), e NAO quando e importado como modulo.
# Isso e uma convencao padrao do Python.
if __name__ == "__main__":
    main()