#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PyBotBit.py        
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

import json
import discord
import asyncio
import PyBCoin
from datetime import datetime
from hashlib import sha256, md5

client = discord.Client(max_messages=None)

# ----------------------------------------------------------------------------------------------------------------------
# classes e funções referentes a carteira


class Criptografia:
    def __init__(self, string) -> None:
        """
        __init__(): Serve para inicializar o objeto da classe Criptografia
        :param string: str, string utilizada pra gerar a hash md5
        """
        for cont in range(2):
            string = str(string) + '#P!B0tB1T#404'
            self.hashmd5 = sha256(string.encode()).hexdigest()
            string = self.hashmd5
        self.hashmd5 = md5(string.encode()).hexdigest()

    def criptografar(self) -> str:
        """
        criptografar(): Serve para retornar uma hash md5
        :return: str, hash md5
        """
        return self.hashmd5


class Carteira:
    def __init__(self, user_id: int or str) -> None:
        """
        __init__(): Serve para inicializar o objeto da classe Carteira
        :param user_id: int or str, id do usuario
        :return: None
        """
        hashmd5 = Criptografia(user_id)
        self.dono = hashmd5.criptografar()
        with open('Data/CarteirasSalvas', 'r') as arq:
            self.__carteiras_salvas = json.loads(arq.read())
        try:
            self.dados = self.__carteiras_salvas[self.dono]
        except KeyError:
            self.dados = {}

    @staticmethod
    def verificar_valido(string: str) -> bool:
        """
        verificar_valido(): Serve para verificar se o comando é válido
        :param string: str, mensagem enviada do usuário
        :return: bool, True se válido
        """
        lista = string.split()
        try:
            if len(lista) == 4:
                if str(lista[3]).find(',') > 0:
                    lista[3] = lista[3].replace(',', '.')

            if lista[1] == 'x':
                return True

            elif lista[1] in '+-' and PyBCoin.verificador(lista[2]) and float(lista[3]):
                return True
            else:
                return False
        except ValueError:
            return False

    def __verificar_vazio(self) -> bool:
        """
        __verificar_vazio(): Serve para verificar se a carteira do usuario esta vazia
        e se estiver vazia, apaga os dados de identificacao da carteira
        :return: bool, True se estiver vazia
        """
        if self.dados == {}:
            del self.__carteiras_salvas[self.dono]
            return True
        else:
            return False

    def __salvar_carteira(self) -> None:
        """
        __salvar_carteira(): Serve para salvar a carteira
        :return: None
        """
        with open('Data/CarteirasSalvas', 'w') as arq:
            arq.write(json.dumps(self.__carteiras_salvas))

    def minha_carteira(self) -> dict:
        """
        minha_carteira(): Serve para mostrar todas as moedas do usuario dentro da carteira
        :return: bool, True se a operação for realizada com sucesso
        """
        try:
            return self.__carteiras_salvas[self.dono]
        except KeyError:
            return {}

    def adicionar_moeda(self, string: str) -> bool:
        """
        adicionar_moeda(): Serve para adicionar moedas na carteira
        :param string: str, dados da moeda e valor a ser adicionados
        :return: bool, True se a operação for realizada com sucesso
        """
        if Carteira.verificar_valido(string):
            string = string.split()
            moeda = string[2]
            if str(string[3]).find(',') > 0:
                string[3] = string[3].replace(',', '.')
            quantidade = float(PyBCoin.remover_virgulas(string[3]))
            try:
                self.dados[moeda] = float(self.dados[moeda])
                self.dados[moeda] += quantidade
            except KeyError:
                self.dados[moeda] = quantidade
            finally:
                self.__carteiras_salvas[self.dono] = self.dados
                self.__salvar_carteira()
            return True
        else:
            return False

    def subtrair_moeda(self, string: str) -> bool:
        """
        subtrair_moeda(): Serve para subtrair moedas da carteira
        :param string: str, dados da moeda e valor a ser removidos
        :return: bool, True se a operação for realizada com sucesso
        """
        if Carteira.verificar_valido(string):
            string = string.split()
            moeda = string[2]
            if str(string[3]).find(',') > 0:
                string[3] = string[3].replace(',', '.')
            quantidade = float(string[3])
            try:
                self.dados[moeda] = float(self.dados[moeda])
                if self.dados[moeda] >= quantidade:
                    self.dados[moeda] -= quantidade
                    if self.dados[moeda] == 0:
                        del self.dados[moeda]
                    if not self.__verificar_vazio():
                        self.__carteiras_salvas[self.dono] = self.dados
                    self.__salvar_carteira()
                    return True
                else:
                    return False
            except KeyError:
                return False

    def excluir_moeda(self, moeda: str) -> bool:
        """
        excluir_moeda(): Serve para excluir uma moeda da carteira
        :param moeda: str, nome da moeda a ser excluida
        :return: bool, True se a operação for realizada com sucesso
        """
        try:
            del self.dados[moeda]
            self.__verificar_vazio()
            self.__salvar_carteira()
            return True
        except KeyError:
            return False

    def excluir_carteira(self) -> bool:
        """
        excluir_carteira(): Serve para excluir a carteira
        :return: bool, True se a operação for realizada com sucesso
        """
        try:
            del self.__carteiras_salvas[self.dono]
            self.__salvar_carteira()
            return True
        except KeyError:
            return False


# ----------------------------------------------------------------------------------------------------------------------
# classe e funções referentes ao log


class Log:
    @staticmethod
    def log_menu() -> None:
        """
        log_menu(): Serve para mostrar no console algumas informações
        :return: None
        """
        print(f'\rPyBotBit status: [ONLINE] [{int(client.latency * 1000)} ms]')
        print(f'Canais aptos a utilizar o PyBotBit: [{Log.aptos(canais=True)}]')
        print(f'Usuários aptos a utilizar o PyBotBit: [{Log.aptos(usuarios=True)}]')
        print(' PyBotBit Log '.center(120, '-'))

    @staticmethod
    def log(mensagem: str, titulo: bool = False) -> None:
        """
        log(): Serve para retornar uma mensagem de log
        :param mensagem: str, mensagem que será usada para o log
        :param titulo: bool, Se a mensagem a ser escrita é um titulo
        :return: None
        """
        if titulo:
            print(f'\n>>>[{datetime.now()}] {mensagem}')
        else:
            print(f'    <<<[{datetime.now()}] {mensagem}')

    @staticmethod
    def aptos(canais: bool = False, usuarios: bool = False) -> int:
        """
        aptos(): Serve para retornar o número de canais ou usuário aptos a utilizar o bot
        :param canais: bool, se True retorna a quantidade de canais
        :param usuarios: bool, se True retorna a quantidade de usuários
        :return: int, quantidade de canais ou usuários
        """
        if canais:
            dados = client.get_all_channels()

        elif usuarios:
            dados = client.get_all_members()

        else:
            return 0

        lista = []
        for dado in dados:
            lista.append(dado)
        return len(lista)

    @staticmethod
    async def mudar_status(txt: str, status: discord.Status) -> None:
        """
        mudar_status(): Serve para mudar o status do bot
        :param txt: str, mensagem para o status
        :param status: discord.Status, status operacional do bot
        :return: None
        """
        await client.change_presence(status=status,
                                     activity=discord.Game(name=txt))

        await asyncio.sleep(1)


# ----------------------------------------------------------------------------------------------------------------------
# classe e funções referentes aos alertas


class Alertas:
    @staticmethod
    def nome_condicao(condicao: str) -> str:
        """
        nome_condicao(): Serve para alterar uma string
        :param condicao: str, condição > ou <
        :return: str, nome da condição
        """
        if condicao == '>':
            return 'acima de'

        elif condicao == '<':
            return 'abaixo de'

    @staticmethod
    def ler_alertas_arq() -> dict:
        """
        ler_alertas_arq(): Serve para retornar uma lista com todos os alertas salvos
        :return: dict, lista com todos os alertas salvos
        """
        with open('Data/Alertas', 'r') as arq:
            alertas = json.loads(arq.read())
        return alertas

    @staticmethod
    def verificar_alerta(alerta: list) -> bool:
        """
        verificar_alerta(): serve para verificar se os dados para criar o alerta estão certos
        :param alerta: list, lista com os dados do alerta
        :return: bool, True se estiver tudo certo com o alerta e False se tiver algum problema
        """
        try:
            criptomoeda = alerta[1]
            condicao = alerta[2]
            preco_alerta = alerta[3]

        except IndexError:
            return False

        if PyBCoin.verificador(criptomoeda) and condicao in ['<', '>'] and len(alerta) == 4:
            try:
                float(preco_alerta)

            except ValueError:
                return False

            finally:
                return True
        else:
            return False

    @staticmethod
    async def monitorar_alertas() -> None:
        """
        monitorar_alertas(): Serve para monitorar os alertas criados
        e avisar o usuário caso a condição seja atendida
        :return: None
        """
        indice = ativado = 0
        dicionario = Alertas.ler_alertas_arq()
        alertas = dicionario["alertas"]
        for alerta in alertas:
            preco = PyBCoin.buscar_preco(alerta["moeda"])

            if (alerta["cond"] == '>' and preco >= float(alerta["preco"]))\
                    or (alerta["cond"] == '<' and preco <= float(alerta["preco"])):

                author = client.get_user(int(alerta["user"]))
                await Mensagens.gerar_dm(author)
                alerta["cond"] = Alertas.nome_condicao(alerta["cond"])

                sigla = 'USD'
                if alerta["moeda"] == 'dolar':
                    sigla = 'BRL'

                await author.dm_channel.send(f'{author.mention} :loudspeaker: Alerta disparado {alerta["moeda"]} '
                                             f'{alerta["cond"]} {sigla} {PyBCoin.adicionar_pontos(alerta["preco"])}')

                await Mensagens.dados_criptomoedas(alerta["moeda"], int(alerta["user"]))
                del alertas[indice]
                dicionario["alertas"] = alertas
                Log.log(f'Alerta {alerta} ativado e excluído com sucesso !')

                ativado += 1
                with open('Data/Alertas', 'w') as arq:
                    arq.write(json.dumps(dicionario))

            indice += 1

        Log.log(f'({len(alertas)} alertas ativos) ({ativado} alertas disparados)')
        await Log.mudar_status('Online', discord.Status.online)
        await asyncio.sleep(30)

    @staticmethod
    async def meus_alertas(author: int or discord.User, enviar: bool = True, enviar_embed: bool = False)\
            -> list or discord.Embed:
        """
        meus_alertas(): Serve para mostrar ao usuário os alertas criados por ele
        :param enviar: bool, Se True ele enviará os alertas para o usuário, criados por ele
        :param author: int ou discord.User, id usuário ou objeto usuário para encontrar e mandar alertas
        :param enviar_embed: bool, se True retorna o embed sem enviar para o usuário
        :return: list, retorna o número de alertas e quem são eles, ou discord.Embed
        """
        author = Mensagens.obter_author(author)
        dicionario = Alertas.ler_alertas_arq()
        alertas = dicionario["alertas"]

        cont = 0
        meus = []
        for alerta in alertas:
            if alerta['user'] == author.id:
                cont += 1
                meus.append(alerta)

        if enviar:
            await Mensagens.gerar_dm(author)
            embed = Mensagens.gerar_embed(color=0x12BCEC,
                                          title='Meus alertas ativos')

            embed.set_author(name='Alertas',
                             icon_url='https://i.pinimg.com/originals/28/33/86/283386fd0a92178f7785da3d566004d0.png')

            embed.set_thumbnail(url='https://i.pinimg.com/originals/28/33/86/283386fd0a92178f7785da3d566004d0.png')
            vazio = True
            for i, meu in enumerate(meus):
                vazio = False
                meu["cond"] = Alertas.nome_condicao(meu["cond"])

                sigla = 'USD'
                if meu["moeda"] == 'dolar':
                    sigla = 'BRL'

                embed.add_field(name=f':bell: Alerta (ID {i})',
                                value=f'{meu["moeda"]} {meu["cond"]} {sigla}'
                                      f' {PyBCoin.adicionar_pontos(meu["preco"])}\n',
                                inline=False)

            if vazio:
                embed.add_field(name='Oops não encontrei nada por aqui !',
                                value=('Você não tem nenhum alerta ativo\n'
                                       'Para criar utilize `!alertar (criptomoeda) (condição) (valor)`'))

                embed.add_field(name='Exemplos de comandos válidos',
                                value='`!alertar bitcoin > 7215.15`\n`!alertar bitcoin < 6010`',
                                inline=False)

                embed.add_field(name='Informações',
                                value='Digite `!ajuda` para saber sobre o PyBotBit',
                                inline=False)

            if enviar_embed:
                return embed

            await author.dm_channel.send(f'{author.mention} Aqui estão seus alertas ativos', embed=embed)
            Log.log(f'({len(meus)}) Alertas encontrados')

        return [len(meus), meus]

    @staticmethod
    async def criar_alerta(message: discord.Message) -> None:
        """
        criar_alerta(): Serve para criar um alerta para o usuário
        :param message: discord.Message, objeto mensagem com os dados para gerar o alerta
        :return: None
        """
        enviado = False
        author = message.author
        mensagem = message.content.lower()
        alerta = str(mensagem).split()
        alerta[0] = author.id
        meus = await Alertas.meus_alertas(author, False)
        if meus[0] < 10:
            if Alertas.verificar_alerta(alerta) and alerta[1]:
                if alerta[3].find(','):
                    alerta[3] = alerta[3].replace(',', '.')
                valor = float(alerta[3])
                with open('Data/Alertas', 'r') as arq:
                    dicionario = json.loads(arq.read())

                alertas = dicionario["alertas"]
                alertas.append({"user": alerta[0], "moeda": alerta[1], "cond": alerta[2], "preco": valor})
                dicionario["alertas"] = alertas
                with open('Data/Alertas', 'w') as arq:
                    arq.write(json.dumps(dicionario))

                valor = PyBCoin.adicionar_pontos(valor)
                alerta[2] = Alertas.nome_condicao(alerta[2])

                sigla = 'USD'
                if alerta[3] == 'dolar':
                    sigla = 'BRL'

                retornar = f'Alerta para {alerta[1]} {alerta[2]} {sigla} {valor} criado com sucesso !'
                Log.log(retornar)

                retornar += f'\nUma mensagem de alerta será enviada para você quando o preço atingir {sigla} {valor} !'

                await Mensagens.gerar_dm(author)

                await author.dm_channel.send(f'{author.mention} {retornar}',
                                             embed=await Alertas.meus_alertas(author, enviar_embed=True))
                enviado = True
            else:
                retornar = f'Erro ao criar o alerta, o comando `{mensagem}` foi digitado errado !'

        else:
            retornar = 'Erro ao criar o alerta, você já tem 10 alertas. Utilize `!delalertar id` para apagar algum'

        if not enviado:
            Log.log(retornar)
            await message.channel.send(f'{author.mention} {retornar}')

    @staticmethod
    async def remover_alerta(message: discord.Message) -> bool:
        """
        remover_alerta(): Serve para remover um alerta ativo do usuário
        :param message: discord.Message, objeto mensagem enviado pelo usuário
        :return: bool, True se o alerta foi removido com sucesso
        """
        await Log.mudar_status('Removendo alerta', discord.Status.idle)
        author = message.author
        mensagem = message.content.lower()
        await Mensagens.gerar_dm(author)

        try:
            id_alerta = int(mensagem.split()[1])

        except (IndexError, ValueError):
            Log.log(f'Erro ao deletar alerta, comando {mensagem} inválido !')

            await author.dm_channel.send(f'{author.mention} Erro ao deletar alerta. comando `{mensagem}`'
                                         f' inválido\nDigite `!ajuda` para saber sobre os comandos disponíveis ')
            return False

        dicionario = Alertas.ler_alertas_arq()
        alertas = dicionario["alertas"]
        remover = await Alertas.meus_alertas(author.id, False)
        try:
            if remover[0] > id_alerta >= 0:
                indice = 0
                for alerta in alertas:
                    if alerta == remover[1][id_alerta]:
                        del alertas[indice]
                        dicionario["alertas"] = alertas
                        break
                    indice += 1

                with open('Data/Alertas', 'w') as arq:
                    arq.write(json.dumps(dicionario))
                Log.log(f'Alerta {remover[1][id_alerta]} removido com sucesso !')

                await author.dm_channel.send(f'{author.mention} Alerta removido com sucesso !',
                                             embed=await Alertas.meus_alertas(author, enviar_embed=True))
                return True

            else:
                Log.log('Erro ao deletar, alerta inexistente !')

                await author.dm_channel.send(f'{author.mention} Erro ao deletar. Alerta inexistente\n'
                                             f'Digite `!alertas` para visualizar seus alertas existentes')
                return False

        except TypeError:
            Log.log(f'Erro ao deletar alerta, comando {mensagem} inválido !')

            await author.dm_channel.send(f'{author.mention} Erro ao deletar alerta. comando `{mensagem}` inválido\n'
                                         f'Digite `!ajuda` para saber sobre os comandos disponíveis ')
            return False


# ----------------------------------------------------------------------------------------------------------------------
# classe e funções referentes ao envio de mensagens


class Mensagens:
    @staticmethod
    def obter_author(author: int or discord.User) -> discord.User:
        """
        obter_author(): Serve para obter o objeto do usário a partir de sua id
        :param author: int ou discord.User, id usuário ou objeto usuário para obter o objeto com os dados usuário
        :return: object, com os dados do usuário
        """
        if str(author).isdecimal():
            author = client.get_user(author)
        return author

    @staticmethod
    def gerar_embed(**kwargs) -> discord.Embed:
        """
        gerar_embed(): serve para gerar um objeto embed
        :return: discord.Embed
        """
        embed = discord.Embed(**kwargs)

        embed.set_footer(text='PyBotBit © 2020 Wesley Dias',
                         icon_url=('https://avatars2.githubusercontent.com'
                                   '/u/56437612?s=88&u=c9ddcaa797c6a84031e4441c7f42fbc72ec6a4b1&v=4'))
        return embed

    @staticmethod
    async def gerar_dm(author: int or discord.User) -> None:
        """
        gerar_dm(): Serve para criar um canal de comunicação direto com usuário
        :param author: int ou object, usuário que mandou a mensagem
        :return: None
        """
        author = Mensagens.obter_author(author)
        if author.dm_channel is None:
            await author.create_dm()

    @staticmethod
    async def ajuda(message: discord.Message) -> None:
        """
        ajuda(): Serve para retornar ao usuário uma mensagem de ajuda
        :param message: discord.Message, objeto mensagem gerado pelo usuário
        :return: None
        """
        embed = Mensagens.gerar_embed(color=0x12BCEC,
                                      title=':robot: Informações sobre o PyBotBit')

        embed.set_thumbnail(url='https://images.emojiterra.com/google/android-nougat/512px/2753.png')

        embed.set_author(name='PyBotBit ajuda',
                         url='https://github.com/wedias',
                         icon_url='https://images.emojiterra.com/google/android-nougat/512px/2753.png')

        sobre = '''
        PyBotBit é um robô/bot para o Discord com o foco no mundo das criptomoedas,
        ele é capaz de informar dados de criptomoedas como: preço, variação,
        criar alertas de preço, para não perder nenhuma oportunidade de compra/venda,
        informar sobre notícias atuais relacionadas ao bitcoin e demais altcoins,
        calcular quanto vale n criptomoedas em dólar e em reais,
        mostrar a cotação atual do dólar. E para facilitar a vida, está disponível
        a função carteira, que  salva quantas e quais moedas você tem e já calcula
        o valor total em USD e em BRL de suas moedas !'''.replace('\n',  ' ')

        desenvolvedor = '''
        Código fonte: [disponível aqui](https://github.com/WeDias/PyBotBit)
        Github: [@WeDias](https://github.com/WeDias/)
        '''

        embed.add_field(name='Sobre o PyBotBit',
                        value=sobre,
                        inline=False)

        embed.add_field(name='Manual de ajuda',
                        value='Para conhecer os comandos disponíveis leia o manual de ajuda\n'
                              '[Disponível aqui](https://github.com/WeDias/PyBotBit)',
                        inline=False)

        embed.add_field(name='Desenvolvedor',
                        value=desenvolvedor,
                        inline=False)

        await message.channel.send(f'{message.author.mention} Espero que isto possa te ajudar', embed=embed)

        Log.log('Ajuda enviada com sucesso !')

    @staticmethod
    async def dados_criptomoedas(message: discord.Message or str, user_id: int = 0) -> None:
        """
        dados_criptomoedas(): Serve para retornar uma mensagem com os dados da criptomoeda solicitada
        :param message: discord.Message, objeto mensagem gerado pelo usuário
        :param user_id: int, id do usuário
        :return: None
        """
        if user_id:
            author = Mensagens.obter_author(user_id)
            await Mensagens.gerar_dm(author)
            channel = author.dm_channel
            criptomoeda = message

        else:
            criptomoeda = message.content.lower()[1:]
            channel = message.channel
            author = message.author

        dados = PyBCoin.buscar_dados(criptomoeda)

        if criptomoeda == 'dolar':
            embed = Mensagens.gerar_embed(color=0x228B22,
                                          title=f'Informações sobre {criptomoeda}')

            embed.set_author(name=dados['nome'],
                             url=f'https://dolarhoje.com',
                             icon_url=dados['imagem'])

            embed.set_thumbnail(url=dados['imagem'])

            embed.add_field(name='Valor',
                            value=f'R$ {PyBCoin.adicionar_pontos(dados["preco"])}')

        else:

            if dados['variação'] > 0:
                cor = 0x228B22

            else:
                cor = 0xB22222

            embed = Mensagens.gerar_embed(color=cor,
                                          title=f'Informações sobre {criptomoeda}')

            embed.set_author(name=dados['nome'],
                             url=f'https://coinmarketcap.com/currencies/{criptomoeda}/',
                             icon_url=dados['imagem'])

            embed.set_thumbnail(url=dados['imagem'])

            embed.add_field(name='Rank',
                            value=f'#{dados["rank"]}')

            embed.add_field(name='Valor',
                            value=f'USD {PyBCoin.adicionar_pontos(dados["preco"])}')

            embed.add_field(name='variação (24H)',
                            value=f'{dados["variação"]}%')

            embed.add_field(name='Volume (24H)',
                            value=f'USD {PyBCoin.adicionar_pontos(dados["volume"])}')

            embed.add_field(name='Market Cap',
                            value=f'USD {PyBCoin.adicionar_pontos(dados["market_cap"])}')

        embed.set_footer(text=f'Fonte: {dados["fonte"]}\nPyBotBit © 2020 Wesley Dias',
                         icon_url=('https://avatars2.githubusercontent.com'
                                   '/u/56437612?s=88&u=c9ddcaa797c6a84031e4441c7f42fbc72ec6a4b1&v=4'))

        await channel.send(f'{author.mention} Encontrei as seguintes informações sobre {criptomoeda}', embed=embed)
        Log.log(f'Dados sobre {criptomoeda} enviados com sucesso !')

    @staticmethod
    async def pizza(message: discord.Message) -> None:
        """
        pizza(): Serve mostar o preço de um pizza comprada por 10.000 BTC
        :param message: discord.Message, objeto message enviado pelo usuário
        :return: None
        """
        valor_pizza = int(PyBCoin.buscar_preco('bitcoin') * 10000)
        pizza_us = PyBCoin.adicionar_pontos(valor_pizza)
        pizza_br = int(valor_pizza * PyBCoin.buscar_dados('dolar')['preco'])
        pizza_br = PyBCoin.adicionar_pontos(pizza_br)

        embed = Mensagens.gerar_embed(color=0xff9900,
                                      title='A história da pizza')

        embed.set_author(name='A pizza',
                         icon_url=('https://www.pngkit.com/png/full/'
                                   '2-20847_file-cpnext-emoticon-pizza-fatia-de-pizza-desenho.png'))

        embed.add_field(name='A pizza mais cara do mundo !',
                        value=(f'Em 22 de maio de 2010 uma pizza foi comprada por **10.000 BTC**'
                               f'\nHoje está pizza custaria **USD {pizza_us}** ou **R$ {pizza_br}**'))

        embed.set_thumbnail(url=('https://www.pngkit.com/png/full/'
                                 '2-20847_file-cpnext-emoticon-pizza-fatia-de-pizza-desenho.png'))

        await message.channel.send(f'{message.author.mention} Alguem pediu uma pizza ?',
                                   embed=embed)

        Log.log('Informações sobre a pizza enviados com sucesso !')

    @staticmethod
    async def calcular_criptomoeda(message: discord.Message) -> None:
        """
        calcular_criptomoeda(): Serve para retornar para o usuário o valor de n criptomoedas
        :param message: discord.Message, objeto message enviado pelo usuário
        :return: None
        """
        dados = message.content.lower()[1:].split()
        try:
            if dados[1].count(','):
                dados[1] = float(dados[1].replace(',', '.'))
            else:
                dados[1] = float(dados[1])
        except ValueError:
            author = message.author
            Log.log('Não entendi o comando solicitado')

            await message.channel.send(f'{author.mention} Não entendi o seu comando `{message.content.lower()}`'
                                       f'\nDigite `!ajuda` para conhecer os comandos disponíveis')
            return None

        if dados[1] > 0:
            nome = dados[0]
            if float(dados[1]) >= 2:
                vale = 'valem'

                if nome == 'dolar':
                    nome = 'dolares'

                else:
                    nome = f'{dados[0]}(s)'
            else:
                vale = 'vale'

            embed = Mensagens.gerar_embed(color=0xdaa520,
                                          title=f'Quanto {vale} {PyBCoin.adicionar_pontos(dados[1])} {nome} ?')

            embed.set_thumbnail(url=('https://content.octadesk.com/hs-fs/hubfs'
                                     '/LP%20-%20RD-35.png?width=316&name=LP%20-%20RD-35.png'))

            embed.set_author(name='Calculadora de criptomoedas',
                             icon_url=('https://content.octadesk.com/hs-fs/'
                                       'hubfs/LP%20-%20RD-35.png?width=316&name=LP%20-%20RD-35.png'))

            if dados[0] == 'dolar':
                preco_br = PyBCoin.buscar_dados('dolar')['preco'] * float(dados[1])
                preco_br = PyBCoin.adicionar_pontos(preco_br)

                embed.add_field(name='Em reais',
                                value=f'R$ {preco_br}')

            else:
                preco_us = PyBCoin.buscar_preco(dados[0]) * float(dados[1])
                preco_br = PyBCoin.buscar_dados('dolar')['preco'] * preco_us
                preco_us = PyBCoin.adicionar_pontos(preco_us)
                preco_br = PyBCoin.adicionar_pontos(preco_br)
                dados[1] = PyBCoin.adicionar_pontos(dados[1])

                embed.add_field(name='Em dólares',
                                value=f'USD {preco_us}')

                embed.add_field(name='Em reais',
                                value=f'R$ {preco_br}')

            await message.channel.send(f'{message.author.mention} Acabei de calcular isto',
                                       embed=embed)

        else:
            Log.log('multiplicação por 0... sério !?')
            await message.channel.send(f'{message.author.mention} Desconsiderei sua mensagem')

    @staticmethod
    async def limpar_mensagens(message: discord.Message) -> None:
        """
        limpar_mensagens(): Serve para limpar todas as mensagens trocados pelo bot e o usuário
        :param message: discord.Message, objeto message enviado pelo usuário
        :return: None
        """
        comando_apagar = apagado = False
        mensagens = message.channel.history()
        async for mensagem in mensagens:
            condicao_a = mensagem.content.startswith('!') and mensagem.author.id == message.author.id
            try:
                condicao_b = mensagem.author == client.user and mensagem.mentions[0].id == message.author.id
            except IndexError:
                condicao_b = False

            if mensagem.id == message.id:
                comando_apagar = True

            elif (condicao_a or condicao_b) and comando_apagar:
                try:
                    await mensagem.delete()
                    apagado = True

                except discord.Forbidden:
                    continue

        if not apagado:
            Log.log(f'Não há mensagens de {message.author} para apagar !')

            await message.channel.send(f'{message.author.mention}'
                                       f' Tudo limpo por aqui !\nVocê não tem mensagens enviadas para eu apagar')

        else:
            Log.log(f'Todas as mensagens de {message.author} foram apagadas com sucesso !')

    @staticmethod
    async def noticias(message: discord.Message) -> None:
        """
        noticias(): Serve para enviar algumas notícias sobre o mundo das criptomoedas
        :param message: discord.Message, objeto mensagem gerado pelo usuário
        :return: None
        """
        embed = Mensagens.gerar_embed(color=0x7b68ee,
                                      title='Últimas notícias')

        embed.set_author(name='Notícias',
                         url='https://www.criptofacil.com/ultimas-noticias/',
                         icon_url='https://cdn3.iconfinder.com/data'
                                  '/icons/ballicons-reloaded-free/512/icon-70-512.png')

        embed.set_thumbnail(url='https://cdn3.iconfinder.com/data/'
                                'icons/ballicons-reloaded-free/512/icon-70-512.png')

        embed.set_footer(text=f'Fonte: criptofacil\nPyBotBit © 2020 Wesley Dias',
                         icon_url='https://avatars2.githubusercontent.com'
                                  '/u/56437612?s=88&u=c9ddcaa797c6a84031e4441c7f42fbc72ec6a4b1&v=4')

        list_noticias = PyBCoin.ultimas_noticias()
        for i, noticia in enumerate(list_noticias):

            embed.add_field(name=noticia['data'],
                            value=f'{noticia["nome"]} [Leia sobre]({noticia["link"]})\n',
                            inline=False)

        Log.log(f'Notícias {list_noticias} enviadas com sucesso !')

        await message.channel.send(f'{message.author.mention} Encontrei estas noticias para você', embed=embed)

    @staticmethod
    async def ping(message: discord.Message) -> None:
        """
        ping(): Serve para retornar a latência do bot
        :return: None
        """
        embed = Mensagens.gerar_embed(title='Ping', color=0xdaa520)

        embed.set_author(name='Devtools',
                         icon_url='https://pngimage.net/wp-content/uploads/2018/05/engrenagem-png-3.png')

        embed.set_thumbnail(url='https://pngimage.net/wp-content/uploads/2018/05/engrenagem-png-3.png')

        embed.add_field(name='ping',
                        value=f'{int(client.latency * 1000)} ms')

        await message.channel.send(f'{message.author.mention} Este é meu ping no momento', embed=embed)

        Log.log(f'[{int(client.latency * 1000)} ms] Este é meu ping no momento')

    @staticmethod
    async def minha_carteira(message: discord.Message) -> None:
        """
        minha_carteira(): Serve para retornar para o usuário uma mensagem sobrensua carteira
        :param message: discord.Message, Objeto message com os dados do usuário e da mensagem
        :return: None
        """
        carteira = Carteira(message.author.id)
        dados = carteira.minha_carteira()
        embed = Mensagens.gerar_embed(title='Carteira', color=0xfffAf0)
        embed.set_author(name='Minha carteira',
                         icon_url='https://bitcoin.netmojo.ca/content/images/2019/09/wallet.png')

        embed.set_thumbnail(url='https://bitcoin.netmojo.ca/content/images/2019/09/wallet.png')
        if dados:
            total = 0
            dolar = PyBCoin.dolar()
            for dado in dados:
                if dado != 'dolar':
                    valor = PyBCoin.buscar_preco(dado) * dados[dado]
                else:
                    valor = dados[dado]

                total += valor
                embed.add_field(name=dado,
                                value=f'{PyBCoin.adicionar_pontos(dados[dado])}'
                                      f' | USD {PyBCoin.adicionar_pontos(valor)}'
                                      f' | BRL {PyBCoin.adicionar_pontos(valor * dolar)}',
                                inline=False)

            embed.add_field(name='Total em USD',
                            value=f'USD {PyBCoin.adicionar_pontos(total)}')

            embed.add_field(name='Total em BRL',
                            value=f'BRL {PyBCoin.adicionar_pontos(total * dolar)}')
        else:
            embed.add_field(name='Você não tem moedas',
                            value='Para adicionar moedas utilize o comando `!carteira + (moeda) (valor)`')

            embed.add_field(name='Exemplos de comandos válidos',
                            value='Ex.: `!carteira + bitcoin 1`\nEx.: `!carteira + ethereum 1.23`',
                            inline=False)

            embed.add_field(name='Informações',
                            value='Digite `!ajuda` para saber sobre o PyBotBit',
                            inline=False)

        await Mensagens.gerar_dm(message.author)
        await message.author.dm_channel.send(f'{message.author.mention} Aqui está sua carteira', embed=embed)


# ----------------------------------------------------------------------------------------------------------------------
# classe Robo e loop de eventos


class Robo:
    @staticmethod
    @client.event
    async def on_ready() -> None:
        """
        on_ready(): Serve para criar um loop e executar
        tarefas quando o bot for iniciado com sucesso
        :return: None
        """
        Log.log_menu()
        while True:
            Log.log('Monitorando alertas...', True)
            await Log.mudar_status('Verificando alertas', discord.Status.idle)
            await Alertas.monitorar_alertas()

    @staticmethod
    @client.event
    async def on_disconnect() -> None:
        """
        on_disconnect(): Serve para retornar se o bot foi desconectado
        :return: None
        """
        Log.log('PyBotBit foi desconectado', True)

    @staticmethod
    @client.event
    async def on_member_join(member: discord.Member) -> None:
        """
        on_member_join(): Serve para verificar quando um novo usuário
        entrou e eniar mensagem de boas vindas
        :param member: discord.Member, objeto member recebido quando o usuário entrou
        :return: None
        """
        await Mensagens.gerar_dm(member)

        text = (f'{member.mention} Seja bem vindo ! Meu nome é PyBotBit'
                f' sou um robô, fui criado para te ajudar!\nDigite `!ajuda`')

        await member.dm_channel.send(text)

    @staticmethod
    @client.event
    async def on_message(message: discord.Message) -> None:
        """
        on_message(): Serve para obter mensagens enviadas pelos
        usuários e realizar tarefas a partir de comandos
        :param message: objeto da mensagem recebida
        :return: None
        """
        if message.author.id != client.user.id:
            author = message.author
            mensagem = message.content.lower()
            criado = True
            if mensagem.startswith('!'):
                await message.add_reaction(emoji='\U0001F504')
                Log.log(f'Verificando comando enviado por: {author.name}, comando: {mensagem} ', True)
                async with message.channel.typing():
                    if mensagem == '!ajuda':
                        await Log.mudar_status('Enviando ajuda', discord.Status.idle)
                        await Mensagens.ajuda(message)

                    elif mensagem == '!alertas':
                        await Log.mudar_status('Enviando alertas', discord.Status.idle)
                        await Alertas.meus_alertas(author, True)

                    elif mensagem == '!pizza':
                        await Log.mudar_status('Enviando pizza', discord.Status.idle)
                        await Mensagens.pizza(message)

                    elif mensagem == '!noticias':
                        await Log.mudar_status('Enviando notícias', discord.Status.idle)
                        await Mensagens.noticias(message)

                    elif mensagem == '!limpar':
                        await Log.mudar_status('Limpando mensagens', discord.Status.idle)
                        await Mensagens.limpar_mensagens(message)

                    elif mensagem == '!ping':
                        await Log.mudar_status('Enviando ping', discord.Status.idle)
                        await Mensagens.ping(message)

                    elif mensagem == '!carteira':
                        await Log.mudar_status('Enviando dados', discord.Status.idle)
                        await Mensagens.minha_carteira(message)
                        Log.log('Carteira envaida com sucesso !')

                    elif mensagem == '!delcarteira':
                        carteira = Carteira(message.author.id)
                        carteira.excluir_carteira()
                        await Log.mudar_status('Deletando dados', discord.Status.idle)
                        await Mensagens.minha_carteira(message)
                        Log.log('Carteira exluida com sucesso !')

                    elif mensagem.startswith('!alertar') and len(mensagem.split()) == 4\
                            and PyBCoin.verificador(mensagem[1:].split()[1]):

                        await Log.mudar_status('Criando alerta', discord.Status.idle)
                        await Alertas.criar_alerta(message)

                    elif mensagem.startswith('!delalertar') and len(mensagem.split()) == 2:
                        if not await Alertas.remover_alerta(message):
                            criado = False
                    else:
                        try:
                            if mensagem.startswith('!carteira') and Carteira.verificar_valido(mensagem):
                                await Log.mudar_status('Enviando dados', discord.Status.idle)
                                carteira = Carteira(message.author.id)
                                if mensagem.split()[1] == '+':
                                    carteira.adicionar_moeda(mensagem)
                                    criado = True
                                    await Mensagens.minha_carteira(message)
                                    Log.log('Adicionando moeda !')

                                elif mensagem.split()[1] == '-':
                                    carteira.subtrair_moeda(mensagem)
                                    criado = True
                                    await Mensagens.minha_carteira(message)
                                    Log.log('Retirando moeda !')

                                elif mensagem.split()[1] == 'x':
                                    carteira.excluir_moeda(mensagem.split()[2])
                                    criado = True
                                    await Mensagens.minha_carteira(message)
                                    Log.log('Excluindo moeda !')

                            elif PyBCoin.verificador(mensagem[1:].split()[0]) and len(mensagem[1:].split()) == 1:
                                await Log.mudar_status('Buscando dados', discord.Status.idle)
                                await Mensagens.dados_criptomoedas(message)

                            elif PyBCoin.verificador(mensagem[1:].split()[0]) and len(mensagem[1:].split()) == 2:
                                await Log.mudar_status('Fazendo cálculos', discord.Status.idle)
                                await Mensagens.calcular_criptomoeda(message)

                            else:
                                criado = False

                        except IndexError:
                            criado = False

                        finally:

                            if not criado:
                                Log.log('Não entendi o comando solicitado')

                                await message.channel.send(
                                    f'{author.mention} Não entendi o seu comando `{message.content.lower()}'
                                    f'`\nDigite `!ajuda` para conhecer os comandos disponíveis')

            else:
                Log.log(f'Verificando mensagem enviada por: {author.name}', True)
                Log.log('A mensagem enviada não era para mim')

            if criado and mensagem.startswith('!'):
                await message.add_reaction(emoji='\U00002705')

            elif not criado and mensagem.startswith('!'):
                await message.add_reaction(emoji='\U0000274C')

        await Log.mudar_status('Online', discord.Status.online)

    @staticmethod
    def main() -> None:
        """
        main(): Função principal do programa, serve para ligar o bot
        :return: None
        """
        print(' PyBotBit Copyright © 2020 Wesley Dias '.rjust(120, '-'))
        print('PyBotBit status: [LIGANDO]', end='')
        with open('Data/Token', 'r') as token_arq:
            token = token_arq.read()
            token = token[token.find('=')+1:]

        if token != '':
            client.run(token)

        else:
            print('ERRO: Token inexistente, adicione o token do bot no arquivo Data/Token')


if __name__ == '__main__':
    Robo.main()
