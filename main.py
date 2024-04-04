import sys, os, re, blend_modes, recordlinkage, openpyxl, pathlib
import pandas as pd
import numpy as np
from PIL import Image, ImageMath, ImageChops, ImageEnhance, ImageFilter
from fuzzywuzzy import fuzz

##### TODO
# get the emboss > curvature > cavity shit done for better results
#
#
#

#rules



input_textures = []

input_arm = []
input_diff = []
input_cavity = []


glock_dir = r"R:\00_Main\Weapons\Pistols\Glock" # glock for testing purposes
gadgets_dir = r"R:\00_Main\Gadgets"
weapons_dir = r"R:\00_Main\Weapons"
test_dir =  r"N:\IGS\aut\cavity\test_dir"


########################################################################################################
########################################################################################################


##########################
# defs for image manipulation
def get_diffs(input):
    diff_count = int()
    for element in input:
        if element.endswith("_DIFF.tga"):
            diff_count += 1
    return diff_count

def mult_cavity_diff(diff, cavity, path):
    # brighten the diff and cavity and multiply them together
    #get filename

    backslash = '\\'
    base_filename = os.path.basename(path)
    title, ext = os.path.splitext(base_filename)
    dir_name = os.path.dirname(path)
    final_filepath = os.path.join(dir_name + backslash + title + ext)

    cavity_enahncer = ImageEnhance.Brightness(cavity)
    bright_cavity = cavity_enahncer.enhance(1.75)
    bright_cavity.save("temp_cavity.tga")

    diff_enahncer = ImageEnhance.Brightness(diff)
    bright_diff = diff_enahncer.enhance(1.1)
    bright_diff.save("temp_diff.tga")

    new_diff = ImageChops.multiply(bright_diff, bright_cavity)

    new_diff.save(final_filepath)
    print(final_filepath)
    #new_diff.show()
    return 0

def mult_cavity_arm(arm, cavity, path):
    #split the arm and cavity into their respective channels and multiply the cavity into the green roughness channel

    backslash = '\\'
    base_filename = os.path.basename(path)
    title, ext = os.path.splitext(base_filename)
    dir_name = os.path.dirname(path)
    final_filepath = os.path.join(dir_name + backslash + title + ext)

    cavity_enahncer = ImageEnhance.Brightness(cavity)
    bright_cavity = cavity_enahncer.enhance(1.75)
    bright_cavity.save("temp_cavity.tga")

    arm_r, arm_g, arm_b = arm.split()
    cavity_r, cavity_g, cavity_b = cavity.split()

    arm_g_new = ImageChops.multiply(arm_g, cavity_g)
    new_arm = Image.merge('RGB', (arm_r, arm_g_new, arm_b))

    new_arm.save(final_filepath)
    print(final_filepath)
    #new_arm.show()
    return 0
#
##########################


########################################################################################################
########################################################################################################


##########################
# walk through the folders, listing the appropriate txs
for path, subdirs, files in os.walk(test_dir):
    for x in files:
        if x.endswith("ARM.tga") == True:
            input_arm.append(os.path.join(path, x))
        if x.endswith("DIFF.tga") == True:
            input_diff.append(os.path.join(path, x))
        if x.endswith("CAVITY.tga") == True:
            input_cavity.append(os.path.join(path, x))


#sort that shit into alphabetical order so the same stuff is next to each other
sorted(input_textures, key=str.lower)
sorted(input_arm, key=str.lower)
sorted(input_diff, key=str.lower)
sorted(input_cavity, key=str.lower)
##########################

diff_counter = get_diffs(input_diff)

##########################
# write the textures into indexable excrl files and easy visualization for outliers

df_diff = pd.DataFrame(input_diff)
df_diff.to_excel("diff.xls",  index=False, header=True)

df_arm = pd.DataFrame(input_arm)
df_arm.to_excel("arm.xls",  index=False, header=True)

df_cavity = pd.DataFrame(input_cavity)
df_cavity.to_excel("cavity.xls",  index=False, header=True)

[
##########################
# match the matching textures

# indexer = recordlinkage.Index()
# indexer.full()
#
# diff_list = pd.read_csv("diff.csv", usecols=['diff_names'])
# cavity_list = pd.read_csv("cavity.csv", usecols=['cavity_names'])
# arm_list = pd.read_csv("arm.csv", usecols=['arm_names'])
#
# candidates = indexer.index(diff_list, cavity_list)
#
# compare = recordlinkage.Compare()
# compare.string('diff_names', 'cavity_names',
#             method='levenshtein',
#             threshold=0.8,
#             label='matches')
#
# features = compare.compute(candidates, diff_list, cavity_list)
#
# features.sum(axis=1).value_counts().sort_index(ascending=False)
#
# potential_matches = features[features.sum(axis=1) > 1].reset_index()
# potential_matches['Score'] = potential_matches.loc[:, 'diff_names':'cavity_names'].sum(axis=1)
#
# df_diff_candidates = pd.DataFrame(features)
# df_diff_candidates.to_csv("matching_diffs.csv")
#
# print("These are the candidates: ")
# print(diff_list)
# print("Num of diffs: ")

##########################
]

##########################
# new fuzzy matching algo cause i suck

### gets the elements in the excel files into lists #

diff_xl = pd.read_excel("diff.xls", sheet_name="Sheet1")
diff_list = list(diff_xl[0])

cavity_xl = pd.read_excel(open("cavity.xls","rb"), sheet_name="Sheet1")
cavity_list = list(cavity_xl[0])

arm_xl = pd.read_excel(open("arm.xls","rb"), sheet_name="Sheet1")
arm_list = list(arm_xl[0])


tuples_list_diff = [max([(fuzz.token_set_ratio(i, j), j) for j in cavity_list]) for i in diff_list]
similarity_score, fuzzy_match = map(list,zip(*tuples_list_diff))

df_diff_list = pd.DataFrame({"diff_list": diff_list, "fuzzy_match": fuzzy_match, "similarity score": similarity_score})
df_diff_list.to_excel("diff_matches.xls", sheet_name="diff_cavity_matches", index=False)

###

tuples_list_arm = [max([(fuzz.token_set_ratio(i, j), j) for j in cavity_list]) for i in arm_list]
similarity_score, fuzzy_match = map(list,zip(*tuples_list_arm))

df_arm_list = pd.DataFrame({"arm_list": arm_list, "fuzzy_match": fuzzy_match, "similarity score": similarity_score})
df_arm_list.to_excel("arm_matches.xls", sheet_name="arm_cavity_matches", index=False)


#print(cavity_list)

#
##########################


##########################
# loops through the matched lists and throws the texture pairs into the image manipulation functions


diff_matches = pd.read_excel("diff_matches.xls", sheet_name="diff_cavity_matches", usecols=["diff_list","fuzzy_match"])
##
diff_matches_list = diff_matches["diff_list"].tolist()
diff_matches_list_cavity = diff_matches["fuzzy_match"].tolist()


arm_matches = pd.read_excel("arm_matches.xls", sheet_name="arm_cavity_matches", usecols=["arm_list","fuzzy_match"])
##
arm_matches_list = arm_matches["arm_list"].tolist()
arm_matches_list_cavity = arm_matches["fuzzy_match"].tolist()

##### loop for diff <> cavity matches
for i, j in zip(diff_matches_list, diff_matches_list_cavity):
    diff_path = i
    diff = Image.open(i)
    cavity = Image.open(j)
    mult_cavity_diff(diff, cavity, diff_path)

##### loop for arm <> cavity matches
for i, j in zip(arm_matches_list, arm_matches_list_cavity):
    arm_path = i
    arm = Image.open(i)
    cavity = Image.open(j)
    mult_cavity_arm(arm, cavity, arm_path)


### pillow debug
im1 = Image.open(r"N:\IGS\aut\cavity\test_dir\T_P90_CAVITY.tga")
im2 = Image.open(r"N:\IGS\aut\cavity\test_dir\T_P90_DIFF.tga")
im3 = Image.open(r"N:\IGS\aut\cavity\test_dir\T_P90_ARM.tga")

#mult_cavity_diff(im2,im1)

#mult_cavity_arm(im3,im1)

##################

####
# DEBUG
#print(diff_counter)
#print(skin_array_whole)
