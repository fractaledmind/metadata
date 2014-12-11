#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

import sys
import itertools
import subprocess

import utils
from classes import MDAttribute

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


def get_all_attributes():
    """Return list of dictionaries with data for all OS X metadata attributes

    :returns: data on all OS X metadata attributes
    :rtype: ``list`` of ``dict``s

    """
    # get all OS X metadata attributes
    attributes = utils.decode(subprocess.check_output(['mdimport', '-A']))
    # prepare key names for the four columns
    keys = ('id', 'name', 'description', 'aliases')
    # create list of dicts, mapping ``keys`` to an item's columns
    data = [dict(itertools.izip(keys,
                                [item.replace("'", "")
                                 for item in attribute.split('\t\t')]))
            for attribute in attributes.splitlines()]
    return data

# dynamically generate module attribute objects
__module = sys.modules[__name__]
__attributes = get_all_attributes()
for __info in __attributes:
    __name = utils.clean_attribute(__info['id'])
    setattr(__module, __name, MDAttribute(__info))

# set ``attributes.all``, filtering out non metadata
all = [attr
       for attr in __module.__dict__.keys()
       if not attr.startswith('__')
       if not attr.startswith('MD')
       if not attr == 'ATTR_GROUPS']

__all__ = all


if __name__ == '__main__':
    pass
