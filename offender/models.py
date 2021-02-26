from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User



# Create your models here.
class Offender(models.Model): 
    
    off_first_name = models.CharField(max_length=200)
    off_last_name = models.CharField(max_length=200)
    off_birth_date = models.DateField()
    off_age = models.CharField(max_length=200)
    off_gender = models.CharField(max_length=200)
    off_race = models.CharField(max_length=200)
    #off_experience = models.TextField()
    #off_permission = models.CharField(max_length=200)
    off_status = models.CharField(max_length=200)
    off_created_date = models.DateTimeField(default=timezone.now)
    off_updated_date = models.DateTimeField()

    def __str__(self):
        return str(self.off_first_name+' '+self.off_last_name)


class Experience(models.Model):
    record_owner_id = models.ForeignKey(User, on_delete=models.CASCADE)
    record_id = models.ForeignKey(Offender, on_delete=models.CASCADE)
    record_experience = models.TextField()
    record_status = models.CharField(max_length=200)
    record_created_date = models.DateTimeField(default=timezone.now)
    record_updated_date = models.DateTimeField()

    def __str__(self):
        return str(str(self.record_id)+' '+ str(self.record_owner_id) +' '+self.record_experience)


class Extra_info(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    security_question = models.TextField()
    security_answer = models.TextField()
    motel_name = models.CharField(max_length=200,null=True)
    motel_address = models.CharField(max_length=200,null=True)
    motel_city = models.CharField(max_length=200,null=True)
    motel_state = models.CharField(max_length=200,null=True)
    motel_country = models.CharField(max_length=200,null=True)
    motel_pincode = models.CharField(max_length=200,null=True)

    def __str__(self):
        return str(self.user.username)


class Blocked_user(models.Model):
    blocked_user_owner_id = models.ForeignKey(User, on_delete=models.CASCADE)
    blocked_record_id = models.ForeignKey(Offender, on_delete=models.CASCADE)
    blocked_user_status = models.CharField(max_length=200)
    blocked_user_created_date = models.DateTimeField(default=timezone.now)
    blocked_user_updated_date = models.DateTimeField()

    def __str__(self):
        return str(str(self.blocked_record_id)+' '+ str(self.blocked_user_owner_id) +' '+self.blocked_user_status)

### nc dps experience

class NC_offender_experience(models.Model):

    nc_off_owner_id = models.ForeignKey(User, on_delete=models.CASCADE)
    nc_off_id = models.CharField(max_length=200)
    nc_off_experience = models.TextField()
    nc_off_exp_status = models.CharField(max_length=200)
    nc_off_exp_created_date = models.DateTimeField(default=timezone.now)
    nc_off_exp_updated_date = models.DateTimeField()

    def __str__(self):
        return str(str(self.nc_off_id)+' '+ str(self.nc_off_owner_id) +' '+self.nc_off_experience)

class NC_Blocked_user(models.Model):
    nc_blocked_user_owner_id = models.ForeignKey(User, on_delete=models.CASCADE)
    nc_blocked_user_id = models.CharField(max_length=200)
    nc_blocked_user_status = models.CharField(max_length=200)
    nc_blocked_user_created_date = models.DateTimeField(default=timezone.now)
    nc_blocked_user_updated_date = models.DateTimeField()
    nc_blocked_user_first_name = models.CharField(max_length=200)
    nc_blocked_user_last_name = models.CharField(max_length=200)
    nc_blocked_user_dob = models.CharField(max_length=200)
    nc_blocked_user_race = models.CharField(max_length=200)
    nc_blocked_user_sex = models.CharField(max_length=200)

    def __str__(self):
        return str(str(self.nc_blocked_user_id)+' '+ str(self.nc_blocked_user_owner_id) +' '+self.nc_blocked_user_status)



### MCSO experience

class MCS_offender_experience(models.Model):

    mcs_off_owner_id = models.ForeignKey(User, on_delete=models.CASCADE)
    mcs_off_pid = models.CharField(max_length=200)
    mcs_off_jid = models.CharField(max_length=200)
    mcs_off_experience = models.TextField()
    mcs_off_exp_status = models.CharField(max_length=200)
    mcs_off_exp_created_date = models.DateTimeField(default=timezone.now)
    mcs_off_exp_updated_date = models.DateTimeField()

    def __str__(self):
        return str(str(self.mcs_off_pid)+' '+ str(self.mcs_off_jid) +' '+str(self.mcs_off_owner_id)+' '+self.mcs_off_experience+' '+self.mcs_off_exp_status)

class MCS_Blocked_user(models.Model):
    mcs_blocked_user_owner_id = models.ForeignKey(User, on_delete=models.CASCADE)
    mcs_blocked_user_pid = models.CharField(max_length=200)
    mcs_blocked_user_jid = models.CharField(max_length=200)
    mcs_blocked_user_status = models.CharField(max_length=200)
    mcs_blocked_user_created_date = models.DateTimeField(default=timezone.now)
    mcs_blocked_user_updated_date = models.DateTimeField()
    mcs_blocked_user_first_name = models.CharField(max_length=200)
    mcs_blocked_user_last_name = models.CharField(max_length=200)
    mcs_blocked_user_dob = models.CharField(max_length=200)
    mcs_blocked_user_race = models.CharField(max_length=200)
    mcs_blocked_user_sex = models.CharField(max_length=200)
    

    def __str__(self):
        return str(str(self.mcs_blocked_user_pid)+' '+ str(self.mcs_blocked_user_jid) +' '+ str(self.mcs_blocked_user_owner_id) +' '+self.nc_blocked_user_status)
