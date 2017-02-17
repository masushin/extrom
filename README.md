# extrom

ROM Extraction tool from archived ROM set file.

## Description

extrom is tool which can extract any roms that matched to specified condition from romset archive file.

***DEMO:***

The following demo shows the step to extract good dump roms of "Thunder Force" series for Japanese ver.



## Features

Filtering rom according to the following conditions.
+ Archive file name or Rom (Game) name.
+ GoodTools standard code.
+ GoodTools country code.

## Requirement

p7zip is needed to extract 7z archive.

## Usage

Executes the following command.
```bash
 extrom
```

### Steps for extracting roms
First, select "RomSetFile", and Press enter. File select dialog will appear. Please select "Romset file". "Romset file" must be struct like the following. Otherwise it make error.
  If specified file has no problem, scanning will start. It may need long time in the case of many rom is included.

After scanning is done, progress dialog will close. Select "OutputPath", Press Enter and selects directory where you want to extract Roms to.

#### RomFilterMode
Select "RomFilterMode". Please select mode you want.
+ All Roms : Filters to all roms which is included in specified Romset.
+ Selected Roms : Filters by selected rom (game) name.
+ Selected Archives : Filters by selected archive file.

If you selects "Selected Roms" or "Selected Archives", 3 buttons will appear on right side.
+ "Select" button
Rom/Archives select dialog will appear.
Press Up or Down key to move cursor.
Press Space bar or Enter key to select or unselect.
List of rom files which is included item on current cursor position will appear by pressing "i" key.
It is useful in case of confirming whether a rom which is you want is include in the archive or romname item.

If you want to search by rom/archives name, press "l" Key.
Search dialog will appear. Input keyword for search and Press Enter key.
Items which is match with the keyword will highlighted by green color.
If you want move cursor to next or previous matched item, Press "n" or "p" key.
(Incidentally, this feature is implemented by npyscreen library.)

##### "Clear" button
Clears current selected items.

##### "List" button
Shows the list of selected items.

#### Goodtools code filter
Configuration of filter for GoodTools standard code.

Standard code select dialog will appear by pressing "Standard code" button.
Please enable any code you want to extract.
For example, if you want to extract only good dump roms, enable "[!] Good dump".

"Exclusion Standard code" button is for selecting code you doesn't want to extract.
For example, If you doesn't want to extract hacked roms, enable "[h] Hacked ROM".

"Country code" and "Exclusion Country code" are similar to the above.
If you want US version roms, enable "United States" in "Country code".
If you doesn't want unlicensed roms, "Unlicensed" in "Exclusion Country code".

In addition, For "Country code" select dialog, Priority can be specified.
Upper item mean higher priority.
To increase priority of a country code on cursor position, Press "u" key.
To decrease, Press "d" key.
Priority has no mean if option "Extracts roms according to priority of country code" (described below) is disabled.

#### Other Configuration
Configuration dialog will appear by pressing "Config" button.

##### "Not extracts rom which has low priority LANG code"
If this config is enabled, only rom which has highest priority country code in selected codes will be extracted.
For example, select "Japanese" and "United states" and set higher priority to "United states".
If a rom archive includes both Japanese ver and US ver, only US ver rom will be extracted. If not includes US ver, Japanese ver (If it be included) will be extracted.
It is useful for the case of that you want extract all roms from rom set file but not want to extract roms which differ by only country code.

##### "Extracts with Zip archiving."
Outputs Roms as zip file.


## Installation

pip install extrom


## Anything Else

## License
