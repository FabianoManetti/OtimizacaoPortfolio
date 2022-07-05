import pandas as pd
from datetime import datetime
import streamlit as st

cadastro_cia = pd.read_csv('cad_cia_aberta.csv', sep = ',')
cadastro_fii = pd.read_csv('fundosListados.csv', sep = ',', encoding = 'utf-8')
cadastro_etf = pd.read_csv('etf_bdr.csv', sep = ';', encoding = 'latin-1')
cadastro_stocks = pd.read_csv('cadastro_stocks.csv')

def main():

    st.title("Portfólio atual")

    if 'data_inicio' not in st.session_state:
        st.session_state.data_inicio = []

    data = st.date_input("Insira a data de início do portfólio", value = datetime(2017,1,4), min_value=datetime(2000, 1, 1))

    if data:
        st.session_state.data_inicio.append(data)

    escolhe_classe = st.selectbox("Escolha a classe de ativos", ('Ações', 'FII', 'ETF / BDR', 'Ativos Exterior'))

    if escolhe_classe == 'Ações':

        if not 'acoes' in st.session_state:
            st.session_state.acoes = []

        if not 'pesos_acoes' in st.session_state:
            st.session_state.pesos_acoes = []

        with st.form(key='form_ações'):
            acoes = st.text_input(label='Insira o Ticker da Ação').upper()
            botao_acoes = st.form_submit_button('adicionar')

        with st.form(key='form_pesos_ações'):
            peso_acao = st.number_input(f'Insira o % da Ação {acoes} no seu portfólio total')
            botao_peso_acao = st.form_submit_button('adicionar')

        if botao_acoes:
            if acoes in cadastro_cia['TICKER'].values:
                st.session_state.acoes.append(acoes)
            else:
                st.info('Insira um ativo válido')

        if botao_peso_acao:
            st.session_state.pesos_acoes.append(peso_acao)

        try:
             df_acoes = pd.DataFrame({'Ativos': st.session_state.acoes, '% no portfólio': st.session_state.pesos_acoes})
             st.dataframe(df_acoes)
        except ValueError:
            pass

    if escolhe_classe == 'FII':

        if not 'fiis' in st.session_state:
            st.session_state.fiis = []

        if not 'pesos_fiis' in st.session_state:
            st.session_state.pesos_fiis = []

        with st.form(key='form_fiis'):
            fiis = st.text_input(label='Insira o Ticker do FII').upper()
            botao_fiis = st.form_submit_button('adicionar')

        with st.form(key='form_pesos_fiis'):
            peso_fii = st.number_input(f'Insira o % do FII {fiis} no seu portfólio total')
            botao_peso_fii = st.form_submit_button('adicionar')

        if botao_fiis:
            if fiis in cadastro_fii['codigo'].values:
                st.session_state.fiis.append(fiis)
            else:
                st.info('Insira um ativo válido')

        if botao_peso_fii:
            st.session_state.pesos_fiis.append(peso_fii)

        try:
             df_fiis = pd.DataFrame({'Ativos': st.session_state.fiis, '% no portfólio': st.session_state.pesos_fiis})
             st.dataframe(df_fiis)
        except ValueError:
            pass

    if escolhe_classe == 'ETF / BDR':

        if not 'etfs' in st.session_state:
            st.session_state.etfs = []

        if not 'pesos_etfs' in st.session_state:
            st.session_state.pesos_etfs = []

        with st.form(key='form_etfs'):
            etfs = st.text_input(label='Insira o Ticker do ETF / BDR').upper()
            botao_etfs = st.form_submit_button('adicionar')

        with st.form(key='form_pesos_etfs'):
            peso_etf = st.number_input(f'Insira o % do ativo {etfs} no seu portfólio total')
            botao_peso_etf = st.form_submit_button('adicionar')

        if botao_etfs:
            if etfs in cadastro_etf['Código'].values:
                st.session_state.etfs.append(etfs)
            else:
                st.info('Insira um ativo válido')

        if botao_peso_etf:
            st.session_state.pesos_etfs.append(peso_etf)

        try:
             df_etfs = pd.DataFrame({'Ativos': st.session_state.etfs, '% no portfólio': st.session_state.pesos_etfs})
             st.dataframe(df_etfs)
        except ValueError:
            pass

    if escolhe_classe == 'Ativos Exterior':

        if not 'exterior' in st.session_state:
            st.session_state.exterior = []

        if not 'pesos_exterior' in st.session_state:
            st.session_state.pesos_exterior = []

        with st.form(key='form_exterior'):
            exterior = st.text_input(label='Insira o Ticker do Ativo no Exterior').upper()
            botao_exterior = st.form_submit_button('adicionar')

        with st.form(key='form_pesos_exterior'):
            peso_exterior = st.number_input(f'Insira o % do ativo {exterior} no seu portfólio total')
            botao_peso_exterior = st.form_submit_button('adicionar')

        if botao_exterior:
            if exterior in cadastro_stocks['Código'].values:
                st.session_state.exterior.append(exterior)
            else:
                st.info('Insira um ativo válido')

        if botao_peso_exterior:
            st.session_state.pesos_exterior.append(peso_exterior)

        try:
             df_exterior = pd.DataFrame({'Ativos': st.session_state.exterior, '% no portfólio': st.session_state.pesos_exterior})
             st.dataframe(df_exterior)
        except ValueError:
            pass

    st.markdown("""&copy; Fabiano Manetti - 2022""", unsafe_allow_html=True)

if __name__ == '__main__':
    main()
