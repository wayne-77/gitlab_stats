# coding=utf-8
import os
import gitlab
import requests
from time import sleep
from influxdb import InfluxDBClient
print("")
print("    88888    88  88888888   88888  88888888  ")
print("  888        88     88     88         88   ")
print(" 888  8888   88     88       88       88  ")
print("  888   88   88     88          88    88   ")
print("   88888     88     88      8888      88    ")
print("")

# Just for testing.
# Sets vars manually if not run from docker-compose
# if "GIT_URL" in os.environ:
git_token = os.environ['GIT_PRIVATE_TOKEN']
git_url = os.environ['GIT_URL']
db_hostname = os.environ['INFLUXDB_HOSTNAME']
db_port = os.environ['INFLUXDB_PORT']
db_user = os.environ['INFLUXDB_ADMIN_USER']
db_password = os.environ['INFLUXDB_ADMIN_PASSWORD']
db_name = os.environ['INFLUXDB_DB']
os.environ['NO_PROXY'] = db_hostname
update_freq = int(os.environ['GRAFANA_FREQ'])
print("These ENVIRONMENTS are set from docker-compose:")
print("Git private token: [OMITTED]")
print("Gitlab URL: " + git_url)
print("InfluxDB hostname: " + db_hostname)
print("InfluxDB Password: [OMITTED]")
print("InfluxDB Port: " + db_port)
print("InfluxDB User: " + db_user)
print("InfluxDB Database: " + db_name)
'''
else:
    git_token = 'CHANGEME'
    git_url ='CHANGEME' 
    db_hostname = 'influxdb'
    db_port = '8086'
    db_user = 'CHANGME'
    db_password = 'CHANGEME'
    db_name = "gitstats"
    update_freq = 5
    print("These env are set from within the python script:")
    print(git_token, git_url, db_hostname, db_password, db_port, db_user, db_name)
'''

def write_influxdb(data):
    print("Writing to DB: {data}".format(data=data))
    try:
        inf_client.write_points(data)
        print("Write Successful")
        return 1
    except:
        print("ERROR: Failed to write to InfluxDB Database")
        print("Killing container...")
        sleep(5)
        exit()
        return 0


def update_all():
    stats = [
        {"stat": "branches", "count": get_branches()},
        {"stat": "projects", "count": get_projects()},
        {"stat": "git_users", "count": get_active_users()},
        {"stat": "git_groups", "count": get_groups()},
        {"stat": "issues", "count": get_issues()},
    ]
    for i in stats:
        json_body = [
            {
                "measurement": i["stat"],
                "fields": {
                    "value": i["count"]
                }
            }
        ]
        write_influxdb(json_body)


def get_projects():
    try:
        projects = gl.projects.list(as_list=False)
        result = projects.total
    except:
        print("failed on getting the total number of all projects")
        result = 0
    return result


def get_groups():
    try:
        groups = gl.groups.list(as_list=False)
        result = groups.total
    except:
        print("failed on getting the total number of all projects")
        result = 0
    return result


def get_active_users():
    try:
        result = gl.users.list(as_list=False).total
    except:
        print("failed on getting the total number of all users")
        result = 0
    return result


def get_branches():
    sum_branches = 0
    i = 0
    print("Counting branches...")
    try:
        projects = gl.projects.list(as_list=False)
    except:
        print("Failed to get projects during branch count")
    for project in projects:
        try:
            branches = len(project.branches.list())
            sum_branches += branches
            i += 1
            if i % 50 == 0:
                print("Still counting...")
            if i % 200 == 0:
                print(str(i) + "" )
        except:
            print("The project '" + project.name + "' could not be accessed. Project ID: " + str(project.id) + ". Skipped...")
            next(projects)
    result = sum_branches
    if not result:
        print("failed on getting the total number of branches")
    else:
        return result


def get_issues():
    headers = {'Private-Token': git_token}
    url = git_url + "/api/v4/issues?scope=all"
    try:
        request = requests.get(url=url, headers=headers, verify='/etc/ssl/certs/ca-certificates.crt')
        result = request.headers['x-total']
    except:
        print("failed on getting the total number of issues")
        result = 0
    return result


def main():
    session = requests.Session()
    session.verify = '/etc/ssl/certs/ca-certificates.crt'

    global gl
    gl = gitlab.Gitlab(git_url, private_token=git_token, api_version='4', session=session)

    global inf_client
    inf_client = InfluxDBClient(host=db_hostname, port=db_port, database=db_name,
                                username=db_user, password=db_password)

    update_all()


while True:
    main()
    print("Sleeping for specified update frequency. Set to " + str(update_freq) + " seconds.")
    sleep(update_freq)
