from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import random

class Camp(models.Model):
    theme = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    logistics = models.TextField(blank=True)

    # Hotel information
    hotel = models.CharField(max_length=30, blank=True)
    hotel_link = models.URLField(blank=True)
    hotel_code = models.CharField(max_length=30, blank=True, verbose_name='Hotel promotion code')
    hotel_deadline = models.DateField(blank=True, null=True)
    
    # Venue information
    venue = models.CharField(max_length=30, blank=True)
    venue_address = models.CharField(max_length=140, blank=True)
    
    # Sub-events
    ignite = models.BooleanField(blank=True, default=False)
    stipends = models.BooleanField(blank=True, default=False)
    
    def __unicode__(self):
        return u'Spark Camp %s' % self.theme

class Invitation(models.Model):
    # Field choices
    STATUS_CHOICES = (
        ('Q', 'Invitation not yet sent'),
        ('P', 'Awaiting a response'),
        ('Y', 'Attendance confirmed'),
        ('N', 'Can\'t make it'),
        ('C', 'Had to cancel'),
        ('X', 'No response'),
        ('Z', 'No show'),
        ('W', 'On the waitlist'),
        ('M', 'Maybe'),
    )
    ATTENDEE_TYPE = (
        ('G', 'Guest'),
        ('S', 'Sponsor'),
        ('H', 'Host'),
        ('A', 'Administrative Support / Staff'),
    )
    
    # Invitation metadata
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='Q')
    type = models.CharField(max_length=1, choices=ATTENDEE_TYPE, default='G')
    plus_one = models.BooleanField(default=False)
    expires = models.DateField(blank=True)
    
    # User-specific metadata
    user = models.ForeignKey(User)
    camp = models.ForeignKey(Camp)
    rand_id = models.CharField(max_length=8, unique=True, editable=False)
    
    # Logistical information
    dietary = models.CharField(max_length=140, blank=True, default='None', help_text='Please note any dietary preferences here.', verbose_name='Dietary preferences')
    arrival_time = models.DateTimeField(blank=True, null=True, help_text='Tell us the time you\'ll be arriving at Spark Camp.')
    departure_time = models.DateTimeField(blank=True, null=True, help_text='Tell us the time you\'ll be leaving Spark Camp.')
    hotel_booked = models.BooleanField(blank=True, default=False, help_text='Check here if you\'ve taken care of your hotel room.')
    
    def __unicode__(self):
        return u'%s Invite: %s %s (%s)' % (self.camp, self.user.first_name, self.user.last_name, self.user.username)
        
    def is_waitlisted(self):
        "Calculates whether the invitation has been waitlisted."
        import datetime
        today = datetime.date.today()
        if self.expires < today and self.status == 'P':
            return True
        else:
            return False
            
    class Meta:
        unique_together = ('user', 'camp')
        
    def save(self, *args, **kwargs):
        if self.id is None:
            self.rand_id = random_number = random.randrange(10000000,99999999) #Generate a random ID so we can retrieve and edit this anonymously
        super(Invitation, self).save(*args, **kwargs) # Call the "real" save() method.

class Stipend(models.Model):
    invitation = models.ForeignKey(Invitation, unique=True)
    SUBSIDY_CHOICES = (
        ('Y', 'Yes'),
        ('N', 'No'),
        ('U', 'Unsure'),
    )
    
    cost_estimate = models.IntegerField(max_length=140, null=True, blank=True, help_text='How much do you estimate air and ground transportation will cost? Don\'t include lodging and meals.')
    employer_subsidized = models.CharField(max_length=1, choices=SUBSIDY_CHOICES, default='U', help_text='Will your employer provide any funds towards travel?', verbose_name='Employer will cover some costs')
    employer_percentage = models.IntegerField(blank=True, null=True, help_text='What part of the cost will your employer cover?')
    invitee_percentage = models.IntegerField(blank=True, null=True, help_text='What part of the cost can you cover yourself?')
    details = models.TextField(blank=True, help_text='Please explain any other factors that would assist us in processing this request.')

class Ignite(models.Model):
    invitation = models.ForeignKey(Invitation, unique=True)
    EXPERIENCE_CHOICES = (
        ('Y', 'Yep, I\'m an Ignite pro.'),
        ('M', 'I think I\'ve done something similar.'),
        ('N', 'No, but I think I\'ll be OK.'),
    )
    
    title = models.CharField(max_length=140, help_text='What\'s the title of your proposed talk?')
    experience = models.CharField(max_length=1, help_text='Have you done an Ignite or similar presentation before?', choices=EXPERIENCE_CHOICES)
    description = models.TextField(help_text='What\'s your talk about? Give us a little detail.')
    
class Roommate(models.Model):
    invitation = models.ForeignKey(Invitation, unique=True)
    SEX_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other / Prefer not to say'),
    )
    ROOMMATE_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('A', 'Comfortable with anyone'),
    )
    
    sex = models.CharField(max_length=1, help_text='What\'s your sex?', choices=SEX_CHOICES)
    roommate = models.CharField(max_length=1, help_text='What sex are you comfortable rooming with?', choices=ROOMMATE_CHOICES)
    more = models.CharField(max_length=140, blank=True, help_text='Anything else we should know?')

# Perhaps declaring this function here would work better?    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        SparkProfile.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User)
    
class SparkProfile(models.Model):
    user = models.OneToOneField(User)
    bio = models.CharField(max_length=140, blank=True, help_text='Tell us your bio. Keep it Twitter-length.')
    employer = models.CharField(max_length=140, blank=True, help_text='The name of your primary employer.')
    job_title = models.CharField(max_length=140, blank=True, help_text='Your job title.')
    phone = models.CharField(max_length=30, blank=True, help_text='Preferred phone number for us to reach you.')
    
    # User details for admins.
    poc = models.BooleanField(blank=True, default=False, verbose_name='Person of color')
    woman = models.BooleanField(blank=True, default=False)
    journo = models.BooleanField(blank=True, default=False, help_text='Works predominantly in the news industry?')
    
    def __unicode__(self):
        return u'%s\'s SparkProfile' % (self.user.username)
