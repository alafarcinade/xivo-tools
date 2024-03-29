# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from __future__ import unicode_literals

import logging
import socket
import select

logger = logging.getLogger(__name__)


class AMIClient(object):
    _BUFSIZE = 4096
    _TIMEOUT = 15

    def __init__(self, hostname):
        self._hostname = hostname
        self._sock = None

    def connect(self):
        logger.info('Connecting to %s', self._hostname)

        new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            new_sock.connect((self._hostname, 5038))
        except Exception:
            new_sock.close()
            raise
        else:
            self._sock = new_sock

    def disconnect(self):
        logger.info('Disconnecting from %s', self._hostname)

        self._sock.close()
        self._sock = None

    def wait_recv(self, timeout=_TIMEOUT):
        if self._is_recv_ready(timeout):
            self.flush_recv()

    def _is_recv_ready(self, timeout=0):
        r_rlist = select.select([self._sock], [], [], timeout)[0]
        return bool(r_rlist)

    def flush_recv(self):
        while self._is_recv_ready():
            data = self._sock.recv(self._BUFSIZE)
            if not data:
                raise Exception('remote end closed the connection')
            logger.debug('Received %r', data)

    def action_login(self, username, password):
        logger.debug('Action login')

        lines = [
            'Action: Login',
            'Username: %s' % username,
            'Secret: %s' % password,
        ]
        self._send_request(lines)

    def _send_request(self, lines):
        data = '\r\n'.join(lines) + '\r\n\r\n'
        self._sock.send(data)

    def action_agent_callback_login(self, agent_num, context, exten):
        logger.debug('Action agent callback login')

        lines = [
            'Action: AgentCallbackLogin',
            'Agent: %s' % agent_num,
            'Context: %s' % context,
            'Exten: %s' % exten,
        ]
        self._send_request(lines)

    def action_agent_logoff(self, agent_num):
        logger.debug('Action agent logoff')

        lines = [
            'Action: AgentLogoff',
            'Agent: %s' % agent_num,
        ]
        self._send_request(lines)

    def action_command(self, cli_command):
        logger.debug('Action command')

        lines = [
            'Action: Command',
            'Command: %s' % cli_command,
        ]
        self._send_request(lines)

    def action_core_show_channels(self):
        logger.debug('Action core show channels')

        lines = [
            'Action: CoreShowChannels',
        ]
        self._send_request(lines)

    def action_show_dialplan(self):
        logger.debug('Action show dialplan')

        lines = [
            'Action: ShowDialPlan',
        ]
        self._send_request(lines)

    def action_status(self, channel_name):
        logger.debug('Action status')

        lines = [
            'Action: Status',
            'Channel: %s' % channel_name,
        ]
        self._send_request(lines)
