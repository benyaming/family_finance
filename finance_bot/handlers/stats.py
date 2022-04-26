from datetime import date
from typing import List, Tuple, Optional

import plotly.graph_objs as go
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from finance_bot import db
from finance_bot import texts
from finance_bot.misc import bot
from finance_bot.keyboards import get_detailed_stats_kb
from finance_bot.settings import env


def parse_stats_args(command: str) -> Tuple[int, int]:
    args = command.removeprefix('/stats').split()
    today = date.today()
    if len(args) == 0:
        return today.month, today.year
    elif len(args) == 1 and 0 < int(args[0]) < 13:
        return int(args[0]), today.year
    elif len(args) == 2 and 0 < int(args[0]) < 13 and int(args[1]) > 0:
        return int(args[0]), int(args[1])
    else:
        raise ValueError('Too many arguments')


def get_plot(
        values: List[int],
        labels: List[str],
        month_name: str,
        year: int,
        group_name: Optional[str] = None
) -> bytes:

    common_props = {
        'labels': labels,
        'values': values,
        'hole': 0.4,
        'showlegend': False,
    }

    trace1 = go.Pie(
        **common_props,
        textinfo='value',
        textposition='outside',
        textfont={
            'size': 50,
        },
        texttemplate=f'%{{label}}<br>%{{value:,}}{env.CURRENCY_CHAR}'
    )
    trace2 = go.Pie(
        **common_props,
        textinfo='percent',
        textposition='inside',
        textfont={'size': 50},
        insidetextorientation='horizontal',
        texttemplate='%{percent:.0%}'
    )

    fig = go.Figure(data=[trace1, trace2])

    fig.add_annotation(
        x=0.5,
        y=0.5,
        text=f'{sum(values):,}{env.CURRENCY_CHAR}'.replace(',', '.'),
        font={
            'size': 70,
            'family': 'Verdana',
            'color': 'black'
        },
        showarrow=False
    )

    fig.update_traces(
        marker={'line': {'color': '#000000', 'width': 4}}
    )

    group_postfix = f' {texts.plot_in_category} {group_name}' if group_name else ''
    fig.update_layout(
        title={
            'text': f'{texts.plot_spends_title} {month_name} {year}{group_postfix}',
            'x': 0.5,
            'y': 0.98,
        },
        font={'size': 50},
        separators=',.'
    )

    return fig.to_image(format='png', width=2000, height=1800)


async def group_stats_for_month(msg: Message, state: FSMContext):
    await state.reset_state(with_data=False)
    await bot.send_chat_action(msg.chat.id, 'upload_photo')

    try:
        month, year = parse_stats_args(msg.text)
    except ValueError:
        return await msg.answer(texts.msg_cant_parse_stats_args)

    labels, values, group_ids = await db.get_group_stats_for_month(month, year)

    if len(labels) == 0:
        return await msg.answer(texts.msg_no_stats_for_month)

    plot = get_plot(values, labels, texts.month_names[month], year)
    kb = get_detailed_stats_kb(group_ids, labels, month, year)
    await msg.answer_photo(plot, reply_markup=kb)


async def category_stats_for_month(call: CallbackQuery):
    await bot.send_chat_action(call.message.chat.id, 'upload_photo')
    group_id, month, year = map(int, call.data.split(':')[1:])
    labels, values = await db.get_category_stats_for_month(group_id, month, year)
    group = await db.get_category_group(group_id)

    plot = get_plot(values, labels, texts.month_names[month], year, group.name)
    await call.answer()
    await call.message.answer_photo(plot)



