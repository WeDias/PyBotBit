# ------------------------------------------------------------- #
#                                          PyBotBit             #
#                                       Github:@WeDias          #
#                                    Licença: MIT License       #
#                                Copyright © 2020 Wesley Dias   #
# ------------------------------------------------------------- #

import discord
import PyBCoin

cliente = discord.Client()


@cliente.event
async def on_message(message):
    if message.content.lower() == '!ajuda':
        embed = discord.Embed(color=0x12BCEC)
        embed.set_thumbnail(url='https://images.emojiterra.com/google/android-nougat/512px/2753.png')
        embed.set_author(name='PyBotBit Ajuda', url='https://github.com/wedias', icon_url='https://images.emojiterra.com/google/android-nougat/512px/2753.png')
        embed.add_field(name='Para que serve ?', value='PyBotBit é capaz de informar dados de preço e variação de qualquer criptomoeda listada no coinmarketcap, e informar o preço atual do dolar', inline=False)
        embed.add_field(name='Como usar ?', value='Para utilizar digite no chat !nome-da-criptomoeda\nEx.: `!bitcoin`\nEntão o PyBotBit retornará dados sobre a criptomoeda escolhida\nNo exemplo utilizado acima retornaria dados do bitcoin', inline=False)
        embed.add_field(name='Observação.', value='Caso o nome da criptomeda seja separado por espaço como por exemplo bitcoin cash\nFavor trocar os espaços por -\nEx: `!bitcoin-cash`', inline=False)
        embed.add_field(name='GitHub', value='https://github.com/wedias', inline=False)
        embed.set_footer(text='PyBotBit © 2020 Wesley Dias', icon_url='https://avatars2.githubusercontent.com/u/56437612?s=88&u=c9ddcaa797c6a84031e4441c7f42fbc72ec6a4b1&v=4')
        await message.channel.send(embed=embed)

    elif message.content.lower().startswith('!'):
        criptomoeda = message.content.lower()[1:]
        try:
            dados = PyBCoin.buscar_dados(criptomoeda)
            if criptomoeda == 'dolar':
                embed = discord.Embed(color=0x228B22)
                embed.set_author(name=dados['nome'], url=f'https://dolarhoje.com', icon_url=dados['imagem'])
                embed.set_thumbnail(url=dados['imagem'])
                embed.add_field(name='Valor', value=f'R$ {dados["preco"]}')
                embed.set_footer(text=f'Fonte: {dados["fonte"]}\nPyBotBit © 2020 Wesley Dias', icon_url='https://avatars2.githubusercontent.com/u/56437612?s=88&u=c9ddcaa797c6a84031e4441c7f42fbc72ec6a4b1&v=4')
                await message.channel.send(embed=embed)

            else:
                if dados['variação'] > 0:
                    cor = 0x228B22
                    dados['variação'] = f'+{dados["variação"]}'
                else:
                    cor = 0xB22222
                embed = discord.Embed(color=cor)
                embed.set_author(name=dados['nome'], url=f'https://coinmarketcap.com/currencies/{criptomoeda}/', icon_url=dados['imagem'])
                embed.set_thumbnail(url=dados['imagem'])
                embed.add_field(name='Rank', value=f'#{dados["rank"]}')
                embed.add_field(name='Valor', value=f'USD {dados["preco"]}')
                embed.add_field(name='variação (24H)', value=f'{dados["variação"]}%')
                embed.add_field(name='Volume (24H)', value=f'USD {PyBCoin.adicinar_pontos(dados["volume"])}')
                embed.add_field(name='Market Cap', value=f'USD {PyBCoin.adicinar_pontos(dados["market_cap"])}')
                embed.set_footer(text=f'Fonte: {dados["fonte"]}\nPyBotBit © 2020 Wesley Dias', icon_url='https://avatars2.githubusercontent.com/u/56437612?s=88&u=c9ddcaa797c6a84031e4441c7f42fbc72ec6a4b1&v=4')
                await message.channel.send(embed=embed)

        except Exception as erro:
            print(erro)
            await message.channel.send(f'Desculpe, mas não entendi este comando `!{criptomoeda}`\nPor favor, utilize `!ajuda`')


cliente.run('INFORMAR O TOKEN AQUI')
