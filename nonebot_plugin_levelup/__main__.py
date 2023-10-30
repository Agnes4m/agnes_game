from typing import Awaitable, Callable, List

from nonebot import on_command
from nonebot.adapters import Event, Message
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, CommandArg
from nonebot.typing import T_State
from nonebot_plugin_saa import Image, MessageFactory, Text
from nonebot_plugin_session import SessionId, SessionIdType

from .config import config
from .draw import draw_user_card_overview, draw_user_profile, i2b
from .error import handle_error
from .message import ErrorMsg, InfoMsg, SendMsg, WarningMsg
from .vrchat import (
    ApiClient,
    ApiException,
    CurrentUser,
    LimitedUserModel,
    NotLoggedInError,
    TwoFactorAuthError,
    get_all_friends,
    get_client,
    get_login_info,
    get_or_random_client,
    get_user,
    login_via_password,
    remove_login_info,
    search_users,
    search_worlds,
)

KEY_ARG = "arg"
KEY_CLIENT = "client"
KEY_LOGIN_INFO = "login_info"
KEY_OVERRIDE_LOGIN_INFO = "override_login_info"
KEY_USERNAME = "username"
KEY_PASSWORD = "password"
KEY_VERIFY_FUNC = "verify_func"
KEY_VERIFY_CODE = "verify_code"
KEY_CURRENT_USER = "current_user"
KEY_SEARCH_RESP = "search_resp"

HELP = """--------vrc指令--------
1、【vrc登录】 | 登录vrc账户，建议私聊
2、【vrc全部好友】 | 获取全部好友信息
3、【vrc查询用户】【text】 | 查询玩家
4、【vrc查询世界】【text】 | 查询世界"""

vrc_help = on_command("vrchelp", aliases={"vrc帮助"}, priority=20)
vrc_login = on_command("vrcl", aliases={"vrc登录"}, priority=20)
friend_request = on_command("vrcrq", aliases={"vrc全部好友"}, priority=20)
search_user = on_command("vrcsu", aliases={"vrc查询用户"}, priority=20)
world_search = on_command("vrcws", aliases={"vrc查询世界"}, priority=20)


@vrc_help.handle()
async def _(matcher: Matcher):
    await matcher.finish(HELP)


@vrc_login.handle()
async def _(
    matcher: Matcher,
    state: T_State,
    session_id: str = SessionId(SessionIdType.USER),
    arg_msg: Message = CommandArg(),
):
    try:
        login_info = get_login_info(session_id)
    except NotLoggedInError:
        login_info = None

    if arg_msg.extract_plain_text().strip():
        if login_info:
            state[KEY_OVERRIDE_LOGIN_INFO] = True
        matcher.set_arg(KEY_LOGIN_INFO, arg_msg)
        return  # skip

    # no arg
    if login_info:
        state[KEY_USERNAME] = login_info.username
        state[KEY_PASSWORD] = login_info.password
        await matcher.send(InfoMsg.Relogin)
        return  # skip

    await matcher.pause(SendMsg.Sendlgoin)


@vrc_login.handle()
async def _(
    matcher: Matcher,
    event: Event,
    state: T_State,
    session_id: str = SessionId(SessionIdType.USER),
):
    if (KEY_USERNAME in state) and (KEY_PASSWORD in state):
        username: str = state[KEY_USERNAME]
        password: str = state[KEY_PASSWORD]
    else:
        if KEY_LOGIN_INFO in state:
            arg_msg: Message = state[KEY_LOGIN_INFO]
            del state[KEY_LOGIN_INFO]
            arg = arg_msg.extract_plain_text()
        else:
            arg = event.get_plaintext()

        arg = arg.strip()
        if arg == "0":
            await matcher.finish(InfoMsg.Dislogin)

        parsed = arg.split(" ")
        if len(parsed) != 2:
            await matcher.reject(WarningMsg.Resendlgoin)
        username, password = parsed

    if KEY_OVERRIDE_LOGIN_INFO in state:
        await matcher.send(WarningMsg.Overwrite)

    try:
        current_user = await login_via_password(session_id, username, password)

    except TwoFactorAuthError as e:
        state[KEY_VERIFY_FUNC] = e.verify_func
        secs = config.session_expire_timeout.seconds
        await matcher.pause(f"请在 {secs} 秒内发送 收到的邮箱验证码 或者 2FA验证码")

    except ApiException as e:
        if e.status == 401:
            if KEY_USERNAME in state:
                del state[KEY_USERNAME]
            if KEY_PASSWORD in state:
                del state[KEY_PASSWORD]
            await matcher.reject(ErrorMsg.login)

        logger.error(f"Api error when logging in: [{e.status}] {e.reason}")
        remove_login_info(session_id)
        await matcher.finish(f"服务器返回异常：[{e.status}] {e.reason}")

    except Exception:
        logger.exception("Exception when logging in")
        remove_login_info(session_id)
        await matcher.finish(ErrorMsg.Unkown)

    state[KEY_CURRENT_USER] = current_user


@vrc_login.handle()
async def _(
    matcher: Matcher,
    state: T_State,
    event: Event,
    session_id: str = SessionId(SessionIdType.USER),
):
    if KEY_CURRENT_USER in state:
        return  # skip

    verify_code = event.get_plaintext().strip()
    if not verify_code.isdigit():
        await matcher.reject(ErrorMsg.Format2FA)

    verify_func: Callable[[str], Awaitable[CurrentUser]] = state[KEY_VERIFY_FUNC]
    try:
        current_user = await verify_func(verify_code)

    except ApiException as e:
        if e.status == 401:
            await matcher.reject(ErrorMsg.Error2FA)

        logger.error(f"Api error when verifying 2FA code: [{e.status}] {e.reason}")
        remove_login_info(session_id)
        await matcher.finish(f"服务器返回异常：[{e.status}] {e.reason}")

    except Exception:
        logger.exception("Exception when verifying 2FA code")
        remove_login_info(session_id)
        await matcher.finish(ErrorMsg.Unkown)

    state[KEY_CURRENT_USER] = current_user


@vrc_login.handle()
async def _(matcher: Matcher, state: T_State):
    current_user: CurrentUser = state[KEY_CURRENT_USER]
    await matcher.finish(f"登录成功，欢迎，{current_user.display_name}")


@friend_request.handle()
async def _(
    matcher: Matcher,
    session_id: str = SessionId(SessionIdType.USER),
):
    try:
        client = await get_client(session_id)
        resp = [x async for x in get_all_friends(client)]
    except Exception as e:
        await handle_error(matcher, e)

    if not resp:
        await matcher.finish(InfoMsg.NoFriend)

    try:
        pic = i2b(await draw_user_card_overview(resp, client=client))
    except Exception as e:
        await handle_error(matcher, e)

    await MessageFactory(Image(pic)).finish()


@search_user.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    if arg.extract_plain_text().strip():
        matcher.set_arg(KEY_ARG, arg)


@search_user.got(KEY_ARG, prompt=SendMsg.User)
async def _(
    matcher: Matcher,
    state: T_State,
    arg: str = ArgPlainText(KEY_ARG),
    session_id: str = SessionId(SessionIdType.USER),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject(SendMsg.SearchNone)

    try:
        client = await get_or_random_client(session_id)
        resp = [x async for x in search_users(client, arg)]
    except Exception as e:
        await handle_error(matcher, e)

    if not resp:
        await matcher.finish("没搜到任何玩家捏")

    state[KEY_CLIENT] = client
    state[KEY_SEARCH_RESP] = resp
    # if len(resp) == 1:
    #     return  # skip

    try:
        resp = [x async for x in search_users(client, arg, max_size=10)]
        pic = i2b(await draw_user_card_overview(resp, group=False, client=client))
    except Exception as e:
        await handle_error(matcher, e)

    await MessageFactory(
        [
            Text(f"搜索到以下 {len(resp)} 个玩家"),
            # Text(f"搜索到以下 {len(resp)} 个玩家，发送序号查看玩家详情，发送 0 取消选择"),
            Image(pic),
        ],
    ).finish()  # .pause()


# TODO 没做完
@search_user.handle()
async def _(matcher: Matcher, state: T_State, event: Event):
    client: ApiClient = state[KEY_CLIENT]
    resp: List[LimitedUserModel] = state[KEY_SEARCH_RESP]

    if len(resp) == 1:
        index = 0
    else:
        arg = event.get_plaintext().strip()
        if arg == "0":
            await matcher.finish(InfoMsg.Deselect)

        if not arg.isdigit():
            await matcher.reject(SendMsg.OrdinalFormat)

        index = int(arg) - 1
        if not (0 <= index < len(resp)):
            await matcher.reject(SendMsg.OrdinalRange)

    user_id = resp[index].user_id
    try:
        user = await get_user(client, user_id)
        pic = i2b(await draw_user_profile(user))
    except Exception as e:
        await handle_error(matcher, e)

    await MessageFactory(Image(pic)).finish()


@world_search.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    if arg.extract_plain_text().strip():
        matcher.set_arg(KEY_ARG, arg)


@world_search.got(KEY_ARG, prompt=SendMsg.Map)
async def _(
    matcher: Matcher,
    arg: str = ArgPlainText(KEY_ARG),
    session_id: str = SessionId(SessionIdType.USER),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject(SendMsg.SearchNone)

    try:
        client = await get_or_random_client(session_id)
        worlds = [x async for x in search_worlds(client, arg, max_size=10)]
    except Exception as e:
        await handle_error(matcher, e)

    if not worlds:
        await matcher.finish(SendMsg.NoMap)

    len_worlds = len(worlds)
    msg_factory = MessageFactory(f"搜索到以下 {len_worlds} 个地图")
    for i, wld in enumerate(worlds, 1):
        msg_factory += Image(wld.thumbnail_image_url)
        msg_factory += f"{i}. {wld.name}\n作者：{wld.author_name}\n创建日期：{wld.created_at}"
        if i != len_worlds:
            msg_factory += "\n-\n"

    await msg_factory.finish()