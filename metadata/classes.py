#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

import time
from datetime import datetime

import parsedatetime
import utils


class MDAttribute(object):
    """Represents an OS X Spotlight Metadata Attribute

    You probably shouldn't use this class directly, but via
    :mod:`~metadata.attributes`.

    :param info: `id`, `name`, `description`, and `aliases` for attribute.
    :type info: :class:`dict`
    :param ignore_case: ignore case in :class:`MDComparison`.
    :type ignore_case: :class:`Boolean`
    :param ignore_diacritics: ignore diacritics in :class:`MDComparison`.
    :type ignore_diacritics: :class:`Boolean`

    """

    def __init__(self, info, ignore_case=True, ignore_diacritics=True):
        self._ignore_case = ignore_case
        self._ignore_diacritics = ignore_diacritics
        # set data attributes from ``info`` dictionary
        for k, v in info.items():
            setattr(self, k, v)
        self.key = utils.clean_attribute(self.id)

    # Representation Magic Methods  -------------------------------------------

    def __str__(self):
        """Return :class:`str` representation of the :class:`MDAttribute`
        object. The :class:`str` representation is a UTF8 encoded string.

        """
        return str(self.__unicode__().encode('utf-8'))

    def __unicode__(self):
        """Return :class:`unicode` representation of the :class:`MDAttribute`
        object.

        """
        return utils.decode(self.id)

    # Modifier Properties  ----------------------------------------------------

    @property
    def ignore_case(self):
        """Ignore case in :class:`MDComparison`.

        """
        return self._ignore_case

    @ignore_case.setter
    def ignore_case(self, value):
        """Change ignore case in :class:`MDComparison`.

        Defaults to ``True`` if ``value`` anything except ``False``.

        """
        self._ignore_case = bool(value)

    @property
    def ignore_diacritics(self):
        """Ignore diacritics in :class:`MDComparison`.

        """
        return self._ignore_diacritics

    @ignore_diacritics.setter
    def ignore_diacritics(self, value):
        """Change ignore diacritics in :class:`MDComparison`.

        Defaults to ``True`` if ``value`` anything except ``False``.

        """
        self._ignore_diacritics = bool(value)

    # Comparison Magic Operators  ---------------------------------------------

    def __eq__(self, value):
        """Defines behavior for the equality operator, ==.

        :returns: :class:`MDComparison` object

        """
        return MDComparison(self, '==', value)

    def __ne__(self, value):
        """Defines behavior for the inequality operator, !=.

        :returns: :class:`MDComparison` object

        """
        return MDComparison(self, '!=', value)

    def __lt__(self, value):
        """Defines behavior for the less-than operator, <.

        ``value`` must be a number or a date.

        :returns: :class:`MDComparison` object

        """
        if self._comparison_check(value):
            return MDComparison(self, '<', value)

    def __gt__(self, value):
        """Defines behavior for the greater-than operator, >.

        ``value`` must be a number or a date.

        :returns: :class:`MDComparison` object

        """
        if self._comparison_check(value):
            return MDComparison(self, '>', value)

    def __le__(self, value):
        """Defines behavior for the less-than-or-equal-to operator, <=.

        ``value`` must be a number or a date.

        :returns: :class:`MDComparison` object

        """
        if self._comparison_check(value):
            return MDComparison(self, '<=', value)

    def __ge__(self, value):
        """Defines behavior for the greater-than-or-equal-to operator, >=.

        ``value`` must be a number or a date.

        :returns: :class:`MDComparison` object

        """
        if self._comparison_check(value):
            return MDComparison(self, '>=', value)

    def in_range(self, min_value, max_value):
        """Defines behavior for the range operation.

        ``min_value`` and ``max_value`` must be a number or a date.

        :returns: :class:`MDComparison` object

        """
        value = (min_value, max_value)
        return MDComparison(self, 'InRange', value)

    # Helper method  ----------------------------------------------------------

    def _comparison_check(self, value):
        """Ensure ``value`` is number or date.

        :returns: ``Boolean`` or ``Exception``

        """
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
    """Represents an OS X Spotlight file metadata query comparison.

    You probably shouldn't use this class directly, but by comparing a
    :class:`MDAttribute` to a predicate.

    :param attribute: the subject of the comparison
    :type attribute: :class:`MDAttribute`
    :param operator: the type of comparison
    :type operator: ``unicode``
    :param predicate: the predicate of the comparison
    :type predicate: ``unicode`` or ``int`` or ``float``

    """

    def __init__(self, attribute, operator, predicate):
        self.attribute = attribute
        self.operator = operator
        self.predicate = utils.decode(predicate)

    # Representation Magic Methods  -------------------------------------------

    def __str__(self):
        """Return :class:`str` representation of the :class:`MDComparison`
        object. The :class:`str` representation is a UTF8 encoded string.

        """
        return str(self.__unicode__().encode('utf-8'))

    def __unicode__(self):
        """Return :class:`unicode` representation of the :class:`MDComparison`
        object.

        """
        # check for `InRange` operator
        if self.operator == 'InRange':
            return self._format_inrange()
        else:
            predicate = self._prepare_predicate(self.predicate)
            query = [self.attribute.id, self.operator, predicate]
            return ' '.join(query)

    # Expression Magic Operators  ---------------------------------------------

    def __and__(self, other):
        """Implements bitwise `and` using the & operator.

        :param other: second half of query expression.
        :type other: :class:`MDComparison` or :class:`MDExpression`
        :returns: :class:`MDExpression` object

        """
        if isinstance(other, MDComparison):
            return MDExpression(' && ', self, other)
        elif isinstance(other, MDExpression):
            return MDExpression(' && ', self, other)
        else:
            msg = ('Invalid query expression! {} must be `MDComparison`'
                   'or `MDExpression` object.'.format(repr(other)))
            raise Exception(msg)

    def __or__(self, other):
        """Implements bitwise `or` using the | operator.

        :param other: second half of query expression.
        :type other: :class:`MDComparison` or :class:`MDExpression`
        :returns: :class:`MDExpression` object

        """
        if isinstance(other, MDComparison):
            return MDExpression(' || ', self, other)
        elif isinstance(other, MDExpression):
            return MDExpression(' && ', self, other)
        else:
            msg = ('Invalid query expression! {} must be `MDComparison`'
                   'or `MDExpression` object.'.format(repr(other)))
            raise Exception(msg)

    # Helper methods  ---------------------------------------------------------

    def _prepare_predicate(self, predicate):
        """Properly handle data, number, and string predicates
        for query comparisons.

        :param predicate: value of the comparison predicate.
        :type predicate: ``unicode``, ``int``, or ``float``
        :returns: ``unicode``

        """
        # if predicate is date attribute
        if 'date' in self.attribute.key:
            predicate = self._parse_date_value(predicate)
        # if predicate is number
        elif isinstance(predicate, int):
            predicate = unicode(predicate)
        # if predicate is float number
        elif isinstance(predicate, float):
            predicate = unicode(predicate)
        # else is string
        else:
            quoted_pred = self._quote_predicate(predicate)
            predicate = self._modify_comparison(quoted_pred)
        return predicate

    @staticmethod
    def _quote_predicate(predicate):
        """Ensure string ``predicate`` is properly quoted.

        :param predicate: string predicate of query comparison.
        :type predicate: ``unicode``
        :returns: properly quoted string
        :rtype: ``unicode``

        """
        clean_pred = predicate.replace('"', '\\"')\
                              .replace("'", "\\'")
        return '"' + clean_pred + '"'

    def _modify_comparison(self, predicate):
        """Ignore case and diacritics in query comparison,
        if :attr:`MDAttribute.ignore_case` or
        :attr:`MDAttribute.ignore_diacritics` is ``True``.

        :param predicate: string predicate of query comparison.
        :type predicate: ``unicode``
        :returns: properly formatted query comparison
        :rtype: ``unicode``

        """
        mod = []
        if self.attribute.ignore_case:
            mod.append('c')
        if self.attribute.ignore_diacritics:
            mod.append('d')
        # return properly formatted comparison expression
        if mod:
            return predicate + ''.join(mod)
        else:
            return predicate

    def _format_inrange(self):
        """Format :attr:`MDAttribute.in_range` string.

        :returns: properly formatted query string
        :rtype: ``unicode``

        """
        if 'date' in self.attribute.key:
            min_v = self._parse_date_value(self.predicate[0])
            max_v = self._parse_date_value(self.predicate[1])
        else:
            min_v, max_v = self.value
        return 'InRange({0}, {1}, {2})'.format(self.attribute.id,
                                               min_v,
                                               max_v)

    def _parse_date_value(self, predicate):
        """Parse human-readable date-related strings into an ISO formatted
        :mod:`datetime` object.

        :param predicate: string predicate of query comparison.
        :type predicate: ``unicode``
        :returns: properly formatted query comparison
        :rtype: ``unicode``

        """
        cal = parsedatetime.Calendar()
        struct_time = cal.parse(predicate)
        timestamp = time.mktime(struct_time[0])
        iso_date = datetime.fromtimestamp(timestamp).isoformat()
        return '$time.iso({})'.format(iso_date)


class MDExpression(object):
    def __init__(self, operator, *units):
        self.operator = operator
        self.units = self.pre_format(units)

    def __str__(self):
        """Return :class:`str` representation of the :class:`MDComparison`
        object. The :class:`str` representation is a UTF8 encoded string.

        """
        return str(self.__unicode__().encode('utf-8'))

    def __unicode__(self):
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
                clean = '(' + str(comparison) + ')'
                clean_units.append(clean)
            elif isinstance(comparison, MDComparison):
                clean_units.append(str(comparison))
        return clean_units
