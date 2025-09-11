from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Order
from .serializers import OrderTrackingSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_status_api(request, order_number):
    """Get order status and tracking information"""
    try:
        order = get_object_or_404(
            Order, 
            order_number=order_number, 
            user=request.user
        )
        
        # Prepare tracking data
        tracking_data = {
            'order_number': order.order_number,
            'status': order.status,
            'tracking_number': order.tracking_number,
            'carrier': order.carrier,
            'carrier_tracking_url': order.get_carrier_tracking_url(),
            'estimated_delivery': order.estimated_delivery.isoformat() if order.estimated_delivery else None,
            'luma_prints_status': order.luma_prints_status,
            'luma_prints_tracking_url': order.luma_prints_tracking_url,
            'luma_prints_updated_at': order.luma_prints_updated_at.isoformat() if order.luma_prints_updated_at else None,
            'tracking_percentage': order.tracking_percentage,
            'current_stage': order.current_stage,
            'tracking_stages': [
                {
                    'key': stage['key'],
                    'title': stage['title'],
                    'description': stage['description'],
                    'completed': stage['completed'],
                    'timestamp': stage['timestamp'].isoformat() if stage['timestamp'] else None,
                    'icon': stage['icon']
                }
                for stage in order.tracking_stages
            ],
            'status_updates': [
                {
                    'id': update.id,
                    'previous_status': update.previous_status,
                    'new_status': update.new_status,
                    'notes': update.notes,
                    'timestamp': update.timestamp.isoformat()
                }
                for update in order.status_updates.all()[:10]  # Last 10 updates
            ]
        }
        
        return JsonResponse(tracking_data)
        
    except Order.DoesNotExist:
        return JsonResponse(
            {'error': 'Order not found'}, 
            status=404
        )
    except Exception as e:
        return JsonResponse(
            {'error': 'Internal server error'}, 
            status=500
        )


@api_view(['POST'])
def luma_prints_webhook(request):
    """Handle LumaPrints webhook notifications"""
    try:
        from .luma_prints_api import LumaPrintsWebhookHandler
        
        # Get webhook signature for verification
        signature = request.META.get('HTTP_X_LUMAPRINTS_SIGNATURE', '')
        
        # Handle the webhook
        handler = LumaPrintsWebhookHandler()
        result = handler.handle_webhook(request.data, signature)
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse(
            {'status': 'error', 'message': str(e)}, 
            status=500
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_order_status(request, order_number):
    """Manually refresh order status from LumaPrints"""
    try:
        order = get_object_or_404(
            Order, 
            order_number=order_number, 
            user=request.user
        )
        
        if not order.luma_prints_order_id:
            return JsonResponse(
                {'error': 'No LumaPrints order ID found'}, 
                status=400
            )
        
        # Check status with LumaPrints
        from .luma_prints_api import check_luma_order_status
        result = check_luma_order_status(order)
        
        if result['status'] == 'success':
            # Refresh order data
            order.refresh_from_db()
            
            # Return updated tracking data
            return order_status_api(request, order_number)
        else:
            return JsonResponse(
                {'error': result.get('message', 'Failed to refresh status')}, 
                status=400
            )
            
    except Order.DoesNotExist:
        return JsonResponse(
            {'error': 'Order not found'}, 
            status=404
        )
    except Exception as e:
        return JsonResponse(
            {'error': 'Internal server error'}, 
            status=500
        )