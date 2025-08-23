import sys
sys.path.append('../') # src/

from exceptions import exceptions_catcher
from utils import respondEvent, datetimeToString
from pagination import Paginator

from api.mrstone import MrStoneAPI

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

import dateutil


router = Router(name=__name__)


@router.message(Command('orders'))
@router.callback_query(F.data.startswith('orders'))
@exceptions_catcher()
async def orders(event: Message | CallbackQuery) -> None:
    username = event.from_user.username

    if not username:
        message_text = (
            '*❌ У Вас не указано имя пользователя Telegram*\n\n'
            + '🔍 Чтобы мы cмогли найти Ваши заказы, укажите имя пользователя.\n\n'
            + '*💡 Настройки ➡️ Мой аккаунт ➡️ Имя пользователя*'
        )
        return await respondEvent(event, text=message_text, parse_mode="Markdown")

    mrstone_api = MrStoneAPI()
    orders = mrstone_api.getOrdersByContact(contact=username, contact_type='telegram')
    orders_count = len(orders)

    if not orders:
        return await respondEvent(event, text='📂 У Вас нет ни одного заказа')

    order_statuses = {
        'created': {'title': 'Сформирован', 'count': 0},
        'in_progress': {'title': 'В работе', 'count': 0},
        'in_delivery': {'title': 'Доставляется', 'count': 0},
        'completed': {'title': 'Завершён', 'count': 0},
        'cancelled': {'title': 'Отменён', 'count': 0},
        'rejected': {'title': 'Отклонён', 'count': 0},
    }

    orders_cards = []
    for order in orders:
        order_id = order['id']
        status = order['status']
        created_at = datetimeToString(
            dateutil.parser.parse(order['created_at'])
        )

        order_statuses[status]['count'] += 1

        orders_cards.append(
            {'text': f'{order_statuses[status]["title"]} | {created_at}', 'callback_data': f'order_card-{order_id}'}
        )

    page = 1
    if isinstance(event, CallbackQuery):
        if '-' in event.data:
            page = int(event.data.split('-')[1])
    paginator = Paginator(array=orders_cards, offset=5, page_callback='orders', back_callback='start')
    keyboard = paginator.getPageKeyboard(page)

    message_text = (
        '*🛒 Список заказов*\n\n'
        + f'🗃️ Всего заказов: {orders_count}\n\n'
        + '🗂 Количество заказов по статусам\n'
    )
    for status in order_statuses.values():
        if status['count'] > 0:
            message_text = message_text + f'{status["title"]}: {status["count"]}'

    await respondEvent(
        event,
        text=message_text, 
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query(F.data.startswith('order_card'))
@exceptions_catcher()
async def order_card(event: CallbackQuery) -> None:
    order_id = '-'.join(event.data.split('-')[1:])

    mrstone_api = MrStoneAPI()
    order = mrstone_api.getOrder(order_id)

    if order['updated_at']:
        updated_at = datetimeToString(
            dateutil.parser.parse(order['updated_at'])
        )
    created_at = datetimeToString(
        dateutil.parser.parse(order['created_at'])
    )

    message_text = (
        '*🛒 Карточка заказа*\n\n'
        + (f'*Обновлён:* {updated_at}\n' if updated_at else '')
        + f'*Сформирован:* {created_at}\n\n'
        + f'*🆔 Номер заказа:* `{order_id}`'
    )

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='⬅️ Назад', callback_data='orders')

    await respondEvent(
        event,
        text=message_text, 
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup(),
    )
