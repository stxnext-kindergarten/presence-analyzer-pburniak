# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
import logging
from collections import OrderedDict

from flask import redirect, abort, url_for, render_template

from presence_analyzer.main import app
from presence_analyzer.utils import (
    jsonify, get_data, mean, group_by_weekday, mean_start_end)

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


ENDPOINTS = OrderedDict([
    ('presence_weekday', 'Presence by weekday'),
    ('mean_time_weekday', 'Presence mean time'),
    ('presence_start_end', 'Presence start - end')
])


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect(url_for('render', site='presence_weekday'))


@app.route('/<site>')
def render(site):
    if site not in ENDPOINTS:
        abort(404)
    return render_template(
        '{}.html'.format(site), name=site, endpoints=ENDPOINTS)


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = get_data()
    return [
        {'user_id': i, 'name': 'User {0}'.format(str(i))}
        for i in data.keys()
    ]


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], mean(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], sum(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_view(user_id):
    """
    Returns mean time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = mean_start_end(data[user_id])
    result = [
        (calendar.day_abbr[weekday], times[0], times[1])
        for weekday, times in enumerate(weekdays)
    ]
    return result
