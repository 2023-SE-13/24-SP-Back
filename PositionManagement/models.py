import uuid
import pytz
from django.db import models
from django.utils import timezone
from CompanyManagement.models import Company
from UserManagement.models import User

class PositionTag(models.Model):
    category = models.CharField(max_length=255)
    specialization = models.CharField(max_length=255)

    class Meta:
        db_table = 'PositionTags'
        unique_together = ('category', 'specialization')

    def __str__(self):
        return f"{self.category} - {self.specialization}"


class Position(models.Model):
    position_id = models.UUIDField(primary_key=True, auto_created=True, unique=True, editable=False, default=uuid.uuid4)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    position_name = models.CharField(max_length=255)
    position_description = models.CharField(max_length=255)
    location = models.CharField(max_length=255, null=True, blank=True)
    education_requirement = models.CharField(max_length=255, null=True, blank=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # 最低薪资
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # 最高薪资
    posted_at = models.DateTimeField(null=True, blank=True)
    skill_required = models.ManyToManyField('UserManagement.Skill', blank=True)
    position_tag = models.ForeignKey(PositionTag, on_delete=models.CASCADE, null=True, blank=True)
    hr = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # 关联 HR 用户
 
    class Meta:
        db_table = 'Positions'

    def __str__(self):
        return self.position_name

    def save(self, *args, **kwargs):
        if not self.posted_at:
            utc_time = timezone.now()
            local_tz = pytz.timezone('Asia/Shanghai')
            local_time = utc_time.astimezone(local_tz)
            self.posted_at = local_time
        super().save(*args, **kwargs)


class Application(models.Model):
    application_id = models.UUIDField(primary_key=True, auto_created=True, unique=True, editable=False,
                                      default=uuid.uuid4)
    position = models.ForeignKey('Position', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    applied_at = models.DateTimeField()
    result = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'applications'

    def __str__(self):
        return f"Application by {self.user.username} for {self.position.position_name}"

    def save(self, *args, **kwargs):
        if not self.applied_at:
            utc_time = timezone.now()
            local_tz = pytz.timezone('Asia/Shanghai')
            local_time = utc_time.astimezone(local_tz)
            self.applied_at = local_time
        super().save(*args, **kwargs)