from django.db import models
from django.conf import settings

# Create your models here.
class Conveyance(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    file_name=models.CharField(max_length=1000)
    file=models.FileField(upload_to='uploads/',blank=False,null=False)  
    file_upload_date=models.DateTimeField(auto_now_add=True)
    file_update_date=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file_name

class AnalyzedConveyance(models.Model):
    #conveyance_doc=models.ForeignKey(Conveyance,on_delete=models.CASCADE)
    
    conveyance=models.OneToOneField(Conveyance,on_delete=models.CASCADE)
    extracted_text=models.TextField(null=True)
    summarized_text=models.TextField(null=True)
    text_extraction_date=models.DateTimeField(auto_now_add=True)
    text_extraction_update=models.DateTimeField(auto_now=True)
    analyzed_file=models.FileField(upload_to='analyzed/',blank=True,null=True)  

    def __str__(self):
        return str(self.conveyance.file_name)

 