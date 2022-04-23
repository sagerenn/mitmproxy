#!/usr/bin/env python3

import copy
import json
import os
import re
import sys
import typing

from mitmproxy import command
from mitmproxy import ctx
from mitmproxy import flow
from mitmproxy import http


body = {
    "checkRequired": False,
    "formState": "edit",
    "metaFields": [
        {
            "metaObjName": "Attendance.FillCheckRecord",
            "name": "PointExtendedField",
            "text": "",
            "value": "RECORDS"
        },
        {
            "metaObjName": "Attendance.FillCheckRecord",
            "name": "StaffId",
            "text": "",
            "value": ""
        }
    ],
    "viewName": "Attendance.SingleFillCheckStickingPointForm"
}

record = [
    {
      "label": "补签点",
      "name": "FillCheckPoint",
      "type": "BC_DateTime",
      "text": "2022/04/06 09:00",
      "value": "2022/04/06 09:00",
      "disabled": False,
      "required": True,
      "cmp_data": {
        "title": "补签点",
        "field_name": "FillCheckPoint",
        "dateTimeType": "dateTime",
        "isLink": False,
        "required": True,
        "data_format": "yyyy/MM/dd HH:mm",
        "isShowTime": True,
        "cmp_state": "edit",
        "cmp_status": "editable",
        "editdisplaystate": "editable",
        "createdisplaystate": "editable",
        "showdisplaystate": "readonly",
        "IsMobileSubjectShowName": False,
        "dataType": "StandradDateTime",
        "icon_name": "",
        "PackId": "f103d4b0-f503-4ed4-b186-bd73569aa7d6",
        "promptmessage": None,
        "refreshParams": None,
        "isShowDepartmentName": False,
        "defaultValueEffectiveScope": "createonly"
      },
      "fileList": [],
      "display": False
    },
    {
      "label": "补签事由",
      "name": "RetroactiveReason",
      "type": "BC_DropDownList",
      "text": "因疫情在家办公",
      "value": "7",
      "disabled": False,
      "required": True,
      "dsName": "2020072011434308135810274-1cce-4d27-8911-d507c1d38",
      "cmp_data": {
        "title": "补签事由",
        "field_name": "RetroactiveReason",
        "isLink": False,
        "required": True,
        "isCheckList": False,
        "cmp_state": "edit",
        "cmp_status": "editable",
        "editdisplaystate": "editable",
        "createdisplaystate": "editable",
        "showdisplaystate": "readonly",
        "datasourcename": "2020072011434308135810274-1cce-4d27-8911-d507c1d38",
        "IsMobileSubjectShowName": False,
        "dataType": "Text",
        "icon_name": "",
        "PackId": "b564baa3-2e6b-4fd7-848c-a2c18895372d",
        "promptmessage": None,
        "refreshParams": None,
        "isShowDepartmentName": False,
        "defaultValueEffectiveScope": "createonly"
      },
      "fileList": [],
      "display": False
    },
    {
      "label": "备注",
      "name": "Remark",
      "type": "BC_TextBox",
      "text": "上海疫情严重，居家办公",
      "value": "上海疫情严重，居家办公",
      "disabled": False,
      "required": False,
      "cmp_data": {
        "title": "备注",
        "field_name": "Remark",
        "isLink": False,
        "required": False,
        "cmp_state": "edit",
        "cmp_status": "editable",
        "editdisplaystate": "editable",
        "createdisplaystate": "editable",
        "showdisplaystate": "readonly",
        "IsMobileSubjectShowName": False,
        "dataType": "Text",
        "icon_name": "",
        "PackId": "e278263d-c19e-40e7-8669-90e4af06c39c",
        "promptmessage": None,
        "refreshParams": None,
        "isShowDepartmentName": False,
        "defaultValueEffectiveScope": "createonly"
      },
      "fileList": [],
      "display": False
    },
    {
      "label": "附件",
      "name": "extAttachments_111613_220176538",
      "type": "BC_FileUploader",
      "text": "",
      "value": "",
      "disabled": False,
      "required": False,
      "cmp_data": {
        "title": "附件",
        "field_name": "extAttachments_111613_220176538",
        "uploadCount": 9,
        "multiple": True,
        "required": False,
        "cmp_state": "edit",
        "cmp_status": "editable",
        "editdisplaystate": "editable",
        "createdisplaystate": "editable",
        "showdisplaystate": "readonly",
        "clientUrl": "",
        "downloadUrl": "",
        "fileName": "",
        "type": "file",
        "uploadUrl": "",
        "deleteUrl": "",
        "IsMobileSubjectShowName": False,
        "dataType": "Text",
        "icon_name": "",
        "PackId": "c331339a-34bf-4515-96be-6d96a1cb02a6",
        "promptmessage": None,
        "refreshParams": None,
        "isShowDepartmentName": False,
        "defaultValueEffectiveScope": "createonly"
      },
      "fileList": [],
      "display": False
    },
    {
      "label": "考勤记录ID",
      "name": "My_StatisticsId",
      "type": "string",
      "text": "28d972e4-5df5-4baa-9d6c-662bbf55246d",
      "value": "28d972e4-5df5-4baa-9d6c-662bbf55246d",
      "error": False,
      "disabled": False,
      "required": False
    },
    {
      "label": "班次ID",
      "name": "My_BatchWorkShiftId",
      "type": "string",
      "text": "",
      "value": "",
      "error": False,
      "disabled": False,
      "required": False
    },
    {
      "label": "卡点类型",
      "name": "My_PointType",
      "type": "string",
      "text": 1,
      "value": 1,
      "error": False,
      "disabled": False,
      "required": False
    },
]


class Employee:

    id = ""
    name = ""
    email = ""

    @classmethod
    def missedInfo(cls) -> bool:
        return cls.id == "" or cls.name == "" or cls.email == ""

class FillBody:

    sent = False
    records = []


    def request(self, flow: http.HTTPFlow):
        if flow:
            if flow.request.host == "cloud.italent.cn":
                if 'AddPunch/SingleAddPunch?&app=Attendance' in flow.request.url:
                    if not self.sent and len(self.records) > 0:
                        flow.request.text = json.dumps(body, ensure_ascii=False)
                        ctx.log.info(f"the request has beed sent")
                        self.sent = True
                    else:
                        ctx.log.info(f"{self.sent} len: {len(self.records)}")

    def response(self, flow: http.HTTPFlow):
        if flow:
            if flow.request.host == "cloud.italent.cn":
                if 'appCode=ITalentApp&pageCode=AbnormalAttendance' in flow.request.url:
                    vMap = {
                        1: "id",
                        2: "name",
                        3: "email",
                    }

                    regex = r'BSGlobal.loginUserInfo.*UserID[":]*(\d*).*UserName[":]*([^"]*).*Email[":]*([a-z0-9-@.]*).*'
                    matches = re.finditer(regex, flow.response.text, re.MULTILINE)


                    for matchNum, match in enumerate(matches, start=1):

                        for groupNum in range(0, len(match.groups())):
                            groupNum = groupNum + 1
                            setattr(Employee, vMap[groupNum], match.group(groupNum))
                    ctx.log.info(vars(Employee))
                    if Employee.missedInfo():
                        ctx.log.error("Error Miss Info")
                        sys.exit(1)
                    for i in body["metaFields"]:
                        if i["name"] == "StaffId":
                            i["text"] = f"{Employee.name}({Employee.email})"
                            i["value"] = f"{Employee.id}"

                elif 'MobileCalendar/ErrorAttendance' in flow.request.url:
                    b = flow.response.json()
                    tss = []
                    self.records = []
                    for i in b["data"]["DateDetailedEntityList"]:
                        for t in i["TimelineNodeList"]:
                            ts = f'{i["Day"].replace("-", "/")} {t["TargetTimePoint"].replace("18", "20")}'
                            tss.append(ts)
                            r = copy.deepcopy(record)
                            for item in r:
                                if item["name"] == "FillCheckPoint":
                                    item["text"] = ts
                                    item["value"] = ts
                            self.records.append(r)
                    for i in body["metaFields"]:
                        if i["name"] == "PointExtendedField":
                            ctx.log.info(f"the records {len(self.records)}")
                            i["value"] = json.dumps(self.records, ensure_ascii=False)
                            
                    ctx.log.info(tss)

addons = [
    FillBody()
]


if __name__ == '__main__':
    r = copy.deepcopy(record)
    for item in r:
        if item["name"] == "FillCheckPoint":
            item["text"] = "sdf"
            item["value"] = "sdfsdf"
    print(r)
