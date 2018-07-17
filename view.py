def download_attachment(request, task_id, file_name):
    current_user = request.user if request.user.is_authenticated() else None
    if current_user:
        tmp_attachment = TaskAttachment.objects.filter(file_name__iexact=file_name,task_id=task_id) 
        file_path =  tmp_attachment[0].file_path               
        response=StreamingHttpResponse(readFile(file_path))
        response['Content-Type']='application/octet-stream'
        response['Content-Disposition']='attachment;filename="{0}"'.format(tmp_attachment[0].file_name)
        return response
    return HttpResponseRedirect(reverse('login'))

def readFile(filename,chunk_size=512):
    with open(filename,'rb') as f:
        while True:
            c=f.read(chunk_size)
            if c:
                yield c
            else:
                break
         
@login_required
def delete_one_attachment(request):
    data={}
    attachments  = []
    delete_flag = 0    
    current_user = request.user if request.user.is_authenticated() else None 
    if current_user:  
        del_file=request.POST["delete_filename"]
        if "task_id" in request.POST:
            task_id=request.POST["task_id"]
        if "attachment_id" in request.POST:
            data["delete_attachment_id"] = request.POST["attachment_id"]
        if "delete_flag" in request.POST:
            delete_flag = request.POST["delete_flag"]
       
        if del_file:  
            #path_file=os.path.join(settings.MEDIA_ROOT,'upload',del_file)
            try: 
                os.remove(del_file)
                if delete_flag == "True":  #if remove before save to DB.
                    global attachments_dict
                    attachments_dict[current_user.username].pop()
                delete_data_in_db = TaskAttachment.objects.filter(file_path=del_file) 
                if len(delete_data_in_db) > 0:
                    delete_data_in_db[0].delete()
                    attachment_ret = TaskAttachment.objects.filter(task_id=task_id)
                    for d in attachment_ret:
                        tmp_dict = {}
                        tmp_dict["id"] = d.id
                        tmp_dict["task_id"] = task_id
                        tmp_dict["upload_user"] = d.upload_user
                        tmp_dict["file_name"] = d.file_name
                        tmp_dict["file_path"] = d.file_path
                        attachments.append(tmp_dict)                   
                    data["attachments"] = attachments
                    data["res"] = 1
                else:
                    data["res"] = 0 #"Failed in DB."
            except Exception as e:
                data["res"] = 0
                data["delete_failed_info"] = e
        return HttpResponse(json.dumps(data), content_type="application/json")
    return HttpResponseRedirect(reverse('login'))
  
@csrf_exempt
def uploadify_script(request):
    attachment_info = {}
    global attachments_dict
    upload_user = request.POST['upload_user']
    if upload_user:
        ret = "0"  
        new_name = ''
        if request.FILES and request.FILES['Filedata']:
            filename = request.FILES.get("Filedata",None)
        if filename:
            result,new_name,file_path=file_upload(filename) #save to local
            if result:
                ret = "1" #upload success
                attachment_info["upload_user"]=upload_user
                attachment_info["filename"]=filename
                attachment_info["file_path"]=file_path
                if not attachments_dict.has_key(upload_user):
                    attachments_dict[upload_user]=[]
                attachments_dict[upload_user].append(attachment_info)  
            else:
                ret = "2"          
        source={'ret':ret,'save_name':new_name, "file_path":file_path}
        return HttpResponse(json.dumps(source), content_type="application/json")
    return HttpResponseRedirect(reverse('login'))
   
def file_upload(filename):  
    '''''文件上传函数'''  
    if filename:
        path=os.path.join(media_path,'upload')
        if not os.path.exists(path):
            os.mkdir(path,0755)
        file_name=str(uuid.uuid1())+'-'+filename.name
        file_path=os.path.join(path,file_name)
        with open(file_path, 'wb') as destination:
            for chunk in filename.chunks():
                destination.write(chunk)             
        return (True, file_name, file_path) #change
    return (False, file_name, file_path)   #change 

def save_one_attachment(attachment):
    task_id = attachment["task_id"]
    upload_user = attachment["upload_user"]
    filename = attachment["filename"]
    file_path = attachment["file_path"]
    Attachment= TaskAttachment()
    Attachment.task = Task.objects.get(pk=task_id)
    Attachment.upload_user = upload_user         
    Attachment.file_name = filename  
    Attachment.file_path = file_path             
    Attachment.save() 