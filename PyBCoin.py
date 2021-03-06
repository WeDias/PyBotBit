#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PyBCoin.py        
# Github:@WeDias

# MIT License

# Copyright (c) 2020 Wesley Ribeiro Dias

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# Fonte: CoinMarketCap, https://coinmarketcap.com/
# Fonte: dolarhoje.com, https://dolarhoje.com/
# Fonte: criptofacil, https://www.criptofacil.com/

import requests
from bs4 import BeautifulSoup


# ----------------------------------------------------------------------------------------------------------------------
# funções referentes a formatação de strings


def adicionar_pontos(numero: int or str or float) -> str:
    """
    adicionar_pontos(): Serve para formatar numeros para facilitar a visualização
    :param numero: str, Número que será formatado
    :return: str, formatada ex: 1.000.000
    """
    decimos = '00'
    numero = str(numero)
    if numero.find('.') and float(numero) >= 1000:
        numero = f'{float(numero):.2f}'
        decimos = numero[numero.find('.') + 1:]
        numero = numero[:numero.find('.')]

    if float(numero) >= 1000:
        cont = 0
        string = numero[::-1]
        string_final = ''
        for letra in string:
            cont += 1
            string_final += letra
            if cont == 3:
                string_final += '.'
                cont = 0
        string_final = string_final[::-1]
        if string_final[0] == '.':
            string_final = string_final[1:]

        if int(decimos) > 0:
            return f'{string_final},{decimos}'

        else:
            return string_final

    if float(numero) > 0:
        if float(numero) >= 0.01:
            numero = f'{float(numero):.2f}'
        else:
            numero = f'{float(numero):.6f}'
        return numero.replace('.', ',')


def remover_virgulas(string: str) -> str:
    """
    remover_virgulas(): Serve para remover vírgulas de uma string
    :param string: string que terá suas vírgulas removidas
    :return: str, string sem vírgulas
    """
    if str(string).find(',') > 0:
        string = string.replace(',', '')

    return string


# ----------------------------------------------------------------------------------------------------------------------
# funções referentes aos dados das criptomoedas


def requisicao(link: str) -> BeautifulSoup:
    """
    requisicao(): Serve para retornar o codigo html do site
    :param link: str, link do site
    :return: BeutifulSoup, codigo html
    """
    headers = {
        'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                       ' (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36')}

    resposta = requests.get(link, headers)
    return BeautifulSoup(resposta.text, 'html.parser')


def dolar() -> float:
    """
    dolar(): Serve para retornar o preço atual do dólar
    :return: float: preço do dólar
    """
    dados = requisicao('https://dolarhoje.com/')
    preco = str(dados.find('span', class_='cotMoeda nacional').find('input'))
    return float(preco[preco.find('value="') + 7:preco.rfind('"')].replace(',', '.'))


def verificador(criptomoeda: str) -> bool:
    """
    verificador(): Verifica se a string digitada é o nome de uma criptomoeda
    :param criptomoeda: Nome da criptomoeda
    :return: bool, True se a criptomoeda existir
    """
    if criptomoeda == 'dolar':
        return True

    link = f'https://coinmarketcap.com/currencies/{criptomoeda}/'
    headers = {
        'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                       ' (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36')}

    try:
        return requests.get(link, headers=headers, timeout=1).status_code == 200

    except requests.exceptions.ReadTimeout:
        return False


def buscar_dados(criptomoeda: str) -> dict:
    """
    buscar_dados(): Serve para buscar os dados de uma determionada criptomoeda
    :param criptomoeda: Nome da criptomoeda para buscar os dados
    :return: dicionário com os dados da criptomoeda
    """
    nome = criptomoeda.lower()
    if nome == 'dolar':
        fonte = 'dolarhoje.com'
        imagem = 'https://pngimage.net/wp-content/uploads/2018/05/dollar-png-4.png'
        dados = requisicao('https://dolarhoje.com/')
        preco = str(dados.find('span', class_='cotMoeda nacional').find('input'))
        preco = float(preco[preco.find('value="') + 7:preco.rfind('"')].replace(',', '.'))
        return {'nome': nome, 'fonte': fonte, 'imagem': imagem, 'preco': preco}

    else:
        fonte = 'CoinMarketCap'
        link = f'https://coinmarketcap.com/currencies/{nome}/'

        headers = {
            'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                           ' (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36')}

        resposta = requests.get(link, headers=headers)
        if resposta.status_code == 200:
            dados = BeautifulSoup(resposta.text, 'html.parser')
            # ----------------------------------------------------------------------------------------------------------
            # rank de mercado da criptomoeda
            rank_mercado = dados.find('tbody', class_='cmc-details-panel-about__table').find_all_next('tr', limit=3)
            rank_mercado = rank_mercado[-1].find('td').get_text()[1:]
            rank_mercado = int(rank_mercado)

            # ----------------------------------------------------------------------------------------------------------
            # preço em dólar
            preco = dados.find(class_='cmc-details-panel-price__price').get_text()[1:]
            preco = float(remover_virgulas(preco))

            # ----------------------------------------------------------------------------------------------------------
            # variação da criptomoeda em relação ao dólar
            variacao = dados.find(class_='cmc--change-negative cmc-details-panel-price__price-change')

            if variacao is None:
                variacao = float(
                    dados.find(class_='cmc--change-positive cmc-details-panel-price__price-change').get_text()[2:-2])
            else:
                variacao = float(variacao.get_text()[2:-2])

            # ----------------------------------------------------------------------------------------------------------
            # preço em bitcoin
            preco_btc = dados.find(class_='cmc-details-panel-price__crypto-price').get_text()
            preco_btc = float(remover_virgulas(preco_btc.split()[0]))

            # ----------------------------------------------------------------------------------------------------------
            # market cap
            market_cap = dados.find('tbody', class_='cmc-details-panel-about__table').find_all_next('tr', limit=4)
            market_cap = market_cap[-1].find('td').get_text()[1:]
            market_cap = int(remover_virgulas(market_cap)[1:-4])

            # ----------------------------------------------------------------------------------------------------------
            # volume (24H)
            volume = str(dados.find('ul',
                                    class_='cmc-details-panel-stats k1ayrc-0 OZKKF').find_all('span')[2].get_text())

            volume = int(remover_virgulas(volume)[1:-4])

            # ----------------------------------------------------------------------------------------------------------
            # imagem
            imagem = str(dados)

            imagem = imagem[
                     imagem.find('https://s2.coinmarketcap.com/static/img/coins/200x200/'):imagem.find('.png"') + 4]

            return {'fonte': fonte,
                    'imagem': imagem,
                    'rank': rank_mercado,
                    'nome': nome,
                    'preco': preco,
                    'variação': variacao,
                    'preco_btc': preco_btc,
                    'market_cap': market_cap,
                    'volume': volume}


def buscar_preco(criptomoeda: str) -> float:
    """
    buscar_preco(): Serve para obter o preço atual de uma determinada criptomoeda
    :param criptomoeda: str, nome da criptomoeda para encontrar seu preço
    :return: float, preço atual da criptomoeda
    """
    preco = 0

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                      ' (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}

    if criptomoeda != 'dolar':
        link = f'https://coinmarketcap.com/currencies/{criptomoeda}/'
        req = requests.get(link, headers=headers)
        if req.status_code == 200:
            dados = BeautifulSoup(req.text, 'html.parser')
            preco = dados.find(class_='cmc-details-panel-price__price').get_text()[1:]
            preco = float(remover_virgulas(preco))
    else:
        preco = dolar()

    return preco


# ----------------------------------------------------------------------------------------------------------------------
# funções referentes as noticias


def ultimas_noticias() -> list:
    """
    ultimas_noticias(): Serve para retornar uma lista com as ultimas noticias
    :return: list, contendo dicionarios, cada dicionario é uma noticia contendo nome, link e data
    """
    retornar = []
    dados = requisicao('https://www.criptofacil.com/ultimas-noticias/')
    noticias = dados.find('div',
                          class_=('uael-post-grid__inner uael-post__columns-3'
                                  ' uael-post__columns-tablet-2 uael-post__'
                                  'columns-mobile-1 uael-post-infinite-scroll uael-post-infinite__event-click'))

    noticias_a = noticias.find_all_next('a', target='_self')

    datas = noticias.find_all('span', class_='uael-post__date')
    for i, noticia in enumerate(noticias_a):
        if noticia.get('title'):
            i = int(i / 2)
            nome_noticia = noticia.get('title')
            link_noticia = noticia.get('href')
            data = datas[i].get_text().strip()
            retornar.append({'nome': nome_noticia, 'link': link_noticia, 'data': data})

            if i == 4:
                break

    return retornar


# ----------------------------------------------------------------------------------------------------------------------
# função para realizar testes

def main() -> None:
    """
    main(): Serve para testar as funções criadas sem interferir na importação das funções para outros arquivos
    :return: None
    """
    print(buscar_dados('bitcoin'))
    pass


if __name__ == '__main__':
    main()
