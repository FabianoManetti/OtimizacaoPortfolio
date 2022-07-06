import pandas as pd
import streamlit as st


cadastro_cia = pd.read_csv('cad_cia_aberta.csv', sep = ',')
cadastro_fii = pd.read_csv('fundosListados.csv', sep = ',', encoding = 'utf-8')
cadastro_etf = pd.read_csv('etf_bdr.csv', sep = ';', encoding = 'latin-1')
cadastro_stocks = pd.read_csv('cadastro_stocks.csv')

lista_port_final = []
lista_port_pesos_final = []

try:
    if st.session_state.port_final:
        lista_port_final.append(st.session_state.port_final)
except:
    pass

try:
    if st.session_state.port_pesos_final:
        lista_port_pesos_final.append(st.session_state.port_pesos_final)
except:
    pass

st.info(lista_port_final)

lista_port_final = lista_port_final[0]
lista_port_pesos_final = lista_port_pesos_final[0]

st.info(lista_port_final)
st.info(lista_port_pesos_final)



def main():

    st.title("Otimização Portfólio")

    otimiza_carteira = st.selectbox('Escolha a forma de otimização do portfólio', ('Remoção de ativos', 'Adição de ativos'))

    if otimiza_carteira == 'Remoção de ativos':

        if not 'ativos_remover' in st.session_state:
            st.session_state.ativos_remover = []

        if not 'remover_pesos' in st.session_state:
            st.session_state.remover_pesos = []

        with st.form(key='form_remover'):
            remove_ativo = st.text_input(label='Insira o Ticker do ativo a remover').upper()
            botao_remover = st.form_submit_button('remover')

        if botao_remover:
            if remove_ativo in cadastro_cia['TICKER'].values or remove_ativo in cadastro_fii['codigo'].values or remove_ativo in cadastro_etf['Código'].values:
                ajuste_ticker = remove_ativo + '.SA'
            elif remove_ativo in cadastro_stocks['Código'].values:
                ajuste_ticker = remove_ativo
            else:
                st.info('Insira um ativo válido')
            for ativo in lista_port_final:
                if ativo == ajuste_ticker:
                    st.session_state.ativos_remover.append(ativo)
                else:
                    continue

        if botao_remover:
            st.session_state.remover_pesos.append(lista_port_peos_final[lista_port_final.index(ajuste_ticker)])

    portfolio_pesos_final_ajust = [x * 100 for x in st.session_state.remover_pesos]
    ativos_remover_ajust =[x.split('.')[0] for x in st.session_state.ativos_remover]

    if otimiza_carteira == 'Adição de ativos':

        if not 'ativos_adicionar' in st.session_state:
            st.session_state.ativos_adicionar = []

        if not 'adicionar_pesos' in st.session_state:
            st.session_state.adicionar_pesos = []

        with st.form(key='form_adicionar'):
            adiciona_ativo = st.text_input(label='Insira o Ticker do ativo a adicionar').upper()
            botao_adicionar = st.form_submit_button('adicionar')

        if botao_adicionar:
            if adiciona_ativo in cadastro_cia['TICKER'].values or adiciona_ativo in cadastro_fii['codigo'].values or adiciona_ativo in cadastro_etf['Código'].values:
                ajuste_ticker = adiciona_ativo + '.SA'
                st.session_state.ativos_adicionar.append(ajuste_ticker)
            elif adiciona_ativo in cadastro_stocks['Código'].values:
                ajuste_ticker = adiciona_ativo
                st.session_state.ativos_adicionar.append(ajuste_ticker)
            else:
                st.info('Insira um ativo válido')

        with st.form(key='form_adicionar_pesos'):
            adiciona_ativo_peso = st.number_input(f'Insira o % do ativo {adiciona_ativo} no seu portfólio total')
            botao_adicionar_peso = st.form_submit_button('adicionar')

        if botao_adicionar_peso:
            st.session_state.adicionar_pesos.append(adiciona_ativo_peso)

    try:
        ativos_adicionar_ajust =[x.split('.')[0] for x in st.session_state.ativos_adicionar]
    except AttributeError:
        pass

    st.subheader('Ativos a remover:')

    try:
        df_remover = pd.DataFrame({'Ativos': ativos_remover_ajust, '% no portfólio': portfolio_pesos_final_ajust})
        st.dataframe(df_remover)
    except ValueError:
        pass

    st.subheader('Ativos a adicionar:')

    try:
        df_adicionar = pd.DataFrame(
            {'Ativos': ativos_adicionar_ajust, '% no portfólio': st.session_state.adicionar_pesos})
        st.dataframe(df_adicionar)
    except (AttributeError, ValueError, UnboundLocalError):
        pass

if __name__ == '__main__':
    main()
