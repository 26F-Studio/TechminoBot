import os
from nonebot import on_command, require, get_bots
from nonebot.config import Config
from nonebot.rule import to_me
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from src.configs import *


async def admin_and_to_me(bot: Bot, event: Event, state: T_State) -> bool:
    return event.is_tome() and event.get_user_id() in SUPERUSERS


delete_file = on_command("del", rule=admin_and_to_me, priority=5)
sync_file = on_command("sync", rule=admin_and_to_me, priority=10)
broadcast = on_command("broadcast", rule=admin_and_to_me, priority=10)
publish_notice = on_command("notice", rule=admin_and_to_me, priority=5)


@delete_file.handle()
async def handle_first_receive(bot: Bot, event: Event):
    args = str(event.get_message()).strip()
    if args:
        await delete_file.reject("del 指令不支持参数！")
    else:
        for group in DIST_GROUPS:
            files = await bot.call_api("get_group_root_files", group_id=group)
            await delete_all(bot, files["folders"])
            await sync_file.send(f"群 {group} 删除文件成功！")
        await delete_file.finish("文件删除成功！")


@sync_file.handle()
async def handle_first_receive(bot: Bot, event: Event):
    args = str(event.get_message()).strip()
    if args:
        await sync_file.reject("sync 指令不支持参数！")
    else:
        await check_and_upload(True)
        await sync_file.finish("文件同步完成！")


@broadcast.handle()
async def handle_first_receive(bot: Bot, event: Event):
    args = str(event.get_message()).strip()
    if args:
        await broadcast_all(bot, args)
        await broadcast.finish("广播消息发送成功！")
    else:
        await broadcast.reject("broadcast 指令需要一个参数！")


@publish_notice.handle()
async def handle_first_receive(bot: Bot, event: Event):
    args = str(event.get_message()).strip()
    print(args)
    if args:
        await notice_all(bot, args)
        await publish_notice.finish("公告发布成功！")
    else:
        await publish_notice.reject("notice 指令需要一个参数！")


async def delete_all(bot: Bot, folders):
    for folder in folders:
        if folder["folder_name"] == "Techmino正式版(禁止外传)":
            files = await bot.call_api(
                "get_group_files_by_folder",
                group_id=folder["group_id"],
                folder_id=folder["folder_id"]
            )
            for file in files["files"]:
                await bot.call_api(
                    "delete_group_file",
                    group_id=folder["group_id"],
                    folder_id=folder["folder_id"],
                    file_id=file["file_id"],
                    bus_id=file["busid"]
                )


async def check_and_upload(show_progress):
    bot = get_bots()["2920573475"]
    for group in DIST_GROUPS:
        root_fs = await bot.call_api("get_group_root_files", group_id=group)
        for folder in root_fs["folders"]:
            if folder["folder_name"] == "Techmino正式版(禁止外传)":
                group_file_list = []
                upload_file_list = []
                files = await bot.call_api(
                    "get_group_files_by_folder",
                    group_id=folder["group_id"],
                    folder_id=folder["folder_id"]
                )
                if files["files"]:
                    for new_file in files["files"]:
                        group_file_list.append(new_file)

                distribution_directory = r"C:\Public\TechminoDistribution"
                for _, _, local_filenames in os.walk(distribution_directory, topdown=False):
                    for local_filename in local_filenames:
                        is_found = False
                        for new_file in group_file_list:
                            if local_filename == new_file["file_name"]:
                                group_file_list.remove(new_file)
                                is_found = True
                                break
                        if not is_found:
                            upload_file_list.append(local_filename)

                for new_file in group_file_list:
                    await bot.call_api(
                        "delete_group_file",
                        group_id=folder["group_id"],
                        folder_id=folder["folder_id"],
                        file_id=new_file["file_id"],
                        bus_id=new_file["busid"]
                    )

                for new_file in upload_file_list:
                    await bot.call_api(
                        "upload_group_file",
                        group_id=folder["group_id"],
                        file=os.path.join(distribution_directory, new_file),
                        name=new_file,
                        folder=folder["folder_id"]
                    )
                if show_progress:
                    await sync_file.send(f"群 {group} 同步成功！")


async def broadcast_all(bot: Bot, message):
    for group in DIST_GROUPS:
        message_id = await bot.call_api("send_group_msg", group_id=group, message=message)


async def notice_all(bot: Bot, notice):
    for group in DIST_GROUPS:
        await bot.call_api("_send_group_notice", group_id=group, content=notice)


scheduler = require('nonebot_plugin_apscheduler').scheduler
scheduler.add_job(check_and_upload, "cron", hour="4", args=[False])
