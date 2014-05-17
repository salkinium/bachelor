#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

import os
import pylab
import logging
import datetime
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import scipy.stats as stats
import pandas as pd
import seaborn as sns
sns.set_style("whitegrid")
import json
import math
import re
from link_file import LinkFile

class FEC_Plotter(object):

    def __init__(self, files, basename):
        self.basename = basename
        self.files = files

        self.logger = logging.getLogger('FEC Plotter')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(name)s: %(message)s')
        # console logging
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self.logger.handlers = []
        self.logger.addHandler(ch)

        self.ranges = {'rssi': range(-100, -80),
                       'lqi': range(20, 115),
                       'power': range(0, 30),
                       'bit_errors': range(0, 80),
                       'byte_errors': range(0, 40),
                       'temperature': range(20, 100)}

        self.raw_dicts = []
        for file in self.files:
            with open(file, 'r') as raw_file:
                # try:
                values = json.load(raw_file)
                values['file'] = file

                match = re.search("-rs_(?P<n>[0-9]{2})_(?P<k>[0-9]{2})_random-2", file)
                values['n']= int(match.group('n'))
                values['k'] = int(match.group('k'))
                self.raw_dicts.append(values)
                # except:
                #     self.logger.error("Raw file corrupted!")


    def get_mean_time_values_for_key(self, key, lower=None, upper=None):
        nkey = key.lower().replace(" ", "_")
        data = dict(self.raw_dicts[0][nkey])

        if len(data['time']) > 0:
            data['time'] = map(lambda dt: datetime.datetime.fromtimestamp(dt), data['time'])
            data.update({'mean': [], 'std_l': [], 'std_u': []})
            for ii in range(len(data['time'])):
                mean = np.mean(data['values'][ii])
                std = np.std(data['values'][ii], ddof=1)

                data['mean'].append(mean)
                data['std_l'].append(max(lower, (mean - std)) if lower != None else mean - std)
                data['std_u'].append(min(upper, (mean - std)) if upper != None else mean + std)

        return data

    def create_prr_plot(self, nax=None):
        for values in self.raw_dicts:
            if values['k'] == 70:
                prr = dict(values['prr'])
                break

        if len(prr['time']) > 0:
            prr['time'] = map(lambda dt: datetime.datetime.fromtimestamp(dt), prr['time'])

            # normalize for all sent messages
            for ii in range(len(prr['time'])):
                all_sent = prr['sent'][ii]
                if all_sent > 0:
                    prr['received'][ii] = float(prr['received'][ii]) / all_sent
                    prr['received_without_error'][ii] = float(prr['received_without_error'][ii]) / all_sent
                    prr['decoded_without_error'][ii] = float(prr['decoded_without_error'][ii]) / all_sent
                    prr['coded_without_error'][ii] = float(prr['coded_without_error'][ii]) / all_sent

            if nax == None:
                fig, ax = plt.subplots(1)
                x, y = fig.get_size_inches()
                fig.set_size_inches(x * 0.625, y * 0.625)
            else:
                ax = nax
            zeros = np.zeros(len(prr['time']))
            ones = np.ones(len(prr['time']))
            legend = {'patches': [], 'labels': []}

            if sum(prr['decoded_without_error']) > 0:
                ax.fill_between(prr['time'], y1=prr['decoded_without_error'], y2=ones,
                                where=prr['decoded_without_error'] < ones, color='r', interpolate=True)
                legend['patches'].append(Rectangle((0, 0), 1, 1, fc="r"))
                legend['labels'].append("Decoded with error")

            ax.fill_between(prr['time'], y1=prr['received'], y2=ones, where=prr['received'] < ones, color='0.65',
                            interpolate=True)
            legend['patches'].append(Rectangle((0, 0), 1, 1, fc="0.65"))
            legend['labels'].append("Reception timeout")

            if sum(prr['coded_without_error']) > 0:
                rx_wo_error, = ax.plot_date(prr['time'], prr['coded_without_error'], markersize=0, c='k', linestyle='-',
                                            linewidth=0.8)
            else:
                rx_wo_error, = ax.plot_date(prr['time'], prr['received_without_error'], markersize=0, c='k',
                                            linestyle='-', linewidth=0.8)
            legend['patches'].append(rx_wo_error)
            legend['labels'].append("Received without Error")

            ax.set_ylim(ymin=0, ymax=1)
            ax.set_ylabel('PRR', fontsize=18)

            ax.legend(legend['patches'],
                      legend['labels'],
                      loc=3,
                      prop={'size': 12})

            if nax == None:
                fig.autofmt_xdate()

            return ax

    def create_mean_time_plot_for_key(self, key, nax=None):
        nkey = key.lower().replace(" ", "_")
        data = self.get_mean_time_values_for_key(key, 0 if 'errors' in nkey else None)

        if len(data['time']) > 0:

            if nax == None:
                fig, ax = plt.subplots(1)
                x, y = fig.get_size_inches()
                fig.set_size_inches(x * 0.625, y * 0.625)
            else:
                ax = nax
            ax.set_ylim(ymin=min(self.ranges[nkey]), ymax=max(self.ranges[nkey]))
            if 'temperature' in nkey:
                key += " ($^\circ$C)"
            ax.set_ylabel(key, fontsize=18)

            if 'temperature' not in nkey:
                ax.plot_date(data['time'], data['std_u'], c='0.5', linestyle='-', markersize=0, linewidth=1)
                ax.plot_date(data['time'], data['std_l'], c='0.5', linestyle='-', markersize=0, linewidth=1)
            ax.plot_date(data['time'], data['mean'], c='k', linestyle='-', markersize=0, linewidth=1.75)

            if nax == None:
                fig.autofmt_xdate()

            return ax



    def create_multiple_plots(self):
        fig, axarr = plt.subplots(3, sharex=True)
        fig.set_size_inches(8 * 0.625, 0.625 * 3 * 5.5)

        self.create_throughput_plot(axarr[0])
        # self.create_prr_plot(axarr[1])
        self.create_mean_time_plot_for_key('Byte Errors', axarr[1])
        # self.create_mean_time_plot_for_key('LQI', axarr[3])
        self.create_mean_time_plot_for_key('Temperature', axarr[2])

        fig.autofmt_xdate()

        # self.logger.debug("Saving Plot to file: '{}_{}'".format(self.basename, "-".join(keys)))
        # plt.savefig("{}_{}.pdf".format(self.basename, "-".join(keys)), bbox_inches='tight', pad_inches=0.1)
        # plt.close()

        return axarr

    def create_throughput_plot(self, nax=None):

        if nax == None:
            fig, ax = plt.subplots(1)
        else:
            ax = nax
        colors = "bgrcmyk"
        color_index = 0

        for file in self.raw_dicts:
            prr = dict(file['prr'])
            prr['time'] = map(lambda dt: datetime.datetime.fromtimestamp(dt), prr['time'])
            n = file['n']
            k = file['k']
            throughput = float(k)/n

            delta_half = datetime.timedelta(minutes=3)

            prr_f = {'time': [prr['time'][0]],
                   'sent': [0],
                   'received': [0],
                   'received_without_error': [0],
                   'coded_without_error': [0],
                   'decoded_without_error': [0]}

            prr_index = 0
            reference_time = prr['time'][0] + delta_half + delta_half

            for time_index in range(len(prr['time'])):
                if prr['time'][time_index] <= reference_time:
                    prr_f['sent'][prr_index] += prr['sent'][time_index]
                    prr_f['received'][prr_index] += prr['received'][time_index]
                    prr_f['received_without_error'][prr_index] += prr['received_without_error'][time_index]
                    prr_f['coded_without_error'][prr_index] += prr['coded_without_error'][time_index]
                    prr_f['decoded_without_error'][prr_index] += prr['decoded_without_error'][time_index]
                else:
                    prr_f['time'].append(reference_time)
                    prr_f['sent'].append(prr['sent'][time_index])
                    prr_f['received'].append(prr['received'][time_index])
                    prr_f['received_without_error'].append(prr['received_without_error'][time_index])
                    prr_f['decoded_without_error'].append(prr['coded_without_error'][time_index])
                    prr_f['coded_without_error'].append(prr['decoded_without_error'][time_index])

                    prr_index += 1
                    reference_time += delta_half + delta_half

            # normalize for all received messages
            for ii in range(len(prr_f['time'])):
                all_received = prr_f['received'][ii]
                if all_received > 0:
                    prr_f['received_without_error'][ii] = float(prr_f['received_without_error'][ii]) / all_received * throughput
                    prr_f['decoded_without_error'][ii] = float(prr_f['decoded_without_error'][ii]) / all_received * throughput
                    prr_f['coded_without_error'][ii] = float(prr_f['coded_without_error'][ii]) / all_received * throughput

            ax.plot_date(prr_f['time'], prr_f['decoded_without_error'], markersize=0, c=colors[color_index], linestyle='-', linewidth=1)
            color_index = (color_index + 1) % (len(colors) - 0)
        ax.set_ylim(ymin=0, ymax=1)
        ax.set_ylabel('Throughput', fontsize=18)

        if nax == None:
            fig.autofmt_xdate()

        return ax

    def save_throughput_plot(self):
        plot = self.create_multiple_plots()
        if plot != None:
            self.logger.debug("Saving Plot to file: '{}_{}'".format(self.basename, "Throughput"))
            plt.savefig("{}_{}.pdf".format(self.basename, "Throughput"), bbox_inches='tight', pad_inches=0.1)
            plt.close()
