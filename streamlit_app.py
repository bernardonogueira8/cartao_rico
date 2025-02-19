import streamlit as st
import pandas as pd
import openpyxl

# Função para processar o arquivo CSV
def processar_csv_streamlit(df):
    portadores_unicos = df['Portador'].unique()
    abas = {str(portador): df[df['Portador'] == portador] for portador in portadores_unicos}
    return abas

# Interface Streamlit
st.title("Organizador de Contas")

# Upload do arquivo CSV
uploaded_file = st.file_uploader("Faça upload de um arquivo CSV", type=["csv"])

if uploaded_file is not None:
    try:
        # Lê o arquivo CSV
        df = pd.read_csv(uploaded_file,sep=";")
        
        if 'Portador' not in df.columns:
            st.error("O arquivo não contém a coluna 'Portador'.")
        else:
            # Processa o CSV
            new_order = ['Data','Valor', 'Parcela', 'Estabelecimento', 'Portador']
            df = df[new_order]
            df.loc[:, 'Valor'] = df.Valor.str.strip()
            df.loc[:, 'Valor'] = df.Valor.str.removeprefix("R$ '")
            df.loc[:, 'Valor'] = df.Valor.str.replace('.', ',')
            # Convertendo a coluna de data para o formato datetime
            df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')

            # Ordenando o DataFrame pela coluna de data
            df = df.sort_values(by='Data')

            # Reseta o índice após a ordenação (opcional)
            df = df.reset_index(drop=True)
            abas = processar_csv_streamlit(df)
            
            # Botão para baixar o arquivo Excel
            with pd.ExcelWriter("saida_streamlit.xlsx", engine='openpyxl') as writer:
                for aba, dados in abas.items():
                    dados.to_excel(writer, sheet_name=aba, index=False)
            
            with open("saida_streamlit.xlsx", "rb") as file:
                st.download_button(
                    label="Baixar arquivo Excel",
                    data=file,
                    file_name="portadores_divididos.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    except Exception as e:
        st.error(f"Ocorreu um erro: {e}")
