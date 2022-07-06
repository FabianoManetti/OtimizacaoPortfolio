import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime
from pandas_datareader import data as web
import plotly.express as px
import yfinance as yf

data_inicio_portfolio = []
if st.session_state.data_inicio:
    data_inicio_portfolio.append(st.session_state.data_inicio[-1])
data_inicio_portfolio = data_inicio_portfolio[0]

lista_acoes = []
lista_fiis =[]
lista_etfs =[]
lista_exterior=[]
lista_pesos_acoes = []
lista_pesos_fiis = []
lista_pesos_etfs = []
lista_pesos_exterior = []

try:
    if st.session_state.acoes:
        lista_acoes.append(st.session_state.acoes)
except:
    pass

try:
    if st.session_state.fiis:
        lista_fiis.append(st.session_state.fiis)
except:
    pass

try:
    if st.session_state.etfs:
        lista_etfs.append(st.session_state.etfs)

except:
    pass

try:
    if st.session_state.exterior:
        lista_exterior.append(st.session_state.exterior)
except:
    pass

if len(lista_exterior) == 0:
    lista_exterior.append([])

portfolio_final_brasil = lista_acoes + lista_fiis + lista_etfs
portfolio_final_brasil = [y + '.SA' for x in portfolio_final_brasil for y in x]
portfolio_final = portfolio_final_brasil + lista_exterior[0]

try:
    if st.session_state.pesos_acoes:
        lista_pesos_acoes.append(st.session_state.pesos_acoes)
except:
    pass

try:
    if st.session_state.pesos_fiis:
        lista_pesos_fiis.append(st.session_state.pesos_fiis)
except:
    pass

try:
    if st.session_state.pesos_etfs:
        lista_pesos_etfs.append(st.session_state.pesos_etfs)
except:
    pass

try:
    if st.session_state.pesos_exterior:
        lista_pesos_exterior.append(st.session_state.pesos_exterior)
except:
    pass

portfolio_pesos_final = lista_pesos_acoes + lista_pesos_fiis + lista_pesos_etfs + lista_pesos_exterior
portfolio_pesos_final = [y/100 for x in portfolio_pesos_final for y in x]
portfolio_pesos_final = np.array(portfolio_pesos_final)

st.info(portfolio_pesos_final)

if len(lista_acoes) == 0:
    lista_acoes.append([])
if len(lista_fiis) == 0:
    lista_fiis.append([])
if len(lista_etfs) == 0:
    lista_etfs.append([])

lista_ativos = lista_acoes[0] + lista_fiis[0] + lista_etfs[0] + lista_exterior[0]
dt = pd.DataFrame({'Ativos': lista_ativos, '% no portfólio': np.multiply(100,portfolio_pesos_final)})

def main():

    st.title("Retorno histórico e volatilidade - Portfólio atual x Benchmark")

    if round(np.sum(portfolio_pesos_final), 2) != 1:
        st.info(f'Percentual atual do portfólio: {np.sum(portfolio_pesos_final * 100)}%. Os ativos inseridos devem representar 100 %.')
    
    if 'port_final' not in st.session_state:
        st.session_state.port_final = portfolio_final
        
    if 'port_pesos_final' not in st.session_state:
        st.session_state.port_pesos_final = portfolio_pesos_final
        
    st.info(st.session_state.port_pesos_final)   
    st.dataframe(dt)

    data_final = datetime.today().strftime('%Y-%m-%d')

    dataframe = pd.DataFrame()

    for ativo in portfolio_final:
        dataframe[ativo] = web.DataReader(ativo, data_source='yahoo', start='2006-01-04', end=data_final)['Adj Close']

    retornos_diarios = dataframe.pct_change()

    cov_matrix_anual = retornos_diarios.cov() * 252

    port_var = np.dot(portfolio_pesos_final.T, np.dot(cov_matrix_anual, portfolio_pesos_final))

    port_vol = np.sqrt(port_var) * 100

    portfolio_ret_anual = np.sum(retornos_diarios.mean() * portfolio_pesos_final) * 252 * 100

    percent_vol = str(round(port_vol, 2)) + '%'
    percent_ret = str(round(portfolio_ret_anual, 2)) + '%'

    st.info('Retorno anual esperado: ' + percent_ret)
    st.info('Volatilidade anual: ' + percent_vol)

    dataframe_mensal = pd.DataFrame()

    for ativo in portfolio_final:
        dataframe_mensal[ativo] = yf.download(ativo, start=data_inicio_portfolio, end=data_final, interval='1mo')['Adj Close']

    retornos_mensais = dataframe_mensal.pct_change()

    lista_portfolio = []
    for i in retornos_mensais.iloc():
        retornos = np.sum(i * portfolio_pesos_final)
        lista_portfolio.append(retornos)

    retornos_portfolio = pd.DataFrame(lista_portfolio, index=retornos_mensais.index, columns=['Portfólio'])
    retornos_portfolio.reset_index(inplace=True)
    retornos_portfolio['mes'] = retornos_portfolio.Date.dt.month
    retornos_portfolio['dif'] = retornos_portfolio['mes'].pct_change()
    retornos_portfolio = retornos_portfolio.loc[retornos_portfolio['dif'] != 0]
    retornos_portfolio = retornos_portfolio.drop(columns={'mes', 'dif'})
    retornos_portfolio.set_index('Date', inplace=True)
    retornos_portfolio = (1 + retornos_portfolio).cumprod() - 1
    retornos_portfolio.index.name = 'Período'

    ibov = pd.DataFrame()
    ibov['IBOV'] = yf.download('^BVSP', start=data_inicio_portfolio, end=data_final, interval='1mo')['Adj Close']
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
    cdi = cdi.loc[data_inicio_portfolio:]
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
    ipca = ipca.loc[data_inicio_portfolio:]
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

    fig = px.line(portfolio_final_graf * 100, height=500, width=980, title='Retorno Histórico Portfólio')

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
    risco_retorno_ibov['IBOV'] = yf.download('^BVSP', start=data_inicio_portfolio, end=data_final, interval='1d')['Adj Close']
    risco_retorno_ibov = risco_retorno_ibov.pct_change()
    cov_ibov = risco_retorno_ibov.cov() * 252
    var_ibov = np.dot([1], np.dot(cov_ibov, [1]))
    vol_ibov = np.sqrt(var_ibov)
    ret_anual_ibov = np.sum(risco_retorno_ibov.mean() * [1]) * 252

    risco_retorno_sp500 = pd.DataFrame()
    risco_retorno_sp500['SP500'] = yf.download('^GSPC', start=data_inicio_portfolio, end=data_final, interval='1d')['Adj Close']
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
    risco_retorno_cdi = risco_retorno_cdi.loc[data_inicio_portfolio:]
    cov_cdi = risco_retorno_cdi.cov() * 252
    var_cdi = np.dot([1], np.dot(cov_cdi, [1]))
    vol_cdi = np.sqrt(var_cdi)
    ret_anual_cdi = np.sum(risco_retorno_cdi.mean() * [1]) * 252

    url_bcb = 'http://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json'
    risco_retorno_ipca = pd.read_json(url_bcb)
    risco_retorno_ipca['data'] = pd.to_datetime(risco_retorno_ipca['data'], dayfirst=True)
    risco_retorno_ipca.set_index('data', inplace=True)
    risco_retorno_ipca = risco_retorno_ipca / 100
    risco_retorno_ipca = risco_retorno_ipca.loc[data_inicio_portfolio:]
    risco_retorno_ipca = ((1 + risco_retorno_ipca) * (1 + 0.004867)) - 1
    cov_ipca = risco_retorno_ipca.cov() * 12
    var_ipca = np.dot([1], np.dot(cov_ipca, [1]))
    vol_ipca = np.sqrt(var_ipca)
    ret_anual_ipca = np.sum(risco_retorno_ipca.mean() * [1]) * 12

    retornos = [portfolio_ret_anual, ret_anual_sp500 * 100, ret_anual_ibov * 100, ret_anual_cdi * 100,
                ret_anual_ipca * 100]
    volatilidades = [port_vol, vol_sp500 * 100, vol_ibov * 100, vol_cdi * 100, vol_ipca * 100]
    indices = ['Portfólio', 'SP500', 'IBOV', 'CDI', 'IPCA']

    vol_retorno = pd.DataFrame(data=[retornos, volatilidades, indices]).T
    vol_retorno = vol_retorno.rename(columns={0: 'retorno %a.a', 1: 'volatilidade %a.a', 2: 'índice'})

    fig = px.scatter(vol_retorno, x='volatilidade %a.a', y='retorno %a.a', color='índice',
                     title='Retorno x Volatilidade')
    fig.update_traces(marker_size=15)

    st.plotly_chart(fig)

if __name__ == '__main__':
    main()
