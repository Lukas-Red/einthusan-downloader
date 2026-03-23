import requests
import re
import json
import base64
from html import unescape

_request_timeout = 10
_csrf_token_pattern = 'data-pageid="'

_arc_version = 12
_app_version = 353
_x_json = '{"EJOutcomes":"WyJodHRwczVovL2NkbjEuZWludGh1c2FuLmlvL3BpbmcubTR2IiwiaHR0cHM6Ly9jZG4yLmVpbnRodXNhbi5pby9waW5nLm00diIsImh0dHBzOi8vY2RuMy5laW50aHVzYW4uaW8vcGluZy5tNHYiXQ==o","NativeHLS":false}'
_x_event = 'UIVideoPlayer.PingOutcome'

_einthusan_cdn_prefixes = [
    'https://cdn1.einthusan.io/etv/content/',
    'https://cdn2.einthusan.io/etv/content/',
    'https://cdn3.einthusan.io/etv/content/'
]


_movie_url_format_helper = 'https://einthusan.tv/movie/watch/<<movieId>>/?lang=<<language>>'

class EinthusianClient():
    def __init__(self, movie_url, user_agent):
        self._movie_url = movie_url
        domain_search = re.search(r'^(.+?\.\w+)', movie_url)
        id_search = re.search(r'/watch/(\S+)/', movie_url)
        if not id_search or not domain_search:
            raise SyntaxError(f'Invalid movie URL {movie_url}: expected format is {_movie_url_format_helper}')
        self._movie_id = id_search.group(1)
        self._movie_domain = domain_search.group(1)
        
        self._session = requests.Session()
        self._session.headers.update(
            {'User-Agent': user_agent}
        )
        self._movie_html = self._get_movie_page_html()
    

    def get_movie_playlist(self) -> str:
        csrf_token = self._get_csrf_token()
        raw_m3u8_data = self._get_m3u8_data(csrf_token=csrf_token)
        return self._set_and_test_m3u8_prefix(raw_m3u8_data)
    
    

    @staticmethod
    def _ejlinks_decrypt_to_dict(b64_str):
        b64_str = b64_str[:10] + b64_str[-1] + b64_str[12:-1]
        return json.loads(base64.b64decode(b64_str + '==').decode())
    

    def _get_movie_page_html(self):
        print(f'Attempting to movie main page...\nGET {self._movie_url}')
        resp = self._session.get(self._movie_url, timeout=_request_timeout)
        resp.raise_for_status()
        print('Success')
        return resp.text

    # gets the movie name from the <title> element.
    # If a set of parenthesis is found (usually the movie year) it stops there instead
    def get_movie_name(self):
        title_tag = '<title>'
        start = self._movie_html.find(title_tag) + len(title_tag)
        end = min(self._movie_html.find(')') + 1, self._movie_html.find('</title>'))
        return self._movie_html[start:end]


    def _get_csrf_token(self):
        start = self._movie_html.find(_csrf_token_pattern) + len(_csrf_token_pattern)
        end = self._movie_html.find('"', start)
        return unescape(self._movie_html[start:end])

    
    def _get_m3u8_data(self, csrf_token):
        ajax_movie_url = self._movie_url.replace(self._movie_domain, self._movie_domain + '/ajax')
        payload = {
            'xEvent': _x_event,
            'xJson': _x_json,
            'arcVersion': _arc_version,
            'appVersion': _app_version,
            'gorilla.csrf.Token': csrf_token
        }
        self._session.headers.update({
            'Origin': self._movie_domain,
            'Referer': self._movie_url
        })
        print(f'Attempting to fetch the m3u8 playlist link...\nPOST {ajax_movie_url}')
        resp = self._session.post(ajax_movie_url, data=payload, timeout=_request_timeout)
        resp.raise_for_status()
        print('Success')

        ej_data = self._ejlinks_decrypt_to_dict(resp.json()['Data']['EJLinks'])
        self._session.headers.update({
            'Referer': self._movie_domain
        })
        playlist_link = ej_data['HLSLink']
        print(f'Attempting to Download the m3u8 playlist...\nGET {playlist_link}')
        resp = self._session.get(playlist_link, timeout=_request_timeout)
        resp.raise_for_status()
        print('Success')
        return resp.text


    def _set_and_test_m3u8_prefix(self, m3u8_data):
        
        lines = m3u8_data.splitlines()
        segment_lines = [l for l in lines if l and not l.startswith('#')]

        if not segment_lines:
            raise ValueError('No segments found in m3u8 playlist')

        cdn_prefix = next(
            (p for p in _einthusan_cdn_prefixes
            if requests.get(p + segment_lines[0], timeout=_request_timeout).status_code < 400),
            None
        )
        if not cdn_prefix:
            raise requests.HTTPError(f'No reachable CDN among {", ".join(_einthusan_cdn_prefixes)}')
        
        return '\n'.join(
            cdn_prefix + line if line and not line.startswith('#') else line
            for line in lines
        )
    
