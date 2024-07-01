import os
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from UserManagement.models import User  # 确保导入你的User模型


class Command(BaseCommand):
    help = 'Set default avatar for users who do not have one'

    def handle(self, *args, **kwargs):
        default_avatar_path = os.path.join(settings.MEDIA_ROOT, 'resources/avatars/default_avatar.png')

        with open(default_avatar_path, 'rb') as f:
            avatar_content = f.read()

        users_without_avatar = User.objects.filter(avatar='')

        for user in users_without_avatar:
            new_filename = f"{user.username}_avatar.png"
            new_file = ContentFile(avatar_content)
            new_file.name = new_filename
            user.avatar.save(new_filename, new_file, save=True)
            self.stdout.write(self.style.SUCCESS(f'Successfully set avatar for {user.username}'))
