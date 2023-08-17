#!/usr/bin/python
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
The module file for sonic_pki
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': '<support_group>'
}

DOCUMENTATION = """
---
module: sonic_pki
version_added: 2.3.0
short_description: 'Manages PKI attributes of Enterprise Sonic'
description: 'Manages PKI attributes of Enterprise Sonic'
author: Eric Seifert
notes:
  - 'Tested against Dell Enterprise SONiC 4.1.0'
options:
  config:
    description: The provided configuration
    type: dict
    suboptions:
      trust-stores:
        description: Store of CA Certificates
        type: list
        elements: dict
        suboptions:
          name:
            type: str
            description: The name of the Trust Store
          ca-name:
            type: list
            elements: str
            description: List of CA certificates in the trust store.
      security-profiles:
        description: Application Security Profiles
        type: list
        elements: dict
        suboptions:
          profile-name:
            type: str
            description: Profile Name
          certificate-name:
            type: str
            description: Host Certificate Name
          trust-store:
            type: str
            description: Name of associated trust-store
          revocation-check:
            description: Require certificate revocation check succeeds
            type: bool
          peer-name-check:
            description: Require peer name is verified
            type: bool
          key-usage-check:
            description: Require key usage is enforced
            type: bool
          cdp-list:
            description: Global list of CDP's
            type: list
            elements: str
          ocsp-responder-list:
            description: Global list of OCSP responders
            type: list
            elements: str
  state:
    description:
      - The state of the configuration after module completion.
    type: str
    choices: ['merged', 'deleted', 'replaced', 'overridden']
    default: merged
"""
EXAMPLES = """
# Using "merged" state for initial config
#
# Before state:
# -------------
#
# sonic# show running-configuration | grep crypto
# sonic#
#
---
- name: PKI Config Test
  hosts: datacenter
  gather_facts: false
  connection: httpapi
  collections:
    - dellemc.enterprise_sonic
  tasks:
    - name: "Initial Config"
      sonic_pki:
        config:
          security-profiles:
            - profile-name: rest
              ocsp-responder-list:
                - http://example.com/ocspa
                - http://example.com/ocspb
              certificate-name: host
              trust-store: default-ts
          trust-stores:
            - name: default-ts
              ca-name:
                - CA2
        state: merged

# After state:
# ------------
#
# sonic# show running-configuration | grep crypto
# crypto trust-store default-ts ca-cert CA2
# crypto security-profile rest
# crypto security-profile trust-store rest default-ts
# crypto security-profile certificate rest host
# crypto security-profile ocsp-list rest http://example.com/ocspa,http://example.com/ocspb

# Using "deleted" state to remove configuration
#
# Before state:
# ------------
#
# sonic# show running-configuration | grep crypto
# crypto trust-store default-ts ca-cert CA2
# crypto security-profile rest
# crypto security-profile trust-store rest default-ts
# crypto security-profile certificate rest host
# crypto security-profile ocsp-list rest http://example.com/ocsp
#
---
- name: PKI Delete Test
  hosts: datacenter
  gather_facts: true
  connection: httpapi
  collections:
    - dellemc.enterprise_sonic
  tasks:
    - name: Remove trust-store from security-profile
      sonic_pki:
        config:
          security-profiles:
            - profile-name: rest
              trust-store: default-ts
        state: deleted
# After state:
# ------------
#
# sonic# show running-configuration | grep crypto
# crypto trust-store default-ts ca-cert CA2
# crypto security-profile rest
# crypto security-profile certificate rest host
# crypto security-profile ocsp-list rest http://example.com/ocsp

# Using "overridden" state

# Before state:
# ------------
#
# sonic# show running-configuration | grep crypto
# crypto trust-store default-ts ca-cert CA2
# crypto security-profile rest
# crypto security-profile trust-store rest default-ts
# crypto security-profile certificate rest host
# crypto security-profile ocsp-list rest http://example.com/ocspa,http://example.com/ocspb
#
---
- name: PKI Overridden Test
  hosts: datacenter
  gather_facts: false
  connection: httpapi
  collections:
    - dellemc.enterprise_sonic
  tasks:
    - name: "Overridden Config"
      sonic_pki:
        config:
          security-profiles:
            - profile-name: telemetry
              ocsp-responder-list:
                - http://example.com/ocspb
              revocation-check: true
              trust-store: telemetry-ts
              certificate-name: host
          trust-stores:
            - name: telemetry-ts
              ca-name: CA
        state: overridden
# After state:
# -----------
#
# sonic# show running-configuration | grep crypto
# crypto trust-store telemetry-ts ca-cert CA
# crypto security-profile telemetry revocation-check true
# crypto security-profile trust-store telemetry telemetry-ts
# crypto security-profile certificate telemetry host
# crypto security-profile ocsp-list telemetry http://example.com/ocspb

# Using "replaced" state to update config

# Before state:
# ------------
#
# sonic# show running-configuration | grep crypto
# crypto trust-store default-ts ca-cert CA2
# crypto security-profile rest
# crypto security-profile trust-store rest default-ts
# crypto security-profile certificate rest host
# crypto security-profile ocsp-list rest http://example.com/ocspa,http://example.com/ocspb
#
---
- name: PKI Replace Test
  hosts: datacenter
  gather_facts: false
  connection: httpapi
  collections:
    - dellemc.enterprise_sonic
  tasks:
    - name: "Replace Config"
      sonic_pki:
        config:
          security-profiles:
            - profile-name: rest
              ocsp-responder-list:
                - http://example.com/ocsp
              revocation-check: false
              trust-store: default-ts
              certificate-name: host
        state: replaced
# After state:
# -----------
#
# sonic# show running-configuration | grep crypto
# crypto trust-store default-ts ca-cert CA2
# crypto security-profile rest
# crypto security-profile trust-store rest default-ts
# crypto security-profile certificate rest host
# crypto security-profile ocsp-list rest http://example.com/ocspa,http://example.com/ocspb

"""
RETURN = """
before:
  description: The configuration prior to the model invocation.
  returned: always
  sample: >
    The configuration returned will always be in the same format
     of the parameters above.
after:
  description: The resulting configuration model invocation.
  returned: when changed
  sample: >
    The configuration returned will always be in the same format
     of the parameters above.
commands:
  description: The set of commands pushed to the remote device.
  returned: always
  type: list
  sample: ['command 1', 'command 2', 'command 3']
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.enterprise_sonic.plugins.module_utils.network.sonic.argspec.pki.pki import PkiArgs
from ansible_collections.dellemc.enterprise_sonic.plugins.module_utils.network.sonic.config.pki.pki import Pki


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=PkiArgs.argument_spec,
                           supports_check_mode=True)

    result = Pki(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
