# ------------------------------------------------------------- #
#                                          PyBotBit             #
#                                       Github:@WeDias          #
#                                    Licença: MIT License       #
#                                Copyright © 2020 Wesley Dias   #
# ------------------------------------------------------------- #

import discord
import PyBCoin
import asyncio
from datetime import datetime

client: discord.Client

# ----------------------------------------------------------------------------------------------------------------------
# funções referentes ao log


def log_menu() -> None:
    """
    log_menu(): Serve para mostrar no console algumas informações
    :return: None
    """
    print(f'\rPyBotBit status: [ONLINE] [{int(client.latency * 1000)} ms]')
    print(f'Canais aptos a utilizar o PyBotBit: [{aptos(canais=True)}]')
    print(f'Usuários aptos a utilizar o PyBotBit: [{aptos(usuarios=True)}]')
    print(' PyBotBit Log '.center(120, '-'))


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


def aptos(canais: bool = False, usuarios: bool = False) -> int:
    """
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


async def mudar_status(txt: str, status: discord.Status) -> None:
    """
    mudar_status(): Serve para mudar o status do bot
    :param txt: str, mensagem para o status
    :param status: discord.Status, status operacional do bot
    :return: None
    """
    await client.change_presence(status=status, activity=discord.Game(name=txt))
    await asyncio.sleep(0.5)


# ----------------------------------------------------------------------------------------------------------------------
# funções referentes aos alertas


def nome_condicao(condicao: str) -> str:
    """
    :param condicao: str, condição > ou <
    :return: str, nome da condição
    """
    if condicao == '>':
        return 'acima de'

    elif condicao == '<':
        return 'abaixo de'


def ler_alertas_arq() -> list:
    """
    ler_alertas_arq(): Serve para retornar uma lista com todos os alertas salvos
    :return: list, lista com todos os alertas salvos
    """
    with open('Data/alertas', 'r') as arq:
        arq_alertas = arq.readlines()
    alertas = []
    for alerta in arq_alertas:
        if alerta != '\n':
            dados = alerta.strip().split()
            alertas.append(dados)
    return alertas


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


async def monitorar_alertas() -> None:
    """
    monitorar_alertas(): Serve para monitorar os alertas criados e avisar o usuário caso a condição seja atendida
    :return: None
    """
    indice = ativado = 0
    alertas = ler_alertas_arq()
    for alerta in alertas:
        preco = PyBCoin.buscar_preco(alerta[1])
        if (alerta[2] == '>' and preco >= float(alerta[3])) or (alerta[2] == '<' and preco <= float(alerta[3])):
            author = client.get_user(int(alerta[0]))
            await gerar_dm(author)
            alerta[2] = nome_condicao(alerta[2])
            await author.dm_channel.send(f'{author.mention} :loudspeaker: Alerta disparado {alerta[1]} {alerta[2]} USD {PyBCoin.adicionar_pontos(alerta[3])}')
            await dados_criptomoedas(alerta[1], int(alerta[0]))
            del alertas[indice]
            log(f'Alerta {alerta} ativado e excluído com sucesso !')
            ativado += 1
            with open('Data/alertas', 'w') as arq:
                for arq_alerta in alertas:
                    arq.writelines(f'{str(arq_alerta[0])} {arq_alerta[1]} {arq_alerta[2]} {arq_alerta[3]}\n')
        indice += 1

    log(f'({len(alertas)} alertas ativos) ({ativado} alertas disparados)')
    await mudar_status('Online', discord.Status.online)
    await asyncio.sleep(10)


async def meus_alertas(author: int or discord.User, enviar: bool = True, enviar_embed: bool = False) -> list or discord.Embed:
    """
    meus_alertas(): Serve para mostrar ao usuário os alertas criados por ele
    :param enviar: bool, Se True ele enviará os alertas para o usuário, criados por ele
    :param author: int ou discord.User, id usuário ou objeto usuário para encontrar e mandar alertas
    :param enviar_embed: bool, se True retorna o embed sem enviar para o usuário
    :return: list, retorna o número de alertas e quem são eles, list[0] = número de alertas, list[1] = list[alertas] ou discord.Embed
    """
    author = obter_author(author)
    alertas = ler_alertas_arq()
    cont = 0
    meus = []
    for alerta in alertas:
        if alerta[0] == str(author.id):
            cont += 1
            meus.append(alerta)

    if enviar:
        await gerar_dm(author)
        embed = gerar_embed(color=0x12BCEC, title='Meus alertas ativos')
        embed.set_author(name='Alertas', icon_url='https://i.pinimg.com/originals/28/33/86/283386fd0a92178f7785da3d566004d0.png')
        embed.set_thumbnail(url='https://i.pinimg.com/originals/28/33/86/283386fd0a92178f7785da3d566004d0.png')
        vazio = True
        for i, meu in enumerate(meus):
            vazio = False
            if meu[2] == '<':
                meu[2] = 'abaixo de'

            elif meu[2] == '>':
                meu[2] = 'acima de'
            embed.add_field(name=f':bell: Alerta (ID {i})', value=f'{meu[1]} {meu[2]} USD {PyBCoin.adicionar_pontos(meu[3])}\n', inline=False)

        if vazio:
            embed.add_field(name='Oops não encontrei nada por aqui !', value='Você não tem nenhum alerta ativo\nPara criar utilize `!alertar (criptomoeda) (condição) (valor)`')
            embed.add_field(name='Exemplos de comandos válidos', value='`!alertar bitcoin > 7215.15`\n`!alertar bitcoin < 6010`', inline=False)
            embed.add_field(name='Informações', value='Digite `!ajuda` para saber sobre o PyBotBit', inline=False)

        if enviar_embed:
            return embed

        await author.dm_channel.send(f'{author.mention} Aqui estão seus alertas ativos', embed=embed)
        log(f'({len(meus)}) Alertas encontrados')
    return [len(meus), meus]


async def criar_alerta(message: discord.Message) -> None:
    """
    :param message: discord.Message, objeto mensagem com os dados para gerar o alerta
    :return: None
    """
    enviado = False
    author = message.author
    mensagem = message.content.lower()
    alerta = str(mensagem).split()
    alerta[0] = author.id
    meus = await meus_alertas(author, False)
    if meus[0] < 10:
        if verificar_alerta(alerta):
            if alerta[3].find(','):
                alerta[3] = alerta[3].replace(',', '.')
            valor = float(alerta[3])
            with open('Data/alertas', 'a') as arq:
                arq.writelines(f'{alerta[0]} {alerta[1]} {alerta[2]} {valor}\n')
            valor = PyBCoin.adicionar_pontos(valor)
            alerta[2] = nome_condicao(alerta[2])
            retornar = f'Alerta para {alerta[1]} {alerta[2]} USD {valor} criado com sucesso !'
            log(retornar)
            retornar += f'\nUma mensagem de alerta será enviada para você quando o preço atingir USD {valor} !'
            await gerar_dm(author)
            await author.dm_channel.send(f'{author.mention} {retornar}', embed=await meus_alertas(author, enviar_embed=True))
            enviado = True
        else:
            retornar = f'Erro ao criar o alerta, o comando `{mensagem}` foi digitado errado !'
    else:
        retornar = 'Erro ao criar o alerta, você já tem 10 alertas. Utilize `!delalertar id` para apagar algum'

    if not enviado:
        log(retornar)
        await message.channel.send(f'{author.mention} {retornar}')


async def remover_alerta(message: discord.Message) -> bool:
    """
    remover_alerta(): Serve para remover um alerta ativo do usuário
    :type message: discord.Message, objeto mensagem enviado pelo usuário
    :return: bool, True se o alerta foi removido com sucesso
    """
    await client.change_presence(status=discord.Status.idle, activity=discord.Game(name='Calculando'))
    author = message.author
    mensagem = message.content.lower()
    await gerar_dm(author)

    try:
        id_alerta = int(mensagem.split()[1])

    except (IndexError, ValueError):
        log(f'Erro ao deletar alerta, comando {mensagem} inválido !')
        await author.dm_channel.send(f'{author.mention} Erro ao deletar alerta. comando `{mensagem}` inválido\nDigite `!ajuda` para saber sobre os comandos disponíveis ')
        return False

    arq_alertas = ler_alertas_arq()
    alertas = arq_alertas
    remover = await meus_alertas(author.id, False)
    try:
        if remover[0] > id_alerta >= 0:
            indice = 0
            for arq_alerta in arq_alertas:
                if arq_alerta == remover[1][id_alerta]:
                    del alertas[indice]
                    break
                indice += 1

            with open('Data/alertas', 'w') as arq:
                for arq_alerta in alertas:
                    arq.writelines(f'{str(arq_alerta[0])} {arq_alerta[1]} {arq_alerta[2]} {arq_alerta[3]}\n')
            log(f'Alerta {remover[1][id_alerta]} removido com sucesso !')
            await author.dm_channel.send(f'{author.mention} Alerta removido com sucesso !', embed=await meus_alertas(author, enviar_embed=True))
            return True

        else:
            log('Erro ao deletar, alerta inexistente !')
            await author.dm_channel.send(f'{author.mention} Erro ao deletar. Alerta inexistente\nDigite `!alertas` para visualizar seus alertas existentes')
            return False

    except TypeError:
        log(f'Erro ao deletar alerta, comando {mensagem} inválido !')
        await author.dm_channel.send(f'{author.mention} Erro ao deletar alerta. comando `{mensagem}` inválido\nDigite `!ajuda` para saber sobre os comandos disponíveis ')
        return False

# ----------------------------------------------------------------------------------------------------------------------
# funções referentes ao envio de mensagens


def obter_author(author: int or discord.User) -> discord.User:
    """
    obter_author(): Serve para obter o objeto do usário a partir de sua id
    :param author: int ou discord.User, id usuário ou objeto usuário para obter o objeto com os dados usuário
    :return: object, com os dados do usuário
    """
    if str(author).isdecimal():
        author = client.get_user(author)
    return author


def gerar_embed(**kwargs) -> discord.Embed:
    """
    gerar_embed(): serve para gerar um objeto embed
    :return: discord.Embed
    """
    embed = discord.Embed(**kwargs)
    embed.set_footer(text='PyBotBit © 2020 Wesley Dias', icon_url='https://avatars2.githubusercontent.com/u/56437612?s=88&u=c9ddcaa797c6a84031e4441c7f42fbc72ec6a4b1&v=4')
    return embed


async def gerar_dm(author: int or discord.User) -> None:
    """
    gerar_dm(): Serve para criar um canal de comunicação direto com usuário
    :param author: int ou object, usuário que mandou a mensagem
    :return: None
    """
    author = obter_author(author)
    if author.dm_channel is None:
        await author.create_dm()


async def ajuda(message: discord.Message) -> None:
    embed = gerar_embed(color=0x12BCEC, title=':robot: Informações sobre o PyBotBit')
    embed.set_thumbnail(url='https://images.emojiterra.com/google/android-nougat/512px/2753.png')
    embed.set_author(name='PyBotBit ajuda', url='https://github.com/wedias', icon_url='https://images.emojiterra.com/google/android-nougat/512px/2753.png')

    sobre = '''
    PyBotBit é um robô/bot para o Discord com o foco no mundo das criptomoedas,
    ele é capaz de informar dados de criptomoedas como: preço, variação,
    criar alertas de preço, para não perder nenhuma oportunidade de compra/venda,
    informar sobre notícias atuais relacionadas ao bitcoin e demais altcoins,
    calcular quanto vale n criptomoedas em dólar e em reais,
    Mostrar a cotação atual do dólar'''.replace('\n',  ' ')

    comandos = '''
    **Comandos de cotação**
    
    `!(criptomoeda)`
    Retorna os dados atuais de determinada criptomoeda
    Ex.: `!bitcoin`
    
    `!(criptomoeda) (quantidade)`
    Retorna o valor de n criptomoedas em dólares e em reais
    Ex.: `!ethereum 2`
    -------------------------------------------------------------
    **Comandos de alerta**
    
    `!alertas`
    Retorna todos os alertas criados pelo usuário e suas IDs
    
    `!alertar (criptomoeda) (condição) (valor)`
    Cria um alerta para uma criptomoeda, valor em USD
    Ex.: `!alertar monero > 55`
    Ex.: `!alertar litecoin < 42`
    
    `!delalertar (id)`
    Deleta um alerta criado
    -------------------------------------------------------------
    **Outros comandos**
    
    `!limpar`
    Apaga as mensagens trocadas entre o usuário e o bot
    
    `!ajuda`
    Retorna uma mensagem com informações de ajuda
    
    `!noticias`
    Retorna notícias sobre criptomoedas
    
    `!pizza`
    Retorna o valor atual da pizza de 10.000 BTC
    '''

    obsevacao = '''
    Caso o nome da criptomeda seja separado por espaço como por exemplo bitcoin cash
    Favor trocar os espaços por `-` (hífen)
    Ex: `!bitcoin-cash`
    
    O bot não é case sensitive, ou seja, ele não diferencia minúsculas de maiúsculas
    BITCOIN, bitcoin, BiTCoiN etc... são válidos
    
    Para utilizar número decimais tanto faz se for delimitado por vírgula ou ponto
    50,12 ou 50.12 são válidos
    '''

    desenvolvedor = '''
    Código fonte: [disponível aqui](https://github.com/WeDias/PyBotBit)
    Github: [@WeDias](https://github.com/WeDias/)
    '''

    embed.add_field(name='Sobre o PyBotBit', value=sobre, inline=False)
    embed.add_field(name='Comandos válidos', value=comandos, inline=False)
    embed.add_field(name='Observações', value=obsevacao, inline=False)
    embed.add_field(name='Desenvolvedor', value=desenvolvedor, inline=False)

    await message.channel.send(f'{message.author.mention} Espero que isto possa te ajudar', embed=embed)
    log('Ajuda enviada com sucesso !')


async def dados_criptomoedas(message: discord.Message or str, user_id: int = 0) -> None:
    """
    dados_criptomoedas(): Serve para retornar uma mensagem com os dados da criptomoeda solicitada
    :param message: discord.Message, objeto mensagem gerado pelo usuário
    :param user_id: int, id do usuário
    :return: None
    """
    if user_id:
        author = obter_author(user_id)
        await gerar_dm(author)
        channel = author.dm_channel
        criptomoeda = message

    else:
        criptomoeda = message.content.lower()[1:]
        channel = message.channel
        author = message.author

    dados = PyBCoin.buscar_dados(criptomoeda)

    if criptomoeda == 'dolar':
        embed = gerar_embed(color=0x228B22, title=f'Informações sobre {criptomoeda}')
        embed.set_author(name=dados['nome'], url=f'https://dolarhoje.com', icon_url=dados['imagem'])
        embed.set_thumbnail(url=dados['imagem'])
        embed.add_field(name='Valor', value=f'R$ {PyBCoin.adicionar_pontos(dados["preco"])}')

    else:

        if dados['variação'] > 0:
            cor = 0x228B22

        else:
            cor = 0xB22222

        embed = gerar_embed(color=cor, title=f'Informações sobre {criptomoeda}')
        embed.set_author(name=dados['nome'], url=f'https://coinmarketcap.com/currencies/{criptomoeda}/', icon_url=dados['imagem'])
        embed.set_thumbnail(url=dados['imagem'])
        embed.add_field(name='Rank', value=f'#{dados["rank"]}')
        embed.add_field(name='Valor', value=f'USD {PyBCoin.adicionar_pontos(dados["preco"])}')
        embed.add_field(name='variação (24H)', value=f'{dados["variação"]}%')
        embed.add_field(name='Volume (24H)', value=f'USD {PyBCoin.adicionar_pontos(dados["volume"])}')
        embed.add_field(name='Market Cap', value=f'USD {PyBCoin.adicionar_pontos(dados["market_cap"])}')

    embed.set_footer(text=f'Fonte: {dados["fonte"]}\nPyBotBit © 2020 Wesley Dias', icon_url='https://avatars2.githubusercontent.com/u/56437612?s=88&u=c9ddcaa797c6a84031e4441c7f42fbc72ec6a4b1&v=4')
    await channel.send(f'{author.mention} Encontrei as seguintes informações sobre {criptomoeda}', embed=embed)
    log(f'Dados sobre {criptomoeda} enviados com sucesso !')


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
    embed = gerar_embed(color=0xff9900, title='A história da pizza')
    embed.set_author(name='A pizza', icon_url='https://www.pngkit.com/png/full/2-20847_file-cpnext-emoticon-pizza-fatia-de-pizza-desenho.png')
    embed.add_field(name='A pizza mais cara do mundo !', value=f'Em 22 de maio de 2010 uma pizza foi comprada por **10.000 BTC**\nHoje está pizza custaria **USD {pizza_us}** ou **R$ {pizza_br}**')
    embed.set_thumbnail(url='https://www.pngkit.com/png/full/2-20847_file-cpnext-emoticon-pizza-fatia-de-pizza-desenho.png')
    await message.channel.send(f'{message.author.mention} Alguem pediu uma pizza ?', embed=embed)
    log('Informações sobre a pizza enviados com sucesso !')


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
        log('Não entendi o comando solicitado')
        await message.channel.send(f'{author.mention} Não entendi o seu comando `{message.content.lower()}`\nDigite `!ajuda` para conhecer os comandos disponíveis')
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

        embed = gerar_embed(color=0xdaa520, title=f'Quanto {vale} {PyBCoin.adicionar_pontos(dados[1])} {nome} ?')
        embed.set_thumbnail(url='https://content.octadesk.com/hs-fs/hubfs/LP%20-%20RD-35.png?width=316&name=LP%20-%20RD-35.png')
        embed.set_author(name='Calculadora de criptomoedas', icon_url='https://content.octadesk.com/hs-fs/hubfs/LP%20-%20RD-35.png?width=316&name=LP%20-%20RD-35.png')

        if dados[0] == 'dolar':
            preco_br = PyBCoin.buscar_dados('dolar')['preco'] * float(dados[1])
            preco_br = PyBCoin.adicionar_pontos(preco_br)
            embed.add_field(name='Em reais', value=f'R$ {preco_br}')

        else:
            preco_us = PyBCoin.buscar_preco(dados[0]) * float(dados[1])
            preco_br = PyBCoin.buscar_dados('dolar')['preco'] * preco_us
            preco_us = PyBCoin.adicionar_pontos(preco_us)
            preco_br = PyBCoin.adicionar_pontos(preco_br)
            dados[1] = PyBCoin.adicionar_pontos(dados[1])
            embed.add_field(name='Em dólares', value=f'USD {preco_us}')
            embed.add_field(name='Em reais', value=f'R$ {preco_br}')

        await message.channel.send(f'{message.author.mention} Acabei de calcular isto', embed=embed)

    else:
        log('multiplicação por 0... sério !?')
        await message.channel.send(f'{message.author.mention} Desconsiderei sua mensagem')


async def limpar_mensagens(message: discord.Message) -> None:
    """
    limpar_mwnsagens(): Serve para limpar todas as mensagens trocados pelo bot e o usuário
    :param message: discord.Message, objeto message enviado pelo usuário
    :return: None
    """
    comando_apagar = apagado = False
    mensagens = message.channel.history()
    async for mensagem in mensagens:
        condicao_a = mensagem.content.startswith('!') and mensagem.author.id == message.author.id
        condicao_b = mensagem.author == client.user and mensagem.mentions[0].id == message.author.id

        if mensagem.id == message.id:
            comando_apagar = True

        elif (condicao_a or condicao_b) and comando_apagar:
            try:
                await mensagem.delete()
                apagado = True

            except discord.Forbidden:
                continue

    if not apagado:
        log(f'Não há mensagens de {message.author} para apagar !')
        await message.channel.send(f'{message.author.mention} Tudo limpo por aqui !\nVocê não tem mensagens enviadas para eu apagar')

    else:
        log(f'Todas as mensagens de {message.author} foram apagada com sucesso !')


async def noticias(message: discord.Message) -> None:
    embed = gerar_embed(color=0x7b68ee, title='Últimas notícias')
    embed.set_author(name='Notícias', url='https://www.criptofacil.com/ultimas-noticias/', icon_url='https://cdn3.iconfinder.com/data/icons/ballicons-reloaded-free/512/icon-70-512.png')
    embed.set_thumbnail(url='https://cdn3.iconfinder.com/data/icons/ballicons-reloaded-free/512/icon-70-512.png')
    embed.set_footer(text=f'Fonte: criptofacil\nPyBotBit © 2020 Wesley Dias', icon_url='https://avatars2.githubusercontent.com/u/56437612?s=88&u=c9ddcaa797c6a84031e4441c7f42fbc72ec6a4b1&v=4')

    list_noticias = PyBCoin.ultimas_noticias()
    for i, noticia in enumerate(list_noticias):
        embed.add_field(name=noticia['data'], value=f'{noticia["nome"]} [Leia sobre]({noticia["link"]})\n', inline=False)

    log(f'Notícias {list_noticias} enviadas com sucesso !')
    await message.channel.send(f'{message.author.mention} Encontrei estas noticias para você', embed=embed)


# ----------------------------------------------------------------------------------------------------------------------
# Loop de eventos, main()


def main() -> None:
    global client
    client = discord.Client(max_messages=None)

    @client.event
    async def on_ready() -> None:
        """
        on_ready(): Serve para criar um loop e executar tarefas quando o bot for iniciado com sucesso
        :return: None
        """
        log_menu()
        while True:
            log('Monitorando alertas...', True)
            await mudar_status('Verificando alertas', discord.Status.idle)
            await monitorar_alertas()

    @client.event
    async def on_disconnect() -> None:
        """
        on_disconnect(): Serve para retornar se o bot foi desconectado
        :return: None
        """
        log('PyBotBit foi desconectado', True)

    @client.event
    async def on_member_join(member: discord.Member) -> None:
        """
        :param member: discord.Member, objeto member recebido quando o usuário entrou
        :return: None
        """
        await gerar_dm(member)
        text = f'{member.mention} Seja bem vindo ! Meu nome é PyBotBit sou um robô, fui criado para te ajudar!\nDigite `!ajuda`'
        await member.dm_channel.send(text)

    @client.event
    async def on_message(message: discord.Message) -> None:
        """
        on_message(): Serve para obter mensagens enviadas pelos usuários e realizar tarefas a partir de comandos
        :param message: objeto da mensagem recebida
        :return: None
        """
        if message.author.id != client.user.id:
            author = message.author
            mensagem = message.content.lower()
            criado = True
            if mensagem.startswith('!'):
                await message.add_reaction(emoji='\U0001F504')
                log(f'Verificando comando enviado por: {author.name}, comando: {mensagem} ', True)
                async with message.channel.typing():
                    if mensagem == '!ajuda':
                        await mudar_status('Enviando ajuda', discord.Status.idle)
                        await ajuda(message)

                    elif mensagem == '!alertas':
                        await mudar_status('Enviando alertas', discord.Status.idle)
                        await meus_alertas(author, True)

                    elif mensagem == '!pizza':
                        await mudar_status('Enviando pizza', discord.Status.idle)
                        await pizza(message)

                    elif mensagem == '!noticias':
                        await mudar_status('Enviando notícias', discord.Status.idle)
                        await noticias(message)

                    elif mensagem == '!limpar':
                        await mudar_status('Limpando mensagens', discord.Status.idle)
                        await limpar_mensagens(message)

                    elif mensagem.startswith('!alertar') and len(mensagem.split()) == 4 and PyBCoin.verificador(mensagem[1:].split()[1]):
                        await mudar_status('Criando alerta', discord.Status.idle)
                        await criar_alerta(message)

                    elif mensagem.startswith('!delalertar') and len(mensagem.split()) == 2:
                        if not await remover_alerta(message):
                            criado = False
                    else:
                        try:
                            if PyBCoin.verificador(mensagem[1:].split()[0]) and len(mensagem[1:].split()) == 1:
                                await mudar_status('Buscando dados', discord.Status.idle)
                                await dados_criptomoedas(message)

                            elif PyBCoin.verificador(mensagem[1:].split()[0]) and len(mensagem[1:].split()) == 2:
                                await mudar_status('Fazendo cálculos', discord.Status.idle)
                                await calcular_criptomoeda(message)

                            else:
                                criado = False

                        except IndexError:
                            criado = False

                        finally:
                            if not criado:
                                log('Não entendi o comando solicitado')
                                await message.channel.send(f'{author.mention} Não entendi o seu comando `{message.content.lower()}`\nDigite `!ajuda` para conhecer os comandos disponíveis')

            else:
                log(f'Verificando mensagem enviada por: {author.name}', True)
                log('A mensagem enviada não era para mim')

            if criado and mensagem.startswith('!'):
                await message.add_reaction(emoji='\U00002705')

            elif not criado and mensagem.startswith('!'):
                await message.add_reaction(emoji='\U0000274C')

        await mudar_status('Online', discord.Status.online)

    print(' PyBotBit Copyright © 2020 Wesley Dias '.rjust(120, '-'))
    print('PyBotBit status: [LIGANDO]', end='')
    client.run('DIGITAR TOKEN DO BOT')


if __name__ == '__main__':
    main()
