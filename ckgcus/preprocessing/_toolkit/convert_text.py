# from copy import deepcopy
#
# (START, END, FAIL, WAIT_TAIL) = list(range(4))
# (TAIL, ERROR, MATCHED_SWITCH, UNMATCHED_SWITCH, CONNECTOR) = list(range(5))
#
# MAPS = {}
#
#
# class Node:
#     def __init__(self, from_word, to_word=None, is_tail=True, have_child=False):
#         self.from_word = from_word
#         self.to_word = to_word if to_word else from_word
#         self.is_tail = is_tail
#         self.have_child = have_child
#
#     def is_original_long_word(self):
#         return self.is_tail and len(self.from_word) > 1
#
#     def is_follow(self, chars):
#         return chars != self.from_word[:-1]
#
#     def __str__(self):
#         return f'<Node, {repr(self.from_word)}, {repr(self.to_word)}, {self.is_tail}, {self.have_child}>'
#
#     __repr__ = __str__
#
#
# class ConvertMap:
#     def __init__(self, name, mapping=None):
#         self.name = name
#         self._map = {}
#         if mapping:
#             self.set_convert_map(mapping)
#
#     def set_convert_map(self, mapping):
#         convert_map = {}
#         have_child = {}
#         max_key_length = 0
#         for key in sorted(mapping.keys()):
#             if len(key) > 1:
#                 for i in range(1, len(key)):
#                     parent_key = key[:i]
#                     have_child[parent_key] = True
#             have_child[key] = False
#             max_key_length = max(max_key_length, len(key))
#         for key in sorted(have_child.keys()):
#             convert_map[key] = (key in mapping, have_child[key], mapping.get(key, ''))
#         self._map = convert_map
#         self.max_key_length = max_key_length
#
#     def __getitem__(self, k):
#         try:
#             is_tail, have_child, to_word = self._map[k]
#             return Node(k, to_word, is_tail, have_child)
#         except KeyError:
#             return Node(k)
#
#     def __contains__(self, k):
#         return k in self._map
#
#     def __len__(self):
#         return len(self._map)
#
#
# class StatesMachineException(Exception):
#     pass
#
#
# class StatesMachine:
#     def __init__(self):
#         self.state = START
#         self.final = ''
#         self.len = 0
#         self.pool = ''
#
#     def clone(self, pool):
#         new = deepcopy(self)
#         new.state = WAIT_TAIL
#         new.pool = pool
#         return new
#
#     def feed(self, char, map):
#         node = map[self.pool + char]
#
#         if node.have_child:
#             if node.is_tail:
#                 if node.is_original_long_word():
#                     cond = UNMATCHED_SWITCH
#                 else:
#                     cond = MATCHED_SWITCH
#             else:
#                 cond = CONNECTOR
#         else:
#             if node.is_tail:
#                 cond = TAIL
#             else:
#                 cond = ERROR
#
#         new = None
#         if cond == ERROR:
#             self.state = FAIL
#         elif cond == TAIL:
#             if self.state == WAIT_TAIL and node.is_original_long_word():
#                 self.state = FAIL
#             else:
#                 self.final += node.to_word
#                 self.len += 1
#                 self.pool = ''
#                 self.state = END
#         elif self.state in [START, WAIT_TAIL]:
#             if cond == MATCHED_SWITCH:
#                 new = self.clone(node.from_word)
#                 self.final += node.to_word
#                 self.len += 1
#                 self.state = END
#                 self.pool = ''
#             elif cond in [UNMATCHED_SWITCH, CONNECTOR]:
#                 if self.state == START:
#                     new = self.clone(node.from_word)
#                     self.final += node.to_word
#                     self.len += 1
#                     self.state = END
#                 else:
#                     if node.is_follow(self.pool):
#                         self.state = FAIL
#                     else:
#                         self.pool = node.from_word
#         elif self.state == END:
#             self.state = START
#             new = self.feed(char, map)
#         elif self.state == FAIL:
#             raise StatesMachineException(f'Translate States Machine have error with input data {node}')
#         return new
#
#     def __len__(self):
#         return self.len + 1
#
#     def __str__(self):
#         return f'<StatesMachine {id(self)}, pool: "{self.pool}", state: {self.state}, final: {self.final}>'
#
#     __repr__ = __str__
#
#
# class TextConverter:
#     def __init__(self, conversion_type='zh-hans'):
#         self.conversion_type = conversion_type
#         if conversion_type not in MAPS:
#             raise ValueError(f"Unsupported conversion type: {conversion_type}")
#         self.map = MAPS[conversion_type]
#         self.start()
#
#     def start(self):
#         self.machines = [StatesMachine()]
#         self.final = ''
#
#     def feed(self, char):
#         branches = []
#         for fsm in self.machines:
#             new = fsm.feed(char, self.map)
#             if new:
#                 branches.append(new)
#         if branches:
#             self.machines.extend(branches)
#         self.machines = [fsm for fsm in self.machines if fsm.state != FAIL]
#         all_ok = True
#         for fsm in self.machines:
#             if fsm.state != END:
#                 all_ok = False
#         if all_ok:
#             self._clean()
#         return self.get_result()
#
#     def _clean(self):
#         if len(self.machines):
#             self.machines.sort(key=lambda x: len(x))
#             self.final += self.machines[0].final
#         self.machines = [StatesMachine()]
#
#     def convert(self, text):
#         self.start()
#         for char in text:
#             self.feed(char)
#         self.end()
#         return self.get_result()
#
#     def get_result(self):
#         return self.final
#
#     def end(self):
#         self.machines = [fsm for fsm in self.machines if fsm.state in [FAIL, END]]
#         self._clean()
#
#     @staticmethod
#     def traditional_to_simplified(text):
#         return TextConverter('zh-hans').convert(text)
#
#     @staticmethod
#     def simplified_to_traditional(text):
#         return TextConverter('zh-hant').convert(text)
#
#
# def registery(name, mapping):
#     global MAPS
#     MAPS[name] = ConvertMap(name, mapping)
#
#
# registery('zh-hant', zh2Hant)
# registery('zh-hans', zh2Hans)
