# ------------------------------------------------------------- #
#                                         PyBCoin               #
#                                       Github:@WeDias          #
#                                    Licença: MIT License       #
#                                Copyright © 2020 Wesley Dias   #
# ------------------------------------------------------------- #

# Fonte: CoinMarketCap, https://coinmarketcap.com/

import requests
from bs4 import BeautifulSoup


def adicinar_pontos(numero: int or str) -> str:
    """
    adicionar_pontos(): Serve para formatar numeros para facilitar a visualização
    :param numero: str, Número que será formatado
    :return: str, formatada ex: 1.000.000
    """
    numero = str(numero)
    if len(numero) > 3:
        cont = 0
        string_final = ''
        string = numero[::-1]
        for letra in string:
            cont += 1
            string_final += letra
            if cont == 3:
                string_final += '.'
                cont = 0
        string_final = string_final[::-1]
        if string_final[0] == '.':
            string_final = string_final[1:]
        return string_final


def remover_virgulas(string: str) -> str:
    """
    :param string: string que terá suas vírgulas removidas
    :return: string sem vírgulas
    """
    if str(string).find(',') > 0:
        string = string.replace(',', '')

    return string


def buscar_dados(criptomoeda: str) -> dict:
    """
    :param criptomoeda: Nome da criptomoeda para buscar os dados
    :return: dicionário com os dados da criptomoeda
    """
    nome = criptomoeda.lower()
    if nome == 'dolar':
        fonte = 'dolarhoje.com'
        imagem = 'https://pngimage.net/wp-content/uploads/2018/05/dollar-png-4.png'
        resposta = requests.get(f'https://dolarhoje.com/', headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'})
        dados = BeautifulSoup(resposta.text, 'html.parser')
        valor = str(dados.find('span', class_='cotMoeda nacional').find('input'))
        valor = float(valor[valor.find('value="')+7:valor.rfind('"')].replace(',', '.'))
        return {'nome': nome, 'fonte': fonte, 'imagem': imagem, 'preco': valor}

    else:
        fonte = 'CoinMarketCap'
        resposta = requests.get(f'https://coinmarketcap.com/currencies/{nome}/', headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'})
        dados = BeautifulSoup(resposta.text, 'html.parser')
        # ------------------------------------------------------------------------------------------------------------------
        # rank de mercado da criptomoeda
        rank_mercado = dados.find(class_='cmc-label cmc-label--success sc-13jrx81-0 FVuRP').get_text()
        rank_mercado = int(rank_mercado.replace('Rank ', ''))

        # ------------------------------------------------------------------------------------------------------------------
        # preço em dólar
        preco = dados.find(class_='cmc-details-panel-price__price').get_text()[1:]
        preco = float(remover_virgulas(preco))

        # ------------------------------------------------------------------------------------------------------------------
        # variação da criptomoeda em relação ao dólar
        variacao = dados.find(class_='cmc--change-negative cmc-details-panel-price__price-change')
        if variacao is None:
            variacao = float(dados.find(class_='cmc--change-positive cmc-details-panel-price__price-change').get_text()[2:-2])
        else:
            variacao = float(variacao.get_text()[2:-2])

        # ------------------------------------------------------------------------------------------------------------------
        # preço em bitcoin
        preco_btc = dados.find(class_='cmc-details-panel-price__crypto-price').get_text()
        preco_btc = float(remover_virgulas(preco_btc.split()[0]))

        # ------------------------------------------------------------------------------------------------------------------
        # market cap
        market_cap = str(dados.find('ul', class_='cmc-details-panel-stats k1ayrc-0 OZKKF').find_next('span').get_text())
        market_cap = int(remover_virgulas(market_cap)[1:-4])

        # ------------------------------------------------------------------------------------------------------------------
        # volume (24H)
        volume = str(dados.find('ul', class_='cmc-details-panel-stats k1ayrc-0 OZKKF').find_all('span')[2].get_text())
        volume = int(remover_virgulas(volume)[1:-4])

        # ------------------------------------------------------------------------------------------------------------------
        # imagem
        imagem = str(dados)
        imagem = imagem[imagem.find('https://s2.coinmarketcap.com/static/img/coins/200x200/'):imagem.find('.png"')+4]
        return {'fonte': fonte, 'imagem': imagem, 'rank': rank_mercado, 'nome': nome, 'preco': preco, 'variação': variacao, 'preco_btc': preco_btc, 'market_cap': market_cap, 'volume': volume}