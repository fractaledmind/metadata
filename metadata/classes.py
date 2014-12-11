#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

import time
import parsedatetime
from datetime import datetime

import utils


class MDAttribute(object):

    def __init__(self, info, ignore_case=True, ignore_diacritics=True):
        self._ignore_case = ignore_case
        self._ignore_diacritics = ignore_diacritics
        for k, v in info.items():
            setattr(self, k, v)
        self.key = utils.clean_attribute(self.id)

    def format(self):
        return self.id

    # Modifier Properties  ----------------------------------------------------

    @property
    def ignore_case(self):
        return self._ignore_case

    @ignore_case.setter
    def ignore_case(self, value):
        self._ignore_case = value

    @property
    def ignore_diacritics(self):
        return self._ignore_diacritics

    @ignore_diacritics.setter
    def ignore_diacritics(self, value):
        self._ignore_diacritics = value

    # Comparison Operators  ---------------------------------------------------

    def __eq__(self, value):
        return MDComparison(self, '==', value)

    def __ne__(self, value):
        return MDComparison(self, '!=', value)

    def __lt__(self, value):
        if self._comparison_check(value):
            return MDComparison(self, '<', value)

    def __gt__(self, value):
        if self._comparison_check(value):
            return MDComparison(self, '>', value)

    def __le__(self, value):
        if self._comparison_check(value):
            return MDComparison(self, '<=', value)

    def __ge__(self, value):
        if self._comparison_check(value):
            return MDComparison(self, '>=', value)

    def in_range(self, min_value, max_value):
        value = (min_value, max_value)
        return MDComparison(self, 'InRange', value)

    # Helper method  ----------------------------------------------------------

    def _comparison_check(self, value):
        if 'date' in self.key:
            return True
        elif isinstance(value, int):
            return True
        elif isinstance(value, float):
            return True
        else:
            try:
                int(value)
                return True
            except TypeError:
                raise Exception('Invalid operator for non-date attribute')


class MDComparison(object):
    def __init__(self, attribute, operator, predicate):
        self.attribute = attribute
        self.operator = operator
        self.predicate = predicate

    def format(self):
        # check for `InRange` operator
        if self.operator == 'InRange':
            return self._format_inrange()
        else:
            # check if attribute is date attribute
            if 'date' in self.attribute.key:
                query_val = self._parse_date_value(self.predicate)
            elif isinstance(self.predicate, int):
                query_val = unicode(self.predicate)
            elif isinstance(self.predicate, float):
                query_val = unicode(self.predicate)
            else:
                quoted_val = self._quote_value(self.predicate)
                query_val = self._modify_comparison(quoted_val)
            query = [self.attribute.id, self.operator, query_val]
            return ' '.join(query)

    # Expression Operators  ---------------------------------------------------

    def __and__(self, other):
        """Implements bitwise and using the & operator."""
        if isinstance(other, MDComparison):
            return MDExpression(' && ', self, other)
        elif isinstance(other, MDExpression):
            return MDExpression(' && ', self, other)

    def __or__(self, other):
        """Implements bitwise or using the | operator."""
        if isinstance(other, MDComparison):
            return MDExpression(' || ', self, other)
        elif isinstance(other, MDExpression):
            return MDExpression(' && ', self, other)

    # Helper methods  ---------------------------------------------------------

    @staticmethod
    def _quote_value(value):
        clean_value = value.replace('"', '\\"')\
                           .replace("'", "\\'")
        return '"' + clean_value + '"'

    def _modify_comparison(self, value):
        mod = []
        if self.attribute.ignore_case:
            mod.append('c')
        if self.attribute.ignore_diacritics:
            mod.append('d')
        # return properly formatted comparison expression
        if mod:
            return value + ''.join(mod)
        else:
            return value

    def _format_inrange(self):
        if 'date' in self.attribute.key:
            min_v = self._parse_date_value(self.predicate[0])
            max_v = self._parse_date_value(self.predicate[1])
        else:
            min_v, max_v = self.value
        return 'InRange({0}, {1}, {2})'.format(self.attribute.id,
                                               min_v,
                                               max_v)

    def _parse_date_value(self, value):
        cal = parsedatetime.Calendar()
        struct_time = cal.parse(value)
        timestamp = time.mktime(struct_time[0])
        iso_date = datetime.fromtimestamp(timestamp).isoformat()
        return '$time.iso({})'.format(iso_date)


class MDExpression(object):
    def __init__(self, operator, *units):
        self.operator = operator
        self.units = self.pre_format(units)

    def format(self):
        return self.operator.join(self.units)

    # Expression Operators  ---------------------------------------------------

    def __and__(self, other):
        """Implements bitwise and using the & operator."""
        if isinstance(other, MDComparison):
            return MDExpression(' && ', self, other)
        elif isinstance(other, MDExpression):
            return MDExpression(' && ', self, other)

    def __or__(self, other):
        """Implements bitwise or using the | operator."""
        if isinstance(other, MDComparison):
            return MDExpression(' || ', self, other)
        elif isinstance(other, MDExpression):
            return MDExpression(' && ', self, other)

    # Helper method  ----------------------------------------------------------

    @staticmethod
    def pre_format(units):
        clean_units = []
        for comparison in units:
            # nested expressions are wrapped in parens
            if isinstance(comparison, MDExpression):
                clean = '(' + comparison.format() + ')'
                clean_units.append(clean)
            elif isinstance(comparison, MDComparison):
                clean_units.append(comparison.format())
        return clean_units
