from django.db import models

# Create your models here.


class UserRegistration(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=150)
    gender = models.CharField(max_length=12)
    password = models.CharField(max_length=100)


    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    
    