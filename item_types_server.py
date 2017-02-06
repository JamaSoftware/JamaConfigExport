import sys
import requests
import json
import cgi
import os

class Admin_report:

    project_blacklist = [
        "parent",
        "isFolder",
        "modifiedBy",
        "modifiedDate",
        "createdBy",
        "createdDate",
        "type",
        "fields",
        "itemtypes"
    ]

    item_type_blacklist = [
        "widgets",
        "fields",
        "image",
        "project_ids",
        "projects"
    ]

    picklist_blacklist = [
        "name",
        "item_types",
        "fields",
        "options"
    ]

    projects = {}
    item_types = {}
    picklists = {}
    big_string = ""
    requests.encoding = "utf8"

    def __init__(self, base_url, username, password, projects):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.authentication = (username, password)
        if projects == "all":
            self.project_list = "all"
        else:
            self.project_list = [p.strip() for p in projects.split(',')]

    def write_headers(self):
        self.big_string += "<html>\n<head>\n<body>"

    def write_footers(self):
        self.big_string += "</body>\n</head>\n</html>"

    def write_anchor(self, anchor):
        self.big_string += "<a name=\"{}\"></a>".format(anchor)

    def write_section_header(self, text, indentation, size):
        html = self.indent_and_size(indentation, size) + "<b><u>" + self.escape(text) + "</b></u></p>"
        self.big_string += unicode(format(html)) + "\n"

    def write_line_from_object(self, key, json, indent):
        line = self.stringify_field(key, json, indent)
        self.big_string += line + "\n"

    def write_plain_line(self, text, indentation):
        to_write = self.indent(indentation) + text + "</p>\n"
        self.big_string += unicode(format(to_write))

    def write_key_value_line(self, key, value, indentation):
        to_write = self.indent(indentation) + "<b>{}</b>: ".format(self.escape(key)) + self.escape(value)
        self.big_string += unicode(format(to_write))

    def indent(self, i):
        html = "<p style=\"margin-left: {}px\">"
        return html.format(i * 20)

    def indent_and_size(self, i, size):
        html = "<p style=\"margin-left:{0}px;font-size:{1}px\">"
        return html.format(i * 20, size)

    def stringify_field(self, key, json, indentation):
        temp = ""
        prefix = self.indent(indentation) + "<b>" + self.escape(key) + "</b>: "
        if key in json:
            temp += unicode(format(json[key]))
        temp = self.escape(temp)
        return prefix + temp + "</p>\n"

    def escape(self, value):
        return value.encode('ascii', 'xmlcharrefreplace')
            
    def get(self, url):
        response = requests.get(url, auth=self.authentication)
        return json.loads(response.text)["data"]

    def get_all(self, url):
        all_results = []
        remaining_results = -1
        start_index = 0

        while remaining_results != 0:
            start_at = "?startAt=" + str(start_index)
            this_url = url + start_at
            result = requests.get(this_url, auth=self.authentication)
            json_response = json.loads(result.text)
            page_info = json_response["meta"]["pageInfo"]
            remaining_results = page_info["totalResults"] - (page_info["startIndex"] + page_info["resultCount"])
            start_index += 20
            all_results.extend(json_response["data"])

        return all_results

    def add_to_dictionary(self, items, dictionary):
        for item in items:
            dictionary[item["id"]] = item

    def populate_dictionaries(self):
        if self.project_list == "all":
            projects_response = self.get_all(self.base_url + "projects")
        else:
            projects_response = []
            item_types_response = []
            for project_id in self.project_list:
                projects_response.append(self.get(self.base_url + "projects/{}".format(project_id)))

        item_types_response = self.get_all(self.base_url + "itemtypes")
        pick_lists_list = self.get_all(self.base_url + "picklists")
        self.add_to_dictionary(projects_response, self.projects)
        self.add_to_dictionary(item_types_response, self.item_types) 
        self.add_to_dictionary(pick_lists_list, self.picklists)

    def cross_reference_item_types_projects(self):
        for project in self.projects:
            self.cross_reference_item_type_project(project)
            
    def cross_reference_item_type_project(self, project_id):
        project = self.projects[project_id]
        project["itemtypes"] = []
        resource = "projects/{0}/itemtypes"
        item_types_in_project = self.get_all(self.base_url + resource.format(project_id))
        for item_type in item_types_in_project:
            to_append = self.create_link(item_type["display"], "I{}".format(item_type["id"]))
            project["itemtypes"].append(to_append)

            global_item_type = self.item_types[item_type["id"]]
            if "projects" not in global_item_type:
                global_item_type["projects"] = []
                global_item_type["project_ids"] = []
            if project_id not in global_item_type["project_ids"]:
                project_name = project["fields"]["name"]
                global_item_type["project_ids"].append(project_id)
                to_append = self.create_link(project_name, "P{}".format(project_id))
                global_item_type["projects"].append(to_append)
            
    def cross_reference_item_types_picklists(self):
        for item_type in self.item_types:
            self.cross_reference_item_type_picklist(item_type)

    def cross_reference_item_type_picklist(self, item_type_id):
        item_type = self.item_types[item_type_id]
        for field in item_type["fields"]:
            if "pickList" in field:
                picklist_id = field["pickList"]
                picklist = self.picklists[picklist_id]
                if "fields" not in picklist:
                    picklist["fields"] = []
                to_append = self.create_link("{0}".format(field["label"]), "F{}".format(field["id"]))
                to_append += " in " + self.create_link(item_type["display"], "I{}".format(item_type["id"]))
                picklist["fields"].append(to_append)

    def create_link(self, link_text, anchor):
        link_template = "<a href=\"#{anchor}\">{link_text}</a>"
        return link_template.format(anchor=anchor, link_text=link_text)

    def create_image_link(self, link_text, url):
        link_template = "<a href=\"{url}\">{link_text}</a>"
        return link_template.format(url=url, link_text=link_text)

    def prep(self):
        self.populate_dictionaries()
        self.get_picklist_options()
        self.cross_reference_item_types_projects()
        self.cross_reference_item_types_picklists()
        if self.project_list != "all":
            self.remove_unused_picklists()
            self.remove_unused_item_types()

    def remove_unused_picklists(self):
        remove_list = []
        for picklist_id in self.picklists:
            picklist = self.picklists[picklist_id]
            if "fields" not in picklist:
                remove_list.append(picklist_id)

        for key in remove_list:
            del self.picklists[key]

    def remove_unused_item_types(self):
        remove_list = []
        for item_type_id in self.item_types:
            item_type = self.item_types[item_type_id]
            if "projects" not in item_type:
                remove_list.append(item_type_id)

        for key in remove_list:
            del self.item_types[key]


    def get_picklist_options(self):
        for picklist_id in self.picklists:
            self.picklists[picklist_id]["options"] = self.get_all(self.base_url + "picklists/{}/options".format(picklist_id))

    def valid_key(self, key, blacklist):
        return key not in blacklist

    def get_html(self):
        self.prep()
        self.write_headers()
        self.write_projects()
        self.write_item_types()
        self.write_picklists()
        self.write_footers()
        return self.big_string
        
    def write_picklists(self):
        self.write_section_header("Picklists", 0, 20)
        for picklist_id in self.picklists:
            picklist = self.picklists[picklist_id]
            
            self.write_anchor("PL{}".format(picklist_id))
            self.write_plain_line(self.break_bar("Picklists"), 1)
            self.write_line_from_object("name", picklist, 1)
            for key in picklist:
                if self.valid_key(key, self.picklist_blacklist):
                    self.write_line_from_object(key, picklist, 2)
            
            self.write_section_header("Fields Using this Picklist", 2, 16)
            self.big_string += self.indent(3)
            first = True
            if "fields" in picklist:
                for field in picklist["fields"]:
                    if first:
                        first = False
                        self.big_string += field
                    else:
                        self.big_string += ", " + field
                self.big_string += "</p>"

            self.write_section_header("Options", 2, 16)
            for option in picklist["options"]:
                link = self.create_link(picklist["name"], "PL{}".format(picklist_id))
                self.write_plain_line(self.break_bar("Option for {}".format(link)), 3)
                self.write_line_from_object("name", option, 3)
                for key in option:
                    if key != "name":
                        self.write_line_from_object(key, option, 4)


    def write_item_types(self):
        self.write_section_header("Item Types", 0, 20)
        for item_type_id in self.item_types:
            item_type = self.item_types[item_type_id]

            self.write_anchor("I{}".format(item_type_id))
            self.write_plain_line(self.break_bar("Item Types"), 1)
            self.write_line_from_object("display", item_type, 1)
            for key in item_type:
                if self.valid_key(key, self.item_type_blacklist):
                    self.write_line_from_object(key, item_type, 2)
                if key == "image":
                    image_url = item_type[key]
                    image_name = image_url.split('/')[-1]
                    line = self.indent(2) + "<b>image</b>: " + self.create_image_link(image_name, image_url)
                    self.big_string += line

            
            self.write_section_header("Projects this Item Type is in", 2, 16) 
            self.big_string += self.indent(3)
            first = True
            if "projects" in item_type:
                for project in item_type["projects"]:
                    if first:
                        first = False
                        self.big_string += project + "\n"
                    else:
                        self.big_string += ", " + project
                self.big_string += "</p>"

            
            self.write_section_header("Fields", 2, 16)
            for field in item_type["fields"]:
                self.write_anchor("F{}".format(field["id"]))
                link = self.create_link(item_type["display"], "I{}".format(item_type_id))
                self.write_plain_line(self.break_bar("Fields for {}".format(link)), 3)
                self.write_line_from_object("label", field, 3)
                for key in field:
                    if key == "name" and '$' in field["name"]:
                        self.write_line_from_object(key, {'name': field['name'].split('$')[0]}, 4)
                    elif key == "pickList":
                        value = self.create_link(field["pickList"], "PL{}".format(field["pickList"]))
                        self.write_line_from_object(key, {"pickList": value}, 4)
                    elif key != "label":
                        self.write_line_from_object(key, field, 4)

    def write_projects(self):
        self.write_section_header("Projects", 0, 20)
        for project_id in self.projects:
            project = self.projects[project_id]

            self.write_anchor("P{}".format(project_id))
            self.write_plain_line(self.break_bar("Projects"), 1)
            self.write_line_from_object("name", project["fields"], 1)

            if "description" in project["fields"]:
                self.write_key_value_line("description", project["fields"]["description"], 2)

            for key in project:
                if self.valid_key(key, self.project_blacklist):
                    self.write_line_from_object(key, project, 2)
                    
            self.write_section_header("Item Types in this Project", 2, 16)
            self.big_string += self.indent(3)
            first = True
            for item_type in project["itemtypes"]:
                if first:
                    first = False
                    self.big_string += item_type + "\n"
                else:
                    self.big_string += ", " + item_type
            self.big_string += "</p>"
        
    def break_bar(self, text):
        return "----------------------{}----------------------".format(text)

#     def write_out(self):
#         prep()
#         f = open("out.html", "w")
#         write_headers(f)
#         write_projects(f)
#         write_item_types(f)
#         write_picklists(f)
#         write_footers(f)
#
#
#
# write_out()
