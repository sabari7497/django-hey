import os
import subprocess
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Creates a Django project and app with a single command: hey django create <project_name> <app_name>'

    def add_arguments(self, parser):
        parser.add_argument('subcommand', help='Subcommand: django')
        parser.add_argument('action', help='Action: create')
        parser.add_argument('project_name', help='Name of the project')
        parser.add_argument('app_name', help='Name of the app')

    def handle(self, *args, **options):
        subcommand = options['subcommand']
        action = options['action']
        project_name = options['project_name']
        app_name = options['app_name']

        if subcommand != 'django' or action != 'create':
            self.stderr.write("Usage: hey django create <project_name> <app_name>")
            return

        # Step 1: Create the Django project
        try:
            subprocess.run(['django-admin', 'startproject', project_name], check=True)
            self.stdout.write(self.style.SUCCESS(f"Project '{project_name}' created successfully!"))
        except subprocess.CalledProcessError:
            self.stderr.write(self.style.ERROR(f"Failed to create project '{project_name}'."))
            return

        # Step 2: Change to project directory
        os.chdir(project_name)

        # Step 3: Create the Django app
        try:
            call_command('startapp', app_name)
            self.stdout.write(self.style.SUCCESS(f"App '{app_name}' created successfully!"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to create app '{app_name}': {str(e)}"))
            return

        # Step 4: Create urls.py in the app
        app_urls_path = os.path.join(app_name, 'urls.py')
        urls_content = """from django.urls import path
from . import views

app_name = '{}'
urlpatterns = [
    path('', views.home, name='home'),
]
""".format(app_name)

        try:
            with open(app_urls_path, 'w') as f:
                f.write(urls_content)
            self.stdout.write(self.style.SUCCESS(f"'urls.py' created in '{app_name}' successfully!"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to create 'urls.py': {str(e)}"))
            return

        # Step 5: Update project settings.py to include the app
        settings_path = os.path.join(project_name, 'settings.py')
        try:
            with open(settings_path, 'r') as f:
                settings_content = f.readlines()

            # Find INSTALLED_APPS and append the app
            for i, line in enumerate(settings_content):
                if 'INSTALLED_APPS' in line:
                    # Look for the closing bracket
                    for j in range(i, len(settings_content)):
                        if ']' in settings_content[j]:
                            settings_content.insert(j, f"    '{app_name}',\n")
                            break
                    break

            with open(settings_path, 'w') as f:
                f.writelines(settings_content)
            self.stdout.write(self.style.SUCCESS(f"App '{app_name}' added to INSTALLED_APPS!"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to update settings.py: {str(e)}"))
            return

        # Step 6: Update project urls.py to include app urls
        project_urls_path = os.path.join(project_name, 'urls.py')
        try:
            with open(project_urls_path, 'r') as f:
                urls_content = f.read()

            # Add include() import if not present
            if 'include' not in urls_content:
                urls_content = urls_content.replace('from django.urls import path',
                                                  'from django.urls import path, include')

            # Add app's URL include
            new_url_pattern = f"    path('', include('{app_name}.urls')),\n"
            urlpatterns_start = urls_content.find('urlpatterns = [') + len('urlpatterns = [')
            urls_content = (urls_content[:urlpatterns_start] +
                            new_url_pattern +
                            urls_content[urlpatterns_start:])

            with open(project_urls_path, 'w') as f:
                f.write(urls_content)
            self.stdout.write(self.style.SUCCESS(f"Project 'urls.py' updated to include '{app_name}.urls'!"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to update project urls.py: {str(e)}"))
            return

        # Step 7: Create a basic home view in app/views.py
        views_path = os.path.join(app_name, 'views.py')
        views_content = """from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to {}!")
""".format(app_name)

        try:
            with open(views_path, 'w') as f:
                f.write(views_content)
            self.stdout.write(self.style.SUCCESS(f"Basic view created in '{app_name}/views.py'!"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to update views.py: {str(e)}"))
            return

def main():
    from django.core.management import execute_from_command_line
    import sys
    execute_from_command_line(['manage.py', 'hey'] + sys.argv[1:])

if __name__ == '__main__':
    main()