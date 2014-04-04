# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

import os
import sys
from multiprocessing import Process, Value, Array

import numpy as np
from matplotlib import pyplot as plt
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'link_analysis'))

from string_message import StringMessage
from link import Link

class MessageVisualizer(Process, object):

    def __init__(self, nodes=5, messages=100):
        super(MessageVisualizer, self).__init__()

        self.nodes = nodes if nodes > 0 else 1
        self.link = None

        self.fig = plt.figure(num=None, figsize=(16, 12), dpi=80, facecolor='w', edgecolor='k')
        self.fig.subplots_adjust(top=0.8)

        self.temperature = self.fig.add_axes([0.05, 0.7, 0.9, 0.2], label='temperature')
        self.temperature.axes.get_xaxis().set_visible(False)
        self.temperature.set_ylim(10, 30)
        self.temperature.set_ylabel('Temperature')

        self.errors = self.fig.add_axes([0.05, 0.5, 0.9, 0.2], label='errors')
        self.errors.axes.get_xaxis().set_visible(False)
        self.errors.set_ylim(0, 100)
        self.errors.set_ylabel('rx bit errors')

        self.lqi = self.fig.add_axes([0.05, 0.3, 0.9, 0.2], label='lqi')
        self.lqi.axes.get_xaxis().set_visible(False)
        self.lqi.set_ylim(40, 120)
        self.lqi.set_ylabel('LQI')

        self.rssi = self.fig.add_axes([0.05, 0.1, 0.9, 0.2], label='rssi')
        self.rssi.set_ylim(-100, -60)
        self.rssi.set_ylabel('RSSI in dB')

        self.rssi.set_xlabel('messages')

        # colors
        self.colors = ['r', 'b', 'g', 'c', 'm', 'b']
        self.lw = 1.5

        self.messages = messages if messages >= 10 else 10
        # reserve the values
        self.x_values = np.arange(0.0, self.messages, 1.0)

        self.temperature_values = []
        self.rssi_values = []
        self.error_values = []
        self.lqi_values = []

        for node in range(self.nodes):
            self.temperature_values.append(np.zeros(self.messages))
            self.rssi_values.append(np.zeros(self.messages))
            self.lqi_values.append(np.zeros(self.messages))
            self.error_values.append(np.zeros(self.messages))

        self.errors_plot = []
        self.temperature_plot = []
        self.rssi_plot = []
        self.lqi_plot = []

        for node in range(self.nodes):
            self.errors_plot.append(self.errors.plot(self.x_values, self.error_values[node], color=self.colors[node], lw=self.lw)[0])
            self.rssi_plot.append(self.rssi.plot(self.x_values, self.rssi_values[node], color=self.colors[node], lw=self.lw)[0])
            self.lqi_plot.append(self.lqi.plot(self.x_values, self.lqi_values[node], color=self.colors[node], lw=self.lw)[0])
            self.temperature_plot.append(self.temperature.plot(self.x_values, self.temperature_values[node], color=self.colors[node], lw=self.lw)[0])

        plt.ion()
        plt.show()

        # multiprocessing support
        self._tx_message = Array('c', 2000)
        self._rx_message = Array('c', 2000)
        self._add_rx = Value('b', False)
        self._add_tx = Value('b', False)

        self.start()

    def add_tx_message(self, message):
        while(self._add_tx.value):
            time.sleep(0)

        self._tx_message.value = message
        self._add_tx.value = True

    def add_rx_message(self, message):
        while (self._add_rx.value):
            time.sleep(0)

        self._rx_message.value = message
        self._add_rx.value = True

    def add_link(self, link):
        for node in range(self.nodes):
            if node == link.tx['id']:
                continue
            # left shift all values
            self.temperature_values[node] = np.roll(self.temperature_values[node], 1)
            self.error_values[node] = np.roll(self.error_values[node], 1)
            self.rssi_values[node] = np.roll(self.rssi_values[node], 1)
            self.lqi_values[node] = np.roll(self.lqi_values[node], 1)

        # for every received message in the link
        for rx in link.rx:
            rx_id = rx['id']
            # can't plot too many things
            if rx_id > self.nodes:
                continue

            # add the required values to the last entry
            self.temperature_values[rx_id][0] = rx['temperature']
            if rx['timeout'] == 0:
                self.rssi_values[rx_id][0] = rx['rssi']
                self.lqi_values[rx_id][0] = rx['lqi']
                if 'errors' in rx:
                    self.error_values[rx_id][0] = rx['errors']
            else:
                self.rssi_values[rx_id][0] = 0
                self.lqi_values[rx_id][0] = 0
                self.error_values[rx_id][0] = 100

        for node in range(self.nodes):
            self.errors_plot[node].set_ydata(self.error_values[node])
            self.lqi_plot[node].set_ydata(self.lqi_values[node])
            self.rssi_plot[node].set_ydata(self.rssi_values[node])
            self.temperature_plot[node].set_ydata(self.temperature_values[node])

        print "hello"
        # update the graph
        plt.draw()

    def run(self):

        while True:
            if self._add_tx.value:
                tx = StringMessage(str(self._tx_message.value))
                if tx:
                    if self.link:
                        self.add_link(self.link)
                    self.link = Link(tx)
                else:
                    self.link = None

                self._add_tx.value = False

            if self._add_rx.value:
                if self.link:
                    rx = StringMessage(str(self._rx_message.value))
                    if rx:
                        self.link.add_rx(rx)
                self._add_rx.value = False

            time.sleep(0.1)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "MessageVisualizer"
