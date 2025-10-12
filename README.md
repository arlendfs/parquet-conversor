# 📋 GUIA: Como Configurar o Tamanho Máximo de Upload

## 🎯 Visão Geral

Este conversor está configurado para aceitar arquivos de até **2048 MB (2 GB)** por padrão. Você pode alterar esse limite editando 3 arquivos.

---

## 📝 PASSO 1: Editar `app.py`

Abra o arquivo `app.py` e encontre as linhas **13-14**:

```python
# ⚙️ CONFIGURAÇÃO DE TAMANHO MÁXIMO DE UPLOAD
# Altere o valor abaixo para o tamanho máximo desejado em MB
MAX_UPLOAD_SIZE_MB = 2048  # 2GB (2048 MB)
```

### 🔧 Exemplos de valores:

| Tamanho Desejado | Valor a colocar |
|------------------|-----------------|
| 500 MB           | `500`           |
| 1 GB             | `1024`          |
| 2 GB             | `2048`          |
| 5 GB             | `5120`          |
| 10 GB            | `10240`         |

### ✏️ Como alterar:

**Para aceitar arquivos de até 5 GB, mude para:**
```python
MAX_UPLOAD_SIZE_MB = 5120  # 5GB (5120 MB)
```

---

## 📝 PASSO 2: Editar `.streamlit/config.toml`

Crie a pasta `.streamlit` (se não existir) e dentro dela crie o arquivo `config.toml`:

```bash
mkdir .streamlit
```

Edite o arquivo `.streamlit/config.toml` na **linha 3**:

```toml
[server]
# Tamanho máximo de upload em MB
maxUploadSize = 2048
```

### ✏️ Como alterar:

**Para 5 GB, mude para:**
```toml
maxUploadSize = 5120
```

---

## 📝 PASSO 3: Editar `render.yaml` (para deploy)

Se você vai fazer deploy no Render.com, edite o arquivo `render.yaml` em **2 lugares**:

### 📍 Local 1 - Linha 8 (comando de inicialização):

```yaml
startCommand: "streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.maxUploadSize 2048"
```

**Para 5 GB, mude para:**
```yaml
startCommand: "streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.maxUploadSize 5120"
```

### 📍 Local 2 - Linha 12 (variável de ambiente):

```yaml
envVars:
  - key: STREAMLIT_SERVER_MAX_UPLOAD_SIZE
    value: 2048
```

**Para 5 GB, mude para:**
```yaml
envVars:
  - key: STREAMLIT_SERVER_MAX_UPLOAD_SIZE
    value: 5120
```

### 📍 Local 3 - Linha 15 (tamanho do disco):

```yaml
disk:
  name: data
  mountPath: /opt/render/project/src/data
  sizeGB: 10
```

**⚠️ IMPORTANTE:** O disco precisa ser maior que o tamanho máximo de upload!

**Para 5 GB de upload, recomendo pelo menos 15 GB de disco:**
```yaml
sizeGB: 15
```

---

## 🚀 RESUMO RÁPIDO

Para aceitar arquivos de **até 5 GB**, mude estes 4 valores:

| Arquivo | Linha | Valor Antigo | Valor Novo |
|---------|-------|--------------|------------|
| `app.py` | 14 | `2048` | `5120` |
| `.streamlit/config.toml` | 3 | `2048` | `5120` |
| `render.yaml` | 8 | `2048` | `5120` |
| `render.yaml` | 12 | `2048` | `5120` |
| `render.yaml` | 15 | `10` | `15` |

---

## 🏃 Como Aplicar as Mudanças

### Local (seu computador):

1. Edite os arquivos conforme acima
2. Salve tudo
3. Execute:
   ```bash
   streamlit run app.py
   ```

### Deploy no Render.com:

1. Edite os arquivos conforme acima
2. Commit e push para o GitHub:
   ```bash
   git add .
   git commit -m "Aumentar limite de upload para 5GB"
   git push
   ```
3. O Render vai fazer redeploy automaticamente

---

## ⚠️ AVISOS IMPORTANTES

### 1. Plano do Render.com

O plano **FREE** do Render tem limitações:
- RAM: 512 MB
- Pode não processar arquivos muito grandes
- Recomendado upgrade para **Starter ($7/mês)** para arquivos 1GB+

### 2. Memória do Servidor

Se o arquivo for muito grande, pode dar erro de memória mesmo com o limite aumentado. Nesse caso:

**Opção A: Aumentar o chunksize no app.py (linha 75):**

```python
# Para arquivos muito grandes, aumente o chunksize
if file_size_mb < 50:
    chunksize = 100000
elif file_size_mb < 200:
    chunksize = 500000
elif file_size_mb < 1000:  # Até 1GB
    chunksize = 1000000
else:  # Acima de 1GB
    chunksize = 2000000  # 2 milhões de linhas por chunk
```

**Opção B: Executar localmente**

Para arquivos MUITO grandes (10GB+), é melhor rodar localmente no seu computador que tem mais RAM.

### 3. Tempo de Upload

Upload de arquivos grandes via internet pode demorar:
- 200 MB: ~2-5 minutos (dependendo da internet)
- 1 GB: ~10-30 minutos
- 5 GB: ~1-2 horas

---

## 🧪 Testando

Após fazer as alterações, teste com arquivos pequenos primeiro:

1. Teste com 50 MB
2. Teste com 200 MB
3. Teste com 500 MB
4. Só então tente com arquivos maiores

---

## 📞 Suporte

Se tiver problemas após alterar os valores, verifique:

1. ✅ Os 3 arquivos estão com o mesmo valor?
2. ✅ Reiniciou o Streamlit depois de editar?
3. ✅ O plano do Render tem RAM suficiente?
4. ✅ O tamanho do disco é maior que o upload?

---

**Última atualização:** 2025-01-11