import asyncio
import json
import logging
import logging.config
import threading
from queue import Empty, Queue
from typing import NamedTuple

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message
from cloudevents.sdk.event import v1
from dapr.ext.grpc import App, InvokeMethodRequest, InvokeMethodResponse

from config import load_config
from formatting import format_telegram_message, split_news_into_chunks


class DigestItem(NamedTuple):
    """Digest item - text + url."""

    text: str
    url: str


class UserMessage(NamedTuple):
    """User message - chat id to send to and the digest."""

    chat_id: int
    digest: list[DigestItem]


config = load_config()
logging.config.dictConfig(config.logging.settings)
logger = logging.getLogger(__name__)

bot = Bot(config.bot.token)
dp = Dispatcher()
app = App()
q = Queue()


@dp.message(Command(commands='start'))
async def welcome_new_user(message: Message) -> None:
    """Welcomes the new user and returns the chat id."""

    logger.info(f'User {message.from_user.id} did a /start, answering.')
    await message.answer(
        f'Welcome to the Zion-net homework bot! Your chat id is {message.from_user.id}\n'
        'Use it for registration. You can always get it by using a /start command.'
    )


async def send_digest_to_user(user_id: int, message: list[DigestItem]) -> None:
    """Sends the digest to a specific chat id."""

    logger.info('Sending result to user')
    if not user_id:
        logger.error('Cannot send a message to a user with no user chat id. Skipping.')
        return
    if not message:
        await bot.send_message(chat_id=user_id, text='Sorry, no new news yet, come back later!')
    logger.info(f'Sending digest to user with chat_id {user_id}')
    valid_chunks = split_news_into_chunks(news_list=message, max_len=config.bot.max_text_length)
    formatted_chunks = format_telegram_message(valid_chunks)
    try:
        for chunk in formatted_chunks:
            await bot.send_message(chat_id=user_id, text=chunk)
            await asyncio.sleep(1)
    except TelegramBadRequest:
        logger.error(f'Looks like the user has deleted the chat, or the contact {user_id} is invalid')
    else:
        logger.info('Digest was sent to the user')


@app.subscribe(pubsub_name=config.service.pubsub, topic=config.service.topic)
def queue_listener(event: v1.Event) -> None:
    """Subscribes to the reports pubsub."""

    data = json.loads(event.Data())
    logger.info('Received event')
    if data['subject'] != 'report_ready':
        logger.info(f'The event is not for {config.service_name}')
        return
    try:
        logger.info('Putting the message to bot sending queue')
        q.put(UserMessage(chat_id=data['contact'], digest=[DigestItem(**i) for i in data['digest']]))
        logger.info('Message put.')
    except Exception:
        logger.exception('Could not put message in a queue')


@app.method('ping')
def ping_service(request: InvokeMethodRequest) -> InvokeMethodResponse:
    """Returns a PONG when pinged."""

    logger.info('Received PING, returning PONG')
    return InvokeMethodResponse(data='PONG')


async def listener(q: Queue) -> None:
    """The listener listens to the Queue to send messages."""

    logging.info('Starting Queue listener')
    while True:
        try:
            message: UserMessage = q.get_nowait()
            logger.info('Got message, sending to the user')
            await send_digest_to_user(message.chat_id, message.digest)
            q.task_done()
        except Empty:
            await asyncio.sleep(1)


def run_dapr():
    """Runs dapr."""

    logger.info('Launching DAPR')
    app.run(config.grpc_port)


async def main() -> None:
    """The startup routine.
    Thread for dapr, event loop for queue listener and telegram bot."""

    loop = asyncio.get_event_loop()
    from signal import SIGINT, SIGTERM
    dapr_thread = threading.Thread(target=run_dapr, daemon=True)
    dapr_thread.start()
    listener_task = asyncio.create_task(listener(q))
    bot_task = asyncio.create_task(dp.start_polling(bot))
    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, listener_task.cancel)
    try:
        await asyncio.gather(listener_task, bot_task)
    except asyncio.CancelledError:
        logger.info('Service cancelled')


if __name__ == '__main__':
    logger.info(f'Starting {config.service_name}')
    asyncio.run(main())
