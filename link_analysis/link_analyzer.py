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
        self.raw_dict = {}
        if os.path.isfile(self.raw_file_name):
            with open(self.raw_file_name, 'r') as raw_file:
                try:
                    self.raw_dict = json.load(raw_file)
                except:
                    print "Error: raw file corrupted!"

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
            print "Requiring array of property for key '{}'".format(key)
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

            ax.axvline(mean, color='k', linewidth=1.75)
            ax.axvline(mean - std, color='0.5', linewidth=1, linestyle="-")
            ax.axvline(mean + std, color='0.5', linewidth=1, linestyle="-")

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
            # normed_bits_array = bits_array

            fig, ax = plt.subplots(1)
            lines = ax.plot(range(len(normed_bits_array)), normed_bits_array)
            pylab.setp(lines, color='k', linewidth=0.2)

            # ax.grid(b=True, which='major', color='0.90', linestyle='-')
            ax.set_axisbelow(True)
            ax.add_patch(Rectangle((0, 0), 12*8, 10000, color='0.90'))
            ax.set_xlim(xmin=0, xmax=max_length*8)
            ax.set_ylim(ymin=0, ymax=0.0025)
            plt.xticks(range(12*8, max_length*8, 64), (range(0, max_length*8, 64)))
            ax.set_ylabel("Frequency of bit errors", fontsize=18)
            ax.set_xlabel("Bit position", fontsize=18)
            return fig, ax, {'errors': bits_array, 'sum': error_sum}

    def get_time_plot_values_for_key(self, key):
        nkey = key.lower().replace(" ", "_")
        results = {'time': [], 'values': []}
        if self.links == None:
            print "Requiring time values for key '{}'".format(key)
            self.links = self.link_file.get_links_for_selector(self.selector)

        for link in self.links:
            for rx in link.rx:
                if nkey in rx and 'timestamp' in rx:
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
            lines = ax.plot_date(values['time'], values['std_u'], c='0.5', linestyle='-',
                                 markersize=0, linewidth=1)
            lines = ax.plot_date(values['time'], values['std_l'], c='0.5', linestyle='-',
                                 markersize=0, linewidth=1)
            lines = ax.plot_date(values['time'], values['mean'], c='k', linestyle='-',
                                 markersize=0, linewidth=1.75)
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
            # lines = ax.plot_date(values['time'], values['values'], markersize=1, c='k')
            ax.set_ylim(ymin=min(self.ranges[nkey]), ymax=max(self.ranges[nkey]))
            ax.set_ylabel(key)

            return fig, ax


    def create_burst_error_plot(self):
        burst_error = self._read_from_raw_file('burst_errors')
        # burst_error = None
        if burst_error == None:
            if self.links == None:
                print "Requiring array of property for key 'burst_errors'"
                self.links = self.link_file.get_links_for_selector(self.selector)

            all_burst_errors = []
            for link in self.links:
                for rx in link.rx:
                    if 'burst_errors' in rx:
                        if rx['bit_errors'] > 0:
                            all_burst_errors.append(rx['burst_errors'])

            burst_error = []

            if len(all_burst_errors) > 0:
                # bit errors per symbol
                burst_error = [ [] for _ in range(16+1) ]

                for ii in range(len(burst_error)):
                    for error in all_burst_errors:
                        burst_error[ii].append(error[ii])

            self._write_to_raw_file('burst_errors', burst_error)

        if len(burst_error) > 0:
            one_bit_errors = float(sum(burst_error[1])) / len(burst_error[1])
            relative_burst_errors = [ [0.0] * len(burst_error[length]) for length in range(len(burst_error)) ]
            confidence_intervals = [[0] * (16+1), [0] * (16+1)]
            mean_burst_error = [0] * (16+1)

            for length in range(1, len(burst_error)):
                # normalize over mean of 1 bit errors
                for sample in range(len(burst_error[length])):
                    relative_burst_errors[length][sample] = float(burst_error[length][sample]) / one_bit_errors

                # confidence intervals
                # n, min_max, mean, var, skew, kurt = stats.describe(relative_burst_errors[length])
                # R = stats.norm.interval(0.95, loc=mean, scale=math.sqrt(var) / math.sqrt(len(burst_error[length])))
                # confidence_intervals[0][length] = R[0]
                # confidence_intervals[1][length] = R[1]
                mean = np.mean(relative_burst_errors[length])
                r = np.percentile(relative_burst_errors[length], 99)
                confidence_intervals[0][length] = mean * (1+r)
                confidence_intervals[1][length] = mean * (1-r)
                mean_burst_error[length] = mean

            fig, ax = plt.subplots(1)
            ax.errorbar(range(len(burst_error)), mean_burst_error, yerr=confidence_intervals, fmt='', ecolor='k', capthick=2)

            ax.set_yscale('log')
            ax.set_xlim(xmin=1, xmax=16)
            ax.set_ylim(ymin=1e-6, ymax=1e-0)
            ax.set_ylabel('Relative occurances', fontsize=18)
            ax.set_xlabel('Error burst length', fontsize=18)
            return fig, ax

    def create_prr_plot(self):
        prr = self._read_from_raw_file('prr')
        if prr == None:
            # we need to know how many messages we sent, to be able to normalize all PRRs
            time_messages = self.get_time_plot_values_for_key('timeout')

            # if the key 'bit_errors' is in the rx message, then there was no timeout, and the message is valid
            # this can therefore be used for two PRRs: general PRR and error-free PRR
            time_bit_errors = self.get_time_plot_values_for_key('bit_errors')

            # we are also interested in how good the coder was able to salvage the payload and make a PRR out of that
            # if no code was used, this will be empty
            time_decoded_bit_errors = self.get_time_plot_values_for_key('decoded_bit_errors')
            # if we use a coder, we need to compare the bit errors in the coded area with the decoded area
            time_coded_bit_errors = self.get_time_plot_values_for_key('coded_bit_errors')

            prr = {'time': [],
                   'sent': [1],
                   'received': [0],
                   'received_without_error': [0],
                   'coded_without_error': [0],
                   'decoded_without_error': [0]}

            if len(time_messages['time']) > 0:
                # - for all messages we are only interested, how many messages per minute were sent
                # - for general PRR we are only interested, how many messages per minute were received
                # - for error-free PRR we are interested, how many messages per minute were received without error
                # - for general PRR we are only interested, how many messages per minute were received

                prr['time'].append(time_messages['time'][0])

                prr_index = 0
                bit_error_index = 0
                coded_error_index = 0
                decoded_error_index = 0
                delta_half = datetime.timedelta(seconds=7, milliseconds=500)
                reference_time = prr['time'][0] + delta_half + delta_half

                for time_index in range(len(time_messages['time'])):
                    if time_messages['time'][time_index] <= reference_time:
                        prr['sent'][prr_index] += 1
                        while (bit_error_index < len(time_bit_errors['time']) and
                                       time_bit_errors['time'][bit_error_index] <= reference_time):
                            prr['received'][prr_index] += 1
                            prr['received_without_error'][prr_index] += 1 if time_bit_errors['values'][bit_error_index] == 0 else 0
                            bit_error_index += 1
                        while (decoded_error_index < len(time_decoded_bit_errors['time']) and
                                       time_decoded_bit_errors['time'][decoded_error_index] <= reference_time):
                            prr['decoded_without_error'][prr_index] += 1 if time_decoded_bit_errors['values'][decoded_error_index] == 0 else 0
                            decoded_error_index += 1
                        while (coded_error_index < len(time_coded_bit_errors['time']) and
                                       time_coded_bit_errors['time'][coded_error_index] <= reference_time):
                            prr['coded_without_error'][prr_index] += 1 if time_coded_bit_errors['values'][coded_error_index] == 0 else 0
                            coded_error_index += 1
                    else:
                        prr['time'].append(reference_time - delta_half)
                        prr['sent'].append(1)
                        prr['received'].append(0)
                        prr['received_without_error'].append(0)
                        prr['decoded_without_error'].append(0)
                        prr['coded_without_error'].append(0)

                        prr_index += 1
                        reference_time += delta_half + delta_half

                prr['time'] = map(lambda dt: int(dt.strftime("%s")), prr['time'])
            self._write_to_raw_file('prr', prr)

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

            fig, ax = plt.subplots(1)
            zeros = np.zeros(len(prr['time']))
            ones = np.ones(len(prr['time']))

            # ax.fill_between(prr['time'], prr['decoded_without_error'], where=prr['decoded_without_error'] >= zeros, color='0.8', interpolate=True)
            # ax.fill_between(prr['time'], prr['received_without_error'], where=prr['received_without_error'] >= zeros, color='1', interpolate=True)

            if sum(prr['decoded_without_error']) > 0:
                ax.fill_between(prr['time'], y1=prr['decoded_without_error'], y2=ones, where=prr['decoded_without_error'] < ones, color='red', interpolate=True)
            ax.fill_between(prr['time'], y1=prr['received'], y2=ones, where=prr['received'] < ones, color='0.5', interpolate=True)

            # lines = ax.plot_date(prr['time'], prr['received'], markersize=1.5, c='b', linestyle='-', linewidth=1)
            # lines = ax.plot_date(prr['time'], prr['decoded_without_error'], markersize=1.5, c='r', linestyle='-', linewidth=1)
            if sum(prr['coded_without_error']) > 0:
                lines = ax.plot_date(prr['time'], prr['coded_without_error'], markersize=0, c='b', linestyle='-', linewidth=0.5)
            else:
                lines = ax.plot_date(prr['time'], prr['received_without_error'], markersize=0, c='k', linestyle='-', linewidth=0.5)

            ax.set_ylim(ymin=0, ymax=1)
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
        if nkey in ['rssi', 'lqi', 'bit_errors', 'byte_errors', 'temperature']:
            plot = self.create_mean_time_plot_for_key(key)
        elif nkey in ['hist_rssi', 'hist_lqi', 'hist_bit_errors', 'hist_byte_errors']:
            plot = self.create_histogram_plot_for_key(nkey)
        elif nkey in ['xor']:
            plot = self.create_xor_plot()
        elif nkey in ['prr']:
            plot = self.create_prr_plot()
        elif nkey in ['burst_errors']:
            plot = self.create_burst_error_plot()

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
        keys = ['Hist RSSI', 'Hist LQI', 'Hist Bit Errors', 'Hist Byte Errors', 'Burst Errors',
                'Xor', 'PRR']
        for key in keys:
            self.save_plot_for_key(key)


    def save_plot_to_file(self, plot, filename):
        if len(self.links) > 0 and plot:
            self.logger.debug("Saving Plot to file: '{}'".format(filename))
            plot.savefig(os.path.join(os.path.dirname(__file__), '..', 'plots', filename))
