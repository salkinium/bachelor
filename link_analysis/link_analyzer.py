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


class Analyzer(object):

    def __init__(self, link_file, selector, basename=None):
        # self.links = [] if not links else [link for link in links if link.is_valid]
        self.links = None
        self.basename = basename if basename else os.path.dirname(__file__)
        self.link_file = link_file
        self.selector = selector

        self.logger = logging.getLogger('LinkAnalyzer')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(name)s: %(message)s')
        # console logging
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self.logger.handlers = []
        self.logger.addHandler(ch)

        self.raw_file_name = "{}_raw.txt".format(self.basename)
        if os.path.isfile(self.raw_file_name):
            with open(self.raw_file_name, 'r') as raw_file:
                self.raw_dict = json.load(raw_file)
        else:
            self.raw_dict = {}

        self.ranges = {'rssi': range(-100, -70),
                       'lqi': range(20, 115),
                       'power': range(0, 30),
                       'bit_errors': range(0, 80),
                       'byte_errors': range(0, 40),
                       'temperature': range(20, 100)}

    def _write_to_raw_file(self, key, data):
        nkey = key.lower().replace(" ", "_")
        self.raw_dict[nkey] = data
        with open(self.raw_file_name, 'w') as raw_file:
            json.dump(self.raw_dict, raw_file)

    def _read_from_raw_file(self, key):
        nkey = key.lower().replace(" ", "_")
        if nkey in self.raw_dict:
            return self.raw_dict[nkey]

        return None

    def get_array_of_property(self, key):
        nkey = key.lower().replace(" ", "_")
        if self.links == None:
            self.links = self.link_file.get_links_for_selector(self.selector)

        results = []
        for link in self.links:
            for rx in link.rx:
                if nkey in rx:
                    results.append(rx[nkey])
        return results

    def get_normed_histogram_for_key(self, key):
        nkey = key.lower().replace(" ", "_")
        data = self._read_from_raw_file(nkey)
        if data == None:
            data = self.get_array_of_property(nkey.replace("hist_", ""))
            self._write_to_raw_file(nkey, data)

        if len(data) > 0:
            return np.histogram(data, bins=sorted(list(set(data))), normed=True), set(data)
        return None

    def create_histogram_plot_for_key(self, key, color='r'):
        nkey = key.lower().replace(" ", "_")
        data = self._read_from_raw_file(nkey)
        if data == None:
            data = self.get_array_of_property(nkey.replace("hist_", ""))
            self._write_to_raw_file(nkey, data)

        if len(data) > 0:
            fig, ax = plt.subplots(1)
            n, bins, patches = ax.hist(data, self.ranges[nkey.replace("hist_", "")], normed=True, histtype='stepfilled', rwidth=0.8)
            pylab.setp(patches, facecolor=color, alpha=0.75)

            ax.set_ylabel("Occurances")
            ax.set_xlabel(key)

            mean = np.mean(data)
            std = np.std(data)

            ax.axvline(mean, color='r', linewidth=2)
            ax.axvline(mean - std, color='b', linewidth=1, linestyle="--")
            ax.axvline(mean + std, color='b', linewidth=1, linestyle="--")

            hist = self.get_normed_histogram_for_key(nkey)
            return fig, ax, {'hist': hist[0], 'bins': hist[1]}

        return None

    def create_xor_plot(self):
        max_length = 12 + 32*2 + 16
        bits_array = self._read_from_raw_file('xor_bits_array')
        if bits_array == None:
            xors = self.get_array_of_property('xor')
            if len(xors) > 0:
                max_length = min(max_length, max(map(len, xors)))
                bits_array = [0] * max_length * 8

                for xor in xors:
                    for ii in range(max_length):
                        for jj in range(8):
                            bits_array[ii * 8 + jj] += 1 if xor[ii] & (1 << (7 - jj)) else 0

            else:
                bits_array = []
            self._write_to_raw_file('xor_bits_array', bits_array)

        error_sum = self._read_from_raw_file('bit_error_sum')
        if error_sum == None:
            error_sum = sum(self.get_array_of_property('bit_errors'))
            self._write_to_raw_file('bit_error_sum', error_sum)

        if len(bits_array):

            if error_sum >= 2:
                normed_bits_array = map(lambda b: float(b)/error_sum, bits_array)

            fig, ax = plt.subplots(1)
            lines = ax.plot(range(len(normed_bits_array)), normed_bits_array)
            pylab.setp(lines, color='k', linewidth=0.2)

            # ax.grid(b=True, which='major', color='0.90', linestyle='-')
            ax.set_axisbelow(True)
            ax.add_patch(Rectangle((0, 0), 12*8, 1, color='0.90'))
            ax.set_xlim(xmin=0, xmax=max_length*8)
            ax.set_ylim(ymin=0, ymax=0.0025)
            plt.xticks(range(12*8, max_length*8, 64), (range(0, max_length*8, 64)))
            ax.set_ylabel("Frequency of bit errors")
            ax.set_xlabel("Bit position")
            return fig, ax, {'errors': bits_array, 'sum': error_sum}

    def get_time_plot_values_for_key(self, key):
        nkey = key.lower().replace(" ", "_")
        results = {'time': [], 'values': []}
        if self.links == None:
            self.links = self.link_file.get_links_for_selector(self.selector)

        for link in self.links:
            for rx in link.rx:
                if nkey in rx:
                    results['time'].append(rx['timestamp'])
                    results['values'].append(rx[nkey])
        return results

    def create_mean_time_plot(self, values, lower=None, upper=None):
        if len(values['time']) > 0:
            for ii in range(len(values['time'])):
                mean = np.mean(values['values'][ii])
                std = np.std(values['values'][ii], ddof=1)
                values['mean'].append(mean)
                values['std_l'].append(max(lower, (mean - std)) if lower != None else mean - std)
                values['std_u'].append(min(upper, (mean - std)) if upper != None else mean + std)

            fig, ax = plt.subplots(1)
            lines = ax.plot_date(values['time'], values['mean'], c='r', linestyle='-',
                                 markersize=0, linewidth=2)
            lines = ax.plot_date(values['time'], values['std_u'], c='b', linestyle='--',
                                 markersize=0, linewidth=1)
            lines = ax.plot_date(values['time'], values['std_l'], c='b', linestyle='--',
                                 markersize=0, linewidth=1)
            fig.autofmt_xdate()
            return fig, ax

    def create_mean_time_plot_for_key(self, key):
        nkey = key.lower().replace(" ", "_")
        values = self.get_time_plot_values_for_key(nkey)

        delta_half = datetime.timedelta(minutes=1)

        if len(values['time']) > 0:
            accumulated_values = {'time': [values['time'][0]], 'values': [[values['values'][0]]], 'mean': [], 'std_l': [], 'std_u': []}
            index = 0
            for ii in range(len(values['time'])):
                if values['time'][ii] <= accumulated_values['time'][index] + delta_half + delta_half:
                    accumulated_values['values'][index].append(values['values'][ii])
                else:
                    accumulated_values['time'].append(values['time'][ii] + delta_half)
                    accumulated_values['values'].append([values['values'][ii]])
                    index += 1

            fig, ax = self.create_mean_time_plot(accumulated_values, 0 if 'errors' in nkey else None)
            lines = ax.plot_date(values['time'], values['values'], markersize=1, c='k')
            ax.set_ylim(ymin=min(self.ranges[nkey]), ymax=max(self.ranges[nkey]))
            ax.set_ylabel(key)

            return fig, ax

    def create_accumulated_inverted_time_plot(self, key='timeout'):
        nkey = key.lower().replace(" ", "_")
        values = self.get_time_plot_values_for_key(nkey)

        if len(values['time']) > 0:
            accumulated_values = {'time': [values['time'][0]], 'values': [values['values'][0]]}
            index = 0
            for ii in range(len(values['time'])):
                if values['time'][ii] <= accumulated_values['time'][index]+datetime.timedelta(minutes=1):
                    accumulated_values['values'][index] += 0 if values['values'][ii] == 1 else 1
                else:
                    accumulated_values['time'].append(values['time'][ii])
                    accumulated_values['values'].append(values['values'][ii])
                    index += 1

            fig, ax = plt.subplots(1)
            # fig, ax = self.create_mean_time_plot(accumulated_values, 0)
            lines = ax.plot_date(accumulated_values['time'], accumulated_values['values'], markersize=1, c='k')
            ax.set_ylabel('PRR')
            fig.autofmt_xdate()
            return fig, ax

    def create_time_plot(self, key='lqi'):
        nkey = key.lower().replace(" ", "_")
        values = self.get_time_plot_values_for_key(nkey)
        if len(values['time']) > 0:
            fig, ax = plt.subplots(1)
            ax.set_ylim(ymin=min(self.ranges[nkey]), ymax=max(self.ranges[nkey]))
            lines = plt.plot_date(values['time'], values['values'], markersize=1, c='k')
            # ax.grid(b=True, which='major', color='0.66', linestyle='-')
            ax.set_ylabel(nkey)
            fig.autofmt_xdate()
            return fig, ax

    def create_plot_for_key(self, key):
        nkey = key.lower().replace(" ", "_")
        plot = None
        if nkey in ['rssi', 'lqi', 'bit_errors', 'byte_errors', 'burst_errors', 'temperature']:
            plot = self.create_mean_time_plot_for_key(key)
        elif nkey in ['hist_rssi', 'hist_lqi', 'hist_bit_errors', 'hist_byte_errors']:
            plot = self.create_histogram_plot_for_key(nkey)
        elif nkey in ['xor']:
            plot = self.create_xor_plot()
        elif nkey in ['prr']:
            plot = self.create_accumulated_inverted_time_plot('timeout')

        return plot

    def save_plot_for_key(self, key):
        plot = self.create_plot_for_key(key)
        if plot != None:
            fig = plot[0]
            ax = plot[1]
            self.logger.debug("Saving Plot to file: '{}_{}'".format(self.basename, key))
            plt.savefig("{}_{}.pdf".format(self.basename, key))
            plt.savefig("{}_{}.png".format(self.basename, key))
            plt.close()

    def save_all_plots(self):
        keys = ['LQI', 'RSSI', 'Bit Errors', 'Byte Errors', 'Burst Errors', 'Temperature',
                'Hist RSSI', 'Hist LQI', 'Hist Bit Errors', 'Hist Byte Errors',
                'Xor',
                'PRR']
        for key in keys:
            self.save_plot_for_key(key)

    def save_all_cached_plots(self):
        keys = ['Hist RSSI', 'Hist LQI', 'Hist Bit Errors', 'Hist Byte Errors',
                'Xor']
        for key in keys:
            self.save_plot_for_key(key)


    def save_plot_to_file(self, plot, filename):
        if len(self.links) > 0 and plot:
            self.logger.debug("Saving Plot to file: '{}'".format(filename))
            plot.savefig(os.path.join(os.path.dirname(__file__), '..', 'plots', filename))
