# ------------------------------------------------------------- #
#                                         PyBCoin               #
#                                       Github:@WeDias          #
#                                    Licença: MIT License       #
#                                Copyright © 2020 Wesley Dias   #
# ------------------------------------------------------------- #

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
        decimos = numero[numero.find('.')+1:]
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
    :param string: string que terá suas vírgulas removidas
    :return: str, string sem vírgulas
    """
    if str(string).find(',') > 0:
        string = string.replace(',', '')

    return string


# ----------------------------------------------------------------------------------------------------------------------
# funções referentes aos dados das criptomoedas


def verificador(criptomoeda: str) -> bool:
    """
    verificador(): Verifica se a string digitada é o nome de uma criptomoeda
    :param criptomoeda: Nome da criptomoeda
    :return: bool, True se a criptomoeda existir
    """
    if criptomoeda == 'dolar':
        return True

    link = f'https://coinmarketcap.com/currencies/{criptomoeda}/'
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
    try:
        return requests.get(link, headers=headers, timeout=1).status_code == 200

    except requests.exceptions.ReadTimeout:
        return False


def buscar_dados(criptomoeda: str) -> dict:
    """
    :param criptomoeda: Nome da criptomoeda para buscar os dados
    :return: dicionário com os dados da criptomoeda
    """
    nome = criptomoeda.lower()
    if nome == 'dolar':
        fonte = 'dolarhoje.com'
        imagem = 'https://pngimage.net/wp-content/uploads/2018/05/dollar-png-4.png'
        link = 'https://dolarhoje.com/'
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
        resposta = requests.get(link, headers=headers)
        dados = BeautifulSoup(resposta.text, 'html.parser')
        valor = str(dados.find('span', class_='cotMoeda nacional').find('input'))
        valor = float(valor[valor.find('value="')+7:valor.rfind('"')].replace(',', '.'))
        return {'nome': nome, 'fonte': fonte, 'imagem': imagem, 'preco': valor}

    else:
        fonte = 'CoinMarketCap'
        link = f'https://coinmarketcap.com/currencies/{nome}/'
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
        resposta = requests.get(link, headers=headers)
        if resposta.status_code == 200:
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


def buscar_preco(criptomoeda: str) -> float:
    """
    buscar_preco(): Serve para obter o preço atual de uma determinada criptomoeda
    :param criptomoeda: str, nome da criptomoeda para encontrar seu preço
    :return: float, preço atual da criptomoeda
    """
    link = f'https://coinmarketcap.com/currencies/{criptomoeda}/'
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
    resposta = requests.get(link, headers=headers)
    if resposta.status_code == 200:
        dados = BeautifulSoup(resposta.text, 'html.parser')
        preco = dados.find(class_='cmc-details-panel-price__price').get_text()[1:]
        return float(remover_virgulas(preco))


# ----------------------------------------------------------------------------------------------------------------------
# funções referentes as noticias

def ultimas_noticias() -> list:
    """
    ultimas_noticias(): Serve para retornar uma lista com as ultimas noticias
    :return: list, contendo dicionarios, cada dicionario é uma noticia contendo nome, link e data
    """
    retornar = []
    link = 'https://www.criptofacil.com/ultimas-noticias/'
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
    resposta = requests.get(link, headers)
    dados = BeautifulSoup(resposta.text, 'html.parser')
    noticias = dados.find('div', class_='uael-post-grid__inner uael-post__columns-3 uael-post__columns-tablet-2 uael-post__columns-mobile-1 uael-post-infinite-scroll uael-post-infinite__event-click')
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

    pass


if __name__ == '__main__':
    main()
