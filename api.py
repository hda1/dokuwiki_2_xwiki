import os
import requests


class Client:


    def __init__(self, api_root, auth_user=None, auth_pass=None):
        self.api_root = api_root
        self.auth = auth_user, auth_pass


    def send_page(self, spaces, page, content):
        url = self.api_root
        for space in spaces:
            url = url + 'spaces/' + space + '/'
        url = url + 'pages/' + page

        data = {}
        data['media'] = 'json'
        #data['title'] = page
        data['content'] = content

        response = requests.put(url, data=data, auth=self.auth)
        return response


    def send_file(self, spaces, page, file_path, file_name):
        if not os.path.exists(file_path):
            return ''
        url = self.api_root
        for space in spaces:
            url = url + 'spaces/' + space + '/'
        url = url + 'pages/' + page + '/attachments/' + os.path.basename(file_name)
        data=open(file_path, 'rb')
        response = requests.put(url, data=data, auth=self.auth)
        data.close()
        return response


