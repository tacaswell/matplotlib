"""

The data_view module provides a set of experimental class to provide semantic


"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
import np


class Histogram(object):
    """
    High-level semantic object for dealing with histograms.

    The 'plotable' data is a histogram is n counts and n+1 bin edges

    The 'secondary data' is a n off sets (think the bottom kwarg)

    The 'raw data' is an arbitrarily long sequence of number

    The 'type' is {'bar', 'line'}

    Styling related properties:
       edgecolor : color of the edges
       linewidth : width of the edges
       base_line_axis : {'t', 'b', 'l', 'r'} which way the bars 'increase'
       base_line_offset : constant, where the baseline is

       bar-only styling:
           facecolor : color of face
           width : scalar, width of the bar (as fraction of bin edge-to-edge)
           edge_offset : scalar, as fraction of bin edge-to-edge where should the
                         left edge of the bar start

    """
    def _draw_as_bar(ax, edges, counts, offset, styling):
        if 'width' not in styling:
            styling['width'] = np.ptp(edges) / len(counts)
        ax.bar(ax, edges, counts, **styling)

    # These should get validation functions
    # maybe we want to do these with traitlets?
    # can traitlets do joint validation, ex edge_offset + width < 1?
    _default_styles = {'edgecolor': 'r',
                       'linewidth': 1,
                       'base_line_axes': 'b',
                       'base_line_offset': 0,
                       'facecolor': 'r',
                       'width': 1,
                       'edge_offset': 0}

    def __init__(self, ax, raw_data, bins=None, hist_type=None, style_dict=None):
        """
        ax : Axes
            The axes object to draw artists to

        raw_data : array-like
            The raw-data to histogram

        bins : array-like, int, or None
            Passed to np.histogram

        hist_type : str
           The type of historgam (line or bar)

        style_dict : dict
           dictionary of style information, unpacked into properties
        """
        #
        self.ax = ax
        # make a copy of the data (paranoia vs memory hit)
        self._raw_data = np.array(raw_data)
        self._counts, self._edges = np.histogram(self._raw_data,
                                                 bins=bins)
        self._artists = None
        if hist_type is None:
            hist_type = 'bar'

        self._hist_type = hist_type

        if style_dict is None:
            style_dict = {}

        final_style_dict = dict(self._default_styles)
        final_style_dict.update(style_dict)

        for k, v in six.iteritems(final_style_dict):
            setattr(self, k, v)

    @property
    def hist_type(self):
        return self._hist_type

    def redraw(self):
        self._remove_artists()
        art_gen_fun = self._style_map[self.style]
        res = art_gen_fun
        self._artist.extends(res)

    def _remove_artists(self):
        if self._artists is not None:
            for a in self._artists:
                a.remove()
