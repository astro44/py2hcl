
import json
import yaml
import copy
from collections import abc

import hcl

# dd = {"name": "joe", "info": {"age": [5, 12, 42], "gender": {"type": "male"}, "accidents": [{"name": "Thursday"}, {"height": "six 2"}, {"color": "blue", "eyes": "brown"}]}, 'status': 'ACTIVE', 'streamspec': {'StreamEnabled': True, 'StreamViewType': 'NEW_AND_OLD_IMAGES'}, 'write_capacity': 1}
dd = {'sb_permissions': {'dynamodbs': [{'arn': 'dddddddd', 'streamspec': {'StreamEnabled': True, 'StreamViewType': 'NEW_AND_OLD_IMAGES'}, 'write_capacity': 1}], 'eid': '///Ro9'}}
# dd = {"a": "b", "c":{"gg": {"name": "dan"}}}


class py2hcl:
    def __init__(self):
        pass

    def loads(self, value):
        return hcl.loads(value)

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
        insideBrace = []
        # wasInsideBrace = False
        # insideCount = 0
        prevObj = None
        # prevInsideSetKey = None

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
                    # print(" IS AAA RRR AAA YYY")

            pre_Key = prevKey.rsplit(",", 1)[0]
            p_insideObj, p_walked = self.prev_brace(pre_Key, brace_contexts)

            if (parentKeyString.rsplit(",", 1)[0] not in prevKey.rsplit(",", 1)[0]) and (prevKey.rsplit(",", 1)[0] not in parentKeyString.rsplit(",", 1)[0]):
                print(f"*  ")
            else:
                if p_insideObj and p_walked not in parentKeyString:
                    isBrace = p_insideObj[pre_Key]['__type']
                    # print(f"------>> {p_walked}  == {parentKeyString}")

            if "," in ppKey:
                appKey = ppKey.split(",")
                mspc = "".join([spaces for spc in appKey])
                ppKey = appKey[0]

            simpleObj = False
            if isinstance(parentObj, abc.Mapping) and (isinstance(value, (int, float)) or isinstance(value, (str))):
                simpleObj = True

            insideObj, walked = self.prev_brace(parentKeyString, brace_contexts)

            if isBrace:
                if txt.strip()[-1] == ',':  # CLEANUP EXTRA COMMAS befor Brace
                    txt = txt[:-1]
                btype = "}z" if isBrace in 'dict' else "]z"
                if isBrace in ('dict', 'array'):
                    txt = txt + f"\n{mspc}" + f" {btype}"
                if isArray:
                    txt = txt + "},"
                # print(f" D  U  D  E ... found  {btype}")
                p_insideObj[pre_Key]['__complete'] = True
                bb, brace = self.brace_nearest(pre_Key, braces)
                braces.remove(brace)

            if isArray:
                mkey = "q{" + key
                braceEND = "}q,"
            if ppKey in prevKey:
                txt = txt + f"\n{mspc}{mkey} = "
            else:
                if txt:
                    txt = txt + f"\n{mspc}{mkey}="
                else:
                    txt = txt + f"{mspc}{mkey}="
            if isinstance(value, list):
                if not self.list_isSimple(value):
                    # print("list")
                    txt = txt + "p["
                    # print(f"--a->{parentKeyString}  {insideObj}")
                    # print(" __            ADD A")
                    braces.append({"name": parentKeyString, "type": "array"})
                    if not insideObj:
                        brace_contexts.update({parentKeyString: {"__type": "array", "__complete": False}})
                    else:
                        brace_contexts[walked].update({parentKeyString: {"__type": "array", "__complete": False}})

            elif isinstance(value, abc.Mapping):
                # print("map")
                txt = txt + "z{"
                # print(f"--b->{parentKeyString}  {insideObj}")
                # print(" __            ADD B")
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

            # if isArray and not insideSet:
            #     txt = txt + "},"

            # print(f"--- -- - -- -- -- -- --{key}--BEGIN")
            # print(f"-------------[{parentKeyString}]----------{value}--------- ")
            # print(f"---------------------- -- -- ----END")
            prevKey = parentKeyString
            prevObj = parentObj
            # prevInsideSetKey = insidesetKEY
            # if 'global_all' in parentKeyString:
            #     print("*******()))()")
            #     print(txt_value)

        if braces:
            txt = txt + "\n"
            braces.reverse()
        for brace in braces:
            if brace['type'] == "array":
                txt = txt + "]"
            elif brace['type'] == "dict":
                txt = txt + "}"
        # print(brace_contexts)
        return txt

    # this guarntees tree is read from the TOP -->DOWN

    def nested_dict_iter(self, nested, parentKey=None):
        pObj = nested
        lastKey = None
        for key, value in nested.items():
            ppkey = "%s,%s" % (parentKey, key)
            if parentKey is None:
                ppkey = key
            # print("    iter.... now---> %s" % (key))
            yield ppkey, key, value, pObj
            if isinstance(value, abc.Mapping):
                yield from self.nested_dict_iter(value, ppkey)
            if isinstance(value, list):
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

    def cleanResult(self, value):
        dy = value
        dy = dy.replace("z{", "{")
        dy = dy.replace("p[", "[")
        dy = dy.replace("z[", "[")
        dy = dy.replace("q{", "{")
        dy = dy.replace("r{", "{")
        dy = dy.replace("}z", "}")
        dy = dy.replace("]z", "]")
        dy = dy.replace("}m", "}")
        dy = dy.replace("}q", "}")
        dy = dy.replace("}r", "}")
        return dy


if __name__ == '__main__':
    pcl = py2hcl()
    # fullTest = False
    fullTest = True

    if not fullTest:
        # braces = {"a": {"b": {"c": {"type": "dict"}}}}
        braces = {'a': {'a,b': {'a,b,c': 'dddddddd', 'a,b,e': {'a,b,e,d': "heyman"}}}}
        parentKey = "a,b,e"
        obj, walked = pcl.prev_brace(parentKey, braces)
        # dd = obj['c']
        print(f"asked for..{parentKey}")
        print(obj)
        print(walked)
    else:
        # dy = pcl.dumps(dd)
        test = True
        isFile = True
        filename = "main.yaml"
        if isFile:
            with open(filename, 'r') as stream:
                dd = yaml.load(stream, Loader=yaml.FullLoader)

        # print(dd)
        # raise
        dy = pcl.dumps(dd)

        print("____________________________________________")
        print("____________________________________________")
        print("_____________HCL ORIGINAL____________")
        print("____________________________________________")
        print("____________________________________________")

        print(dy)
        final_hcl = pcl.cleanResult(dy)
        if test:
            # final_hcl = dy
            print(" ====================== CLEAN")
            print(final_hcl)
            # exit()
            jsonAgain = pcl.loads(final_hcl)
            print("____________________________________________")
            print("____________________________________________")
            print("_____________back to JSON____________")
            print("____________________________________________")
            print("____________________________________________")
            print(jsonAgain)
