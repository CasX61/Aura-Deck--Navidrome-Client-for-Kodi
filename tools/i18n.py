#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 CasX61
"""
Single source for every user-visible string.

Writes the Kodi language files and resources/lib/strings.py (key -> id).
Ids are assigned in table order starting at 32000, so only ever append new
strings at the end, or existing translations get shifted.

    python3 tools/i18n.py
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDON = os.path.join(ROOT, 'script.auradeck')
FIRST_ID = 32000

# (key, English, German)
TABLE = [
    # Navigation
    ('nav_home', 'Home', 'Startseite'),
    ('nav_search', 'Search', 'Suche'),
    ('nav_artists', 'Artists', 'Künstler'),
    ('nav_albums', 'Albums', 'Alben'),
    ('nav_playlists', 'Playlists', 'Playlists'),
    ('nav_favourites', 'Favourites', 'Favoriten'),
    ('nav_genres', 'Genres', 'Genres'),
    ('nav_radio', 'Radio', 'Radio'),
    ('nav_offline', 'Offline', 'Offline'),
    ('nav_settings', 'Settings', 'Einstellungen'),

    # Home
    ('greeting_morning', 'Good morning', 'Guten Morgen'),
    ('greeting_day', 'Good afternoon', 'Guten Tag'),
    ('greeting_evening', 'Good evening', 'Guten Abend'),
    ('home_subtitle', 'What would you like to hear today?', 'Was möchtest du heute hören?'),
    ('home_recent', 'Recently played', 'Zuletzt gespielt'),
    ('home_newest', 'Recently added', 'Neu hinzugefügt'),
    ('home_starred', 'Favourite albums', 'Lieblingsalben'),
    ('home_discover', 'Discover', 'Entdecken'),
    ('home_frequent', 'Most played', 'Meistgespielt'),
    ('home_highest', 'Top rated', 'Bestbewertet'),
    ('home_playlists', 'Your playlists', 'Deine Playlists'),
    ('home_empty', 'Your library is empty.', 'Deine Bibliothek ist leer.'),

    # Buttons
    ('btn_random_mix', 'Random mix', 'Zufallsmix'),
    ('btn_fav_mix', 'Favourites mix', 'Favoriten-Mix'),
    ('btn_play', 'Play', 'Abspielen'),
    ('btn_shuffle', 'Shuffle', 'Zufällig'),
    ('btn_queue', 'Queue', 'Einreihen'),
    ('btn_download', 'Download', 'Herunterladen'),
    ('btn_more', 'More', 'Mehr'),
    ('btn_favourite', 'Favourite', 'Favorit'),
    ('btn_unfavourite', 'Favourited', 'Favorisiert'),
    ('btn_top_songs', 'Top songs', 'Top-Titel'),
    ('btn_artist_mix', 'Artist mix', 'Künstler-Mix'),
    ('btn_genre_mix', 'Genre mix', 'Genre-Mix'),
    ('btn_play_favs', 'Play all', 'Alle abspielen'),
    ('btn_go_artist', 'Go to artist', 'Zum Künstler'),
    ('btn_retry', 'Try again', 'Erneut versuchen'),
    ('btn_setup', 'Connect server', 'Server verbinden'),
    ('btn_clear_offline', 'Delete all', 'Alle löschen'),
    ('show_all', 'Show all', 'Alle anzeigen'),
    ('disc', 'Disc {0}', 'CD {0}'),

    # Search
    ('search_heading', 'Search artists, albums and songs', 'Künstler, Alben und Titel suchen'),
    ('search_placeholder', 'Artists, albums, songs …', 'Künstler, Alben, Titel …'),
    ('search_songs', 'Songs', 'Titel'),
    ('search_artists', 'Artists', 'Künstler'),
    ('search_albums', 'Albums', 'Alben'),
    ('search_browse', 'Browse genres', 'Genres entdecken'),
    ('search_nothing', 'Nothing found for "{0}".', 'Nichts gefunden für „{0}“.'),
    ('search_songs_for', 'Songs: {0}', 'Titel: {0}'),

    # Artist
    ('artist_top', 'Popular', 'Beliebt'),
    ('artist_albums', 'Albums', 'Alben'),
    ('artist_singles', 'Singles & EPs', 'Singles & EPs'),
    ('artist_compilations', 'Compilations', 'Kompilationen'),
    ('artist_similar', 'Similar artists', 'Ähnliche Künstler'),

    # Favourites
    ('fav_songs', 'Favourite songs', 'Lieblingstitel'),
    ('fav_albums', 'Albums', 'Alben'),
    ('fav_artists', 'Artists', 'Künstler'),
    ('fav_empty', 'Nothing here yet. Mark songs, albums or artists as favourites.',
     'Noch nichts hier. Markiere Titel, Alben oder Künstler als Favoriten.'),
    ('fav_added', 'Added to favourites', 'Zu Favoriten hinzugefügt'),
    ('fav_removed', 'Removed from favourites', 'Aus Favoriten entfernt'),

    # Kinds
    ('kind_album', 'Album', 'Album'),
    ('kind_single', 'Single', 'Single'),
    ('kind_ep', 'EP', 'EP'),
    ('kind_compilation', 'Compilation', 'Kompilation'),
    ('kind_playlist', 'Playlist', 'Playlist'),
    ('kind_genre', 'Genre', 'Genre'),

    # Counts and durations
    ('count_song', '{0} song', '{0} Titel'),
    ('count_songs', '{0} songs', '{0} Titel'),
    ('count_album', '{0} album', '{0} Album'),
    ('count_albums', '{0} albums', '{0} Alben'),
    ('count_artist', '{0} artist', '{0} Künstler'),
    ('count_artists', '{0} artists', '{0} Künstler'),
    ('count_genre', '{0} genre', '{0} Genre'),
    ('count_genres', '{0} genres', '{0} Genres'),
    ('count_playlist', '{0} playlist', '{0} Playlist'),
    ('count_playlists', '{0} playlists', '{0} Playlists'),
    ('count_station', '{0} station', '{0} Sender'),
    ('count_stations', '{0} stations', '{0} Sender'),
    ('fmt_hours_minutes', '{0} hr {1} min', '{0} Std. {1} Min.'),
    ('fmt_minutes', '{0} min', '{0} Min.'),

    # Sorting
    ('sort_title', 'Sort by', 'Sortieren nach'),
    ('sorted_by', 'Sorted by: {0}', 'Sortiert nach: {0}'),
    ('sort_name', 'Name', 'Name'),
    ('sort_artist', 'Artist', 'Künstler'),
    ('sort_newest', 'Recently added', 'Neu hinzugefügt'),
    ('sort_year', 'Release year', 'Erscheinungsjahr'),
    ('sort_recent', 'Recently played', 'Zuletzt gespielt'),
    ('sort_frequent', 'Most played', 'Meistgespielt'),
    ('sort_rating', 'Rating', 'Bewertung'),
    ('sort_random', 'Random', 'Zufällig'),
    ('sort_album_count', 'Number of albums', 'Anzahl Alben'),
    ('sort_song_count', 'Number of songs', 'Anzahl Titel'),

    # Ratings
    ('rating_title', 'Rate: {0}', 'Bewerten: {0}'),
    ('rating_none', 'No rating', 'Keine Bewertung'),
    ('rating_stars_one', '1 star', '1 Stern'),
    ('rating_stars', '{0} stars', '{0} Sterne'),
    ('rating_short', 'Rated {0}/5', 'Bewertet mit {0}/5'),
    ('play_count', 'Played {0}×', '{0}× gespielt'),

    # Playlists
    ('playlist_new', 'New playlist', 'Neue Playlist'),
    ('playlist_name', 'Playlist name', 'Name der Playlist'),
    ('playlist_add_title', 'Add to playlist', 'Zur Playlist hinzufügen'),
    ('playlist_added', '{0} song(s) added to "{1}"', '{0} Titel zu „{1}“ hinzugefügt'),
    ('playlist_delete_confirm', 'Delete the playlist "{0}"?', 'Playlist „{0}“ wirklich löschen?'),
    ('playlist_empty', 'This playlist is empty.', 'Diese Playlist ist leer.'),
    ('playlist_owner', 'by {0}', 'von {0}'),

    # Empty states
    ('radio_empty', "No radio stations yet. Add them in Navidrome's web interface.",
     'Noch keine Radiosender. Du kannst sie in der Navidrome-Weboberfläche anlegen.'),
    ('empty_generic', 'Nothing here.', 'Hier ist nichts.'),

    # Offline
    ('offline_empty', 'No downloads yet. Use "Download" on an album, a playlist or a song.',
     'Noch keine Downloads. Nutze „Herunterladen“ bei einem Album, einer Playlist oder einem Titel.'),
    ('offline_already', 'Already available offline', 'Bereits offline verfügbar'),
    ('offline_busy', 'A download is already running', 'Es läuft bereits ein Download'),
    ('offline_downloading', 'Downloading {0}', 'Lade {0} herunter'),
    ('offline_done', 'Downloaded {0} of {1} songs', '{0} von {1} Titeln heruntergeladen'),
    ('offline_removed', 'Download removed', 'Download entfernt'),
    ('offline_clear_confirm', 'Delete all downloads ({0:.0f} MB)?', 'Alle Downloads löschen ({0:.0f} MB)?'),
    ('offline_cleared', 'All downloads deleted', 'Alle Downloads gelöscht'),

    # Context menus
    ('ctx_play', 'Play', 'Abspielen'),
    ('ctx_shuffle', 'Shuffle', 'Zufallswiedergabe'),
    ('ctx_play_next', 'Play next', 'Als Nächstes abspielen'),
    ('ctx_queue', 'Add to queue', 'Zur Warteschlange hinzufügen'),
    ('ctx_song_mix', 'Start song mix', 'Song-Mix starten'),
    ('ctx_artist_mix', 'Artist mix', 'Künstler-Mix'),
    ('ctx_genre_mix', 'Play genre mix', 'Genre-Mix abspielen'),
    ('ctx_add_playlist', 'Add to playlist …', 'Zur Playlist hinzufügen …'),
    ('ctx_favourite', 'Add to favourites', 'Zu Favoriten hinzufügen'),
    ('ctx_unfavourite', 'Remove from favourites', 'Aus Favoriten entfernen'),
    ('ctx_rate', 'Rate …', 'Bewerten …'),
    ('ctx_download', 'Download', 'Herunterladen'),
    ('ctx_remove_download', 'Remove download', 'Download entfernen'),
    ('ctx_go_album', 'Go to album', 'Zum Album'),
    ('ctx_go_artist', 'Go to artist', 'Zum Künstler'),
    ('ctx_remove_from_playlist', 'Remove from playlist', 'Aus Playlist entfernen'),
    ('ctx_rename', 'Rename', 'Umbenennen'),
    ('ctx_delete', 'Delete', 'Löschen'),
    ('ctx_open_in_app', 'Open in Aura-Deck', 'In Aura-Deck öffnen'),

    # Playback
    ('queued_next', '{0} song(s) will play next', '{0} Titel als Nächstes eingereiht'),
    ('queued_end', '{0} song(s) added to the queue', '{0} Titel zur Warteschlange hinzugefügt'),
    ('nothing_to_play', 'Nothing to play', 'Nichts zum Abspielen'),
    ('np_nothing', 'Nothing is playing', 'Gerade läuft nichts'),
    ('np_queue_info', 'Track {0} of {1}', 'Titel {0} von {1}'),
    ('np_title', 'Now playing', 'Läuft gerade'),
    ('np_lyrics', 'Lyrics', 'Songtext'),
    ('np_queue', 'Queue', 'Warteschlange'),
    ('np_no_lyrics', 'No lyrics for this song', 'Kein Songtext für diesen Titel'),
    ('np_loading', 'Loading …', 'Lade …'),

    # Errors
    ('err_title', "Can't reach your server", 'Server nicht erreichbar'),
    ('err_auth', 'Wrong username or password.', 'Benutzername oder Passwort ist falsch.'),
    ('err_token_unsupported', "This server doesn't support token login (for example with LDAP).",
     'Dieser Server unterstützt keine Token-Anmeldung (zum Beispiel bei LDAP).'),
    ('err_tls', "The server's TLS certificate isn't trusted. Check the TLS settings.",
     'Das TLS-Zertifikat des Servers ist nicht vertrauenswürdig. Prüfe die TLS-Einstellungen.'),
    ('err_network', 'Connection failed: {0}', 'Verbindung fehlgeschlagen: {0}'),
    ('err_server', 'Server error: {0}', 'Serverfehler: {0}'),
    ('err_unexpected', 'Something went wrong. Details are in the Kodi log.',
     'Etwas ist schiefgelaufen. Details stehen im Kodi-Log.'),
    ('err_not_configured', 'No server connected yet.', 'Noch kein Server verbunden.'),

    # Setup wizard
    ('wizard_title', 'Connect Navidrome', 'Navidrome verbinden'),
    ('wizard_url', 'Server address (e.g. https://music.example.com)',
     'Serveradresse (z. B. https://musik.example.com)'),
    ('wizard_user', 'Username', 'Benutzername'),
    ('wizard_password', 'Password', 'Passwort'),
    ('wizard_testing', 'Connecting to {0} …', 'Verbinde mit {0} …'),
    ('wizard_tls_question',
     "The server's certificate couldn't be verified (self-signed?). Connect anyway, without verification?",
     'Das Zertifikat des Servers konnte nicht geprüft werden (selbst signiert?). Trotzdem ohne Prüfung verbinden?'),
    ('wizard_connected', 'Connected to {0} {1}', 'Verbunden mit {0} {1}'),

    # Widgets
    ('widget_random_songs', 'Random songs', 'Zufällige Titel'),

    # Settings
    ('set_cat_server', 'Server', 'Server'),
    ('set_group_connection', 'Connection', 'Verbindung'),
    ('set_connect', 'Connect to a server …', 'Mit Server verbinden …'),
    ('set_connect_help', 'Enter address, username and password. Only a login token is stored, never the password.',
     'Adresse, Benutzername und Passwort eingeben. Gespeichert wird nur ein Anmelde-Token, nie das Passwort.'),
    ('set_server_url', 'Server address', 'Serveradresse'),
    ('set_username', 'Username', 'Benutzername'),
    ('set_group_security', 'Security', 'Sicherheit'),
    ('set_verify_tls', 'Verify TLS certificate', 'TLS-Zertifikat prüfen'),
    ('set_verify_tls_help', 'Turn off only for servers with a self-signed certificate.',
     'Nur für Server mit selbst signiertem Zertifikat ausschalten.'),
    ('set_ca_file', 'Custom CA certificate (PEM)', 'Eigenes CA-Zertifikat (PEM)'),
    ('set_timeout', 'Network timeout (seconds)', 'Netzwerk-Timeout (Sekunden)'),
    ('set_cat_playback', 'Playback', 'Wiedergabe'),
    ('set_transcode', 'Streaming quality', 'Streaming-Qualität'),
    ('set_transcode_help', 'Original streams the file as stored. Lower qualities save bandwidth on slow connections.',
     'Original streamt die Datei unverändert. Geringere Qualität spart Bandbreite bei langsamen Verbindungen.'),
    ('q_original', 'Original (no transcoding)', 'Original (ohne Transcoding)'),
    ('set_cat_scrobble', 'Scrobbling', 'Scrobbling'),
    ('set_scrobble', 'Report played songs to Navidrome', 'Gespielte Titel an Navidrome melden'),
    ('set_now_playing', 'Show "now playing" in Navidrome', '„Läuft gerade“ in Navidrome anzeigen'),
    ('set_scrobble_percent', 'Count a play after (% of the song)', 'Als gespielt zählen nach (% des Titels)'),
    ('set_cat_offline', 'Offline', 'Offline'),
    ('set_offline_enabled', 'Enable downloads', 'Downloads aktivieren'),
    ('set_offline_size', 'Maximum storage (MB)', 'Maximaler Speicher (MB)'),
    ('set_offline_clear', 'Delete all downloads', 'Alle Downloads löschen'),
    ('set_cat_advanced', 'Advanced', 'Erweitert'),
    ('set_debug', 'Debug logging', 'Debug-Protokoll'),
    ('q_mp3_320', 'MP3 · 320 kbit/s', 'MP3 · 320 kbit/s'),
    ('q_mp3_192', 'MP3 · 192 kbit/s', 'MP3 · 192 kbit/s'),
    ('q_mp3_128', 'MP3 · 128 kbit/s', 'MP3 · 128 kbit/s'),
    ('q_opus_160', 'Opus · 160 kbit/s', 'Opus · 160 kbit/s'),
    ('q_opus_96', 'Opus · 96 kbit/s (mobile)', 'Opus · 96 kbit/s (mobil)'),
    ('q_aac_256', 'AAC · 256 kbit/s', 'AAC · 256 kbit/s'),
    ('sort_playlist_order', 'Playlist order', 'Playlist-Reihenfolge'),
    ('sort_recently_added', 'Recently added', 'Zuletzt hinzugefügt'),
    ('sort_title_az', 'Title', 'Titel'),
    ('sort_album', 'Album', 'Album'),
    ('sort_duration', 'Length', 'Länge'),
    ('set_local_url', 'Local address (optional)', 'Lokale Adresse (optional)'),
    ('set_local_url_help', 'e.g. http://192.168.0.10:4533 - used instead of the server address whenever it can be '
     'reached, which avoids the detour through the internet at home.',
     'z. B. http://192.168.0.10:4533 - wird statt der Serveradresse genutzt, sobald sie erreichbar ist. Das spart '
     'zu Hause den Umweg über das Internet.'),
]


def po_escape(text):
    return text.replace('\\', '\\\\').replace('"', '\\"')


def write_po(language, column):
    folder = os.path.join(ADDON, 'resources', 'language', f'resource.language.{language}')
    os.makedirs(folder, exist_ok=True)
    lines = [
        '# Aura-Deck language file',
        '# SPDX-License-Identifier: GPL-3.0-or-later',
        '# Generated by tools/i18n.py - edit the table there, not this file.',
        'msgid ""',
        'msgstr ""',
        '"Content-Type: text/plain; charset=UTF-8\\n"',
        f'"Language: {language}\\n"',
        '',
    ]
    for index, row in enumerate(TABLE):
        english = row[1]
        translated = '' if column == 1 else row[column]
        lines += [
            f'msgctxt "#{FIRST_ID + index}"',
            f'msgid "{po_escape(english)}"',
            f'msgstr "{po_escape(translated)}"',
            '',
        ]
    with open(os.path.join(folder, 'strings.po'), 'w', encoding='utf-8') as handle:
        handle.write('\n'.join(lines))


def write_python():
    target = os.path.join(ADDON, 'resources', 'lib', 'strings.py')
    with open(target, 'w', encoding='utf-8') as handle:
        handle.write('# SPDX-License-Identifier: GPL-3.0-or-later\n# Copyright (C) 2026 CasX61\n')
        handle.write('"""Generated by tools/i18n.py - string key -> Kodi string id."""\n\n')
        handle.write('STRINGS = {\n')
        for index, row in enumerate(TABLE):
            handle.write(f"    '{row[0]}': {FIRST_ID + index},\n")
        handle.write('}\n')


def string_id(key):
    for index, row in enumerate(TABLE):
        if row[0] == key:
            return FIRST_ID + index
    raise KeyError(key)


def main():
    keys = [row[0] for row in TABLE]
    duplicates = {k for k in keys if keys.count(k) > 1}
    if duplicates:
        raise SystemExit(f'duplicate keys: {sorted(duplicates)}')
    write_po('en_gb', 1)
    write_po('de_de', 2)
    write_python()
    print(f'{len(TABLE)} strings written')


if __name__ == '__main__':
    main()
