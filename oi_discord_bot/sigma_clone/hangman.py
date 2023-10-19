"""
Apex Sigma: The Database Giant Discord Bot.
Copyright (C) 2019  Lucia's Cipher

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import asyncio
import secrets
import random
import discord

from sigma_clone.generic_responses import GenericResponse
from sigma_clone.gallows_core import Gallows
from sigma_clone.ongoing import Ongoing
from wiktionaryparser import WiktionaryParser
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(" "message)s",
    handlers=[logging.FileHandler("oi.log"), logging.StreamHandler()],
)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

parser = WiktionaryParser()

NAME = "Hangman"


def load_words():
    with open("words_alpha.txt") as word_file:
        valid_words = set(word_file.read().split())

    long_words = [word for word in valid_words if len(word) > 3]
    return long_words


english_words = load_words()


def get_definition(word):
    """
    :type word: str
    :rtype: str
    """
    definition = ""
    query = parser.fetch(word)
    if len(query) > 0 and query[0]["definitions"]:
        for i in range(len(query[0]["definitions"])):
            definition += f'{query[0]["definitions"][i]["partOfSpeech"]}:\n'
            for j in range(len(query[0]["definitions"][i]["text"])):
                if j == 0:
                    definition += f'{query[0]["definitions"][i]["text"][j]}\n'
                else:
                    if j > 4:
                        break
                    definition += f'{j}: {query[0]["definitions"][i]["text"][j]}\n'

            definition += "\n"
    else:
        log.error(f"No definition found for {word}")
        return "No definition found on wiktionary... :("

    return definition


def generate_response(gallows):
    """
    :type gallows: sigma.modules.minigames.quiz.hang_man.core.Gallows
    :rtype: discord.Embed
    """
    hangman_resp = discord.Embed(color=0x3B88C3, title="🔣 Hangman")
    hangman_resp.add_field(
        name="Gallows", value=f"```\n{gallows.make_gallows_man()}\n```", inline=False
    )
    used_letters = (
        ", ".join(sorted(gallows.wrong_letters))
        if gallows.wrong_letters
        else "Nothing Yet."
    )
    hangman_resp.add_field(name="Used Letters", value=used_letters, inline=False)
    hangman_resp.add_field(name="Word", value=gallows.make_word_space(), inline=False)
    return hangman_resp


async def send_hangman_msg(message, hangman_msg, hangman_resp):
    """
    :type message: discord.Message
    :type hangman_msg: discord.Message
    :type hangman_resp: discord.Embed
    :rtype: discord.Message
    """
    if hangman_msg:
        try:
            await hangman_msg.edit(embed=hangman_resp)
        except discord.NotFound:
            hangman_msg = await message.channel.send(embed=hangman_resp)
    else:
        hangman_msg = await message.channel.send(embed=hangman_resp)
    return hangman_msg


async def hangman(bot, db, message, funny=False):
    if not Ongoing.is_ongoing(NAME, message.channel.id):
        Ongoing.set_ongoing(NAME, message.channel.id)
        if random.random() > 0.01 and not funny:
            word = secrets.choice(english_words)
            word_description = get_definition(word)
        else:
            # funny word
            word_tup = db.get_random_word()
            if word_tup:
                word, word_description = word_tup
            else:
                log.error("No funny words found in database!!!")
                word = secrets.choice(english_words)
                word_description = get_definition(word)
        gallows = Gallows(word)
        author = message.author.display_name
        hangman_resp = generate_response(gallows)
        hangman_msg = await message.channel.send(embed=hangman_resp)

        def check_answer(msg):
            """
            Checks if the answer message is correct.
            :type msg: discord.Message
            :rtype: bool
            """
            if message.channel.id != msg.channel.id:
                return
            if message.author.id != msg.author.id:
                return
            if len(msg.content) == 1:
                if msg.content.isalpha():
                    correct = True
                else:
                    correct = False
            else:
                correct = False
            return correct

        finished = False
        timeout = False
        while not timeout and not finished:
            try:
                answer_message = await bot.wait_for(
                    "message", check=check_answer, timeout=30
                )
                letter = answer_message.content.lower()
                if letter in gallows.word:
                    if letter not in gallows.right_letters:
                        gallows.right_letters.append(letter)
                else:
                    if letter.upper() not in gallows.wrong_letters:
                        gallows.wrong_letters.append(letter.upper())
                        gallows.use_part()
                hangman_msg = await send_hangman_msg(
                    message, hangman_msg, generate_response(gallows)
                )
                finished = gallows.victory or gallows.dead
            except asyncio.TimeoutError:
                timeout = True
                timeout_title = "🕙 Time's up!"
                timeout_embed = discord.Embed(color=0x696969, title=timeout_title)
                timeout_embed.add_field(
                    name=f"It was {gallows.word}.", value=word_description
                )
                await message.channel.send(embed=timeout_embed)

        if gallows.dead:
            lose_title = f"💥 Ooh, sorry {author}, it was {gallows.word}."
            final_embed = discord.Embed(color=0xFF3300, title=lose_title)
            db.increment_hangman_lb(message.author.id, False)
            await message.channel.send(embed=final_embed)
        elif gallows.victory:
            db.increment_hangman_lb(message.author.id, True)
            win_title = f"🎉 Correct, {author}, it was {gallows.word}!"
            win_embed = discord.Embed(color=0x77B255, title=win_title)
            await message.channel.send(embed=win_embed)

        if Ongoing.is_ongoing(NAME, message.channel.id):
            Ongoing.del_ongoing(NAME, message.channel.id)
    else:
        ongoing_error = GenericResponse("There is one already ongoing.").error()
        await message.channel.send(embed=ongoing_error)
