from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

try:
    # IPython 4 import
    from traitlets.config import Configurable
    from traitlets import (Int, Float, Bool, Dict, List, Instance,
                            Union, TraitError, HasTraits, Unicode,
                            NoDefaultSpecified, TraitType, Tuple,
                            Undefined, TraitError, getargspec)
except ImportError:
    # IPython 3 import
    from IPython.utils.traitlest.config import Configurable
    from IPython.utils.traitlets import (Int, Float, Bool, Dict, List, Instance,
                                         Union, TraitError, HasTraits, TraitError,
                                         NoDefaultSpecified, TraitType)
import numpy as np
import re

# override for backward compatability
class Configurable(Configurable): pass
class TraitType(TraitType): pass

# overload handle is probably temporary
class OverloadMixin(object):

    def validate(self, obj, value):
        try:
            return super(OverloadMixin,self).validate(obj,value)
        except TraitError:
            if self.name:
                ohandle = '_%s_overload'%self.name
                if hasattr(obj, ohandle):
                    return getattr(obj, ohandle)(self, value)
            self.error(obj, value)

    def info(self):
        i = super(OverloadMixin,self).info()
        return 'overload resolvable, ' + i

class oInstance(OverloadMixin,Instance): pass

class Callable(TraitType):
    """A trait which is callable.

    Notes
    -----
    Classes are callable, as are instances
    with a __call__() method."""

    info_text = 'a callable'

    def validate(self, obj, value):
        if callable(value):
            return value
        else:
            self.error(obj, value)

class Color(TraitType):
    """A trait representing a color, can be either in RGB, or RGBA format.

    Arguments:
        force_rgb: bool: Force the return in RGB format instead of RGB. Default: False
        as_hex: bool: Return the hex value instead. Default: False
        default_alpha: float (0.0-1.0) or integer (0-255). Default alpha value (1.0)

    Accepts:
        string: a valid hex color string (i.e. #FFFFFF). With 4 or 7 chars.
        tuple: a tuple of ints (0-255), or tuple of floats (0.0-1.0)
        float: A gray shade (0-1)
        integer: A gray shade (0-255)

    Defaults: RGBA tuple, color black (0.0, 0.0, 0.0, 1.0)

    Return:
       A tuple of floats (r,g,b,a), (r,g,b) or a hex color string. i.e. "#FFFFFF".

    """
    metadata = {
        'force_rgb': False,
        'as_hex' : False,
        'default_alpha' : 1.0,
        }
    allow_none = True
    info_text = 'float, int, tuple of float or int, or a hex string color'
    default_value = (0.0,0.0,0.0, metadata['default_alpha'])
    named_colors = {}
    _re_color_hex = re.compile(r'#[a-fA-F0-9]{3}(?:[a-fA-F0-9]{3})?$')

    def _int_to_float(self, value):
        as_float = (np.array(value)/255).tolist()
        return as_float

    def _float_to_hex(self, value):
        as_hex = '#%02x%02x%02x' % tuple([int(np.round(v * 255)) for v in\
                                                                 value[:3]])
        return as_hex

    def _int_to_hex(self, value):
        as_hex = '#%02x%02x%02x' % value[:3]
        return as_hex

    def _hex_to_float(self, value):
        if len(value) == 7:
            split_hex = (value[1:3],value[3:5],value[5:7])
            as_float = (np.array([int(v,16) for v in split_hex])/255.0).tolist()
        elif len(value) == 4:
            as_float = (np.array([int(v+v,16) for v in value[1:]])/255.0).tolist()
        return as_float

    def _float_to_shade(self, value):
        grade = value*255.0
        return (grade,grade,grade)

    def _int_to_shade(self, value):
        grade = value/255.0
        return (grade,grade,grade)

    def validate(self, obj, value):
        in_range = False
        if value is True:
            self.error(obj, value)

        elif value is None or value is False or value in ['none','']:
            value = (0.0, 0.0, 0.0, 0.0)
            in_range = True

        elif isinstance(value, float):
            if 0 <= value <= 1:
                value = self._float_to_shade(value)
                in_range = True
            else:
                in_range = False

        elif isinstance(value, int):
            if 0 <= value <= 255:
                value = self._int_to_shade(value)
                in_range = True
            else:
                in_range = False

        elif isinstance(value, (tuple, list)) and len(value) in (3,4):
            is_all_float = np.prod([isinstance(v, (float)) for v in value])
            in_range = np.prod([(0 <= v <= 1) for v in value])
            if is_all_float and in_range:
                value = value
            else:
                is_all_int = np.prod([isinstance(v, int) for v in value])
                in_range = np.prod([(0 <= v <= 255) for v in value])
                if is_all_int and in_range:
                    value = self._int_to_float(value)

        elif isinstance(value, str) and len(value) in [4,7] and value[0] == '#':
            if self._re_color_hex.match(value):
                value = self._hex_to_float(value)
                in_range = np.prod([(0 <= v <= 1) for v in value])
                if in_range:
                    value = value

        elif isinstance(value, str) and value in self.named_colors:
            value = self.validate(obj, self.named_colors[value])
            in_range = True
            
        if in_range:
            # Convert to hex color string
            if self._metadata['as_hex']:
                return self._float_to_hex(value)

            # Ignores alpha and return rgb
            if self._metadata['force_rgb'] and in_range:
                return tuple(np.round(value[:3],5).tolist())

            # If no alpha provided, use default_alpha, also round the output
            if len(value) == 3:
                value = tuple(np.round((value[0], value[1], value[2], 
                             self._metadata['default_alpha']),5).tolist())
            elif len(value) == 4:
            # If no alpha provided, use default_alpha
                value = tuple(np.round(value,5).tolist())

            return value

        self.error(obj, value)