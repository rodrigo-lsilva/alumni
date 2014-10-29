'''
Created on 13/11/2013

@author: rodrigo
'''
from django.db import models

class Infos(models.Model):
    info1 = models.CharField(max_length=100)
    
    def __str__(self):
        print self.info1
        
    def __unicode__(self):
        return self.info1
        

 
a = Infos()
a.info1="abc"
a.__str__()
b = Infos()
b.info1="def"
b.__str__()
