import os
import re
import glob
import linecache
import json
import subprocess
import tempfile
import zipfile


class color:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class LangCode:
    CODE = {"All": "All Language", "A": "Australia", "As": "Asia", "B": "Brazil",
            "C": "Canada", "Ch": "China", "D": "Netherlands(Dutch)",
            "E": "Europe", "F": "France", "G": "Germany", "Gr": "Greece",
            "HK": "Hong Kong", "I": "Italy", "J": "Japan",
            "K": "Korea", "Nl": "Netherlands", "No": "Norway",
            "R": "Russia", "S": "Spain", "Sw": "Sweden",
            "U": "United States", "UK": "United Kingdom",
            "W": "World", "Unl": "Unlicensed",
            "PD": "Public domain", "Unk": "Unknown country"}

    def CodeKeyList(self):
        return list(self.CODE.keys())

    def NameToCode(self, name):
        for key,value in self.CODE.items():
            if name == value:
                return key
        else:
            return ""

    def CodeNameList(self):
        namelist = []
        keylist = self.CodeKeyList()
        for key in keylist:
            namelist.append(self.CODE[key])
        return namelist

    def CodeListFromName(self,nameList):
        codelist = []
        for name in nameList:
            for key in self.CODE.keys():
                if name == self.CODE[key]:
                    codelist.append(key)
        return codelist



class RomCode:
    CODE = {'All': "All codes", 'None': "No code", '[!]': "[!] Good dump",
            '[a]': "[a] Alternative version", '[b]': "[b] Bad dump",
            '[f]': "[f] Fixed dump", '[h]': "[h] Hacked ROM",
            '[o]': "[o] Overdumped ROM", '[p]': "[p] Pirated version",
            '[t]': "[t] Trained version", '[!p]': "[!p] Pending dump",
            '[T]': "[T] Translated version"}

    def __init__(self):
        self.codes = dict(zip(self.CODE.keys(),[False for i in range(len(self.CODE))]))

    def CodeKeyList(self):
        return list(self.CODE.keys())

    def NameToCode(self, name):
        for key,value in self.CODE.items():
            if name == value:
                return key
        else:
            return "None"

    def CodeNameList(self):
        namelist = []
        keylist = self.CodeKeyList()
        for key in keylist:
            namelist.append(self.CODE[key])
        return namelist

    def clearCode(self):
        for key in self.codes.keys():
            self.codes[key] = False

    def setCodeByFilename(self, name):
        root, ext = os.path.splitext(name)
        self.clearCode()
        self.codes['[!]'] = True if re.search("\[!\]", root) else False
        self.codes['[a]'] = True if re.search("\[a.*\]", root) else False
        self.codes['[b]'] = True if re.search("\[b.*\]", root) else False
        self.codes['[f]'] = True if re.search("\[f[0-9+C]*\]", root) else False
        self.codes['[h]'] = True if re.search("\[h.*\]", root) else False
        self.codes['[h]'] = True if self.codes['[h]'] or re.search("\[f.*\]", root) else False
        self.codes['[o]'] = True if re.search("\[o.*\]", root) else False
        self.codes['[p]'] = True if re.search("\[p.*\]", root) else False
        self.codes['[t]'] = True if re.search("\[t.*\]", root) else False
        self.codes['[!p]'] = True if re.search("\[!p.*\]", root) else False
        self.codes['[T]'] = True if re.search("\[T.*\]", root) else False

        for key, code in self.codes.items():
            if self.codes[key] == True:
                break
        else:
            self.codes['None'] = True

        return

    def isMatch(self, romcode):
        if self.codes['All']:
            return True
        for key in self.codes.keys():
            if key == 'All':
                continue
            if self.codes[key] and romcode.codes[key]:
                return True
        return False

    def setCodeByFlag(self, flags):
        self.clearCode()
        for flag in flags:
            if flag in self.codes:
                self.codes[flag] = True
        return

    def setCodeByName(self, names):
        self.clearCode()
        for name in names:
            if key in self.CODE.keys():
                if name == self.CODE[key]:
                    self.codes[key]=True
        return


    def getCodeText(self):
        text = []
        if self.codes['All']:
            return ["All"]
        for key in self.codes.keys():
            if self.codes[key]:
                text.append(key)
        return text


class RomFile:

    def __init__(self, filename):
        self.filename = filename
        self.romcode = RomCode()
        self.romcode.setCodeByFilename(filename)
        self.langcodes = None
        self.setLang()
        self.unclassified_code = []

    def PureName(self):
        root, ext = os.path.splitext(os.path.basename(self.filename))
        match = re.match("(?P<purename>^([^(^)^[^]]*)*)", root)
        if match is not None:
            return match.group("purename").rstrip()
        else:
            return None

    def setLang(self):
        self.langcodes = []
        root, ext = os.path.splitext(self.filename)
        pattern = "\((?P<langcode>("
        for idx, langkey in enumerate(LangCode.CODE.keys()):
            pattern += "{}{}".format("|" if idx is not 0 else "", langkey)
        pattern += ")+)\)"

        match = re.search(pattern, root)
        if match is not None:
            langcode = match.group("langcode")
            for langkey in sorted(LangCode.CODE.keys(), key=lambda a: len(a), reverse=True):
                if langkey in langcode:
                    self.langcodes.append(langkey)
                    langcode = langcode.replace(langkey, "")

        match_unc_list = re.findall(
            "\((?P<uncCode>[^(^)]+)\)", root.replace(match.group("langcode") if match is not None else "", ""))

        return

    def langName(self):
        name = []
        for langcode in self.langcodes:
            for langkey in LangCode.CODE.keys():
                if langcode == langkey:
                    name.append(LangCode.CODE[langkey])

        return name


class ArchivedRom:

    def __init__(self, path):
        self.path = path
        self.roms = self.setupRoms()

    def setupRoms(self):
        pass


class ArchivedRom7z(ArchivedRom):

    def setupRoms(self):
        roms = []
        proc_result = subprocess.check_output(["7z", "l", "-slt",
                                               "{}".format(self.path)],
                                              universal_newlines=True)
        for info in re.split("(^Path = .*)", proc_result, flags=re.MULTILINE):
            match = re.search(
                "^Path = (?P<rom>.+\.[^(7z)]+$)", info, re.MULTILINE)
            if match is not None:
                roms.append(RomFile(match.group("rom")))
        return roms



class ExtractFilter:
    FILTER_MODE_ALL = 0
    FILTER_MODE_ROM = 1
    FILTER_MODE_ARCHIVEDROM = 2
    FILTER_FLAG_LISTUP_ONLY = 0x1
    FILTER_FLAG_LANG_PRIORITY = 0x2
    FILTER_FLAG_WITH_ZIP = 0x4

    def __init__(self, destPath, Mode, RomNames=None, Archives=None,
                 RomCodeList=[], ExRomCodeList=[], LangCodeList=[], ExLangCodeList=[], flags=0):
        self.destPath = destPath
        self.Mode = Mode
        self.TargetArchives = Archives
        self.TargetRoms = RomNames
        self.RomCode = RomCode()
        self.RomCode.setCodeByFlag(RomCodeList)
        self.ExRomCode = RomCode()
        self.ExRomCode.setCodeByFlag(ExRomCodeList)
        self.LangCode = LangCodeList
        self.ExLangCode = ExLangCodeList
        self.flags = flags

class ArchivedRomSet:

    def __init__(self, path):
        self.path = path
        self.archivedRomsDict = self.prepareArchivedRomsDict()

    def prepareArchivedRomsDict(self):
        pass

    def setupArchivedRomDict(self, key):
        pass

    def extractRomsDict(self, filter):
        extract_dict = {}
        for archive_key in self.archivedRomsDict.keys():
            if filter.Mode == ExtractFilter.FILTER_MODE_ARCHIVEDROM:
                if not os.path.basename(archive_key) in filter.TargetArchives:
                    continue
            extract_list = []
            for rom in self.archivedRomsDict[archive_key].roms:
                if filter.Mode == ExtractFilter.FILTER_MODE_ROM:
                    if rom.PureName() in filter.TargetRoms:
                        extract_list.append(rom)
                else:
                    extract_list.append(rom)
            extract_list_romcode = []
            for rom in extract_list:
                if filter.RomCode.isMatch(rom.romcode) and not filter.ExRomCode.isMatch(rom.romcode):
                    extract_list_romcode.append(rom)

            extract_list_lang = []
            if not "All" in filter.LangCode:
                found_flag = False
                for lang in filter.LangCode:
                    for rom in extract_list_romcode:
                        if lang in rom.langcodes:
                            if not rom in extract_list_lang:
                                extract_list_lang.append(rom)
                                found_flag = True
                    if found_flag and filter.flags & ExtractFilter.FILTER_FLAG_LANG_PRIORITY == ExtractFilter.FILTER_FLAG_LANG_PRIORITY:
                        break
            else:
                extract_list_lang.extend(extract_list_romcode)

            extract_list_exlang = []
            for rom in extract_list_lang:
                for romlang in rom.langcodes:
                    if romlang in filter.ExLangCode:
                        break
                else:
                    extract_list_exlang.append(rom)

            if not len(extract_list_exlang) == 0:
                extract_dict[archive_key] = extract_list_exlang

        return extract_dict


    def extractRomKeys(self, key, filter):
        extract_dict = self.extractRomsDict(filter)
        if not key in extract_dict:
            return

        with tempfile.TemporaryDirectory() as temp:
            with zipfile.ZipFile(self.path, mode="r") as z:
                z.extract(key, path=temp)
            with tempfile.TemporaryDirectory() as temp_archive:
                for rom in extract_dict[key]:
                    if filter.flags & ExtractFilter.FILTER_FLAG_WITH_ZIP == ExtractFilter.FILTER_FLAG_WITH_ZIP:
                        proc_result = subprocess.check_output(["7z", "e", "-o{}".format(temp_archive),
                                                                "{}/{}".format(temp,key),"{}".format(rom.filename)], universal_newlines=True)
                        root,ext = os.path.splitext(os.path.basename(rom.filename))
                        zipedfile = "{}{}".format(root,".zip")
                        with zipfile.ZipFile("{}/{}".format(filter.destPath, zipedfile),"w") as zz:
                            zz.write(os.path.join(temp_archive, os.path.basename(rom.filename)))
                    else:
                        proc_result = subprocess.check_output(["7z", "e", "-o{}".format(filter.destPath),
                                                                "{}/{}".format(temp,key),"{}".format(rom.filename)], universal_newlines=True)


class ArchivedRomSetZip(ArchivedRomSet):

    def prepareArchivedRomsDict(self):
        archivedRoms = {}
        with zipfile.ZipFile(self.path, mode="r") as z:
            infolist = z.infolist()
            for info in infolist:
                if not info.file_size == 0:
                    root, ext = os.path.splitext(
                        os.path.basename(info.filename))
                    if ext == ".7z":
                        archivedRoms[info.filename] = ""
        return archivedRoms

    def setupArchivedRomDict(self, key):
        if key in self.archivedRomsDict:
            with tempfile.TemporaryDirectory() as temp:
                with zipfile.ZipFile(self.path, mode="r") as z:
                    z.extract(key, path=temp)
                    self.archivedRomsDict[key] = ArchivedRom7z(
                        "{}/{}".format(temp, key))

    def RomNumsTotally(self):
        num = 0
        for key in self.archivedRomsDict:
            num += len(self.archivedRomsDict[key].roms)
        return num

    def RomNameList(self, archive=None):
        if archive == None:
            list = []
            for key in self.archivedRomsDict:
                for rom in self.archivedRomsDict[key].roms:
                    root, ext = os.path.splitext(os.path.basename(rom.filename))
                    list.append(root)
            return list
        else:
            list = []
            for key in self.archivedRomsDict:
                if archive == os.path.basename(key):
                    for rom in self.archivedRomsDict[key].roms:
                        root, ext = os.path.splitext(os.path.basename(rom.filename))
                        list.append(root)
            return list

    def FileNameList(self, archive=None):
        if archive == None:
            list = []
            for key in self.archivedRomsDict:
                for rom in self.archivedRomsDict[key].roms:
                    list.append(os.path.basename(rom.filename))
            return list
        else:
            list = []
            for key in self.archivedRomsDict:
                if archive == os.path.basename(key):
                    for rom in self.archivedRomsDict[key].roms:
                        list.append(os.path.basename(rom.filename))
            return list

    def RomPureNameList(self):
        list = []
        for key in self.archivedRomsDict:
            for rom in self.archivedRomsDict[key].roms:
                purename = rom.PureName()
                if purename is not None:
                    if not purename in list:
                        list.append(purename)
                else:
                    pass
                    # print("NOPURE:{}".format(rom.filename))
        return sorted(list)
