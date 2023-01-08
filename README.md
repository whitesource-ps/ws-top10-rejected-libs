[![Logo](https://resources.mend.io/mend-sig/logo/mend-dark-logo-horizontal.png)](https://www.mend.io/)  

[![License](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI](https://github.com/whitesource-ps/ws-top10-rejected-libs/actions/workflows/ci.yml/badge.svg)](https://github.com/whitesource-ps/ws-top10-rejected-libs/actions/workflows/ci.yml)
[![Python 3.6](https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Blue_Python_3.6%2B_Shield_Badge.svg/86px-Blue_Python_3.6%2B_Shield_Badge.svg.png)](https://www.python.org/downloads/release/python-360/)
[![GitHub release](https://img.shields.io/github/v/release/whitesource-ps/ws-top10-rejected-libs)](https://github.com/whitesource-ps/ws-top10-rejected-libs/releases/latest)  
[![PyPI](https://img.shields.io/pypi/v/ws-top10-rejected?style=plastic)](https://pypi.org/project/ws-top10-rejected-libs/)  

# [WhiteSource Top 10 Rejected Libraries](https://github.com/whitesource-ps/ws-top10-rejected-libs)
Generate a spreadsheet listing the 10 most common libraries in your WhiteSource inventory that were rejected by policies.

## Supported Operating Systems
- **Linux (Bash):**	CentOS, Debian, Ubuntu, RedHat
- **Windows (PowerShell):**	10, 2012, 2016

## Prerequisites
Python 3.6+

## Installation
1. Clone the **ws-top10-rejected-libs** repository to your environment:  
    `git clone https://github.com/whitesource-ft/ws-top10-rejected-libs.git`  
2. Navigate into the created directory and install the required dependencies:  
    `cd ./ws-top10-rejected-libs`  
    `pip install -r requirements.txt`  
3. Navigate into the main application directory:  
    `cd ./ws_top10_rejected_libs`  
4. Execute the application following the instructions below.  
   The first execution will require a one time configuration, prompting for the following parameters, which will be saved into an automatically-generated local `top10_rejected.py.config` file:  
   - **Organization Name** - your WhiteSource organization name
   - **API Key** - your WhiteSource API Key (organization token)
   - **User Key** - a WhiteSource User Key with admin permissions (this could be either an individual user or a service user)
   - **Domain** - the domain prefix of your WhiteSource Server Url (e.g. `saas`, `saas-eu`, `app`, `app-eu`)
   - **Company Name** - the display name to be used for the generated spreadsheet (defaults to the organization name, if not provided)
   - **Default Period** - the default period in months to generate the spreadsheet for (defaults to 3) 
   - **Use Header Image** - whether the spreadsheet should include a header image
   - **Start Date** - start date for the reported period in `yyyy-MM-dd` format (this parameter is not part of the one time configuration, it's part of the execution itself, and will only be prompted if not provided as a command-line argument as detailed below)  

## Execution
Show help and usage menu:  
`python top10_rejected.py --help`  

Interactive execution (mandatory parameters will be prompted for input):  
`python top10_rejected.py`  

Unattended execution (specifying command-line arguments):  
`python top10_rejected.py --argument "value"`  
`python top10_rejected.py -arg "value"`    

Example:  
`python top10_rejected.py --start "2021-02-27"`  

### Command-Line Arguments
The following command line arguments can be specified to override configuration set by the local `top10_rejected.py.config` file.  
The parameters marked as **Required** are typically saved to the config file during the first execution and thus are not required for every execution, unless the config file is not present.  

| Parameter | Type | Required | Description |
| :--- | :---: | :---: | :--- |
| **&#x2011;h,&nbsp;&#x2011;&#x2011;help** | switch | No | Show help and usage menu |
| **&#x2011;s,&nbsp;&#x2011;&#x2011;start** | string | Yes | Start date in format `yyyy-MM-dd`. Default: config file option `DefaultPeriodMonths`. |
| **&#x2011;e,&nbsp;&#x2011;&#x2011;end** | string | No | End date in format `yyyy-MM-dd`. Default: current date. |
| **&#x2011;o,&nbsp;&#x2011;&#x2011;organization** | string | Yes | WhiteSource Organization Name |
| **&#x2011;c,&nbsp;&#x2011;&#x2011;company** | string | No | Company name. If not provided, WhiteSource Organization name will be used. |
| **&#x2011;d,&nbsp;&#x2011;&#x2011;domain** | string | Yes | WhiteSource server domain prefix: `https://DOMAIN.whitesourcesoftware.com` (e.g: `saas`). |
| **&#x2011;apiKey** | string | Yes | WhiteSource API Key (Organization Token). |
| **&#x2011;userKey** | string | Yes | A WhiteSource User Key with admin permissions (this could be either an individual user or a service user). |