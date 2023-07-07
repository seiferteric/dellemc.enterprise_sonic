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
from ansible_collections.dellemc.enterprise_sonic.plugins.module_utils.network.sonic.facts.facts import (
    Facts,
)
from ansible_collections.dellemc.enterprise_sonic.plugins.module_utils.network.sonic.sonic import (
    to_request,
    edit_config,
)
from ansible_collections.dellemc.enterprise_sonic.plugins.module_utils.network.sonic.utils.utils import (
    update_states,
    get_diff,
)


TRUST_STORES_PATH = "data/openconfig-pki:pki/trust-stores"
SECURITY_PROFILES_PATH = "data/openconfig-pki:pki/security-profiles"
TRUST_STORE_PATH = "data/openconfig-pki:pki/trust-stores/trust-store"
SECURITY_PROFILE_PATH = "data/openconfig-pki:pki/security-profiles/security-profile"

PATCH = "patch"
DELETE = "delete"
PUT = "put"
TEST_KEYS = [
    {"security-profiles": {"profile-name": ""}},
    {"trust-stores": {"name": ""}},
]


class Pki(ConfigBase):
    """
    The sonic_pki class
    """

    gather_subset = [
        "!all",
        "!min",
    ]

    gather_network_resources = [
        "pki",
    ]

    def get_pki_facts(self):
        """Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(
            self.gather_subset, self.gather_network_resources
        )
        pki_facts = facts["ansible_network_resources"].get("pki")
        if not pki_facts:
            return {}
        return pki_facts

    def execute_module(self):
        """Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {"changed": False}
        warnings = list()
        commands = list()

        existing_pki_facts = self.get_pki_facts()
        commands, requests = self.set_config(existing_pki_facts)
        if commands and len(requests) > 0:
            if not self._module.check_mode:
                try:
                    edit_config(self._module, to_request(self._module, requests))
                except ConnectionError as exc:
                    self._module.fail_json(msg=str(exc), code=exc.code)
            result["changed"] = True
        result["commands"] = commands

        changed_pki_facts = self.get_pki_facts()

        result["before"] = existing_pki_facts
        if result["changed"]:
            result["after"] = changed_pki_facts

        result["warnings"] = warnings

        return result

    def set_config(self, existing_pki_facts):
        """Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params["config"]
        have = existing_pki_facts
        resp = self.set_state(want, have)
        return to_list(resp)

    def set_state(self, want, have):
        """Select the appropriate function based on the state provided

        :param want: the desired configuration as a dictionary
        :param have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        requests = []
        state = self._module.params["state"]
        if not want:
            want = {}

        diff = get_diff(want, have, list(TEST_KEYS))

        if state == "overridden":
            commands, requests = self._state_overridden(want, have, diff)
        elif state == "deleted":
            commands, requests = self._state_deleted(want, have, diff)
        elif state == "merged":
            commands, requests = self._state_merged(want, have, diff)
        elif state == "replaced":
            commands, requests = self._state_replaced(want, have, diff)
        return commands, requests

    def _state_replaced(self, want, have, diff):
        """Select the appropriate function based on the state provided

        :param want: the desired configuration as a dictionary
        :param have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = diff or {}
        requests = []

        sps = diff.get("security-profiles") or []
        tss = diff.get("trust-stores") or []
        for sp in sps:
            requests.append(
                {
                    "path": SECURITY_PROFILE_PATH + "=" + sp.get("profile-name"),
                    "method": PUT,
                    "data": mk_sp_config(sp),
                }
            )
        for ts in tss:
            requests.append(
                {
                    "path": TRUST_STORE_PATH + "=" + ts.get("name"),
                    "method": PUT,
                    "data": mk_ts_config(ts),
                }
            )
        if commands and requests:
            commands = update_states(commands, "replaced")
        else:
            commands = []

        return commands, requests

    def _state_overridden(self, want, have, diff):
        """The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """

        commands = []
        requests = []
        # import epdb; epdb.serve()
        want_tss = [ts.get("name") for ts in want.get("trust-stores") or []]
        want_sps = [
            sp.get("profile-name") for sp in want.get("security-profiles") or []
        ]
        have_tss = [ts.get("name") for ts in have.get("trust-stores") or []]
        have_sps = [
            sp.get("profile-name") for sp in have.get("security-profiles") or []
        ]

        have_dict = {
            "security-profiles": {
                sp.get("profile-name"): sp for sp in have.get("security-profiles") or []
            },
            "trust-stores": {
                ts.get("name"): ts for ts in have.get("trust-stores") or []
            },
        }

        for sp in have_sps:
            if sp not in want_sps:
                requests.append(
                    {"path": SECURITY_PROFILE_PATH + "=" + sp, "method": DELETE}
                )
                commands.append(
                    update_states(have_dict["security-profiles"][sp], "deleted")
                )

        for ts in have_tss:
            if ts not in want_tss:
                requests.append({"path": TRUST_STORE_PATH + "=" + ts, "method": DELETE})
                commands.append(update_states(have_dict["trust-stores"][ts], "deleted"))

        for sp in want.get("security-profiles") or []:
            if sp != have_dict["security-profiles"].get(sp.get("profile-name")):
                requests.append(
                    {
                        "path": SECURITY_PROFILE_PATH + "=" + sp.get("profile-name"),
                        "method": PUT,
                        "data": mk_sp_config(sp),
                    }
                )
                commands.append(
                    update_states(sp, "overridden")
                )
        for ts in want.get("trust-stores") or []:
            if ts != have_dict["trust-stores"].get(ts.get("name")):
                requests.append(
                    {
                        "path": TRUST_STORE_PATH + "=" + ts.get("name"),
                        "method": PUT,
                        "data": mk_ts_config(ts),
                    }
                )
                commands.append(
                    update_states(ts, "overridden")
                )

        return commands, requests

    def _state_merged(self, want, have, diff):
        """The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = diff or {}
        requests = []

        for ts in commands.get("trust-stores") or []:
            requests.append(
                {"path": TRUST_STORE_PATH, "method": PATCH, "data": mk_ts_config(ts)}
            )

        for sp in commands.get("security-profiles") or []:
            requests.append(
                {
                    "path": SECURITY_PROFILE_PATH,
                    "method": PATCH,
                    "data": mk_sp_config(sp),
                }
            )

        if commands and requests:
            commands = update_states(commands, "merged")
        else:
            commands = []

        return commands, requests

    def _state_deleted(self, want, have, diff):
        """The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        requests = []
        current_ts = [
            ts.get("name") for ts in have.get("trust-stores") or [] if ts.get("name")
        ]
        current_sp = [
            sp.get("profile-name")
            for sp in have.get("security-profiles") or []
            if sp.get("profile-name")
        ]
        if not want:
            commands = have
            for sp in current_sp:
                requests.append(
                    {"path": SECURITY_PROFILE_PATH + "=" + sp, "method": DELETE}
                )
            for ts in current_ts:
                requests.append({"path": TRUST_STORE_PATH + "=" + ts, "method": DELETE})
        else:
            commands = want
            for sp in commands.get("security-profiles") or []:
                if sp.get("profile-name") in current_sp:
                    requests.append(
                        {
                            "path": SECURITY_PROFILE_PATH
                            + "="
                            + sp.get("profile-name"),
                            "method": DELETE,
                        }
                    )
            for ts in commands.get("trust-stores") or []:
                if ts.get("name") in current_ts:
                    requests.append(
                        {
                            "path": TRUST_STORE_PATH + "=" + ts.get("profile-name"),
                            "method": DELETE,
                        }
                    )

        if commands and requests:
            commands = update_states([commands], "deleted")
        else:
            commands = []

        return commands, requests


def mk_sp_config(indata):
    outdata = {k: v for k, v in indata.items() if v is not None}
    output = {
        "openconfig-pki:security-profile": [
            {"profile-name": outdata.get("profile-name"), "config": outdata}
        ]
    }
    return output


def mk_ts_config(indata):
    outdata = {k: v for k, v in indata.items() if v is not None}
    output = {
        "openconfig-pki:trust-store": [{"name": outdata.get("name"), "config": outdata}]
    }
    return output
