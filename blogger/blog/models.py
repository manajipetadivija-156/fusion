from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Username
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Hashed password
    desc = models.TextField(blank=True)  # User bio/description
    img = models.ImageField(upload_to='Users/', blank=True, null=True)  # Profile picture

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def post_count(self):
        return self.posts.count()  # Returns number of posts by this User

# Post model
class Post(models.Model):
    title = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)  # Post image

    def __str__(self):
        return self.title
