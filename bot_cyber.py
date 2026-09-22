import discord
from discord.ext import commands

from quiz_cyber import QUIZZES

from datacyber import (
    criar_usuario,
    salvar_resposta,
    ranking
)

token = "SEU_TOKEN_AQUI"

intents = discord.Intents.default()
intents.message_content = True


bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


quiz_atual = None
respostas = {}


class QuizView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    async def responder(
        self,
        interaction: discord.Interaction,
        alternativa: str
    ):
        global quiz_atual

        if quiz_atual is None:
            await interaction.response.send_message(
                "não há nenhum quiz ativo.",
                ephemeral=True
            )
            return

        usuario = interaction.user

        criar_usuario(
            usuario.id,
            usuario.display_name
        )

        respostas[usuario.id] = alternativa

        await interaction.response.send_message(
            f"você respondeu **{alternativa}**!",
            ephemeral=True
        )

    @discord.ui.button(
        label="a",
        style=discord.ButtonStyle.secondary
    )
    async def botao_a(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.responder(interaction, "a")

    @discord.ui.button(
        label="b",
        style=discord.ButtonStyle.secondary
    )
    async def botao_b(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.responder(interaction, "b")

    @discord.ui.button(
        label="c",
        style=discord.ButtonStyle.secondary
    )
    async def botao_c(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.responder(interaction, "c")

    @discord.ui.button(
        label="d",
        style=discord.ButtonStyle.secondary
    )
    async def botao_d(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.responder(interaction, "d")


async def enviar_quiz(canal):

    global quiz_atual

    quiz_atual = QUIZZES[0]

    respostas.clear()

    quiz = quiz_atual

    embed = discord.Embed(
        title=(
            f"quiz #{quiz['id']} — "
            f"{quiz['categoria']}"
        ),
        description=(
            f"🟢 **dificuldade:** "
            f"{quiz['dificuldade']}\n\n"

            f"**{quiz['texto']}**\n\n"

            f"a) {quiz['alternativas']['a']}\n"
            f"b) {quiz['alternativas']['b']}\n"
            f"c) {quiz['alternativas']['c']}\n"
            f"d) {quiz['alternativas']['d']}\n\n"

            "👇 clique em um botão para responder.\n\n"
            "⏰ a resposta será revelada mais tarde!"
        )
    )

    await canal.send(
        embed=embed,
        view=QuizView()
    )


async def revelar_quiz(canal):

    global quiz_atual

    if quiz_atual is None:
        await canal.send(
            "não há nenhum quiz ativo."
        )
        return

    quiz = quiz_atual
    correta = quiz["correta"]

    for usuario_id, resposta in respostas.items():

        acertou = resposta == correta

        salvar_resposta(
            usuario_id,
            quiz["id"],
            resposta,
            acertou
        )

    texto_alternativas = ""

    for letra, texto in quiz["alternativas"].items():

        if letra == correta:
            texto_alternativas += (
                f"🟩 **{letra}) {texto}** ✅\n"
            )
        else:
            texto_alternativas += (
                f"~~{letra}) {texto}~~\n"
            )

    dados_ranking = ranking(3)

    top = ""

    medalhas = {
        1: "🥇",
        2: "🥈",
        3: "🥉"
    }

    for posicao, (
        usuario_id,
        nome,
        pontos
    ) in enumerate(
        dados_ranking,
        start=1
    ):
        top += (
            f"{medalhas[posicao]} "
            f"{nome} — **{pontos} pts**\n"
        )

    if not top:
        top = "ainda não há pontuação."

    embed = discord.Embed(
        title=(
            f"✅ resposta — quiz #{quiz['id']} "
            f"({quiz['categoria']})"
        ),
        description=(
            f"{texto_alternativas}\n"
            f"**explicação:** "
            f"{quiz['explicacao']}\n\n"
            f"🏆 **ranking:**\n"
            f"{top}"
        )
    )

    await canal.send(embed=embed)


@bot.command()
async def pergunta(ctx):

    await enviar_quiz(ctx.channel)


@bot.command()
async def resposta(ctx):

    await revelar_quiz(ctx.channel)


@bot.event
async def on_ready():

    print(
        f"bot conectado como {bot.user}"
    )


bot.run(token)