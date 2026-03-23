"""
================================================================
database_ops.py — Operacoes com Azure Database for MySQL
================================================================
Este modulo gerencia a conexao com o banco de dados MySQL gerenciado
no Azure e fornece a funcao de consulta a tabela 'produtos'.

Dependencias:
  - mysql-connector-python (conector oficial MySQL para Python)
  - python-dotenv (para carregar variaveis de ambiente do .env)

Configuracao necessaria (.env):
  - DB_HOST: endereco do servidor MySQL (ex: servidor.mysql.database.azure.com)
  - DB_PORT: porta do MySQL (padrao: 3306)
  - DB_NAME: nome do banco de dados (ex: app_projeto)
  - DB_USER: usuario do banco
  - DB_PASSWORD: senha do usuario

Seguranca:
  - A conexao utiliza SSL (ssl_disabled=False) para criptografar o trafego
    entre a aplicacao e o banco de dados na nuvem.
  - As credenciais sao lidas exclusivamente de variaveis de ambiente.
================================================================
"""

# --- Imports necessarios ---

# 'os' para acessar variaveis de ambiente
import os

# 'mysql.connector' e o conector oficial do MySQL para Python.
# Permite abrir conexoes, executar queries e obter resultados.
import mysql.connector

# 'dotenv' carrega variaveis do arquivo .env para o ambiente
from dotenv import load_dotenv

# Carrega as variaveis do .env para que os.getenv() funcione corretamente
load_dotenv()

# --- Leitura das variaveis de ambiente do banco de dados ---

# Host: endereco FQDN do servidor MySQL no Azure
# Formato tipico: nome-do-servidor.mysql.database.azure.com
DB_HOST = os.getenv("DB_HOST")

# Porta: padrao do MySQL e 3306. Convertido para int pois o conector exige numero.
DB_PORT = int(os.getenv("DB_PORT", "3306"))

# Nome do banco de dados que contem a tabela 'produtos'
DB_NAME = os.getenv("DB_NAME")

# Usuario administrador do banco (criado durante o provisionamento)
DB_USER = os.getenv("DB_USER")

# Senha do usuario (NUNCA hardcoded no codigo — sempre via .env)
DB_PASSWORD = os.getenv("DB_PASSWORD")


def _obter_conexao():
    """
    Funcao auxiliar (privada) que cria e retorna uma conexao com o MySQL.

    Utiliza os parametros lidos das variaveis de ambiente para estabelecer
    uma conexao TCP com o servidor MySQL no Azure.

    Parametros de conexao:
      - host: endereco do servidor
      - port: porta TCP (3306)
      - database: nome do banco
      - user: usuario
      - password: senha
      - ssl_disabled: False (forca uso de SSL para seguranca)
      - connection_timeout: 10 segundos (evita travar se o servidor nao responder)

    Raises:
        ValueError: Se variaveis de ambiente nao estiverem configuradas.
        mysql.connector.Error: Se a conexao falhar (credenciais, rede, firewall).

    Returns:
        mysql.connector.connection.MySQLConnection: objeto de conexao ativo.
    """
    # Valida se todas as variaveis necessarias foram definidas
    if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
        raise ValueError(
            "Uma ou mais variaveis de banco de dados nao estao definidas no .env. "
            "Verifique: DB_HOST, DB_NAME, DB_USER, DB_PASSWORD"
        )

    # mysql.connector.connect() abre uma conexao TCP com o servidor MySQL.
    # Os parametros sao passados como keyword arguments para clareza.
    conexao = mysql.connector.connect(
        host=DB_HOST,              # Endereco do servidor Azure MySQL
        port=DB_PORT,              # Porta TCP (3306)
        database=DB_NAME,          # Banco de dados a ser utilizado
        user=DB_USER,              # Usuario de autenticacao
        password=DB_PASSWORD,      # Senha (vinda do .env, nunca hardcoded)
        ssl_disabled=False,        # SSL habilitado (obrigatorio no Azure)
        connection_timeout=10      # Timeout de 10s para evitar bloqueio
    )

    return conexao


def consultar_produtos() -> list:
    """
    Conecta ao MySQL e retorna todos os registros da tabela 'produtos'.

    Fluxo:
        1. Abre uma conexao com o banco via _obter_conexao().
        2. Cria um cursor (objeto que permite executar queries SQL).
        3. Executa SELECT * na tabela 'produtos' ordenando por ID.
        4. Obtem todas as linhas do resultado (fetchall).
        5. Obtem os nomes das colunas a partir do cursor.description.
        6. Monta uma lista de dicionarios (chave=coluna, valor=dado).
        7. Fecha cursor e conexao para liberar recursos.
        8. Retorna a lista de dicionarios.

    Por que usar dicionarios?
        Porque facilita a exibicao no terminal com tabulate e permite
        acessar campos pelo nome (ex: registro['nome']) em vez de indice.

    Raises:
        mysql.connector.Error: Se a query falhar ou a tabela nao existir.

    Returns:
        list[dict]: lista de registros, cada um como dicionario.
                    Exemplo: [{'id': 1, 'nome': 'Notebook', 'preco': 5499.90}, ...]
    """
    # Variaveis inicializadas como None para o bloco finally
    conexao = None
    cursor = None

    try:
        # Passo 1: Estabelece conexao com o banco MySQL no Azure
        conexao = _obter_conexao()

        # Passo 2: Cria um cursor — e atraves dele que enviamos SQL ao banco.
        # O cursor mantem o estado da query (resultados, posicao, metadados).
        cursor = conexao.cursor()

        # Passo 3: Executa a query SELECT.
        # 'ORDER BY id' garante que os registros venham na ordem de insercao.
        # Usar SELECT * retorna todas as colunas da tabela.
        cursor.execute("SELECT * FROM produtos ORDER BY id")

        # Passo 4: fetchall() busca TODAS as linhas do resultado de uma vez.
        # Cada linha e retornada como uma tupla — ex: (1, 'Notebook', ..., datetime)
        linhas = cursor.fetchall()

        # Passo 5: cursor.description contem metadados das colunas retornadas.
        # Cada item e uma tupla onde o indice [0] e o nome da coluna.
        # Exemplo: [('id',), ('nome',), ('descricao',), ...]
        colunas = [desc[0] for desc in cursor.description]

        # Passo 6: Monta a lista de dicionarios usando zip().
        # zip(colunas, linha) emparelha cada nome de coluna com seu valor.
        # dict() converte os pares em dicionario.
        # Exemplo: dict(zip(['id','nome'], (1,'Notebook'))) resulta em {'id':1, 'nome':'Notebook'}
        resultados = [dict(zip(colunas, linha)) for linha in linhas]

        return resultados

    finally:
        # Passo 7: Bloco finally garante que cursor e conexao sao fechados
        # mesmo se ocorrer uma excecao durante a execucao da query.
        # Isso evita "vazamento" de conexoes (connection leak).
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()