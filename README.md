
#Jama Software
Jama Software is the definitive system of record and action for product development. The company’s modern requirements and test management solution helps enterprises accelerate development time, mitigate risk, slash complexity and verify regulatory compliance. More than 600 product-centric organizations, including NASA, Boeing and Caterpillar use Jama to modernize their process for bringing complex products to market. The venture-backed company is headquartered in Portland, Oregon. For more information, visit [jamasoftware.com](http://jamasoftware.com).

Please visit [dev.jamasoftware.com](http://dev.jamasoftware.com) for additional resources and join the discussion in our community [community.jamasoftware.com](http://community.jamasoftware.com).

##Admin Report Generator
```generateAdminReport.py``` is a script which extracts any and all configurations for projects, item types, and picklists in a Jama instance using the Jama REST API. The script will output the configuration information to a file called `out.html` which can be viewed in your internet browser.

Please note that this script is distrubuted as-is as an example and will likely require modification to work for your specific use-case.  This example omits error checking. Jama Support will not assist with the use or modification of the script.

### Before you begin
- Install Python 2.7 or higher and the requests library.  [Python](https://www.python.org/) and [Requests](http://docs.python-requests.org/en/latest/)

### Setup
1. As always, set up a test environment and project to test the script.

2. Fill out the CONFIG section of the script.  The necessary fields are:
  - ```username```
  - ```password```
  - ```base_url```

3. Fill in the following field according to the projects you wish exported:
  - ```projects``` -- A comma-separated list of project API IDs.  These are available from the Admin area in Jama, under 'Manage All Projects'. 
                         This can also be configured to `all` if you wish to export all project configuration information. 

