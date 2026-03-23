"""
================================================================
storage_ops.py — Operacoes com Azure Blob Storage
================================================================
Este modulo encapsula as tres operacoes exigidas para o storage:
  1. upload_arquivo()  — envia um arquivo local para o container
  2. deletar_arquivo() — remove um blob do container
  3. listar_arquivos() — lista todos os blobs do container

Dependencias:
  - azure-storage-blob (SDK oficial da Microsoft para Python)
  - python-dotenv (para carregar variaveis de ambiente do .env)

Configuracao necessaria (.env):
  - AZURE_STORAGE_CONNECTION_STRING: string de conexao da Storage Account
  - AZURE_CONTAINER_NAME: nome do container (ex: 'arquivos')
================================================================
"""

# --- Imports necessarios ---

# 'os' e usado para manipular caminhos de arquivos (extrair nome do arquivo)
import os

# 'BlobServiceClient' e a classe principal do SDK que gerencia a conexao
# com a conta de armazenamento e permite acessar containers e blobs
from azure.storage.blob import BlobServiceClient

# 'dotenv' carrega as variaveis do arquivo .env para o ambiente do processo,
# permitindo acessa-las via os.environ ou os.getenv sem expor credenciais no codigo
from dotenv import load_dotenv

# Carrega as variaveis de ambiente do arquivo .env localizado na raiz do projeto.
# Isso deve ser chamado antes de qualquer os.getenv() para garantir que as
# variaveis estejam disponiveis.
load_dotenv()

# --- Leitura das variaveis de ambiente ---

# Busca a connection string da Storage Account. Essa string contem o nome da conta,
# a chave de acesso e o protocolo — tudo necessario para autenticar no Azure.
AZURE_CONN_STR = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

# Nome do container onde os arquivos (blobs) serao armazenados.
# Um container e analogo a uma "pasta raiz" dentro da Storage Account.
AZURE_CONTAINER = os.getenv("AZURE_CONTAINER_NAME")


def _obter_container_client():
    """
    Funcao auxiliar (privada) que cria e retorna um ContainerClient.

    O ContainerClient e o objeto do SDK que permite interagir diretamente
    com um container especifico — fazer upload, deletar, listar blobs, etc.

    Fluxo:
      1. Cria um BlobServiceClient usando a connection string
         (autentica na Storage Account).
      2. A partir dele, obtem um ContainerClient para o container desejado.

    Raises:
        ValueError: Se as variaveis de ambiente nao estiverem configuradas.
        Exception: Se a conexao com o Azure falhar.

    Returns:
        ContainerClient: objeto pronto para operacoes no container.
    """
    # Valida se as variaveis de ambiente foram carregadas corretamente
    if not AZURE_CONN_STR or not AZURE_CONTAINER:
        raise ValueError(
            "Variaveis AZURE_STORAGE_CONNECTION_STRING e/ou "
            "AZURE_CONTAINER_NAME nao definidas no .env"
        )

    # Cria o client do servico de blobs usando a connection string.
    # Internamente, ele faz o parsing da string para extrair AccountName,
    # AccountKey e endpoint.
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONN_STR)

    # Retorna um client especifico para o container configurado.
    # Todas as operacoes subsequentes (upload, delete, list) usarao este client.
    container_client = blob_service_client.get_container_client(AZURE_CONTAINER)

    return container_client


def upload_arquivo(caminho_arquivo: str) -> str:
    """
    Faz o upload de um arquivo local para o container no Azure Blob Storage.

    Parametros:
        caminho_arquivo (str): caminho completo ou relativo do arquivo no disco local.
                               Exemplo: 'test_files/documento.pdf'

    Fluxo:
        1. Obtem o ContainerClient (autenticado).
        2. Extrai apenas o nome do arquivo do caminho (ex: 'documento.pdf').
        3. Abre o arquivo em modo binario ('rb') para leitura.
        4. Chama upload_blob() que envia os bytes para o Azure.
           - overwrite=True: se ja existir um blob com o mesmo nome, substitui.
        5. Retorna o nome do blob criado.

    Raises:
        FileNotFoundError: Se o arquivo local nao for encontrado.
        Exception: Se o upload falhar (rede, permissao, etc.).

    Returns:
        str: nome do blob (arquivo) criado no container.
    """
    # Obtem o client autenticado para o container
    container_client = _obter_container_client()

    # os.path.basename extrai o nome do arquivo de um caminho.
    # Exemplo: '/home/user/docs/foto.png' resulta em 'foto.png'
    # Isso e importante porque no blob storage o "nome" do blob e o identificador.
    nome_blob = os.path.basename(caminho_arquivo)

    # Abre o arquivo em modo binario de leitura.
    # 'rb' = read binary — necessario para enviar qualquer tipo de arquivo
    # (imagem, PDF, texto) sem corromper os dados.
    with open(caminho_arquivo, "rb") as dados:
        # upload_blob() envia o conteudo do arquivo para o Azure.
        # - name: nome que o blob tera no container
        # - data: objeto file-like com os bytes do arquivo
        # - overwrite: True permite sobrescrever se ja existir
        container_client.upload_blob(
            name=nome_blob,
            data=dados,
            overwrite=True
        )

    # Retorna o nome para que o chamador saiba qual blob foi criado
    return nome_blob


def deletar_arquivo(nome_blob: str) -> None:
    """
    Remove (deleta) um blob especifico do container no Azure Blob Storage.

    Parametros:
        nome_blob (str): nome exato do blob a ser excluido.
                         Exemplo: 'documento.pdf'

    Fluxo:
        1. Obtem o ContainerClient (autenticado).
        2. Chama delete_blob() com o nome do blob.
        3. Se o blob nao existir, o Azure retorna um erro 404 (tratado pelo chamador).

    Raises:
        ResourceNotFoundError: Se o blob nao existir no container.
        Exception: Se a exclusao falhar por outro motivo.
    """
    # Obtem o client autenticado para o container
    container_client = _obter_container_client()

    # delete_blob() envia uma requisicao DELETE para o Azure.
    # O blob e removido permanentemente (a menos que soft-delete esteja habilitado).
    container_client.delete_blob(nome_blob)


def listar_arquivos() -> list:
    """
    Lista todos os blobs (arquivos) presentes no container.

    Retorna uma lista de dicionarios contendo informacoes de cada blob:
      - nome: nome do arquivo
      - tamanho: tamanho em bytes
      - ultima_modificacao: data/hora da ultima modificacao

    Fluxo:
        1. Obtem o ContainerClient (autenticado).
        2. Chama list_blobs() que retorna um iteravel com os metadados de cada blob.
        3. Para cada blob, extrai nome, tamanho e data de modificacao.
        4. Retorna a lista completa.

    Returns:
        list[dict]: lista de dicionarios com informacoes dos blobs.
                    Retorna lista vazia se o container estiver vazio.
    """
    # Obtem o client autenticado para o container
    container_client = _obter_container_client()

    # list_blobs() retorna um iteravel (ItemPaged) com objetos BlobProperties.
    # Cada objeto contem metadados do blob: nome, tamanho, content_type, etc.
    blobs = container_client.list_blobs()

    # Monta uma lista de dicionarios com as informacoes mais relevantes
    lista = []
    for blob in blobs:
        lista.append({
            "nome": blob.name,                            # Nome do arquivo
            "tamanho": blob.size,                          # Tamanho em bytes
            "ultima_modificacao": str(blob.last_modified)  # Convertido para string
        })

    return lista