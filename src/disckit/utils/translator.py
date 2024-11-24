import discord
import json


from pprint import pprint

from discord import app_commands
from typing import Optional

from disckit.config import UtilConfig


class LemmaTranslator(app_commands.Translator):
    async def load(self) -> None:
        """This gets called when the translator first gets loaded."""
        print("Lemma Translator has been loaded.")

        self.translations = {}
        for locale, path in UtilConfig.LEMMA_TRANS_PATHS.items():
            with open(path) as f:
                self.translations[locale] = json.load(f)

    async def unload(self) -> None:
        """This gets called when being removed."""

    async def translate(
        self,
        string: app_commands.locale_str,
        locale: discord.Locale,
        context: app_commands.TranslationContext,
    ) -> Optional[str]:
        """This function must return a string (that's been translated), or `None` to
        signal no available translation available, and will default to the original.

        Parameters
        ----------
        string :class:`app_commands.locale_str`
            The string that is requesting to be translated.
        locale :class:`discord.Locale`
            The target language to translate to.
        context :class:`app_commands.TranslationContext`
            The origin of the requested string context.
        """
        # message_str = string.message.lower().strip()
        # for mark in self.IGNORE_MARKS:
        #    message_str = message_str.replace(mark, "")
        #
        # if message_str == "supports all urls and search queries":
        #    return "सभी URL और खोज क्वेरी का समर्थन करता है |"

        pprint(f"EXTRA: {string.extras}\nMESSAGE: {string.message}")
        print()
        print()
        print("DATA-")
        pprint(context.data)
        print()
        print("LOCATION-")
        print(context.location)
        print()
        print()

        # print("\nREQUESTED:", string.message)
