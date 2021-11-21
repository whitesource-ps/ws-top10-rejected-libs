from argparse import ArgumentParser, REMAINDER, SUPPRESS, RawTextHelpFormatter
import base64
import configparser
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from collections import Counter
import getopt
import imghdr
import inspect
import json
import logging
import math
import os
import re
import requests
import rsa
import shutil
import struct
import subprocess
import sys
from typing import Dict
import xlsxwriter

logging.basicConfig(level=logging.DEBUG if os.environ.get("DEBUG") else logging.INFO,
                    handlers=[logging.StreamHandler(stream=sys.stdout)],
                    format='%(levelname)s %(asctime)s %(thread)d %(name)s: %(message)s',
                    datefmt='%y-%m-%d %H:%M:%S')

today = datetime.today()
default_period_months = 3
prompt_date = True

title = "Top 10 Rejected Libraries"
cfg_file = "{}.config".format(__file__)
agent_info = 'agentInfo'
AGENT_NAME = 'top10-rejected-libs'
AGENT_VERSION = '1.0.0'
agent_info_details = {'agent': AGENT_NAME, 'agentVersion': AGENT_VERSION}

# cfg var names
SEC_WS = 'WhiteSource'
SEC_ST = 'Settings'
ORG_NAME = 'OrganizationName'
ORG_TOKEN = 'ApiKey'
ORG_ENV = 'Domain'
USER_KEY = 'UserKey'
COMP_NAME = 'CompanyName'
DFLT_PRD = 'DefaultPeriodMonths'
HDR_IMG = 'IncludeHeaderImage'

argparser = ArgumentParser(prog="ws-top-10-rejected-libs",
                           description="Generate a spreadsheet listing the 10 most commonly used libraries "
                                       "that violate organizational policies",
                           epilog="WhiteSource Field Toolkit\nhttps://github.com/whitesource-ft\n",
                           formatter_class=RawTextHelpFormatter)
argparser.add_argument("-s", "--start", dest="start_date", default="", metavar="",
                       help="Start date in format yyyy-MM-dd. Default: config file option '{}'.".format(DFLT_PRD))
argparser.add_argument("-e", "--end", dest="end_date", default="", metavar="",
                       help="End date in format yyyy-MM-dd. Default: 'Today()'.")
argparser.add_argument("-o", "--organization", dest="org_name", default="", metavar="",
                       help="WhiteSource Organization Name")
argparser.add_argument("-c", "--company", dest="company_name", default="", metavar="",
                       help="Company name. If not provided, WhiteSource Organization name will be used.")
argparser.add_argument("-d", "--domain", dest="org_env", default="", metavar="",
                       help="WhiteSource server domain prefix: 'https://DOMAIN.whitesourcesoftware.com' (e.g: 'saas')")
argparser.add_argument("-apiKey", dest="api_key", default="", metavar="",
                       help="WhiteSource API Key (Organization Token)")
argparser.add_argument("-userKey", dest="user_key", default="", metavar="",
                       help="WhiteSource User Key")
argparser.add_argument("-debug", "--debug", dest="debug", action='store_true', help=SUPPRESS)
argparser.set_defaults(debug=False)
args = argparser.parse_args()
# argparser.add_argument('args', nargs=REMAINDER)
# args, unknown = argparser.parse_known_args()

start_date = args.start_date
end_date = args.end_date
debug = args.debug

s_args = sys.argv

use_date_picker = False
# ToDo - complete date picker implementation
if use_date_picker:
    import tkinter as tk
    from tkcalendar import DateEntry

# spreadsheet settings
# vba_org = False
# ToDo - Add title_headers for VBA orgs if vba_org = True
# title_headers = ["Creation Time", "Level", "Type", "Library", "Description", "Details", "Product", "Project",
#                  "Impact Analysis Status", "Impact Analysis Results", "Library Type"]
title_headers = ["Name", "Type", "Group", "Artifact", "Version", "Occurrences"]

default_include_header_image = True
limit_image_height = 30  # Limit the header image row height. 0 will retain the original image height
header_image_file = "header_image.png"
default_image_b64 = "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"


def s_line():
    return "{0}:{1}".format(os.path.basename(__file__), str(inspect.currentframe().f_back.f_lineno))


def fnm():
    # Return the name of the calling function
    return inspect.stack()[1][3]


def pnm():
    # Return the name of the calling function's parent
    try:
        return inspect.stack()[2][3]
    except Exception as e:
        return 'np'


def set_config():
    c = configparser.ConfigParser()
    c.optionxform = str
    if os.path.isfile(cfg_file):
        c.read(cfg_file)
    if not c.has_section(SEC_WS):
        c.add_section(SEC_WS)
    if not c.has_section(SEC_ST):
        c.add_section(SEC_ST)
    c_ws = c[SEC_WS]
    c_st = c[SEC_ST]
    c_ws[ORG_NAME] = input("Organization Name: ")
    c_ws[ORG_TOKEN] = input("API Key: ")
    c_ws[USER_KEY] = input("User Key: ")
    c_ws[ORG_ENV] = input("Domain: ")
    comp_name = input("Company Name ({}): ".format(c_ws[ORG_NAME]))
    c_st[COMP_NAME] = c_ws[ORG_NAME] if not comp_name else comp_name
    dflt_period = input("Default Period in months ({}): ".format(str(default_period_months)))
    c_st[DFLT_PRD] = str(default_period_months) if not dflt_period else str(dflt_period)
    c_st[HDR_IMG] = "True" if re.match('y|yes|true|1', input("Use Header Image (Y|N): "), re.IGNORECASE) else "False"
    with open(cfg_file, 'w+') as c_file:
        c.write(c_file, space_around_delimiters=False)


def get_config():
    if not os.path.isfile(cfg_file):
        set_config()
    config = configparser.ConfigParser()
    config.read(cfg_file)
    return config


def update_config(section, key, value):
    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    cfg.read(cfg_file)
    cfg.set(section, key, value)
    with open(cfg_file, 'w+') as c_file:
        cfg.write(c_file, space_around_delimiters=False)
    return cfg


def get_image_type(img_file):
    if os.path.isfile(img_file):
        return imghdr.what(img_file)
    return ""


def get_image_res(img_file):
    if os.path.isfile(img_file):
        with open(img_file, 'rb') as f:
            data = f.read()
            img_type = get_image_type(img_file)
            if img_type == "png":
                fw, fh = struct.unpack('>LL', data[16:24])
                width = int(fw)
                height = int(fh)
                return width, height
            elif img_type == "bmp":
                pass
            elif img_type == "jpeg":
                pass
            else:
                raise ValueError('Image type is unsupported')
        return 0, 0


def validate_date(dt: str) -> str:
    try:
        darr = dt.split('-')
        dt_valid = date(year=int(darr[0]), month=int(darr[1]), day=int(darr[2]))
        return ""
    except ValueError as invalid_date_err:
        return str(invalid_date_err)


def date_picker():
    # ret_date = None
    def get_selected_date(event):
        w = event.widget
        w_date = w.get_date()
        # print('Selected Date:{}'.format(w_date))
        widget.destroy()
        return w_date

    widget = tk.Tk(screenName="Date Picker", baseName="DatePicker", className="Select Date")
    widget.title("Select Date")
    picker = DateEntry(widget, year=today.year, month=today.month, day=today.day, borderwidth=1, width=35, height=20)
    picker.bind("<<DateEntrySelected>>", get_selected_date)
    picker.pack(padx=10, pady=10)
    widget.mainloop()
    ret_date = picker.get_date()
    if ret_date:
        return str(ret_date)
    return ""


def api_request(payload: Dict[str, str]):
    r = requests.post(ws_api_url, json=payload)
    r_json = json.loads(r.text)
    try:
        if r_json['errorCode']:
            if debug:
                print('[{}] [{}] Error {}: {}'.format(s_line(), fnm(), r_json['errorCode'], r_json['errorMessage']))
            else:
                print('Error {}: {}'.format(r_json['errorCode'], r_json['errorMessage']))
            exit(int(r_json['errorCode']))
    except KeyError:
        pass
    return r_json


try:
    cfg = get_config()
    cfg_ws = cfg[SEC_WS]
    cfg_st = cfg[SEC_ST]
    if not cfg_ws[ORG_NAME]:
        cfg_ws[ORG_NAME] = input("Organization Name: ")
        cfg = update_config(SEC_WS, ORG_NAME, cfg_ws[ORG_NAME])
    if not cfg_ws[ORG_ENV]:
        cfg_ws[ORG_ENV] = input("Domain: ")
        cfg = update_config(SEC_WS, ORG_ENV, cfg_ws[ORG_ENV])
    if not cfg_ws[ORG_TOKEN]:
        cfg_ws[ORG_TOKEN] = input("API Key: ")
        cfg = update_config(SEC_WS, ORG_TOKEN, cfg_ws[ORG_TOKEN])
    if not cfg_ws[USER_KEY]:
        cfg_ws[USER_KEY] = input("User Key: ")
        cfg = update_config(SEC_WS, USER_KEY, cfg_ws[USER_KEY])
    if not cfg_st[COMP_NAME]:
        cfg_st[COMP_NAME] = cfg_ws[ORG_NAME]
        cfg = update_config(SEC_ST, COMP_NAME, cfg_st[COMP_NAME])
    if not cfg_st[DFLT_PRD]:
        cfg_st[DFLT_PRD] = str(default_period_months)
    if not end_date:
        end_date = today.strftime('%Y-%m-%d')
    if not start_date:
        if prompt_date:
            if use_date_picker:
                start_date = date_picker()
            else:
                start_date = input("Start Date (yyyy-MM-dd): ")
        else:
            dt_end = datetime.strptime(end_date, '%Y-%m-%d')
            dt_start = dt_end - relativedelta(months=int(cfg_st[DFLT_PRD]))
            start_date = dt_start.strftime('%Y-%m-%d')

    # Validate start and end dates
    sdate_validation = validate_date(start_date)
    if sdate_validation:
        err_txt = 'Invalid Start Date: {}'.format(sdate_validation)
        if debug:
            err_txt = '[{}] [{}] {}'.format(s_line(), fnm(), err_txt)
        print(err_txt)
        exit(1)
    edate_validation = validate_date(end_date)
    if edate_validation:
        err_txt = 'Invalid End Date: {}'.format(edate_validation)
        if debug:
            err_txt = '[{}] [{}] {}'.format(s_line(), fnm(), err_txt)
        print(err_txt)
        exit(1)

    print("")
    ws_url = "https://{0}.whitesourcesoftware.com".format(cfg_ws[ORG_ENV])
    ws_api_url = "{0}/api/v1.3".format(ws_url)
    ws_lib_url = "{0}/Wss/WSS.html#!libraryDetails;uuid=".format(ws_url)
    output_title = "{} - {}".format(cfg_st[COMP_NAME], title)
    if start_date and end_date:
        output_title = "{} - {}-{}".format(output_title, start_date, end_date)

    cwd = os.getcwd()
    files_dir = os.path.join(cwd, "files")
    if os.path.isdir(files_dir):
        shutil.rmtree(files_dir)
    spreadsheet_filename = "{}.xlsx".format(output_title)
    spreadsheet_file = os.path.join(files_dir, spreadsheet_filename)
    sheet_name = title

    # Get all Policy Violation Alerts
    payload_alerts = {
        agent_info: agent_info_details,
        "requestType": "getOrganizationAlertsByType",
        "userKey": cfg_ws[USER_KEY],
        "orgToken": cfg_ws[ORG_TOKEN],
        "alertType": "REJECTED_BY_POLICY_RESOURCE",
        "fromDate": start_date,
        "toDate": end_date
    }
    res_alerts = api_request(payload_alerts)
    alerts = res_alerts["alerts"]
    alerts_count = len(alerts)

    # Get list of unique GAVs
    lib_gavs = []
    for a in range(alerts_count):
        alt = alerts[a]["library"]
        try:
            alt_g = alt["groupId"]
        except KeyError:
            alt_g = ""
        try:
            alt_a = alt["artifactId"]  # ["name"]
        except KeyError:
            alt_a = ""
        try:
            alt_v = alt["version"]
        except KeyError:
            alt_v = ""
        try:
            lib_n = alt["filename"]
        except KeyError:
            lib_n = ""
        try:
            lib_t = alt["type"]
        except KeyError:
            lib_t = ""
        try:
            lib_u = alt["keyUuid"]
        except KeyError:
            lib_u = ""
        # gav = "{}|{}|{}".format(alt_g, alt_a, alt_v)
        gav = "{}|{}|{}|{}|{}|{}".format(lib_n, lib_u, lib_t, alt_g, alt_a, alt_v)
        lib_gavs.append(gav)
    lib_gavs_count = len(lib_gavs)

    # Find the number of occurrences of each GAV
    lib_occs = Counter(lib_gavs)
    # Get the top 10 from the list
    most_common = lib_occs.most_common(10)

    # Create a spreadsheet
    print("Generating spreadsheet: {}".format(spreadsheet_filename))
    os.mkdir(files_dir)
    workbook = xlsxwriter.Workbook(spreadsheet_file)
    sheet = workbook.add_worksheet(sheet_name)

    format_header = workbook.add_format({'bold': True})
    format_align_right = workbook.add_format({'align': 'right'})
    format_url = workbook.get_default_url_format()
    # format_novuln = workbook.add_format({'color': '#969696'})
    sheet.activate()

    # Insert image
    header_row = 0
    if cfg_st[HDR_IMG]:
        if os.path.isfile(header_image_file):
            if get_image_type(header_image_file) not in ["bmp", "jpeg", "png"]:
                print("Specified header image type is unsupported")
                include_header_image = False
        else:
            with open(header_image_file, "wb") as img:
                image_b64 = default_image_b64
                img.write(base64.decodebytes(image_b64.encode()))

    if cfg_st[HDR_IMG]:
        try:
            img_w, img_h = get_image_res(header_image_file)
            header_row += 1
            img_scale = limit_image_height / img_h if limit_image_height > 0 else 1
            img_row_height = limit_image_height if limit_image_height > 0 else img_h
            sheet.insert_image(0, 0, header_image_file, {'object_position': 1, 'x_scale': img_scale, 'y_scale': img_scale})
            sheet.set_row(0, img_row_height)
            sheet.merge_range('A1:{}1'.format(chr(ord('@')+len(title_headers))), "")
        except ValueError as val_err:
            if debug:
                print('[{}] [{}] Error: {}'.format(s_line(), fnm(), val_err))
            else:
                print('Error: {}'.format(val_err))
            include_header_image = False

    max_col_widths = []
    # Populate headers
    for h in range(len(title_headers)):
        sheet.write(header_row, h, title_headers[h], format_header)
        col_width = len(title_headers[h])
        max_col_widths.append(col_width)

    # Populate table
    for t in range(len(title_headers)):
        col_width = len(title_headers[t])

    row = header_row + 1
    for i, item in enumerate(most_common):
        name, uuid, type, grp, art, ver = item[0].split('|')
        occ = item[1]
        lib_url = ws_lib_url + uuid
        lib = [name, type, grp, art, ver, occ]
        for m in range(len(title_headers)):
            if m == 0:
                sheet.write_url(row, m, lib_url, string=name)
            else:
                sheet.write(row, m, lib[m])
            max_col_widths[m] = max(len(str(lib[m])), max_col_widths[m])
        row += 1

    for c in range(len(max_col_widths)):
        sheet.set_column(c, c, max_col_widths[c])

    sheet.freeze_panes(header_row + 1, 0)  # Freeze first row
    workbook.close()

    if cfg_st[HDR_IMG] and os.path.isfile(header_image_file):
        os.remove(header_image_file)

    print("Done")
except KeyboardInterrupt:
    sys.exit(0)
