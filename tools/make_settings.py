#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 CasX61
"""
Generate resources/settings.xml (Kodi's settings format version 1) with the
string ids from tools/i18n.py.

    python3 tools/make_settings.py
"""

import os

from i18n import ADDON, string_id as S

ID = 'script.auradeck'
TARGET = os.path.join(ADDON, 'resources', 'settings.xml')

QUALITIES = ['q_original', 'q_mp3_320', 'q_mp3_192', 'q_mp3_128', 'q_opus_160', 'q_opus_96', 'q_aac_256']


def _help(key):
    return f' help="{S(key)}"' if key else ''


def _depends(setting):
    if not setting:
        return ''
    return f'''
          <dependencies>
            <dependency type="enable" setting="{setting}">true</dependency>
          </dependencies>'''


def edit(setting_id, key, level=0, visible=True, help_key=None):
    hidden = '' if visible else '\n          <visible>false</visible>'
    return f'''        <setting id="{setting_id}" type="string" label="{S(key)}"{_help(help_key)}>
          <level>{level}</level>
          <default/>{hidden}
          <constraints>
            <allowempty>true</allowempty>
          </constraints>
          <control type="edit" format="string">
            <heading>{S(key)}</heading>
          </control>
        </setting>'''


def toggle(setting_id, key, default=True, help_key=None, depends=None, level=0):
    return f'''        <setting id="{setting_id}" type="boolean" label="{S(key)}"{_help(help_key)}>
          <level>{level}</level>
          <default>{'true' if default else 'false'}</default>{_depends(depends)}
          <control type="toggle"/>
        </setting>'''


def spinner(setting_id, key, default, minimum, step, maximum, depends=None, level=0):
    return f'''        <setting id="{setting_id}" type="integer" label="{S(key)}">
          <level>{level}</level>
          <default>{default}</default>
          <constraints>
            <minimum>{minimum}</minimum>
            <step>{step}</step>
            <maximum>{maximum}</maximum>
          </constraints>{_depends(depends)}
          <control type="spinner" format="integer"/>
        </setting>'''


def options(setting_id, key, labels, help_key=None):
    entries = '\n'.join(f'              <option label="{S(label)}">{index}</option>'
                        for index, label in enumerate(labels))
    return f'''        <setting id="{setting_id}" type="integer" label="{S(key)}"{_help(help_key)}>
          <level>0</level>
          <default>0</default>
          <constraints>
            <options>
{entries}
            </options>
          </constraints>
          <control type="spinner" format="string"/>
        </setting>'''


def action(setting_id, key, data, close, help_key=None, depends=None):
    return f'''        <setting id="{setting_id}" type="action" label="{S(key)}"{_help(help_key)}>
          <level>0</level>
          <data>{data}</data>{_depends(depends)}
          <constraints>
            <allowempty>true</allowempty>
          </constraints>
          <control type="button" format="action">
            <close>{'true' if close else 'false'}</close>
          </control>
        </setting>'''


def file_picker(setting_id, key, depends=None):
    return f'''        <setting id="{setting_id}" type="path" label="{S(key)}">
          <level>2</level>
          <default/>
          <constraints>
            <allowempty>true</allowempty>
            <writable>false</writable>
          </constraints>{_depends(depends)}
          <control type="button" format="file">
            <heading>{S(key)}</heading>
          </control>
        </setting>'''


def category(category_id, key, groups):
    body = []
    for group_id, label, settings in groups:
        label_attr = f' label="{S(label)}"' if label else ''
        body.append(f'      <group id="{group_id}"{label_attr}>\n' + '\n'.join(settings) + '\n      </group>')
    return f'    <category id="{category_id}" label="{S(key)}">\n' + '\n'.join(body) + '\n    </category>'


def build():
    categories = [
        category('server', 'set_cat_server', [
            ('1', 'set_group_connection', [
                action('connect', 'set_connect', f'RunPlugin(plugin://{ID}/?action=setup)', True, 'set_connect_help'),
                edit('server_url', 'set_server_url'),
                edit('local_url', 'set_local_url', help_key='set_local_url_help'),
                edit('username', 'set_username'),
                # Written by the setup wizard: salt + md5(password + salt)
                edit('auth_salt', 'set_username', level=4, visible=False),
                edit('auth_token', 'set_username', level=4, visible=False),
            ]),
            ('2', 'set_group_security', [
                toggle('verify_tls', 'set_verify_tls', True, 'set_verify_tls_help'),
                file_picker('ca_file', 'set_ca_file', depends='verify_tls'),
            ]),
        ]),
        category('playback', 'set_cat_playback', [
            ('1', None, [options('transcode', 'set_transcode', QUALITIES, 'set_transcode_help')]),
        ]),
        category('scrobbling', 'set_cat_scrobble', [
            ('1', None, [
                toggle('scrobble', 'set_scrobble'),
                toggle('now_playing', 'set_now_playing', depends='scrobble'),
                spinner('scrobble_percent', 'set_scrobble_percent', 50, 10, 5, 90, depends='scrobble'),
            ]),
        ]),
        category('offline', 'set_cat_offline', [
            ('1', None, [
                toggle('offline_enabled', 'set_offline_enabled'),
                spinner('offline_size', 'set_offline_size', 4000, 500, 500, 100000, depends='offline_enabled'),
                action('offline_clear', 'set_offline_clear', f'RunPlugin(plugin://{ID}/?action=clear_offline)', False),
            ]),
        ]),
        category('advanced', 'set_cat_advanced', [
            ('1', None, [
                spinner('timeout', 'set_timeout', 15, 5, 5, 60, level=2),
                toggle('debug', 'set_debug', False, level=2),
            ]),
        ]),
    ]
    return ('<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n'
            '<!-- SPDX-License-Identifier: GPL-3.0-or-later. Generated by tools/make_settings.py -->\n'
            '<settings version="1">\n'
            f'  <section id="{ID}">\n' + '\n'.join(categories) + '\n  </section>\n</settings>\n')


def main():
    with open(TARGET, 'w', encoding='utf-8') as handle:
        handle.write(build())
    print('settings written to', TARGET)


if __name__ == '__main__':
    main()
