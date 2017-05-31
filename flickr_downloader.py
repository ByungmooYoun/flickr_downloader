import os
import requests
import hashlib
import xml.etree.ElementTree as ET

class flickr_app() :
    
    def __init__(self, *args, **kwds) :
       self.api_key    = ##############################
       self.secret_key = ##############################
       self.user_id    = ##############################
       
       self.frob       = None
       self.auth_token = None

       self.param_set  = {
            "method" : None,
            "api_key" : self.api_key,
            "secret_key" : self.secret_key,
            "frob" : self.frob,
            "auth_token" : self.auth_token,
            "perms" : None,
            "format" : None,
            "api_sig" : None,
            "photo_id" : None,
            "user_id" : self.user_id
       }

    def make_call_url(self, api_url, param_list) :
        call_url = api_url

        temp_list = []
        
        for key in param_list :
            value = self.param_set[key]
            if value != None :
                temp_list.append("%s%s" % (key, value))
                call_url += "&%s=%s" % (key, value)
            else :
                raise RuntimeError("%s's value is not exist." % key)
            
        temp_list.sort()

        api_sig = hashlib.md5(("%s%s" % (self.secret_key, "".join(temp_list))).encode()).hexdigest()
        
        call_url += "&api_sig=%s" % api_sig

        return(call_url)

    # def make_api_sig(self, param_list) :
    #     temp_list = []
        
    #     for key in param_list :
    #         value = self.param_set[key]
    #         if value != None :
    #             temp_list.append("%s%s" % (key, value))
    #         else :
    #             raise RuntimeError("%s's value is not exist.")
            
    #     temp_list.sort()

    #     return hashlib.md5(("%s%s" % (self.secret_key, "".join(temp_list))).encode()).hexdigest()

    def get_frob(self) :
        api_url = "https://www.flickr.com/services/auth/?"

        param_list = ["api_key", "perms", "method"]

        self.param_set["method"] = "flickr.auth.getFrob"
        self.param_set["perms"] = "read"

        call_url = self.make_call_url(api_url, param_list)

        print("Execute following link in your browser, and paste frob value to here.")
        print(call_url)
        self.frob = input("frob:")
        self.param_set["frob"] = self.frob
        print(self.frob)

    def get_auth_token(self) :
        api_url = "https://www.flickr.com/services/rest/?"

        param_list = ["api_key", "frob", "method"]

        self.param_set["method"] = "flickr.auth.getToken"
        
        call_url = self.make_call_url(api_url, param_list)

        print(call_url)
        result = requests.get(call_url)
        print(result)
        print(result.content)
        root = ET.fromstring(result.content)
        for x in root.iter("token") :
            self.auth_token = x.text
            break
        self.param_set["auth_token"] = self.auth_token
        print(self.auth_token)        
        
    def photos_search(self, min_taken_date, max_taken_date) :
        api_url = "https://www.flickr.com/services/rest/?"

        param_list = ["api_key", "user_id", "method", "auth_token", "min_taken_date", "max_taken_date"]

        self.param_set["method"] = "flickr.photos.search"
        self.param_set.setdefault("min_taken_date", min_taken_date)
        self.param_set.setdefault("max_taken_date", max_taken_date)
        
        call_url = self.make_call_url(api_url, param_list)
        
        print(call_url)
        result = requests.get(call_url)
        print(result)
        print(result.content)
    
    def photos_search_all(self) :
        api_url = "https://www.flickr.com/services/rest/?"

        param_list = ["api_key", "user_id", "method", "auth_token", "per_page", "page"]

        self.param_set["method"] = "flickr.photos.search"
        self.param_set.setdefault("per_page", "500")
        self.param_set.setdefault("page", "1")

        photos_list = []

        for x in range(63) :        
            print(self.param_set["page"])
            call_url = self.make_call_url(api_url, param_list)
            result = requests.get(call_url)
            photos_list.append(result.content)
            self.param_set["page"] = str(int(self.param_set["page"]) + 1)

        print(len(photos_list))
        fp = open("photos_list", "wb")
        fp.write(b"\n".join(photos_list))
        fp.close()

    def photos_getsizes(self, photo_id) :
        api_url = "https://www.flickr.com/services/rest/?"

        param_list = ["api_key", "photo_id", "method", "auth_token"]

        self.param_set["method"] = "flickr.photos.getSizes"
        #self.param_set["photo_id"] = "34944479495"
        self.param_set["photo_id"] = photo_id

        call_url = self.make_call_url(api_url, param_list)
        
        download_url = ""
        
        #print(call_url)
        result = requests.get(call_url)
        #print(result)
        #print(result.content)
        root = ET.fromstring(result.content)
        for x in root.iter("size") :
            if x.attrib["label"] == "Original" :
                download_url = x.attrib["source"]
                break
        print(download_url)
        return download_url

    def photos_download(self, download_url) :
        result = requests.get(download_url)
        
        with open("download_log", "a") as log_file :

            if result.status_code == 200 :
                file_name = "download/%s" % os.path.basename(download_url)
                with open(file_name, "wb") as image_file :
                    image_file.write(result.content)
                    log_file.write("%s\n" % file_name)


if __name__ == "__main__" :
    app = flickr_app()
    app.get_frob()
    app.get_auth_token()
    # app.photos_search_all()
    # app.photos_search("2010-05-15", "2010-05-16")
    # photo_id_list = ##############################
    # for x in photo_id_list :
    #     app.photos_download(app.photos_getsizes(x))
    photo_id_list = open("photo_id_list", "r").read().split("\n")
    
    for x in photo_id_list :
        app.photos_download(app.photos_getsizes(x))        


