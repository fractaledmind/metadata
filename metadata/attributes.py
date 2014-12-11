#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2014 stephen.margheim@gmail.com
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 9 December 2014
#
from __future__ import unicode_literals

import sys
import time
import itertools
import subprocess
import parsedatetime
from datetime import datetime

from utils import text


ATTR_GROUPS = {
    "File System Metadata Attribute Keys": [
        "kMDItemDisplayName",
        "kMDItemFSContentChangeDate",
        "kMDItemFSCreationDate",
        "kMDItemFSInvisible",
        "kMDItemFSIsExtensionHidden",
        "kMDItemFSLabel",
        "kMDItemFSName",
        "kMDItemFSNodeCount",
        "kMDItemFSOwnerGroupID",
        "kMDItemFSOwnerUserID",
        "kMDItemFSSize",
        "kMDItemPath"
    ],
    "Video Metadata Attribute Keys": [
        "kMDItemAudioBitRate",
        "kMDItemCodecs",
        "kMDItemDeliveryType",
        "kMDItemMediaTypes",
        "kMDItemStreamable",
        "kMDItemTotalBitRate",
        "kMDItemVideoBitRate",
        "kMDItemDirector",
        "kMDItemProducer",
        "kMDItemGenre",
        "kMDItemPerformers",
        "kMDItemOriginalFormat",
        "kMDItemOriginalSource"
    ],
    "Audio Metadata Attribute Keys": [
        "kMDItemAppleLoopDescriptors",
        "kMDItemAppleLoopsKeyFilterType",
        "kMDItemAppleLoopsLoopMode",
        "kMDItemAppleLoopsRootKey",
        "kMDItemAudioChannelCount",
        "kMDItemAudioEncodingApplication",
        "kMDItemAudioSampleRate",
        "kMDItemAudioTrackNumber",
        "kMDItemComposer",
        "kMDItemIsGeneralMIDISequence",
        "kMDItemKeySignature",
        "kMDItemLyricist",
        "kMDItemMusicalGenre",
        "kMDItemMusicalInstrumentCategory",
        "kMDItemMusicalInstrumentName",
        "kMDItemRecordingDate",
        "kMDItemRecordingYear",
        "kMDItemTempo",
        "kMDItemTimeSignature"
    ],
    "Common Metadata Attribute Keys": [
        "kMDItemAttributeChangeDate",
        "kMDItemAudiences",
        "kMDItemAuthors",
        "kMDItemAuthorAddresses",
        "kMDItemCity",
        "kMDItemComment",
        "kMDItemContactKeywords",
        "kMDItemContentCreationDate",
        "kMDItemContentModificationDate",
        "kMDItemContentType",
        "kMDItemContributors",
        "kMDItemCopyright",
        "kMDItemCountry",
        "kMDItemCoverage",
        "kMDItemCreator",
        "kMDItemDescription",
        "kMDItemDueDate",
        "kMDItemDurationSeconds",
        "kMDItemEmailAddresses",
        "kMDItemEncodingApplications",
        "kMDItemFinderComment",
        "kMDItemFonts",
        "kMDItemHeadline",
        "kMDItemIdentifier",
        "kMDItemInstantMessageAddresses",
        "kMDItemInstructions",
        "kMDItemKeywords",
        "kMDItemKind",
        "kMDItemLanguages",
        "kMDItemLastUsedDate",
        "kMDItemNumberOfPages",
        "kMDItemOrganizations",
        "kMDItemPageHeight",
        "kMDItemPageWidth",
        "kMDItemParticipants",
        "kMDItemPhoneNumbers",
        "kMDItemProjects",
        "kMDItemPublishers",
        "kMDItemRecipients",
        "kMDItemRecipientAddresses",
        "kMDItemRights",
        "kMDItemSecurityMethod",
        "kMDItemStarRating",
        "kMDItemStateOrProvince",
        "kMDItemTextContent",
        "kMDItemTitle",
        "kMDItemVersion",
        "kMDItemWhereFroms",
        "kMDItemAuthorEmailAddresses",
        "kMDItemRecipientEmailAddresses",
        "kMDItemTheme",
        "kMDItemSubject",
        "kMDItemCFBundleIdentifier",
        "kMDItemFSHasCustomIcon",
        "kMDItemFSIsStationery",
        "kMDItemInformation",
        "kMDItemURL"
    ],
    "Image Metadata Attribute Keys": [
        "kMDItemPixelHeight",
        "kMDItemPixelWidth",
        "kMDItemPixelCount",
        "kMDItemColorSpace",
        "kMDItemBitsPerSample",
        "kMDItemFlashOnOff",
        "kMDItemFocalLength",
        "kMDItemAcquisitionMake",
        "kMDItemAcquisitionModel",
        "kMDItemISOSpeed",
        "kMDItemOrientation",
        "kMDItemLayerNames",
        "kMDItemWhiteBalance",
        "kMDItemAperture",
        "kMDItemProfileName",
        "kMDItemResolutionWidthDPI",
        "kMDItemResolutionHeightDPI",
        "kMDItemExposureMode",
        "kMDItemExposureTimeSeconds",
        "kMDItemEXIFVersion",
        "kMDItemAlbum",
        "kMDItemHasAlphaChannel",
        "kMDItemRedEyeOnOff",
        "kMDItemMeteringMode",
        "kMDItemMaxAperture",
        "kMDItemFNumber",
        "kMDItemExposureProgram",
        "kMDItemExposureTimeString",
        "kMDItemEXIFGPSVersion",
        "kMDItemAltitude",
        "kMDItemLatitude",
        "kMDItemLongitude",
        "kMDItemTimestamp",
        "kMDItemSpeed",
        "kMDItemGPSTrack",
        "kMDItemImageDirection",
        "kMDItemNamedLocation"
    ]
}


def get_all_attributes():
    """Get dictionary of all possible metadata attributes."""
    # get all OS X metadata attributes
    attributes = text.decode(subprocess.check_output(['mdimport', '-A']))
    # prepare key names for the four columns
    keys = ('id', 'name', 'description', 'aliases')
    # create list of dicts, mapping ``keys`` to an item's columns
    data = [dict(itertools.izip(keys,
                                [item.replace("'", "")
                                 for item in attribute.split('\t\t')]))
            for attribute in attributes.splitlines()]
    return data


class MDAttribute(object):

    def __init__(self, info, ignore_case=True, ignore_diacritics=True):
        self._ignore_case = ignore_case
        self._ignore_diacritics = ignore_diacritics
        for k, v in info.items():
            setattr(self, k, v)
        self.key = text.clean_key(self.id)

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


# dynamically generate module attribute objects
__module = sys.modules[__name__]
__attributes = get_all_attributes()
# prepare attribute group lists
#file_system, image, audio, video, common = ([], [], [], [], [])
for __info in __attributes:
    __name = text.clean_key(__info['id'])
    """
    for _group, ids in ATTR_GROUPS.items():
        # ensure item matches to group
        if __info['id'] in ids:
            # add group name to `__info` dict
            __info.update({'group': _group})
            __info.update({'key': __name})
            # add `__info` dict to proper sub-group
            if 'Image' in _group:
                image.append(__info)
            elif 'Audio' in _group:
                audio.append(__info)
            elif 'Video' in _group:
                video.append(__info)
            elif 'Common' in _group:
                common.append(__info)
            elif 'File System' in _group:
                file_system.append(__info)
        print(__info)
    """
    setattr(__module, __name, MDAttribute(__info))

all = [attr
       for attr in __module.__dict__.keys()
       if not attr.startswith('__')
       if not attr.startswith('MD')
       if not attr == 'ATTR_GROUPS']

__all__ = all


if __name__ == '__main__':
    pass
