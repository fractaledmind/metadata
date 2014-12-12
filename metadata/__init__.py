#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

__title__ = 'metadata'
__version__ = '0.4.0'
__author__ = 'Stephen Margheim'
__license__ = 'MIT'
__copyright__ = 'Copyright © 2014 Stephen Margheim'

import sys
import itertools

import utils
from functions import find, list, write
from classes import MDAttribute, MDComparison, MDExpression

# TODO: organize attributes into groups
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


def attributes_generator():
    """Generate dictionaries with data for all OS X metadata attributes

    :returns: data on all OS X metadata attributes
    :rtype: ``generator`` of ``dict``s

    """
    # get all OS X metadata attributes
    attributes = utils.run_process(['mdimport', '-A'])
    # prepare key names for the four columns
    keys = ('id', 'name', 'description', 'aliases')
    # create list of dicts, mapping ``keys`` to an item's columns
    for attribute in attributes:
        attribute_data = [item.replace("'", "")
                          for item in attribute.split('\t\t')]
        keyed_data = itertools.izip(keys, attribute_data)
        yield dict(keyed_data)

# dynamically generate module attribute objects
__module = sys.modules[__name__]
for __info in attributes_generator():
    __name = utils.clean_attribute(__info['id'])
    setattr(__module, __name, MDAttribute(__info))

# set ``attributes``, filtering out non metadata
attributes = [attr
              for attr in __module.__dict__.keys()
              if not attr.startswith('__')
              if not attr.startswith('MD')
              if not attr == 'ATTR_GROUPS']


if __name__ == '__main__':
    pass
