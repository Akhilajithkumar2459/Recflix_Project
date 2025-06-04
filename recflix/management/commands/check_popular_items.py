from django.core.management.base import BaseCommand
from recflix.models import PopularItem

class Command(BaseCommand):
    help = 'Check popular items in the database'

    def handle(self, *args, **options):
        self.stdout.write('Checking popular items...')
        
        # Check total count
        total = PopularItem.objects.count()
        self.stdout.write(f'Total popular items: {total}')
        
        # Check by category
        categories = ['movies', 'books', 'games']
        for category in categories:
            items = PopularItem.objects.filter(category=category)
            self.stdout.write(f'\nCategory: {category}')
            self.stdout.write(f'Total items: {items.count()}')
            
            # Show items with count >= 2
            popular = items.filter(count__gte=2)
            self.stdout.write(f'Items with count >= 2: {popular.count()}')
            
            # Show all items and their counts
            for item in items:
                self.stdout.write(f'- {item.title}: {item.count} times') 