'''
Created on 18/12/2013

@author: rodrigo
'''
from egressos.logica.models import Centro
from django import forms
from django.forms import ModelForm

class CentroForm(ModelForm):
    class Meta:
        model = Centro
        fields = ['nome']
    
    
    
