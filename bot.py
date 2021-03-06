#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nonebot
from nonebot_adapter_gocq import Bot as GOCQBot

# Custom your logger

from nonebot.log import logger, default_format
logger.add("error.log",
           rotation="00:00",
           diagnose=False,
           level="ERROR",
           format=default_format)

# You can pass some keyword args config to init function
nonebot.init()
nonebot.get_driver().register_adapter("gocq", GOCQBot)
nonebot.load_from_toml("pyproject.toml")

nonebot.load_plugin("nonebot_plugin_status")

nonebot.load_plugins("awesome_bot/plugins")

app = nonebot.get_asgi()

# Modify some config / config depends on loaded configs
# 
# config = driver.config
# do something...


if __name__ == "__main__":
    nonebot.logger.warning("Always use `nb run` to start the bot instead of manually running!")
    nonebot.run(app="__mp_main__:app")
