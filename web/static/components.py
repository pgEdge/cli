import sqlite3, sys, oscg

grp_cat = ""
web_page = ""

NUM_COLS = 3

PG_NUM_COLS = 10

ALL_PLATFORMS = "arm, amd"
isSHOW_COMP_PLAT = "Y"
isEXTRA_SPACING = "N"
isSHOW_DESCRIPTION = "Y"
HEADING_SIZE = "+1"

FONT_SIZE = 3
IMG_SIZE = 30
BORDER=0

# condensed format
if NUM_COLS == 1:
  BR = "&nbsp;"
  FONT_SIZE = 4
  COLS_SIZE = 600
  IMG_SIZE = 35
  BORDER=1

# logo's for slide decks
if NUM_COLS == 2:
  COLS_SIZE = 600
  isSHOW_COMP_PLAT = "N"
  isEXTRA_SPACING = "Y"
  IMG_SIZE = 65
  FONT_SIZE = 6
  HEADING_SIZE = "+3"

rh=0


def print_top():
  oscg.print_file(
"""

<!--------------- component print_top() --------------->
<div class=row>
"""
)
  return

 
def print_bottom(pOptFile=""):
  oscg.print_file(
"""

<!------------- component print_bottom() -------------->
</div>
"""
, pOptFile)
  oscg.print_footer(pOptFile)
  return


def get_columns(d):
  global grp_sort, cat_sort, rel_sort, grp, grp_short_desc 
  global grp_cat, web_page, page_title, grp_cat_desc
  global image_file, component, project, stage, rel_name
  global version, source_url, project_url, platform, rel_date
  global rel_month, rel_day, rel_yy 
  global proj_desc, rel_desc, pre_reqs, license
  global version, rel_notes

  grp_sort = str(d[0])
  cat_sort = str(d[1])
  rel_sort = str(d[2])
  grp = str(d[3])
  grp_short_desc = str(d[4])

  grp_cat = str(d[5])
  web_page = str(d[6])
  page_title = str(d[7])
  grp_cat_desc = str(d[8])

  image_file = str(d[9])
  component = str(d[10])
  project = str(d[11])
  stage = str(d[12])
  rel_name = str(d[13])

  version = str(d[14])
  source_url = str(d[15])
  project_url = str(d[16])
  platform = str(d[17])
  rel_date = str(d[18])

  proj_desc = str(d[19])
  rel_desc = str(d[20])
  pre_reqs = str(d[21])
  license = str(d[22])

  rel_notes = str(d[23])
  depends = str(d[24])

  version = version.replace("-1", "")

  pre_reqs = pre_reqs.lower()
  pre_reqs = pre_reqs.replace('amd', 'linux')
  pre_reqs = pre_reqs.replace('openjdk', 'jdk')
  platform = platform.replace('amd', 'linux')
  if platform > "":
    platform = "[" + platform + "]"

  rel_yy = rel_date[2:4]
  rel_month = rel_date[4:6]
  if rel_month == "01":
     rel_month = "Jan"
  elif rel_month == "02":
     rel_month = "Feb"
  elif rel_month == "03":
     rel_month = "Mar"
  elif rel_month == "04":
     rel_month = "Apr"
  elif rel_month == "05":
     rel_month = "May"
  elif rel_month == "06":
     rel_month = "Jun"
  elif rel_month == "07":
     rel_month = "Jul"
  elif rel_month == "08":
     rel_month = "Aug"
  elif rel_month == "09":
     rel_month = "Sep"
  elif rel_month == "10":
     rel_month = "Oct"
  elif rel_month == "11":
     rel_month = "Nov"
  elif rel_month == "12":
     rel_month = "Dec"

  rel_day = rel_date[6:]
  if rel_day[0:1] == "0":
    rel_day = rel_day[1]

  return


def print_card():
  global proj_desc, rel_desc, component, rel_name, source_url
  global image_file, rel_date, version, platform

  oscg.print_file("\n <!---------------------- print_card()  ------------------------->")

  platd = ""
  if isSHOW_COMP_PLAT == "Y":
    platd = component + " " + platform + " " + stage

  if str(rel_yy) < "22":
    rel_yy_display = "-" + rel_yy
  else:
    rel_yy_display = ""
    
  if rel_date in ('', '19700101'):
    rel_date_display = ""
  else:
    rel_date_display = rel_day + "-" + rel_month + rel_yy_display

  if isSHOW_DESCRIPTION == "N" or component[0:3] in ("pg9", "pg1"):
    proj_desc = ""

  if rel_desc > '':
    proj_desc = rel_desc

  plat_desc = "<i>" + proj_desc + "</i>"

  oscg.print_file(
"""
 <div class='card mb-3 m-2' style='min-width: 325px; max-width: 325px;'>
  <div class='row g-0'>
    <div class='col-md-2'>
"""
)

  oscg.print_file("       <br><br><img src=img/" + image_file + " height=45 width=45 />&nbsp;")

  oscg.print_file(
"""
    </div>
    <div class=col-md-10>
      <div class=card-body>
"""
)

  string = \
    "        <h5 class=card-title>" + rel_name  + "</h5> \n" + \
    "        <p class=card-text>" + plat_desc + "</p> \n" + \
    "        <p class=card-text><font size=-1>" + component + "&nbsp; \n" + \
    "          <a href='" + source_url + "'>v" + version + "</a></font> \n" + \
    "          <font size=-2> \n" + \
    "            <sup><font color=red>" + rel_date_display + "</font></sup> \n" + \
    "          </font> \n" + \
    "        </p> \n" + \
    "        <p class=card-text>" + platform + "</p>"
  oscg.print_file(string)

  oscg.print_file(
"""
      </div>                                                                       
    </div>                                                                         
  </div>
 </div>
"""
)

  return


##################################################################
#   MAINLINE
##################################################################
con = sqlite3.connect("local.db")
c = con.cursor()

sql = \
"""
 SELECT grp_sort, cat_sort, rel_sort, grp, grp_short_desc, grp_cat,
        web_page, page_title, grp_cat_desc,
        image_file, component, project, stage, rel_name,
        version, sources_url, project_url, platform, rel_date,
        proj_desc, rel_desc, pre_reqs, license, depends, rel_notes
   FROM v_versions
  WHERE is_current = 1 and component <> 'hub'
ORDER BY grp_sort, cat_sort, rel_sort
"""

c.execute(sql)
data = c.fetchall()

old_grp_cat = ""
old_web_page = ""
oscg.COMPONENT = "yes"
i = 0
for d in data:
  i = i + 1

  get_columns(d)

  oscg.PFILE = web_page 
  oscg.PAGE_TITLE = page_title
  oscg.PAGE_DESC = grp_cat_desc 

  if i == 1:
    print("  page = " + web_page)
    oscg.print_header()
    print_top()
  elif old_grp_cat != grp_cat:
    print_bottom(old_web_page)
    print("  page = " + web_page)
    oscg.print_header()
    print_top()

  print_card()

  old_grp_cat = grp_cat
  old_web_page = web_page 

if i > 0:
  print_bottom(old_web_page)

sys.exit(0)


