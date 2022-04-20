import sys
from io import BytesIO
from datetime import date
from typing import List
from pathlib import Path

import plotly.express as px
from plotly.offline import iplot
import plotly.graph_objs as go
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from PIL import Image

from finance_bot import db
from finance_bot import misc
from finance_bot import texts
from finance_bot.misc import bot


def parse_stats_args(command: str) -> dict:
    args = command.removeprefix('/stats').split()
    today = date.today()
    if len(args) == 0:
        return {'month': today.month, 'year': today.year}
    elif len(args) == 1 and 0 < int(args[0]) < 13:
        return {'month': int(args[0]), 'year': today.year}
    elif len(args) == 2 and 0 < int(args[0]) < 13 and int(args[1]) > 0:
        return {'month': int(args[0]), 'year': int(args[1])}
    else:
        raise ValueError('Too many arguments')


def get_plot(values: List[int], labels: List[str], month_name: str, year: int) -> bytes:

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
        textfont={'size': 50},
        texttemplate='%{label}<br>%{value}₪'
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
        text=f'{sum(values)}₪',
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

    fig.update_layout(
        title={
            'text': f'Траты за {month_name} {year}',
            'x': 0.5,
            'y': 0.98,
        },
        font={'size': 50}
    )

    return fig.to_image(format='png', width=2000, height=1800)


async def stats_for_month(msg: Message, state: FSMContext):
    await state.reset_state(with_data=False)
    await bot.send_chat_action(msg.chat.id, 'upload_photo')

    try:
        args = parse_stats_args(msg.text)
    except ValueError:
        return await msg.answer(texts.msg_cant_parse_stats_args)

    labels, values = await db.get_stats_for_month(**args)

    if len(labels) == 0:
        return await msg.answer(texts.msg_no_stats_for_month)

    plot = get_plot(values, labels, texts.month_names[args['month']], args['year'])
    await msg.answer_photo(plot)




