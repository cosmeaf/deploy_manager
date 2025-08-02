from django.db import models

class GitProject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    repository_url = models.URLField()
    webhook_secret = models.CharField(max_length=255, blank=True)
    last_deploy = models.DateTimeField(null=True, blank=True)
    new_push = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class GitPushEvent(models.Model):
    project = models.ForeignKey(GitProject, on_delete=models.CASCADE)
    pusher = models.CharField(max_length=100)
    ref = models.CharField(max_length=255)
    commit_count = models.IntegerField()
    raw_payload = models.JSONField()
    pushed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.pushed_at}] {self.project.name} - by {self.pusher}"