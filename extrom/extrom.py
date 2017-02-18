#!/usr/bin/env python

from extrom.gdromlib import ArchivedRom7z, ArchivedRomSetZip, ExtractFilter, LangCode, RomCode, color
import os
import sys
import npyscreen
import curses


class WidgetSet:

    def __init__(self, widget_list=None):
        if list == None:
            self.widgets = []
        else:
            self.widgets = widget_list

    def add(self, widget):
        self.widgets.append(widget)

    def hidden(self, hidden):
        for w in self.widgets:
            w.hidden = hidden
            w.display()

    def display(self):
        for w in self.widgets:
            w.display()

class FormDescription:
    def setDesc(self, desc):
        self.desc.value = desc
        self.desc.display()

class FormItems:
    def setItems(self, items, value=[]):
        self.itemlist = items
        self.list.values = self.itemlist
        self.list.value = value
        self.list.display()

    def getItems(self):
        return self.itemlist

    def getValue(self):
        return self.list.value

class FormProgress(npyscreen.Popup, FormDescription):

    def create(self):
        self.desc = self.add(npyscreen.Textfield, editable=False)
        self.bar = self.add(npyscreen.SliderPercent, editable=False)
        self.text = self.add(npyscreen.MultiLine, editable=False)
        self.textValue = []

    def setProgress(self, value):
        self.bar.value = value
        self.bar.display()

    def addText(self, text):
        self.textValue.append(text)
        if len(self.textValue) > self.text.height:
            self.textValue.pop(0)
        self.text.values = self.textValue
        self.text.display()

class FormItemList(npyscreen.Form, FormDescription, FormItems):
    OK_BUTTON_TEXT = "Close"

    def create(self):
        self.desc = self.add(npyscreen.Textfield, editable=False)
        self.desc.color = 'CAUTION'
        self.nextrely+=1
        self.list = self.add(npyscreen.MultiLine)

class FormSelectList(npyscreen.Form, FormDescription, FormItems):
    def create(self):
        self.desc = self.add(npyscreen.Textfield, editable=False)
        self.desc.color = 'CAUTION'
        self.nextrely+=1
        self.list = self.add(npyscreen.MultiSelect)

class FormSelectListWithOrderChangeable(FormSelectList):
    def __init__(self, *key, **argv):
        super().__init__(*key, **argv)
        self.add_handlers({ord('u'): self.change_priority,
                           ord('d'): self.change_priority})

    def change_priority(self, key):
        if key == ord('u'):
            if self.list.cursor_line <= 1:
                return
            l = self.list.cursor_line
            self.itemlist[l], self.itemlist[l - 1] = self.itemlist[l - 1], self.itemlist[l]
            if not self.list.value.count(l) == 0:
                if self.list.value.count(l - 1) == 0:
                    self.list.value[self.list.value.index(l)] = l - 1
            else:
                if not self.list.value.count(l - 1) == 0:
                    self.list.value[self.list.value.index(l - 1)] = l

            self.list.cursor_line -= 1
        elif key == ord('d'):
            if self.list.cursor_line == len(self.itemlist) - 1 or self.list.cursor_line == 0:
                return
            l = self.list.cursor_line
            self.itemlist[l], self.itemlist[l + 1] = self.itemlist[l + 1], self.itemlist[l]
            if not self.list.value.count(l) == 0:
                if self.list.value.count(l + 1) == 0:
                    self.list.value[self.list.value.index(l)] = l + 1
            else:
                if not self.list.value.count(l + 1) == 0:
                    self.list.value[self.list.value.index(l + 1)] = l
            self.list.cursor_line += 1

        self.list.values = self.itemlist
        self.display()


class FormSelectOne(npyscreen.Form, FormDescription):
    def create(self):
        self.desc = self.add(npyscreen.Textfield, editable=False)
        self.option = self.add(npyscreen.SelectOne)

    def setOption(self, option):
        self.option.values = option
        self.option.display()

class FormPopupInfo(npyscreen.PopupWide,FormItems):
    def create(self):
        self.list = self.add(npyscreen.MultiLine)

# Widgets
class TitleFileNameComboRomSet(npyscreen.TitleFilenameCombo):
    name = "RomSetFile"

    def when_value_edited(self):
        if self.value == None:
            return
        romsetfile = self.find_parent_app().getForm("MAIN").wdgtRomPath.value
        self.find_parent_app().getForm("COMPLETE").multiline.value = []
        self.find_parent_app().getForm("COMPLETE_ARCHIVE").multiline.value = []


        try:
            archiveRomSetZip = ArchivedRomSetZip(romsetfile)
            max_value = len(archiveRomSetZip.archivedRomsDict)

            progress_form = self.find_parent_app().getForm("PROGRESS")
            progress_form.name = "Scanning .."
            progress_form.setProgress(0)
            progress_form.display()

            for idx, key in enumerate(archiveRomSetZip.archivedRomsDict.keys()):
                progress_form.addText("({:3d}/{:3d}) {}".format(idx, max_value, os.path.basename(key)))
                progress_form.setProgress(int(((idx + 1) * 100) / max_value))
                archiveRomSetZip.setupArchivedRomDict(key)

            progress_form.setDesc("Complete scanning roms.")
            self.find_parent_app().getForm("MAIN").romScaned = True

            self.find_parent_app().archivedRomSetZip = archiveRomSetZip
            self.find_parent_app().RomPureNameList = archiveRomSetZip.RomPureNameList()
        except:
            npyscreen.notify_confirm("Scanning is failed..")
            self.value = None


class TitleFileNameComboOutputPath(npyscreen.TitleFilenameCombo):
    name = "OutputPath"

    def when_value_edited(self):
        if self.value == None:
            return

        if not os.path.isdir(self.value):
            npyscreen.notify_confirm("Not directory.", title="Error")
            self.value = None


class ButtonSelect(npyscreen.ButtonPress):

    def whenPressed(self):
        if not self.find_parent_app().getForm("MAIN").romScaned:
            npyscreen.notify_confirm("Rom set file is not specified.", title="Error")
            return

        mode = self.find_parent_app().getForm("MAIN").wdgtRomFilterMode.value[0]
        if mode == RomFilterMode.ROM_FILTER_MODE_ROMS:
            complete_form = self.find_parent_app().getForm("COMPLETE")
            complete_form.multiline.values = self.find_parent_app().archivedRomSetZip.RomPureNameList()
            complete_form.display()
            complete_form.edit()
            self.display()
        elif mode == RomFilterMode.ROM_FILTER_MODE_ARCHIVES:
            complete_form = self.find_parent_app().getForm("COMPLETE_ARCHIVE")
            complete_form.multiline.values = sorted([os.path.basename(x) for x in self.find_parent_app().archivedRomSetZip.archivedRomsDict.keys()])
            complete_form.display()
            complete_form.edit()
            self.display()
        else:
            npyscreen.notify_confirm("MODE:{} /{}{}".format(mode,RomFilterMode.ROM_FILTER_MODE_ROMS,RomFilterMode.ROM_FILTER_MODE_ARCHIVES))


class ButtonClear(npyscreen.ButtonPress):

    def whenPressed(self):
        if not self.find_parent_app().getForm("MAIN").romScaned:
            npyscreen.notify_confirm("Rom set file is not specified.", title="Error")
            return

        mode = self.find_parent_app().getForm("MAIN").wdgtRomFilterMode.value[0]
        if mode == RomFilterMode.ROM_FILTER_MODE_ROMS:
            self.find_parent_app().getForm("COMPLETE").multiline.value = []
        elif mode == RomFilterMode.ROM_FILTER_MODE_ARCHIVES:
            self.find_parent_app().getForm("COMPLETE_ARCHIVE").multiline.value = []
        npyscreen.notify_confirm("Selected items has been cleared.")

class ButtonList(npyscreen.ButtonPress):

    def whenPressed(self):
        if not self.find_parent_app().getForm("MAIN").romScaned:
            npyscreen.notify_confirm("Rom set file is not specified.", title="Error")
            return

        mode = self.find_parent_app().getForm("MAIN").wdgtRomFilterMode.value[0]
        itemlist = []
        itemlist_form = self.find_parent_app().getForm("ITEMLIST")
        if mode == RomFilterMode.ROM_FILTER_MODE_ROMS:
            form = self.find_parent_app().getForm("COMPLETE")
            for idx in form.multiline.value:
                itemlist.append(form.multiline.values[idx])
            itemlist_form.setItems(itemlist)
            itemlist_form.setDesc("Selected ROMs [{} items]".format(len(itemlist)))
            itemlist_form.display()
            itemlist_form.edit()
        elif mode == RomFilterMode.ROM_FILTER_MODE_ARCHIVES:
            form = self.find_parent_app().getForm("COMPLETE_ARCHIVE")
            for idx in form.multiline.value:
                itemlist.append(form.multiline.values[idx])
            itemlist_form.setItems(itemlist)
            itemlist_form.setDesc("Selected Archives [{} items]".format(len(itemlist)))
            itemlist_form.display()
            itemlist_form.edit()


class RomFilterMode(npyscreen.TitleSelectOne):
    name = "RomFilterMode"
    ROM_FILTER_MODE_ALL = 0
    ROM_FILTER_MODE_ROMS = 1
    ROM_FILTER_MODE_ARCHIVES = 2

    def when_value_edited(self):
        if self.value[0] == self.ROM_FILTER_MODE_ALL:
            self.find_parent_app().getForm("MAIN").wdgtSetButtons.hidden(True)
        else:
            self.find_parent_app().getForm("MAIN").wdgtSetButtons.hidden(False)


class ButtonRomCode(npyscreen.ButtonPress):
    def __init__(self, *key, **argv):
        super().__init__(*key, **argv)
        self.romcodeValue = [0]
        self.romcodeText = []
        pass

    def whenPressed(self):
        selectlist_form = self.find_parent_app().getForm("SELECTLIST")
        selectlist_form.setDesc("Selects Standard Code")
        selectlist_form.setItems([x for k,x in RomCode().CODE.items()], self.romcodeValue)
        selectlist_form.display()
        selectlist_form.edit()
        self.romcodeText = []
        self.romcodeValue = sorted(selectlist_form.getValue())
        if 0 in self.romcodeValue:
            self.romcodeText.append(RomCode().NameToCode(selectlist_form.getItems()[0]))
        else:
            for idx in self.romcodeValue:
                self.romcodeText.append(RomCode().NameToCode(selectlist_form.getItems()[idx]))

        self.find_parent_app().getForm("MAIN").wdgtTextRomCode.value = " ".join(self.romcodeText)
        self.find_parent_app().getForm("MAIN").wdgtTextRomCode.display()

class ButtonExRomCode(npyscreen.ButtonPress):
    def __init__(self, *key, **argv):
        super().__init__(*key, **argv)
        self.romcodeValue = []
        self.romcodeText = []
        pass

    def whenPressed(self):
        selectlist_form = self.find_parent_app().getForm("SELECTLIST")
        selectlist_form.setDesc("Selects Standard Code")
        selectlist_form.setItems([x for k,x in RomCode().CODE.items()], self.romcodeValue)
        selectlist_form.display()
        selectlist_form.edit()
        self.romcodeText = []
        self.romcodeValue = sorted(selectlist_form.getValue())
        if 0 in self.romcodeValue:
            self.romcodeText.append(RomCode().NameToCode(selectlist_form.getItems()[0]))
        else:
            for idx in self.romcodeValue:
                self.romcodeText.append(RomCode().NameToCode(selectlist_form.getItems()[idx]))

        self.find_parent_app().getForm("MAIN").wdgtTextExRomCode.value = " ".join(self.romcodeText)
        self.find_parent_app().getForm("MAIN").wdgtTextExRomCode.display()



class ButtonCountryCode(npyscreen.ButtonPress):
    def __init__(self, *key, **argv):
        super().__init__(*key, **argv)
        self.itemValue = [0]
        self.items = [x for k,x in LangCode().CODE.items()]
        self.text = []

    def whenPressed(self):
        selectlist_form = self.find_parent_app().getForm("SELECTLISTCHGABLE")
        selectlist_form.setDesc("Selects Country Code")
        selectlist_form.setItems(self.items, self.itemValue)
        selectlist_form.display()
        selectlist_form.edit()
        self.text = []
        self.items = selectlist_form.getItems()
        self.itemValue= sorted(selectlist_form.getValue())
        if 0 in self.itemValue:
            self.text.append(LangCode().NameToCode(selectlist_form.getItems()[0]))
            self.find_parent_app().getForm("MAIN").wdgtTextCountryCode.value = " ".join(["{}".format(x) for x in self.text])
        else:
            for idx in self.itemValue:
                self.text.append(LangCode().NameToCode(selectlist_form.getItems()[idx]))
            self.find_parent_app().getForm("MAIN").wdgtTextCountryCode.value = " ".join(["({})".format(x) for x in self.text])

        self.find_parent_app().getForm("MAIN").wdgtTextCountryCode.display()

class ButtonExCountryCode(npyscreen.ButtonPress):
    def __init__(self, *key, **argv):
        super().__init__(*key, **argv)
        self.itemValue = []
        self.items = [x for k,x in LangCode().CODE.items()]
        self.text = []
        pass

    def whenPressed(self):
        selectlist_form = self.find_parent_app().getForm("SELECTLIST")
        selectlist_form.setDesc("Selects Standard Code")
        selectlist_form.setItems(self.items, self.itemValue)
        selectlist_form.display()
        selectlist_form.edit()
        self.text = []
        self.itemValue = sorted(selectlist_form.getValue())
        self.items = selectlist_form.getItems()
        if 0 in self.itemValue:
            self.text.append(LangCode().NameToCode(selectlist_form.getItems()[0]))
        else:
            for idx in self.itemValue:
                self.text.append(LangCode().NameToCode(selectlist_form.getItems()[idx]))

        self.find_parent_app().getForm("MAIN").wdgtTextExCountryCode.value = " ".join(["({})".format(x) for x in self.text])
        self.find_parent_app().getForm("MAIN").wdgtTextExCountryCode.display()


class ButtonOptions(npyscreen.ButtonPress):
    def __init__(self, *key, **argv):
        super().__init__(*key, **argv)
        self.itemValues = ["Extracts roms according to priority of country code.",
                           "Extracts with Zip archiving."]
        self.itemValue = [1]
        pass

    def whenPressed(self):
        selectlist_form = self.find_parent_app().getForm("SELECTLIST")
        selectlist_form.setDesc("Other Configuration")
        selectlist_form.setItems(self.itemValues, self.itemValue)
        selectlist_form.display()
        selectlist_form.edit()
        self.itemValue = sorted(selectlist_form.getValue())




class OtherOptionSelect(npyscreen.TitleMultiSelect):
    name = "Other Options"

    def __init__(self, *key, **argv):
        super().__init__(*key, **argv)
        self.values = ["Not extracts rom which has low priority LANG code.",
                       "Extracts with Zip archiving."]
        self.value = [1]

class MultiLineForRomInfo(npyscreen.MultiSelect):
    def __init__(self, *key, **argv):
        super().__init__(*key, **argv)
        self.add_handlers({ord('i'): self.popup_info})

    def popup_info(self, val):
        item = self.values[self.cursor_line]
        rom_list = []
        for key in self.find_parent_app().archivedRomSetZip.archivedRomsDict.keys():
            for rom in self.find_parent_app().archivedRomSetZip.archivedRomsDict[key].roms:
                if item == rom.PureName():
                    rom_list.append(os.path.basename(rom.filename))
        popupform = self.find_parent_app().getForm("POPUPINFO")
        popupform.name = "{}".format(item)
        popupform.setItems(rom_list)
        popupform.display()
        popupform.edit()


class MultiLineForArchiveInfo(npyscreen.MultiSelect):
    def __init__(self, *key, **argv):
        super().__init__(*key, **argv)
        self.add_handlers({ord('i'): self.popup_info})

    def popup_info(self, val):
        item = self.values[self.cursor_line]
        all_roms = self.find_parent_app().archivedRomSetZip.FileNameList(item)
        popupform = self.find_parent_app().getForm("POPUPINFO")
        popupform.name = "{}".format(item)
        popupform.setItems(all_roms)
        popupform.display()
        popupform.edit()


class FormRomComplete(npyscreen.Form):
    def create(self):
        self.multiline = self.add(MultiLineForRomInfo)


class FormArchiveComplete(npyscreen.Form):
    def create(self):
        self.multiline = self.add(MultiLineForArchiveInfo)


class FormMainMenu(npyscreen.ActionFormV2):

    def __init__(self, *key, **argv):
        super().__init__(*key, **argv)
        self.romScaned = False

    def _on_cancel(self):
        self.parentApp.setNextForm(None)
        self.editing = False

    def _on_ok(self):
        if self.wdgtDestPath.value is None:
            npyscreen.notify_confirm("RomDestPath is not specified.")
            return

        if not os.path.isdir(self.wdgtDestPath.value):
            npyscreen.notify_confirm("RomDestPath is not directory.")
            return

        if not self.romScaned:
            npyscreen.notify_confirm("Scanning ROM is not done.")
            return

        self.filter_destpath = self.wdgtDestPath.value
        if self.wdgtRomFilterMode.value[0] == RomFilterMode.ROM_FILTER_MODE_ALL:
            self.filter_mode = ExtractFilter.FILTER_MODE_ALL
        elif self.wdgtRomFilterMode.value[0] == RomFilterMode.ROM_FILTER_MODE_ROMS:
            self.filter_mode = ExtractFilter.FILTER_MODE_ROM
        elif self.wdgtRomFilterMode.value[0] == RomFilterMode.ROM_FILTER_MODE_ARCHIVES:
            self.filter_mode = ExtractFilter.FILTER_MODE_ARCHIVEDROM
        else:
            npyscreen.notify_confirm(
                "Unknown Error.. {}".format(self.wdgtRomFilterMode.value))
            return

        if self.filter_mode == ExtractFilter.FILTER_MODE_ROM:
            form = self.find_parent_app().getForm("COMPLETE")
            self.filter_RomNames = [form.multiline.values[x] for x in form.multiline.value]
        else:
            self.filter_RomNames = []

        if self.filter_mode == ExtractFilter.FILTER_MODE_ARCHIVEDROM:
            form = self.find_parent_app().getForm("COMPLETE_ARCHIVE")
            self.filter_Archives = [form.multiline.values[x] for x in form.multiline.value]
        else:
            self.filter_Archives = []


        form = self.find_parent_app().getForm("MAIN")
        self.filter_RomCodeList = [RomCode().CodeKeyList()[x] for x in form.wdgtButtonRomCode.romcodeValue]
        self.filter_ExRomCodeList = [RomCode().CodeKeyList()[x] for x in form.wdgtButtonExRomCode.romcodeValue]
        self.filter_LangCodeList = LangCode().CodeListFromName([form.wdgtButtonCountyCode.items[x] for x in form.wdgtButtonCountyCode.itemValue])
        self.filter_ExLangCodeList = LangCode().CodeListFromName([form.wdgtButtonExCountryCode.items[x] for x in form.wdgtButtonExCountryCode.itemValue])

        self.filter_flags = ExtractFilter.FILTER_FLAG_LISTUP_ONLY
        if 0 in form.wdgtButtonOptions.itemValue:
            self.filter_flags |= ExtractFilter.FILTER_FLAG_LANG_PRIORITY
        if 1 in form.wdgtButtonOptions.itemValue:
            self.filter_flags |= ExtractFilter.FILTER_FLAG_WITH_ZIP

        self.filterSetting = ExtractFilter(destPath=self.filter_destpath,
                                           Mode=self.filter_mode,
                                           RomNames=self.filter_RomNames,
                                           Archives=self.filter_Archives,
                                           RomCodeList=self.filter_RomCodeList,
                                           ExRomCodeList=self.filter_ExRomCodeList,
                                           LangCodeList=self.filter_LangCodeList,
                                           ExLangCodeList=self.filter_ExLangCodeList,
                                           flags=self.filter_flags)
        self.parentApp.getForm("EXTRACT").filterSetting = self.filterSetting

        extract_dict = self.parentApp.archivedRomSetZip.extractRomsDict(
            self.filterSetting)
        extract_list = []
        for key in extract_dict.keys():
            extract_list.extend([os.path.basename(x.filename)
                                 for x in extract_dict[key]])
        self.parentApp.getForm(
            "EXTRACT").extractinfo.values = sorted(extract_list)

        self.parentApp.getForm(
            "EXTRACT").filterinfo.value = "<< {} Roms >>".format(len(extract_list))
        # self.parentApp.getForm("EXTRACT").filterinfo.values = [self.filter_destpath,
        #                                                        self.filter_mode,
        #                                                        self.filter_RomNames,
        #                                                        self.filter_Archives,
        #                                                        self.filter_RomCodeList,
        #                                                        self.filter_ExRomCodeList,
        #                                                        self.filter_LangCodeList,
        #                                                        self.filter_ExLangCodeList,
        #                                                        self.filter_flags]

        # self.extract_list = self.parentApp.archivedRomSetZip.extractRoms(self.filterSetting)

        self.parentApp.setNextForm("EXTRACT")
        self.editing = False
        # self.parentApp.setNextForm(None)

    def create(self):
        self.wdgtRomPath = self.add(TitleFileNameComboRomSet)
        self.nextrely+=1

        self.wdgtDestPath = self.add(TitleFileNameComboOutputPath)

        self.nextrely+=1
        self.wdgtRomFilterMode = self.add(RomFilterMode, max_width=41, max_height=4, value=0,
                                          values=["All Roms", "Selected Roms", "Selected Archives"], scroll_exit=True)

        self.wdgtButtonSelect = self.add(ButtonSelect, name="Select", relx=41, rely=6)
        self.wdgtButtonClear = self.add(ButtonClear, name="Clear", relx=41)
        self.wdgtButtonList = self.add(ButtonList, name="List", relx=41)
        self.wdgtSetButtons = WidgetSet([self.wdgtButtonSelect,self.wdgtButtonClear,self.wdgtButtonList])
        self.wdgtSetButtons.hidden(True)

        self.nextrely+=2

        # Standard Code
        self.wdgtText1 = self.add(npyscreen.Textfield, value="Good code filter", editable=False)
        self.wdgtText1.color = 'LABEL'
        self.wdgtButtonRomCode = self.add(ButtonRomCode,    name="Standard code          :")
        self.nextrely-=1
        self.wdgtTextRomCode = self.add(npyscreen.Textfield, relx=30, editable=False, value="All")
        self.wdgtButtonExRomCode = self.add(ButtonExRomCode,  name="Exclusion Standard code:")
        self.nextrely-=1
        self.wdgtTextExRomCode = self.add(npyscreen.Textfield, relx=30, editable=False)

        # Country Code
        self.nextrely+=1
        self.wdgtButtonCountyCode = self.add(ButtonCountryCode,   name="Country code           :")
        self.nextrely-=1
        self.wdgtTextCountryCode = self.add(npyscreen.Textfield, relx=30, editable=False, value="All")
        self.wdgtButtonExCountryCode = self.add(ButtonExCountryCode , name="Exclusion Country code :")
        self.nextrely-=1
        self.wdgtTextExCountryCode = self.add(npyscreen.Textfield, relx=30, editable=False)

        #Other Options
        self.nextrely+=1
        self.wdgtText3 = self.add(npyscreen.Textfield, value="Other Configuration", editable=False)
        self.wdgtText3.color = 'LABEL'
        self.wdgtButtonOptions = self.add(ButtonOptions,    name="Config ")

        # self.wdgtRomCodeSelect = self.add(npyscreen.TitleMultiSelect, name="Rom code",
        #                                   values=RomCode().CodeNameList(), value=[0], rely=14, max_width=50, max_height=7)
        # self.wdgtExRomCodeSelect = self.add(npyscreen.TitleMultiSelect, name="Exclusion",
        #                                     values=RomCode().CodeNameList(), rely=14, relx=52, max_height=7)
        # self.wdgtLangCodeSelect = self.add(
        #     LangCodeSelect, values=LangCode().CodeNameList(), rely=22, max_width=50, max_height=8)
        # self.wdgtExLangCodeSelect = self.add(
        #     ExLangCodeSelect, values=LangCode().CodeNameList(), rely=22, relx=52, max_width=50, max_height=8)
        # self.wdgtOtherOption = self.add(OtherOptionSelect, rely=31)


class FormExtract(npyscreen.ActionFormV2):
    OK_BUTTON_TEXT = "Extract"
    CANCEL_BUTTON_BR_OFFSET = (2, 20)

    def __init__(self, *key, **argv):
        super().__init__(*key, **argv)
        self.filterSetting = None

    def _on_ok(self):
        complete_form = self.find_parent_app().getForm("EXTRACTING")
        complete_form.display()

        extract_dict = self.parentApp.archivedRomSetZip.extractRomsDict(
            self.filterSetting)
        num = len(extract_dict)
        for idx, key in enumerate(extract_dict.keys()):
            complete_form.progress_text.value = "Extracting from {}..".format(
                key)
            complete_form.progress.value = int(((idx + 1) * 100) / num)
            complete_form.progress_text.display()
            complete_form.progress.display()
            self.parentApp.archivedRomSetZip.extractRomKeys(
                key, self.filterSetting)

        self.parentApp.setNextForm("MAIN")
        self.editing = False

    def _on_cancel(self):
        self.parentApp.setNextForm("MAIN")
        self.editing = False

    def create(self):
        self.filterinfo = self.add(npyscreen.Textfield, editable=False)
        self.extractinfo = self.add(npyscreen.MultiLine, rely=4)


class FormExtracting(npyscreen.Popup):

    def afterEditing(self):
        self.parentApp.setNextForm("MAIN")

    def create(self):
        self.progress_text = self.add(
            npyscreen.Textfield, value="Extracting ROMS ...")
        self.progress = self.add(npyscreen.SliderPercent, editable=False)


class AppRomExtractor(npyscreen.NPSAppManaged):

    def __init__(self):
        super().__init__()
        self.archivedRomSetZip = None
        self.RomPureNameList = None

        self.romList = []
        self.archiveList = []

    def onStart(self):
        self.main_form = self.addForm("MAIN", FormMainMenu, name="ExtROM")

        self.progress_form = self.addForm("PROGRESS", FormProgress)
        self.itemlist_form = self.addForm("ITEMLIST", FormItemList)
        self.selectOne_form = self.addForm("SELECTONE", FormSelectOne)
        self.selectList_form = self.addForm("SELECTLIST", FormSelectList)
        self.popupinfo_form = self.addForm("POPUPINFO", FormPopupInfo)
        self.selectListChgAble_form = self.addForm("SELECTLISTCHGABLE", FormSelectListWithOrderChangeable)

        self.complete_form = self.addForm("COMPLETE", FormRomComplete, name="Select ROMs")
        self.complete_ar_form = self.addForm("COMPLETE_ARCHIVE", FormArchiveComplete, name="Select ROM Archives")

        self.extract_form = self.addForm("EXTRACT", FormExtract, name="Filtered ROMs")
        self.extracting_form = self.addForm("EXTRACTING", FormExtracting, name="Extracting ...")

def extrom():
    app = AppRomExtractor()
    app.run()

def main():
    extrom()

if __name__ == '__main__':
    main()
