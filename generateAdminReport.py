from item_types_server import Admin_report

# replace {base_url}, username and password
baseUrl = "https://<base_url>/rest/v1/"
username = "username"
password = "password"

# Comma separated list of project Ids, or the word all

projects = "all"
# or
# projects = {"project1", "project2", "project3", ...}

admin_report = Admin_report(base_url=baseUrl, username=username, password=password, projects=projects)

f = open("out.json", "w")
f.write(str(admin_report.get_json()))
