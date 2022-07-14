from pandas_datareader import data as web
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import yfinance as yf
import streamlit as st

cadastro_cia = pd.read_csv('cad_cia_aberta.csv', sep = ',')
cadastro_fii = pd.read_csv('fundosListados.csv', sep = ',', encoding = 'utf-8')
cadastro_etf = pd.read_csv('etf_bdr.csv', sep = ';', encoding = 'latin-1')
cadastro_stocks = pd.read_csv('cadastro_stocks.csv')

lista_port_final_temp = []
lista_port_pesos_final_temp = []

lista_port_pesos_final_temp.append(st.session_state.port_pesos_final)

try:
    if st.session_state.port_final:
        lista_port_final_temp.append(st.session_state.port_final)
except:
    pass

try:
    if st.session_state.port_pesos_final:
        lista_port_pesos_final_temp.append(st.session_state.port_pesos_final)
except:
    pass

lista_port_final = [y for x in lista_port_final_temp for y in x]
lista_port_pesos_final = [y for x in lista_port_pesos_final_temp for y in x]

data_inicio_port_ajust = []
if st.session_state.data_inicio:
    data_inicio_port_ajust.append(st.session_state.data_inicio[-1])
data_inicio_port_ajust = data_inicio_port_ajust[0]

adicionar_pesos_ajust = []

try:
    if st.session_state.adicionar_pesos:
        adicionar_pesos_ajust.append(st.session_state.adicionar_pesos)
except:
    pass

adicionar_pesos_ajust = [y/100 for x in adicionar_pesos_ajust for y in x]

dicionario_port_final = {}

for i, j in zip(lista_port_final, lista_port_pesos_final):
    dicionario_port_final[i] = j
   
remove = [dicionario_port_final.pop(key) for key in st.session_state.ativos_remover]

portfolio_pesos_ajustado = []

for i in dicionario_port_final.values():
    portfolio_pesos_ajustado.append(i)

for l in adicionar_pesos_ajust:
    portfolio_pesos_ajustado.append(l)

portfolio_pesos_ajustado = np.array(portfolio_pesos_ajustado)

lista_ativos_adicionar = []
lista_ativos_remover = []

try:
    if st.session_state.ativos_adicionar:
        lista_ativos_adicionar.append(st.session_state.ativos_adicionar)
except:
    pass

try:
    if st.session_state.ativos_remover:
        lista_ativos_remover.append(st.session_state.ativos_remover)
except:
    pass

if len(lista_ativos_adicionar) == 0:
    lista_ativos_adicionar.append([])
if len(lista_ativos_remover) == 0:
    lista_ativos_remover.append([])

ativos_adicionar_final = list(set(lista_ativos_adicionar[0]))
ativos_remover_final = list(set(lista_ativos_remover[0]))

def main():

    st.title("Retorno histórico e volatilidade - Portfólio atualizado x Benchmark")

    if round(np.sum(portfolio_pesos_ajustado), 2) != 1:
        st.info(f'Percentual atual do portfólio: {np.sum(portfolio_pesos_ajustado * 100)}%. Os ativos inseridos devem representar 100 %.')

    if not 'ativos_adicionar_check' in st.session_state:
        st.session_state.ativos_adicionar_check = []

    if not 'ativos_remover_check' in st.session_state:
        st.session_state.ativos_remover_check = []

    for i in ativos_adicionar_final:

        if i.split('.')[0] in cadastro_cia['TICKER'].values or i.split('.')[0] in cadastro_fii['codigo'].values or i.split('.')[0] in cadastro_etf['Código'].values or i in cadastro_stocks['Código'].values:
            st.session_state.ativos_adicionar_check.append(i)
        else:
            print(f'Ativo {i} não corresponde a um ticker válido')

    for i in ativos_remover_final:
        if i.split('.')[0] in cadastro_cia['TICKER'].values or i.split('.')[0] in cadastro_fii['codigo'].values or i.split('.')[0] in cadastro_etf['Código'].values or i in cadastro_stocks['Código'].values:
            st.session_state.ativos_remover_check.append(i)
        else:
            print(f'Ativo {i} não corresponde a um ticker válido')
          
    portfolio_final_ajustado = [i for i in lista_port_final if i not in st.session_state.ativos_remover_check]
    portfolio_final_ajustado = portfolio_final_ajustado + st.session_state.ativos_adicionar_check
    
    dataframe_ajustado = pd.DataFrame()

    data_final_ajust = datetime.today().strftime('%Y-%m-%d')

    for ativo in portfolio_final_ajustado:
        dataframe_ajustado[ativo] = web.DataReader(ativo, data_source='yahoo', start='2006-01-04', end=data_final_ajust)['Adj Close']

    retornos_diarios_ajustados = dataframe_ajustado.pct_change()

    cov_matrix_anual_ajustado = retornos_diarios_ajustados.cov() * 252
    
    port_var_ajustado = np.dot(portfolio_pesos_ajustado.T, np.dot(cov_matrix_anual_ajustado, portfolio_pesos_ajustado))

    port_vol_ajustado = np.sqrt(port_var_ajustado) * 100

    portfolio_ret_anual_ajustado = np.sum(retornos_diarios_ajustados.mean() * portfolio_pesos_ajustado) * 252 * 100

    percent_vol_ajust = str(round(port_vol_ajustado, 2)) + '%'
    percent_ret_ajust = str(round(portfolio_ret_anual_ajustado, 2)) + '%'

    st.info('Retorno anual esperado: ' + percent_ret_ajust)
    st.info('Volatilidade anual: ' + percent_vol_ajust)

    dataframe_mensal_ajust = pd.DataFrame()

    for ativo in portfolio_final_ajustado:
        dataframe_mensal_ajust[ativo] = yf.download(ativo, start=data_inicio_port_ajust, end=data_final_ajust, interval='1mo')['Adj Close']

    retornos_mensais_ajust = dataframe_mensal_ajust.pct_change()

    lista_portfolio = []
    for i in retornos_mensais_ajust.iloc():
        retornos = np.sum(i * portfolio_pesos_ajustado)
        lista_portfolio.append(retornos)

    try:    
        
        retornos_portfolio = pd.DataFrame(lista_portfolio, index=retornos_mensais_ajust.index, columns=['Portfólio'])
        retornos_portfolio.reset_index(inplace=True)
        retornos_portfolio['mes'] = retornos_portfolio.Date.dt.month
        retornos_portfolio['dif'] = retornos_portfolio['mes'].pct_change()
        retornos_portfolio = retornos_portfolio.loc[retornos_portfolio['dif'] != 0]
        retornos_portfolio = retornos_portfolio.drop(columns={'mes', 'dif'})
        retornos_portfolio.set_index('Date', inplace=True)
        retornos_portfolio = (1 + retornos_portfolio).cumprod() - 1
        retornos_portfolio.index.name = 'Período'

        ibov = pd.DataFrame()
        ibov['IBOV'] = yf.download('^BVSP', start=data_inicio_port_ajust, end=data_final_ajust, interval='1mo')['Adj Close']
        ibov = ibov.pct_change()
        ibov.reset_index(inplace=True)
        ibov['mes'] = ibov.Date.dt.month
        ibov['dif'] = ibov['mes'].pct_change()
        ibov = ibov.loc[ibov['dif'] != 0]
        ibov = ibov.drop(columns={'mes', 'dif'})
        ibov.set_index('Date', inplace=True)
        ibov = (1 + ibov).cumprod() - 1
        ibov.index.name = 'Período'

        url_bcb = 'http://api.bcb.gov.br/dados/serie/bcdata.sgs.4391/dados?formato=json'
        cdi = pd.read_json(url_bcb)
        cdi['data'] = pd.to_datetime(cdi['data'], dayfirst=True)
        cdi.set_index('data', inplace=True)
        cdi = cdi.loc[data_inicio_port_ajust:]
        cdi.reset_index(inplace=True)
        cdi['mes'] = cdi.data.dt.month
        cdi['dif'] = cdi['mes'].pct_change()
        cdi = cdi.loc[cdi['dif'] != 0]
        cdi = cdi.drop(columns={'mes', 'dif'})
        cdi.set_index('data', inplace=True)
        cdi = cdi / 100
        cdi = (1 + cdi).cumprod() - 1
        cdi.index.name = 'Período'
        cdi.rename(columns={'valor': 'CDI'}, inplace=True)

        url_bcb = 'http://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json'
        ipca = pd.read_json(url_bcb)
        ipca['data'] = pd.to_datetime(ipca['data'], dayfirst=True)
        ipca.set_index('data', inplace=True)
        ipca = ipca.loc[data_inicio_port_ajust:]
        ipca.reset_index(inplace=True)
        ipca['mes'] = ipca.data.dt.month
        ipca['dif'] = ipca['mes'].pct_change()
        ipca = ipca.loc[ipca['dif'] != 0]
        ipca = ipca.drop(columns={'mes', 'dif'})
        ipca.set_index('data', inplace=True)
        ipca = ipca / 100
        ipca['IPCA + 6%'] = ((1 + ipca['valor']) * (1 + 0.004867)) - 1
        ipca = (1 + ipca).cumprod() - 1
        ipca.index.name = 'Período'
        ipca.rename(columns={'valor': 'IPCA'}, inplace=True)

        portfolio_final_graf = pd.concat([retornos_portfolio, ipca, cdi, ibov], axis=1, join='inner')

        fig = px.line(portfolio_final_graf * 100, height=500, width=980, title='Retorno Histórico Portfólio Ajustado')

        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )

        st.plotly_chart(fig)

        risco_retorno_ibov = pd.DataFrame()
        risco_retorno_ibov['IBOV'] = yf.download('^BVSP', start=data_inicio_port_ajust, end=data_final_ajust, interval='1d')['Adj Close']
        risco_retorno_ibov = risco_retorno_ibov.pct_change()
        cov_ibov = risco_retorno_ibov.cov() * 252
        var_ibov = np.dot([1], np.dot(cov_ibov, [1]))
        vol_ibov = np.sqrt(var_ibov)
        ret_anual_ibov = np.sum(risco_retorno_ibov.mean() * [1]) * 252

        risco_retorno_sp500 = pd.DataFrame()
        risco_retorno_sp500['SP500'] = yf.download('^GSPC', start=data_inicio_port_ajust, end=data_final_ajust, interval='1d')['Adj Close']
        risco_retorno_sp500 = risco_retorno_sp500.pct_change()
        cov_sp500 = risco_retorno_sp500.cov() * 252
        var_sp500 = np.dot([1], np.dot(cov_sp500, [1]))
        vol_sp500 = np.sqrt(var_sp500)
        ret_anual_sp500 = np.sum(risco_retorno_sp500.mean() * [1]) * 252

        url_bcb = 'http://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados?formato=json'
        risco_retorno_cdi = pd.read_json(url_bcb)
        risco_retorno_cdi['data'] = pd.to_datetime(risco_retorno_cdi['data'], dayfirst=True)
        risco_retorno_cdi.set_index('data', inplace=True)
        risco_retorno_cdi = risco_retorno_cdi / 100
        risco_retorno_cdi = risco_retorno_cdi.loc[data_inicio_port_ajust:]
        cov_cdi = risco_retorno_cdi.cov() * 252
        var_cdi = np.dot([1], np.dot(cov_cdi, [1]))
        vol_cdi = np.sqrt(var_cdi)
        ret_anual_cdi = np.sum(risco_retorno_cdi.mean() * [1]) * 252

        url_bcb = 'http://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json'
        risco_retorno_ipca = pd.read_json(url_bcb)
        risco_retorno_ipca['data'] = pd.to_datetime(risco_retorno_ipca['data'], dayfirst=True)
        risco_retorno_ipca.set_index('data', inplace=True)
        risco_retorno_ipca = risco_retorno_ipca / 100
        risco_retorno_ipca = risco_retorno_ipca.loc[data_inicio_port_ajust:]
        risco_retorno_ipca = ((1 + risco_retorno_ipca) * (1 + 0.004867)) - 1
        cov_ipca = risco_retorno_ipca.cov() * 12
        var_ipca = np.dot([1], np.dot(cov_ipca, [1]))
        vol_ipca = np.sqrt(var_ipca)
        ret_anual_ipca = np.sum(risco_retorno_ipca.mean() * [1]) * 12

        retornos = [portfolio_ret_anual_ajustado, ret_anual_sp500 * 100, ret_anual_ibov * 100, ret_anual_cdi * 100, ret_anual_ipca * 100]
        volatilidades = [port_vol_ajustado, vol_sp500 * 100, vol_ibov * 100, vol_cdi * 100, vol_ipca * 100]
        indices = ['Portfólio', 'SP500', 'IBOV', 'CDI', 'IPCA']

        vol_retorno = pd.DataFrame(data=[retornos, volatilidades, indices]).T
        vol_retorno = vol_retorno.rename(columns={0: 'retorno %a.a', 1: 'volatilidade %a.a', 2: 'índice'})

        fig = px.scatter(vol_retorno, x='volatilidade %a.a', y='retorno %a.a', color='índice',
                         title='Retorno x Volatilidade')
        fig.update_traces(marker_size=15)

        st.plotly_chart(fig)
        
    except:
        pass

if __name__ == '__main__':
    main()
