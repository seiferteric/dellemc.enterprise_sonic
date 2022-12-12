#
# -*- coding: utf-8 -*-
# Copyright 2022 Dell EMC
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

#############################################
#                WARNING                    #
#############################################
#
# This file is auto generated by the resource
#   module builder playbook.
#
# Do not edit this file manually.
#
# Changes to this file will be over written
#   by the resource module builder.
#
# Changes should be made in the model used to
#   generate this file or in the resource module
#   builder template.
#
#############################################

"""
The arg spec for the sonic_pki module
"""


class PkiArgs(object):  # pylint: disable=R0903
    """The arg spec for the sonic_pki module
    """

    def __init__(self, **kwargs):
        pass

    argument_spec = {'config': {'options': {'security-profiles': {'elements': 'list',
                                              'options': {'cdp-list': {'elements': 'str',
                                                                       'type': 'list'},
                                                          'certificate-name': {'type': 'str'},
                                                          'key-usage-check': {'type': 'bool'},
                                                          'ocsp-responder-list': {'elements': 'str',
                                                                                  'type': 'list'},
                                                          'peer-name-check': {'type': 'bool'},
                                                          'profile-name': {'type': 'str'},
                                                          'revocation-check': {'type': 'bool'},
                                                          'trust-store': {'type': 'str'}},
                                              'type': 'dict'},
                        'trust-stores': {'elements': 'dict',
                                         'options': {'ca-names': {'elements': 'str',
                                                                  'type': 'list'},
                                                     'name': {'type': 'str'}},
                                         'type': 'list'}},
            'type': 'dict'}}  # pylint: disable=C0301
