import os
import json
import jsonpath


class ConfigBrick:
    project_root_dir = 'PROJDIR'
    def __init__(self, file_name:str, enabled:bool=True):
        # fix file name format
        self.file_name = self.fix_file_name(file_name)
        self.enabled = enabled
        self.data = {}
        file_path = os.path.join(self.project_root_dir, 'configuration', self.file_name)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as fp:
                    self.data = json.load(fp)
            except Exception as ex:
                print(f'failed to load config file:{ex}')

    @classmethod
    def fix_file_name(cls, file_name):
        if '.' not in file_name and not file_name.endswith('.json'):
            file_name += '.json'
        return file_name

    def get_file_name(self):
        return self.file_name

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def get(self, key_path):
        if self.enabled:
            result = jsonpath.jsonpath(self.data, key_path)
            if result:
                return result[0]
            else:
                return None
        else:
            return None

class ConfigPile:
    def __init__(self, file_name_pile):
        """
        :param file_name_pile: is a two-dimension array
        """
        self.file_pile = file_name_pile
        # load data to convert file name into config_brick object
        self.load_pile()

    def set_file_pile(self, file_pile):
        self.file_pile = file_pile

    def load_pile(self, new_file_name_pile = None):
        if new_file_name_pile:
            self.file_pile = new_file_name_pile

        self.pile = []
        #     file_loading_sequance = []
        for file_name_def in self.file_pile:
            if isinstance(file_name_def, list):
                # it is a config file list
                self.pile.extend([ConfigBrick(file_name) for file_name in file_name_def])
            else:
                # it is a config file
                self.pile.append(ConfigBrick(file_name_def))

    def _disable_or_enable(self, file_name, action=False):
        """
        :param file_name: brick to find by file name
        :param action: True/False, means to enable or disable the brick
        """
        file_name = ConfigBrick.fix_file_name(file_name)
        for brick_row in reversed(self.pile):
            if isinstance(brick_row, list):
                for brick in brick_row:
                    if brick.get_file_name() == file_name:
                        if action:
                            brick.enable()
                        else:
                            brick.disable()
            else:
                if brick_row.get_file_name() == file_name:
                    if action:
                        brick_row.enable()
                    else:
                        brick_row.disable()

    def disable(self, file_name):
        self._disable_or_enable(file_name, False)

    def enable(self, file_name):
        self._disable_or_enable(file_name, True)

    def get(self, key_path):
        ## search order within different levels of the pile, from top to down
        ## search order within the same level, from left to right (first appear first)
        for brick_row in reversed(self.pile):
            if isinstance(brick_row, list):
                for brick in brick_row:
                    result = brick.get(key_path)
                    if result is not None:
                        return result
            else:
                result = brick_row.get(key_path)
                if result is not None:
                    return result
        return None

if __name__ == '__main__':
    # brick = config_brick('config_file1.json')
    # value = brick.get('attr')
    # print(value)
    #
    # value = brick.get('attr.jsonpath')
    # print(value)
    #
    # brick.disable()
    # value = brick.get('attr.jsonpath')
    # print(repr(value))
    #
    # brick.enable()
    # value = brick.get('attr.jsonpath')
    # print(repr(value))

    config = ConfigPile(['config_file1', 'config_file2.json'])
    value = config.get('implicit_timeout')
    print(value)
    value = config.get('attr.jsonpath')
    print(repr(value))
    config.disable('config_file1')
    value = config.get('attr.jsonpath')
    print(repr(value))
    config.enable('config_file1')
    value = config.get('attr.jsonpath')
    print(repr(value))

#
#
#
# def load_config_stack(config_file_sequence: list):
#     """
#     load configuration by file name stacked, files are searched within folder configuration and in json format
#     :param config_file_sequence:
#     :return: loaded config in dict format
#     """
#
#     config_root_dir = 'configuration'
#
#     config = {}
#     file_loading_sequance = []
#     for file_name_def in config_file_sequence:
#         if isinstance(file_name_def, list):
#             file_loading_sequance.extend(file_name_def)
#         else:
#             # it is a config file already
#             file_loading_sequance.append(file_name_def)
#
#     for file_name in file_loading_sequance:
#         if '.' not in file_name and not file_name.endswith('.json'):
#             file_name += '.json'
#         # load json file in order
#         with open(os.path.join(config_root_dir, file_name), 'r') as fp:
#             conf_info = json.load(fp)
#             config.update(conf_info)
#
#     return config

