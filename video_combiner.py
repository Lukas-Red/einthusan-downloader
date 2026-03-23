import json
import subprocess


class VideoCombiner():
    def __init__(self, config_dict_path, combine_method=None):
        self._config = json.load(open(config_dict_path, 'r'))
        if combine_method:
            if not self._check_method(combine_method):
                raise ValueError(f'Error using specified method {combine_method}')
        else:
            print('No priority method set. Testing all methods...')
            combine_method = next(
                (k for k in self._config.keys()
                if self._check_method(k)),
                None
            )
            if not combine_method:
                raise RuntimeError('None of the video combining tools were found. Install at least one of them.')
        self._method = combine_method


    def _check_method(self, method_key):
        try:
            print(f'Testing video combiner {method_key}...')
            result = subprocess.run(
                self._config[method_key]['version_check'],
                capture_output=True
            )
            print(result.stdout.splitlines()[0].decode('utf-8'))
            return result.returncode == 0
        except FileNotFoundError:
            return False
    

    def combine_video_from_m3u8_file(self, m3u8_path, output_file):
        config_mapper = {
            'm3u8_path': m3u8_path,
            'output_file': output_file
        }
        run_args = [s.format_map(config_mapper) for s in self._config[self._method]['run']]
        print(f'Starting the subprocess {self._method} with destination {output_file}...')
        subprocess.run(run_args)
        print('\nSubprocess complete')