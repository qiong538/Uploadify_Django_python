from django.db import models
from userInfo.models import UserInfo
from project.models import Project


class TaskAttachment(models.Model):
    task = models.ForeignKey(Task)   
    upload_user = models.CharField(max_length=40)
    file_name = models.CharField(max_length=500)
    file_path = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'task_attachments'
        verbose_name = '附件管理'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.file_name 