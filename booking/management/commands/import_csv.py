from django.core.management.base import BaseCommand
import pandas as pd
from booking.models import Member, Inventory

class Command(BaseCommand):
    help = 'Import data from CSV files'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the CSV file')
        parser.add_argument('type', type=str, help='Type of data (members/inventory)')

    def handle(self, *args, **options):
        file_path = options['file_path']
        file_type = options['type']

        try:
            df = pd.read_csv(file_path)
            
            if file_type == 'members':
                for _, row in df.iterrows():
                    Member.objects.create(
                        name=row['name'],
                        email=row['email']
                    )
                self.stdout.write(self.style.SUCCESS('Successfully imported members'))
                
            elif file_type == 'inventory':
                for _, row in df.iterrows():
                    Inventory.objects.create(
                        name=row['name'],
                        description=row['description'],
                        total_count=row['total_count'],
                        remaining_count=row['total_count']
                    )
                self.stdout.write(self.style.SUCCESS('Successfully imported inventory'))
                
            else:
                self.stdout.write(self.style.ERROR('Invalid type. Use "members" or "inventory"'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))