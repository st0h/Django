from django.db import models
from django.conf import settings

class Post(models.Model):
    """
        The database model representing an individual post. These make up the bulk of the app's
        content.
    """
    title = models.CharField(max_length=100, blank=False)
    body = models.TextField(max_length=25000, blank=False)
    pub_date = models.DateTimeField("Published on")
    # The author field should be linked to the user object that created it.
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    # The "string representation" for the admin interface will be the post's title.
    def __str__(self):
        return self.title.title()

class Comment(models.Model):
    """
        A Comment is, in essence, a reply to a Post (tied to an authenticated user).
    """
    # Associate the comment with an existing post.
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    # The author field should be linked to the user object that created it.
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    body = models.TextField(max_length=1000, blank=False)
    pub_date = models.DateTimeField("Published on")
    # The string representation should include the post's title and the username associated with it.
    def __str__(self):
        return "Reply to " + self.post.title.title() + " by " + self.author.username
