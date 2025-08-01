import streamlit as st
import pandas as pd
from io import BytesIO


def processar_csv_streamlit(df):
    portadores_unicos = df['Portador'].unique()
    abas = {str(portador): df[df['Portador'] == portador]
            for portador in portadores_unicos}
    return abas


st.title("Organizador de Contas")

uploaded_file = st.file_uploader("Faça upload de um arquivo CSV", type=["csv"])

if uploaded_file is not None:
    try:
        # Lê o arquivo CSV
        df = pd.read_csv(uploaded_file, sep=";")

        title = st.text_input("Nome da Planilha", "Planilha_Dividida")

        if 'Portador' not in df.columns:
            st.error("O arquivo não contém a coluna 'Portador'.")
        else:
            # Reordena as colunas
            new_order = ['Data', 'Valor', 'Parcela',
                         'Estabelecimento', 'Portador']
            df = df[new_order]

            # Remove linhas indesejadas
            df = df[df["Estabelecimento"] != "Pagamento de fatura"]

            # Limpa e converte os valores da coluna 'Valor'
            df['Valor'] = (
                df['Valor']
                .astype(str)
                .str.strip()
                .str.replace("R$", "", regex=False)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
            )
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')

            # Converte a coluna de data para datetime
            df['Data'] = pd.to_datetime(
                df['Data'], format='%d/%m/%Y', errors='coerce')

            # Ordena e reseta índice
            df = df.sort_values(by='Data').reset_index(drop=True)

            # Cria os DataFrames por portador
            abas = processar_csv_streamlit(df)

            # Gera o Excel em memória
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                for aba, dados in abas.items():
                    dados.to_excel(writer, sheet_name=aba, index=False)
            output.seek(0)

            # Botão para download
            st.download_button(
                label="📥 Baixar arquivo Excel",
                data=output,
                file_name=f"{title}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"Ocorreu um erro: {e}")
