from django.db import migrations


def create_superuser(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    if not User.objects.filter(username='mnraynor90@gmail.com').exists():
        User.objects.create_superuser(
            username='mnraynor90@gmail.com',
            email='mnraynor90@gmail.com',
            password='Dun3R0ad455@$$'
        )


def delete_superuser(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(username='mnraynor90@gmail.com').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_superuser, delete_superuser),
    ]
