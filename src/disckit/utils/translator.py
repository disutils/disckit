import asyncio
import discord
import json
import os

from pprint import pprint
from discord import app_commands, Locale
from discord.ext.commands import Bot
from typing import Optional, TypeAlias, Dict, List

from disckit.config import UtilConfig
from disckit.errors import LemmaLoadError

_TransMap: TypeAlias = Dict[str, str]


class LemmaTranslator(app_commands.Translator):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.command_trans: _TransMap = {}
        self.command_desc_trans: _TransMap = {}
        self.paramter_trans: _TransMap = {}
        self.paramter_desc_trans: _TransMap = {}
        self.group_trans: _TransMap = {}
        self.group_desc_trans: _TransMap = {}

    @classmethod
    async def setup(cls, bot: Bot, tree: app_commands.CommandTree) -> None:
        loop = asyncio.get_event_loop()
        loop.create_task(tree.set_translator(cls(bot)))

    def __get_groups(
        self,
        group: app_commands.Group,
        all_groups: Optional[List[app_commands.Group]] = None,
    ) -> List[app_commands.Group]:
        all_groups = all_groups or []
        all_groups.append(group)

        if group.parent is None:
            return all_groups

        self.__get_groups(group.parent, all_groups)

    async def load(self) -> None:
        """This gets called when the translator first gets loaded."""

        # print("Lemma Translator is loading", end="", flush=True)
        await self.bot.wait_until_ready()
        print("START\n\n")

        self.command_trans.clear()
        self.command_desc_trans.clear()
        self.paramter_trans.clear()
        self.paramter_desc_trans.clear()
        self.group_trans.clear()
        self.group_desc_trans.clear()
        # Clearing them in the case of reloading the Translator.

        temp_cmd_trans: List[str] = []
        temp_grp_trans: List[str] = []

        for cmd in self.bot.walk_commands():
            print("COMMAND / GROUP:", cmd.name)
            if isinstance(cmd, app_commands.Command):
                # self.command_trans[Locale.american_english][cmd.name] = ""
                # print("COMMAND:", cmd.name)
                print("COMMAND")

                temp_cmd_trans.append(cmd.name)
                temp_cmd_trans.append(cmd.description)
                # self.command_desc_trans[cmd.description] = ""
                for p in cmd.parameters:
                    temp_cmd_trans.append(cmd.name)
                    temp_cmd_trans.append(p.name)
                    temp_cmd_trans.append(p.description)
                    # self.paramter_trans[p.name] = ""
                    # self.paramter_desc_trans[p.description] = ""

            elif isinstance(cmd, app_commands.Group):
                print("GROUP")
                groups = self.__get_groups(cmd)
                for group in groups:
                    self.group_trans[Locale.american_english][group.name] = ""
                    temp_grp_trans.append(group.name)
                    temp_grp_trans.append(group.description)

                    # self.group_desc_trans[group.description] = ""

        # print(end=".")

        print("\n\nTEMP CMDS-\n")
        pprint(temp_cmd_trans)

        total_temp_cmd = len(temp_cmd_trans)
        # total_temp_groups = len(temp_grp_trans)

        if UtilConfig.LEMMA_TRANS_COMMANDS:  # if UtilConfig.LEMMA_TRANS_GROUPS:
            print("IDENTIFY")
            for (
                locale,
                path,
            ) in (
                UtilConfig.LEMMA_TRANS_COMMANDS.items()
            ):  # CHANGEEEEEEEEEEEEEEEEEEEEEEEE
                self.command_trans.setdefault(locale, {})
                self.command_desc_trans.setdefault(locale, {})
                self.paramter_trans.setdefault(locale, {})
                self.paramter_desc_trans.setdefault(locale, {})
                self.group_trans.setdefault(locale, {})
                self.group_desc_trans.setdefault(locale, {})

                if os.path.isfile(path):
                    with open(path, encoding="utf8") as f:
                        data = json.load(f)
                        for cmd_name in data:
                            self.command_trans[locale][cmd_name] = data[cmd_name][
                                "command_name"
                            ]

                            cmd_data = temp_cmd_trans.index(cmd_name)
                            description = temp_cmd_trans[cmd_data + 1]
                            self.command_desc_trans[locale][description] = data[
                                cmd_name
                            ]["command_description"]

                            for i in range(cmd_data + 1, total_temp_cmd, 3):
                                if temp_cmd_trans[i + 1] != cmd_name:
                                    break

                                param_name = temp_cmd_trans[i + 2]
                                param_desc = temp_cmd_trans[i + 3]
                                self.paramter_trans[locale][param_name] = data[
                                    cmd_name
                                ]["parameter_name"].get(param_name, None)
                                self.paramter_trans[locale][param_desc] = data[
                                    cmd_name
                                ]["parameter_description"].get(param_name, None)

                elif os.path.isdir(path):
                    ...

                else:
                    error_code = 1
                    raise LemmaLoadError(
                        f"Invalid path set to `UtilConfig.LEMMA_TRANS_GROUPS`. {error_code=}",
                        error_code,
                    )

        # if UtilConfig.LEMMA_TRANS_COMMANDS:
        #    for locale, path in UtilConfig.LEMMA_TRANS_GROUPS.items():
        #        if os.path.isfile(path):
        #            with open(path, encoding="utf8") as f:
        #                data = json.load(f)
        #                for cmd_name in data:
        #                    self.command_trans[cmd_name] = data[cmd_name][
        #                        "command_name"
        #                    ]
        #                    self.command_desc_trans[cmd_name] = data[cmd_name][
        #                        "command_description"
        #                    ]
        #
        #        elif os.path.isdir(path):
        #            ...
        #
        #        else:
        #            error_code = 1
        #            raise LemmaLoadError(
        #                f"Invalid path set to `UtilConfig.LEMMA_TRANS_COMMANDS`. {error_code=}",
        #                error_code,
        #            )

        else:
            error_code = 2
            raise LemmaLoadError(
                f"`UtilConfig.LEMMA_TRANS_COMMANDS` was not defined to get command translations. {error_code=}",
                error_code,
            )

        # try:
        #     command_items = UtilConfig.LEMMA_TRANS_COMMANDS.items()
        #     for locale, path in command_items:
        #         with open(path) as f:
        #             self.translations[locale] = json.load(f)
        # except (
        #     AttributeError
        # ):  # Raised when `UtilConfig.LEMMA_TRANS_COMMANDS` is not defined.
        #     raise LemmaLoadError(
        #         "`UtilConfig.LEMMA_TRANS_COMMANDS` was not defined to get command translations."
        #     )

        # print(".")
        print("Lemma translator has successfully loaded.")

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
        print("GROUP-")

        # print("\nREQUESTED:", string.message)
