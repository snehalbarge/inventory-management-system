from datetime import datetime
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from .models import Member, Inventory, Booking
import json


@csrf_exempt
def upload_csv(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        file_type = request.POST.get('type')
        
        if not file or not file_type:
            return JsonResponse({'error': 'File and type are required'}, status=400)
        
        try:
            df = pd.read_csv(file)
            
            if file_type == 'members':
                for _, row in df.iterrows():
                    Member.objects.create(
                        name=row['name'],
                        surname=row['surname'],
                        booking_count=row['booking_count'],
                        date_joined=row['date_joined']
                    )
            elif file_type == 'inventory':
                for _, row in df.iterrows():
                    date_str = row['expiration_date']
                    date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                    formatted_date = date_obj.strftime('%Y-%m-%d')
                    
                    Inventory.objects.create(
                        title=row['title'],
                        description=row['description'],
                        remaining_count=row['remaining_count'],
                        expiration_date=formatted_date
                    )
            else:
                return JsonResponse({'error': 'Invalid file type'}, status=400)
                
            return JsonResponse({'message': f'{file_type} uploaded successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({
        'message': 'Please use POST request to upload CSV files',
        'supported_types': ['members', 'inventory']
    })


@csrf_exempt
def book_item(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        member = get_object_or_404(Member, id=data['member_id'])
        item = get_object_or_404(Inventory, id=data['item_id'])
        
        booking = Booking.objects.create(member=member, item=item)
        return JsonResponse({
            'message': 'Booking successful',
            'booking_id': booking.id
        })


@csrf_exempt
def cancel_booking(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            booking_id = data.get('booking_id')
            
            if not booking_id:
                return JsonResponse({'error': 'booking_id is required'}, status=400)
            
            booking = Booking.objects.get(id=booking_id)
            
            item = booking.item
            item.remaining_count += 1
            item.save()
            
            member = booking.member
            member.booking_count -= 1
            member.save()
            
            booking.delete()
            
            return JsonResponse({'message': 'Booking cancelled successfully'})
        except Booking.DoesNotExist:
            return JsonResponse({'error': 'Booking not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)