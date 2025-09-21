from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('trainer', 'Antrenor'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_approved = models.BooleanField(default=False)  # doar pentru antrenori
    trainer = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, limit_choices_to={'role': 'trainer'})
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class WorkoutPlan(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_plans')
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trainer_workout_plans')
    date = models.DateField()
    workout_description = models.TextField()

    class Meta:
        unique_together = ('client', 'date')

    def __str__(self):
        return f"{self.client.username} - {self.date}"
