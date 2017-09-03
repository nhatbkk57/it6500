import os
import json
import keystoneclient.v3 as keystoneclient
import swiftclient.client as swiftclient

class Storage(object):
    def __init__(self,container_name="guest"):
        # cloudant_service = json.loads(os.environ['VCAP_SERVICES'])['Object-Storage'][0]
        # objectstorage_creds = cloudant_service['credentials']
        # if objectstorage_creds:
        #     auth_url = objectstorage_creds['auth_url'] + '/v3'
        #     project_name = objectstorage_creds['project']
        #     password = objectstorage_creds['password']
        #     user_domain_name = objectstorage_creds['domainName']
        #     project_id = objectstorage_creds['projectId']
        #     user_id = objectstorage_creds['userId']
        #     region_name = o bjectstorage_creds['region']
        auth_url = "https://identity.open.softlayer.com/v3" #add "/v3" at the ending of URL
        password = "G{v,AP4#ublR7iPj"
        project_id = "1abdaeace790484fbc8d756331e58c16"
        user_id = "32f7dd2e775241e3a6e03ecf59c310c7"
        region_name = "dallas"

        # Get a Swift client connection object
        self.conn = swiftclient.Connection(
            key=password,
            authurl=auth_url,
            auth_version='3',
            os_options={"project_id": project_id,
                        "user_id": user_id,
                        "region_name": region_name})
        self.container_name = container_name
    def put(self, file_name, content):
        self.conn.put_object(self.container_name,file_name,content,content_type='image/png')
    def get(self,file_name):
        obj = self.conn.get_object(self.container_name, file_name)
        return obj
    def create_container(self,container_name):
        self.conn.put_container(container_name)
        self.container_name = container_name
    
    def list_container(self):
        for container in self.conn.get_account()[1]:
            print container["name"]
    def list_object(self):
        result = []
        # List objects in a container, and prints out each object name, the file size, and last modified date
        # print ("\nObject List:")
        for container in self.conn.get_account()[1]:
            for data in self.conn.get_container(container['name'])[1]:
                json_obj = {"object":data['name'], "size": data['bytes'],"date": data['last_modified']}
                print data
                result.append(json_obj)
        return result
    def delete_object(self,file_name):
        # Delete an object
        self.conn.delete_object(self.container_name, file_name)
        print "\nObject %s deleted successfully." % file_name

    def delete_container(self,container_name):
        # To delete a container. Note: The container must be empty!
        self.conn.delete_container(container_name)
        print "\nContainer %s deleted successfully.\n" % container_name