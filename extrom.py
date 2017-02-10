#!/usr/bin/env python

from gdromlib import ArchivedRom7z, ArchivedRomSetZip, ExtractFilter, LangCode, RomCode
import os
import sys
import npyscreen
import curses


class WidgetSet:

    def __init__(self, list=None):
        if list == None:
            self.widgets = []
        else:
            self.widgets = list

    def add(self, widget):
        self.widgets.append(widget)

    def hidden(self, hidden):
        for w in self.widgets:
            w.hidden = hidden

    def display(self):
        for w in self.widgets:
            w.display()


class BoxRomInfo(npyscreen.BoxTitle):
    name = "Rom Info"
    _contained_widget = npyscreen.MultiLine


class SliderPercentRomScanProgress(npyscreen.SliderPercent):

    def when_value_edited(self):
        pass


class BoxProgress(npyscreen.BoxTitle):
    _contained_widget = SliderPercentRomScanProgress


class TitleFileNameComboRomSet(npyscreen.TitleFilenameCombo):
    name = "RomSet"

    def when_value_edited(self):
        self.find_parent_app().getForm("MAIN").wdgtBoxProgress.value = 0
        self.find_parent_app().getForm("MAIN").wdgtBoxProgress.display()


class ButtonPressRomScan(npyscreen.ButtonPress):

    def whenPressed(self):
        if self.find_parent_app().getForm("MAIN").wdgtRomPath.value is None:
            npyscreen.notify_confirm("Romset file is not set.", title="Error")
            return

        romsetfile = self.find_parent_app().getForm("MAIN").wdgtRomPath.value
        widget_barbox = self.find_parent_app().getForm("MAIN").wdgtBoxProgress
        # widget_rominfo = self.find_parent_app().getForm("MAIN").wdgtBoxRomInfo
        archiveRomSetZip = ArchivedRomSetZip(romsetfile)
        max_value = len(archiveRomSetZip.archivedRomsDict)

        for idx, key in enumerate(archiveRomSetZip.archivedRomsDict.keys()):
            widget_barbox.footer = "{} ({}/{})".format(
                os.path.basename(key), idx, max_value)
            widget_barbox.value = int(((idx + 1) * 100) / max_value)
            widget_barbox.display()
            archiveRomSetZip.setupArchivedRomDict(key)

        widget_barbox.footer = "Scanning has been done."
        widget_barbox.display()

        self.find_parent_app().archivedRomSetZip = archiveRomSetZip
        self.find_parent_app().RomPureNameList = archiveRomSetZip.RomPureNameList()


class RomFilterRomSearchButton(npyscreen.ButtonPress):

    def whenPressed(self):
        if not self.find_parent_app().getForm("MAIN").wdgtBoxProgress.value == 100:
            npyscreen.notify_confirm("Please scan rom first.", title="Error")
            return

        complete_form = self.find_parent_app().getForm("COMPLETE")
        complete_form.multiline.values = self.find_parent_app().archivedRomSetZip.RomPureNameList()
        complete_form.display()
        complete_form.edit()
        self.display()


class RomFilterRomClearButton(npyscreen.ButtonPress):

    def whenPressed(self):
        self.find_parent_app().getForm("COMPLETE").multiline.value = []
        self.find_parent_app().getForm("MAIN").wdgtRomFilterSelectedRomList.values = []
        self.find_parent_app().getForm("MAIN").wdgtRomFilterSelectedRomList.display()


class RomFilterArchiveSearchButton(npyscreen.ButtonPress):

    def whenPressed(self):
        if not self.find_parent_app().getForm("MAIN").wdgtBoxProgress.value == 100:
            npyscreen.notify_confirm("Please scan rom first.", title="Error")
            return

        complete_form = self.find_parent_app().getForm("COMPLETE_ARCHIVE")
        complete_form.multiline.values = sorted([os.path.basename(x) for x in self.find_parent_app().archivedRomSetZip.archivedRomsDict.keys()])
        complete_form.display()
        complete_form.edit()
        self.display()


class RomFilterArchiveClearButton(npyscreen.ButtonPress):

    def whenPressed(self):
        self.find_parent_app().getForm("COMPLETE_ARCHIVE").multiline.value = []
        self.find_parent_app().getForm("MAIN").wdgtRomFilterSelectedArchiveList.values = []
        self.find_parent_app().getForm("MAIN").wdgtRomFilterSelectedArchiveList.display()


class RomFilterMode(npyscreen.TitleSelectOne):
    name = "RomFilterMode"

    def when_value_edited(self):
        ws1 = WidgetSet([self.find_parent_app().getForm("MAIN").wdgtRomFilterRomSearchButton,
                         self.find_parent_app().getForm("MAIN").wdgtRomFilterRomClearButton,
                         self.find_parent_app().getForm("MAIN").wdgtRomFilterSelectedRomList])

        ws2 = WidgetSet([self.find_parent_app().getForm("MAIN").wdgtRomFilterArchiveSearchButton,
                         self.find_parent_app().getForm("MAIN").wdgtRomFilterArchiveClearButton,
                         self.find_parent_app().getForm("MAIN").wdgtRomFilterSelectedArchiveList])

        if self.value[0] == 0:
            ws1.hidden(True)
            ws2.hidden(True)
            ws1.display()
            ws2.display()
        elif self.value[0] == 1:
            ws1.hidden(False)
            ws2.hidden(True)
            ws1.display()
        elif self.value[0] == 2:
            ws1.hidden(True)
            ws2.hidden(False)
            ws2.display()


class LangCodeSelect(npyscreen.TitleMultiSelect):
    name = "Lang code"

    def __init__(self, *key, **argv):
        super().__init__(*key, **argv)
        self.add_handlers({ord('u'): self.change_priority,
                           ord('d'): self.change_priority})
        self.langCodeList = LangCode().CodeNameList()
        self.values = self.langCodeList
        self.value = [0]

    def change_priority(self, key):
        if key == ord('u'):
            if self.entry_widget.cursor_line <= 1:
                return
            l = self.entry_widget.cursor_line
            self.langCodeList[l], self.langCodeList[l - 1] = self.langCodeList[l - 1], self.langCodeList[l]
            if not self.value.count(l) == 0:
                if self.value.count(l - 1) == 0:
                    self.value[self.value.index(l)] = l - 1
            else:
                if not self.value.count(l - 1) == 0:
                    self.value[self.value.index(l - 1)] = l

            self.entry_widget.cursor_line -= 1
        elif key == ord('d'):
            if self.entry_widget.cursor_line == len(self.langCodeList) - 1 or self.entry_widget.cursor_line == 0:
                return
            l = self.entry_widget.cursor_line
            self.langCodeList[l], self.langCodeList[l + 1] = self.langCodeList[l + 1], self.langCodeList[l]
            if not self.value.count(l) == 0:
                if self.value.count(l + 1) == 0:
                    self.value[self.value.index(l)] = l + 1
            else:
                if not self.value.count(l + 1) == 0:
                    self.value[self.value.index(l + 1)] = l
            self.entry_widget.cursor_line += 1

        self.values = self.langCodeList
        self.display()


class ExLangCodeSelect(npyscreen.TitleMultiSelect):
    name = "Exclusion"

    def __init__(self, *key, **argv):
        super().__init__(*key, **argv)
        self.langCodeList = LangCode().CodeNameList()
        self.values = self.langCodeList


class OtherOptionSelect(npyscreen.TitleMultiSelect):
    name = "Other Options"

    def __init__(self, *key, **argv):
        super().__init__(*key, **argv)
        self.values = ["Not extracts rom which has low priority LANG code.",
                       "Extracts with Zip archiving."]
        self.value = [1]


class FormRomComplete(npyscreen.ActionFormExpandedV2):

    def on_ok(self):
        selected_list = []
        widget_list = self.find_parent_app().getForm(
            "MAIN").wdgtRomFilterSelectedRomList
        for idx in self.multiline.value:
            selected_list.append(self.find_parent_app(
            ).archivedRomSetZip.RomPureNameList()[idx])
        widget_list.values = selected_list
        widget_list.display()

    def create(self):
        self.multiline = self.add(npyscreen.MultiSelect)


class FormArchiveComplete(npyscreen.ActionFormExpandedV2):

    def on_ok(self):
        archive_list = sorted([os.path.basename(x) for x in self.find_parent_app().archivedRomSetZip.archivedRomsDict.keys()])
        selected_list = []
        widget_list = self.find_parent_app().getForm(
            "MAIN").wdgtRomFilterSelectedArchiveList
        for idx in self.multiline.value:
            selected_list.append(archive_list[idx])
        widget_list.values = selected_list
        widget_list.display()

    def create(self):
        self.multiline = self.add(npyscreen.MultiSelect)


class FormMainMenu(npyscreen.ActionFormV2):

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

        if not self.wdgtBoxProgress.value == 100:
            npyscreen.notify_confirm("Scanning ROM is not done.")
            return

        self.filter_destpath = self.wdgtDestPath.value
        if self.wdgtRomFilterMode.value[0] == 0:
            self.filter_mode = ExtractFilter.FILTER_MODE_ALL
        elif self.wdgtRomFilterMode.value[0] == 1:
            self.filter_mode = ExtractFilter.FILTER_MODE_ROM
        elif self.wdgtRomFilterMode.value[0] == 2:
            self.filter_mode = ExtractFilter.FILTER_MODE_ARCHIVEDROM
        else:
            npyscreen.notify_confirm(
                "Unknown Error.. {}".format(self.wdgtRomFilterMode.value))
            return

        if self.filter_mode == ExtractFilter.FILTER_MODE_ROM:
            self.filter_RomNames = self.wdgtRomFilterSelectedRomList.values
        else:
            self.filter_RomNames = []

        if self.filter_mode == ExtractFilter.FILTER_MODE_ARCHIVEDROM:
            self.filter_Archives = self.wdgtRomFilterSelectedArchiveList.values
        else:
            self.filter_Archives = []

        self.filter_RomCodeList = [RomCode().CodeKeyList()[x]
                                   for x in self.wdgtRomCodeSelect.value]
        self.filter_ExRomCodeList = [RomCode().CodeKeyList()[x]
                                     for x in self.wdgtExRomCodeSelect.value]
        self.filter_LangCodeList = LangCode().CodeListFromName(
            [self.wdgtLangCodeSelect.values[x] for x in self.wdgtLangCodeSelect.value])
        self.filter_ExLangCodeList = LangCode().CodeListFromName(
            [self.wdgtExLangCodeSelect.values[x] for x in self.wdgtExLangCodeSelect.value])

        self.filter_flags = ExtractFilter.FILTER_FLAG_LISTUP_ONLY
        if 0 in self.wdgtOtherOption.value:
            self.filter_flags |= ExtractFilter.FILTER_FLAG_LANG_PRIORITY
        if 1 in self.wdgtOtherOption.value:
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
        self.wdgtRomPath = self.add(
            TitleFileNameComboRomSet, max_width=68, begin_entry_at=9)
        self.wdgtScanButton = self.add(
            ButtonPressRomScan, name="Scan")
        self.wdgtBoxProgress = self.add(
            BoxProgress, max_height=3, relx=70, rely=1, editable=False)

        self.wdgtDestPath = self.add(
            npyscreen.TitleFilenameCombo, name="OutputPath", rely=5)
        self.wdgtRomFilterMode = self.add(RomFilterMode, rely=6, max_width=41, max_height=6, value=0,
                                          values=["All Roms", "Selected Roms", "Selected Archives"])

        self.wdgtRomFilterRomSearchButton = self.add(
            RomFilterRomSearchButton, rely=6, relx=42, hidden=True, name="Search")
        self.wdgtRomFilterRomClearButton = self.add(
            RomFilterRomClearButton, rely=7, relx=42, hidden=True, name="Clear")
        self.wdgtRomFilterSelectedRomList = self.add(npyscreen.MultiLineEditableBoxed,
                                                     rely=6, relx=58, max_height=7, hidden=True, name="Selected Roms")
        self.wdgtRomFilterArchiveSearchButton = self.add(
            RomFilterArchiveSearchButton, rely=6, relx=42, hidden=True, name="Search")
        self.wdgtRomFilterArchiveClearButton = self.add(
            RomFilterArchiveClearButton, rely=7, relx=42, hidden=True, name="Clear")
        self.wdgtRomFilterSelectedArchiveList = self.add(npyscreen.MultiLineEditableBoxed,
                                                         rely=6, relx=58, max_height=7, hidden=True, name="Selected Archives")

        self.wdgtRomCodeSelect = self.add(npyscreen.TitleMultiSelect, name="Rom code",
                                          values=RomCode().CodeNameList(), value=[0], rely=14, max_width=50, max_height=7)
        self.wdgtExRomCodeSelect = self.add(npyscreen.TitleMultiSelect, name="Exclusion",
                                            values=RomCode().CodeNameList(), rely=14, relx=52, max_height=7)
        self.wdgtLangCodeSelect = self.add(
            LangCodeSelect, values=LangCode().CodeNameList(), rely=22, max_width=50, max_height=8)
        self.wdgtExLangCodeSelect = self.add(
            ExLangCodeSelect, values=LangCode().CodeNameList(), rely=22, relx=52, max_width=50, max_height=8)
        self.wdgtOtherOption = self.add(OtherOptionSelect, rely=31)


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

    def onStart(self):
        self.main_form = self.addForm(
            "MAIN", FormMainMenu, name="ExtROM")
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
