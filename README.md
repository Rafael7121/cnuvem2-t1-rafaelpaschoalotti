# Atividade 4.1 — Armazenamento de Dados em Nuvem

## Identificacao

| Campo          | Valor                                    |
|----------------|------------------------------------------|
| **Aluno**      | Rafael Paschoalotti                      |
| **Disciplina** | Computacao em Nuvem II (ISW035)          |
| **Semestre**   | 2025/1                                   |
| **Professor**  | Ronan Adriel Zenatti                     |
| **Instituicao**| FATEC Jahu — Centro Paula Souza          |

---

## Descricao do Projeto

Esta aplicacao em **Python** demonstra a integracao com dois servicos gerenciados
na **Microsoft Azure**:

1. **Azure Blob Storage** — upload, exclusao e listagem de arquivos em um container.
2. **Azure Database for MySQL (Servidor Flexivel)** — conexao e consulta a uma tabela
   com dados pre-inseridos.

O programa apresenta um menu interativo no terminal que permite ao usuario executar
cada operacao individualmente e verificar os resultados em tempo real.

---

## Plataforma Escolhida

**Microsoft Azure** — escolhida por oferecer creditos gratuitos via Azure for Students
(US$ 100) sem necessidade de cartao de credito, alem de possuir ampla documentacao
em portugues e integracao nativa entre seus servicos.

---

## Servicos Utilizados

| Servico | Configuracao |
|---------|-------------|
| **Azure Blob Storage** | Account: `Standard LRS` (Locally Redundant), Tier: `Hot`, Regiao: `Brazil South` |
| **Azure Database for MySQL — Flexible Server** | SKU: `Standard_B1ms` (Burstable, 1 vCPU, 2 GB RAM), Versao: `8.0`, Regiao: `Brazil South` |
| **Resource Group** | `rg-cnuvem2-t1` (agrupa todos os recursos para facil gerenciamento e exclusao) |

---

## Como os Servicos Foram Configurados

### Storage Account + Container

```bash
# 1. Criar grupo de recursos
az group create \
  --name rg-cnuvem2-t1 \
  --location brazilsouth

# 2. Criar conta de armazenamento
az storage account create \
  --name stcnuvem2t1rafael \
  --resource-group rg-cnuvem2-t1 \
  --location brazilsouth \
  --sku Standard_LRS \
  --kind StorageV2 \
  --access-tier Hot

# 3. Criar container (acesso privado)
az storage container create \
  --name arquivos \
  --account-name stcnuvem2t1rafael \
  --auth-mode login

# 4. Obter connection string (guardar no .env)
az storage account show-connection-string \
  --name stcnuvem2t1rafael \
  --resource-group rg-cnuvem2-t1 \
  --output tsv
