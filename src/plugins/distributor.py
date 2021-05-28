import os
from nonebot import on_command, require, get_bots
from nonebot.rule import to_me
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from src.configs import *

delete_file = on_command("del", rule=to_me(), priority=5)
sync_file = on_command("sync", rule=to_me(), priority=10)


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


@sync_file.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if args:
        await sync_file.reject("sync 指令不支持参数！")
    else:
        await check_and_upload()
        await sync_file.finish("文件同步完成！")


async def check_and_upload():
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
                await sync_file.send(f"群 {group} 同步成功！")


scheduler = require('nonebot_plugin_apscheduler').scheduler
scheduler.add_job(check_and_upload, "cron", hour="4")
