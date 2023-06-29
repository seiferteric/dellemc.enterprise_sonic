#
# -*- coding: utf-8 -*-
# Copyright 2022 Dell EMC
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The sonic_pki class
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to it's desired end-state is
created
"""
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base import (
    ConfigBase,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    to_list,
)
from ansible_collections.dellemc.enterprise_sonic.plugins.module_utils.network.sonic.facts.facts import Facts
from ansible_collections.dellemc.enterprise_sonic.plugins.module_utils.network.sonic.sonic import (
    to_request,
    edit_config
)
from ansible_collections.dellemc.enterprise_sonic.plugins.module_utils.network.sonic.utils.utils import (
    update_states,
    get_diff,
    get_replaced_config,
    get_normalize_interface_name,
)


trust_stores_path="/data/openconfig-pki:pki/trust-stores"
security_profiles_path="/data/openconfig-pki:pki/security-profiles"
trust_store_path="/data/openconfig-pki:pki/trust-stores/trust-store"
security_profile_path="/data/openconfig-pki:pki/security-profiles/security-profile"

PATCH = 'patch'
DELETE = 'delete'
TEST_KEYS = [
    {'host': {'name': ''}},
]


class Pki(ConfigBase):
    """
    The sonic_pki class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'pki',
    ]

    def __init__(self, module):
        super(Pki, self).__init__(module)

    def get_pki_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        pki_facts = facts['ansible_network_resources'].get('pki')
        if not pki_facts:
            return []
        return pki_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        existing_pki_facts = self.get_pki_facts()
        commands.extend(self.set_config(existing_pki_facts))
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_pki_facts = self.get_pki_facts()

        result['before'] = existing_pki_facts
        if result['changed']:
            result['after'] = changed_pki_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_pki_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_pki_facts
        resp = self.set_state(want, have)
        return to_list(resp)

    def set_state(self, want, have):
        """ Select the appropriate function based on the state provided

        :param want: the desired configuration as a dictionary
        :param have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        requests = []
        state = self._module.params['state']
        if not want:
            want = {}

        diff = get_diff(want, have, TEST_KEYS)

        if state == 'overridden':
            commands, requests = self._state_overridden(want, have, diff)
        elif state == 'deleted':
            commands, requests = self._state_deleted(want, have, diff)
        elif state == 'merged':
            commands, requests = self._state_merged(want, have, diff)
        elif state == 'replaced':
            commands, requests = self._state_replaced(want, have, diff)
        return commands, requests

    def _state_replaced(self, want, have, diff):
        """ Select the appropriate function based on the state provided

        :param want: the desired configuration as a dictionary
        :param have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        requests = []
        replaced_config = get_replaced_config(want, have, TEST_KEYS)

        add_commands = []
        if replaced_config:
            del_requests = self.get_delete_pki_requests(replaced_config, have)
            requests.extend(del_requests)
            commands.extend(update_states(replaced_config, "deleted"))
            add_commands = want
        else:
            add_commands = diff

        if add_commands:
            add_requests = self.get_modify_pki_requests(add_commands, have)
            if len(add_requests) > 0:
                requests.extend(add_requests)
                commands.extend(update_states(add_commands, "replaced"))

        return commands, requests


    def _state_overridden(self, **kwargs):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        return commands

    def _state_merged(self, want):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        if want and want.get('trust-stores'):
            for ts in want.get('trust-stores'):
                commands.append({"path": trust_store_path, "method": "patch", "data": {"sonic-pki:TRUST_STORES_LIST": [ts]}})
        if want and want.get('security-profiles'):
            for sp in want.get('security-profiles'):
                commands.append({"path": security_profile_path, "method": "patch", "data": {"openconfig-pki:security-profile": [{"profile-name": sp.get("profile-name"), "config": sp}]}})
        
        return commands

    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        want = False
        commands = []
        if not want:
            commands.append({"path": trust_stores_path, "method": "delete", "data": ""})
            commands.append({"path": security_profiles_path, "method": "delete", "data": ""})
        else:
            pass
            

        return commands
    def get_delete_security_profiles(self, command, have):
        requests = []
        url = security_profile_path + "="

        mat_sp = []
        if have.get('security-profiles', None) and have['security-profiles'].get('profile-name', None):
            mat_sp = have['security-profiles']['profile-name']

        sps = []
        if command.get('security-profiles', None):
            if command['security-profiles'].get('profile-name', None):
                sps = command['security-profiles']['profile-name']
            else:
                sps = mat_sp

        if mat_sp and sps:
            for sp in sps:
                if next((m_sp for m_sp in mat_sp if m_sp['profile-name'] == sp['profile-name']), None):
                    requests.append({'path': url + sp['profile-name'], 'method': DELETE})

        return requests


    def get_delete_pki_requests(self, command, have):
        requests = []
        if not command:
            return requests

        requests.extend(self.get_delete_security_profiles(command, have))
        #requests.extend(self.get_delete_trust_stores(command, have))

        return requests


