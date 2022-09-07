
import json
# import yaml
import copy
from collections import abc

# https://github.com/astro44/py2hcl/blob/main/py2hcl.py
# import hcl
# Author: rcolvin
# use at own risk.

class py2hcl:

    def __init__(self):
        pass

    # def loads(self, value):
    #     return hcl.loads(value)

    def prev_brace(self, keyString, braces, walk=""):
        for parentKeyString, key, value, parentObj in self.nested_dict_iter(braces):
            if key == keyString:
                return parentObj, key
        return None, None

    def dumps(self, nested):
        nn = copy.deepcopy(nested)
        txt = ""
        prevKey = ""
        spaces = "    "
        braces = []

        brace_contexts = {}
        for parentKeyString, key, value, parentObj in self.nested_dict_iter(nn):
            ppKey = parentKeyString
            mkey = key
            mspc = ""
            braceEND = ""
            isArray = False
            isBrace = ""

            penKey = parentKeyString.rsplit(",", 1)[0]
            pre_insideObj, pre_walked = self.prev_brace(penKey, brace_contexts)
            if pre_insideObj:
                if pre_insideObj[penKey]['__type'] == 'array':
                    isArray = True

            pre_Key = prevKey.rsplit(",", 1)[0]
            p_insideObj, p_walked = self.prev_brace(pre_Key, brace_contexts)

            if (parentKeyString.rsplit(",", 1)[0] not in prevKey.rsplit(",", 1)[0]) and (prevKey.rsplit(",", 1)[0] not in parentKeyString.rsplit(",", 1)[0]):
                print(f"*  ")
            else:
                if p_insideObj and p_walked not in parentKeyString:
                    isBrace = p_insideObj[pre_Key]['__type']

            if "," in ppKey:
                appKey = ppKey.split(",")
                mspc = "".join([spaces for spc in appKey])
                ppKey = appKey[0]

            # simpleObj = False
            # if isinstance(parentObj, abc.Mapping) and (isinstance(value, (int, float)) or isinstance(value, (str))):
            #     simpleObj = True

            insideObj, walked = self.prev_brace(parentKeyString, brace_contexts)

            if isBrace:
                if txt.strip()[-1] == ',':  # CLEANUP EXTRA COMMAS befor Brace
                    txt = txt[:-1]
                btype = "}" if isBrace in 'dict' else "]"
                if isBrace in ('dict', 'array'):
                    txt = txt + f"\n{mspc}" + f" {btype}"
                if isArray:
                    txt = txt + "},"
                p_insideObj[pre_Key]['__complete'] = True
                bb, brace = self.brace_nearest(pre_Key, braces)
                braces.remove(brace)

            if isArray:
                mkey = "{" + key
                braceEND = "},"
            if ppKey in prevKey:
                txt = txt + f"\n{mspc}{mkey} = "
            else:
                if txt:
                    txt = txt + f"\n{mspc}{mkey}="
                else:
                    txt = txt + f"{mspc}{mkey}="
            if isinstance(value, list):
                if not self.list_isSimple(value):
                    txt = txt + "["
                    braces.append({"name": parentKeyString, "type": "array"})
                    if not insideObj:
                        brace_contexts.update({parentKeyString: {"__type": "array", "__complete": False}})
                    else:
                        brace_contexts[walked].update({parentKeyString: {"__type": "array", "__complete": False}})

            elif isinstance(value, abc.Mapping):
                txt = txt + "{"
                braces.append({"name": parentKeyString, "type": "dict"})
                if not insideObj:
                    brace_contexts.update({parentKeyString: {"__type": "dict", "__complete": False}})
                elif walked != parentKeyString:
                    brace_contexts[walked].update({parentKeyString: {"__type": "dict", "__complete": False}})

            txt_value = self.resolve_valueInType(value)
            if txt_value:
                txt = txt + txt_value + f' {braceEND}'
            elif value is None:
                txt = txt + '"NULL"' + f' {braceEND}'

            prevKey = parentKeyString

        if braces:
            txt = txt + "\n"
            braces.reverse()
        for brace in braces:
            if brace['type'] == "array":
                txt = txt + "]"
            elif brace['type'] == "dict":
                txt = txt + "}"
        return txt

    # this guarntees tree is read from the TOP -->DOWN

    def nested_dict_iter(self, nested, parentKey=None):
        pObj = nested
        for key, value in nested.items():
            ppkey = "%s,%s" % (parentKey, key)
            if parentKey is None:
                ppkey = key
            # print("    iter.... now---> %s" % (key))
            yield ppkey, key, value, pObj
            if value:
                if isinstance(value, abc.Mapping):
                    yield from self.nested_dict_iter(value, ppkey)
                if isinstance(value, list):
                    # print(value)
                    if isinstance(value[0], abc.Mapping):
                        for vv in value:
                            yield from self.nested_dict_iter(vv, ppkey)

    def brace_nearest(self, key, braces):
        for brace in braces:
            if key in brace['name']:
                return brace['type'], brace
        return None, None

    def resolve_valueInType(self, value):
        txt = ""
        if isinstance(value, str):
            begin = end = ""
            if '\n' in value or '"' in value:
                begin = "<<EOF\n"
                end = "\nEOF"
                txt = txt + f'{begin}{value}{end}'
            else:
                txt = txt + f'"{value}"'
        elif isinstance(value, bool):
            vbool = 'true' if value else 'false'
            txt = txt + f'{vbool}'
        elif isinstance(value, (int, float)):
            txt = txt + f'{value}'
        elif isinstance(value, list):
            isSimple = True
            items = []
            for iv in value:
                if not isinstance(iv, (str, bool, int, float)):
                    isSimple = False
                    break
                items.append(self.resolve_valueInType(iv))
            if isSimple:
                txt = "[" + ",".join(items) + "]"

        return txt

    def list_isSimple(self, value):
        isSimple = True
        for iv in value:
            if not isinstance(iv, (str, bool, int, float)):
                isSimple = False
                break
        return isSimple

if __name__ == '__main__':
    pcl = py2hcl()
    # fullTest = False
    fullTest = True
    dd = {'sb_permissions': {'dynamodbs': [{'arn': 'dddddddd', 'streamspec': {'StreamEnabled': True, 'StreamViewType': 'NEW_AND_OLD_IMAGES'}, 'write_capacity': 1}], 'eid': '///Ro9'}}
    dy = pcl.dumps(dd)

    # print(dy)

    #END
