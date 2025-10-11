import streamlit as st
import pandas as pd
import os
import time
from pathlib import Path

# Configuração da página
st.set_page_config(
    page_title="Conversor CSV → Parquet",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS customizado para dark mode e design limpo
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stApp {
        background-color: #0e1117;
    }
    h1 {
        color: #ffffff;
        text-align: center;
        padding: 1rem 0;
    }
    .subtitle {
        text-align: center;
        color: #a0a0a0;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #1a1a1a;
        color: #666;
        text-align: center;
        padding: 0.5rem;
        font-size: 0.85rem;
        border-top: 1px solid #333;
    }
    .stProgress > div > div > div > div {
        background-color: #00d4ff;
    }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho
st.title("🚀 Conversor CSV → Parquet")
st.markdown('<p class="subtitle">Powered by Streamlit + Render | Converta grandes arquivos CSV para Parquet de forma rápida e eficiente</p>', unsafe_allow_html=True)

# Criar diretório de dados
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Upload de arquivo
uploaded_file = st.file_uploader(
    "📂 Faça upload do seu arquivo CSV (suporta até 1GB)",
    type=["csv"],
    help="Selecione um arquivo CSV para converter em formato Parquet"
)

if uploaded_file:
    # Exibir informações do arquivo
    file_size_mb = uploaded_file.size / (1024 * 1024)
    st.info(f"📊 **Arquivo:** {uploaded_file.name} | **Tamanho:** {file_size_mb:.2f} MB")
    
    # Salvar arquivo temporariamente
    file_path = DATA_DIR / uploaded_file.name
    parquet_path = DATA_DIR / uploaded_file.name.replace(".csv", ".parquet")
    
    # Barra de progresso
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Fase 1: Salvando arquivo
        status_text.text("⏳ Salvando arquivo...")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        progress_bar.progress(20)
        time.sleep(0.3)
        
        # Fase 2: Lendo e convertendo
        status_text.text("🔄 Lendo CSV e convertendo para Parquet...")
        progress_bar.progress(40)
        
        # Determinar tamanho do chunk baseado no tamanho do arquivo
        if file_size_mb < 50:
            chunksize = 100000
        elif file_size_mb < 200:
            chunksize = 500000
        else:
            chunksize = 1000000
        
        # Ler e converter em chunks para evitar problemas de memória
        reader = pd.read_csv(file_path, chunksize=chunksize, low_memory=False)
        
        first_chunk = True
        chunk_count = 0
        total_rows = 0
        
        for chunk in reader:
            chunk_count += 1
            total_rows += len(chunk)
            
            if first_chunk:
                # Primeiro chunk: criar arquivo
                chunk.to_parquet(parquet_path, index=False, engine='pyarrow', compression='snappy')
                first_chunk = False
                st.session_state['preview_df'] = chunk.head(5)
            else:
                # Chunks subsequentes: fazer append
                existing_df = pd.read_parquet(parquet_path)
                combined_df = pd.concat([existing_df, chunk], ignore_index=True)
                combined_df.to_parquet(parquet_path, index=False, engine='pyarrow', compression='snappy')
            
            # Atualizar progresso
            progress = min(40 + (chunk_count * 10), 90)
            progress_bar.progress(progress)
            status_text.text(f"🔄 Processando... ({total_rows:,} linhas processadas)")
        
        # Finalização
        progress_bar.progress(100)
        status_text.text("✅ Conversão concluída!")
        time.sleep(0.5)
        
        # Estatísticas do arquivo convertido
        parquet_size_mb = parquet_path.stat().st_size / (1024 * 1024)
        compression_ratio = ((file_size_mb - parquet_size_mb) / file_size_mb) * 100
        
        # Exibir resultados
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total de Linhas", f"{total_rows:,}")
        with col2:
            st.metric("💾 Tamanho Parquet", f"{parquet_size_mb:.2f} MB")
        with col3:
            st.metric("📉 Redução de Tamanho", f"{compression_ratio:.1f}%")
        
        st.success("✅ **Conversão concluída com sucesso!**")
        
        # Preview dos dados
        if 'preview_df' in st.session_state:
            st.subheader("👀 Preview dos Dados (primeiras 5 linhas)")
            st.dataframe(st.session_state['preview_df'], use_container_width=True)
        
        # Botão de download
        with open(parquet_path, "rb") as f:
            st.download_button(
                label="⬇️ Baixar Arquivo Parquet",
                data=f,
                file_name=parquet_path.name,
                mime="application/octet-stream",
                help="Clique para fazer download do arquivo convertido",
                use_container_width=True
            )
        
        # Limpar arquivos temporários após conversão
        if file_path.exists():
            file_path.unlink()
        
    except MemoryError:
        st.error("❌ **Erro de Memória:** O arquivo é muito grande para ser processado com a memória disponível. Tente um arquivo menor ou entre em contato com o suporte.")
        progress_bar.empty()
        status_text.empty()
        
    except pd.errors.EmptyDataError:
        st.error("❌ **Erro:** O arquivo CSV está vazio ou não contém dados válidos.")
        progress_bar.empty()
        status_text.empty()
        
    except pd.errors.ParserError as e:
        st.error(f"❌ **Erro ao ler CSV:** O arquivo pode estar corrompido ou ter formato inválido.\n\nDetalhes: {str(e)}")
        progress_bar.empty()
        status_text.empty()
        
    except Exception as e:
        st.error(f"❌ **Erro inesperado durante a conversão:**\n\n{str(e)}")
        progress_bar.empty()
        status_text.empty()
        
    finally:
        # Limpar barra de progresso se ainda estiver visível
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()

else:
    # Instruções quando nenhum arquivo foi enviado
    st.markdown("""
    ### 📋 Como usar:
    
    1. **Upload:** Clique no botão acima e selecione seu arquivo CSV
    2. **Processamento:** Aguarde enquanto o arquivo é convertido
    3. **Download:** Baixe o arquivo Parquet otimizado
    
    ### ✨ Vantagens do formato Parquet:
    
    - **Compressão eficiente:** Reduz o tamanho do arquivo em até 80%
    - **Leitura mais rápida:** Otimizado para análise de dados
    - **Compatível:** Funciona com Pandas, Spark, Dask e outras ferramentas
    - **Tipagem preservada:** Mantém os tipos de dados originais
    """)

# Rodapé
st.markdown('<div class="footer">Desenvolvido por Arlen | © 2025</div>', unsafe_allow_html=True)