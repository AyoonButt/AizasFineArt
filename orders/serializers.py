from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusUpdate


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusUpdate
        fields = ['id', 'previous_status', 'new_status', 'notes', 'timestamp']


class OrderTrackingSerializer(serializers.ModelSerializer):
    tracking_stages = serializers.SerializerMethodField()
    tracking_percentage = serializers.SerializerMethodField()
    current_stage = serializers.SerializerMethodField()
    carrier_tracking_url = serializers.SerializerMethodField()
    status_updates = OrderStatusUpdateSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'order_number', 'status', 'tracking_number', 'carrier',
            'estimated_delivery', 'luma_prints_status', 
            'luma_prints_tracking_url', 'luma_prints_updated_at',
            'tracking_stages', 'tracking_percentage', 'current_stage',
            'carrier_tracking_url', 'status_updates'
        ]

    def get_tracking_stages(self, obj):
        return [
            {
                'key': stage['key'],
                'title': stage['title'],
                'description': stage['description'],
                'completed': stage['completed'],
                'timestamp': stage['timestamp'].isoformat() if stage['timestamp'] else None,
                'icon': stage['icon']
            }
            for stage in obj.tracking_stages
        ]

    def get_tracking_percentage(self, obj):
        return obj.tracking_percentage

    def get_current_stage(self, obj):
        return obj.current_stage

    def get_carrier_tracking_url(self, obj):
        return obj.get_carrier_tracking_url()


class OrderItemSerializer(serializers.ModelSerializer):
    artwork_title = serializers.CharField(source='artwork.title', read_only=True)
    artwork_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 'item_type', 'title', 'description', 'unit_price', 
            'quantity', 'total_price', 'print_size', 'print_material',
            'artwork_title', 'artwork_image'
        ]

    def get_artwork_image(self, obj):
        if obj.artwork and obj.artwork.image_url:
            return obj.artwork.image_url
        return None


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    tracking_data = OrderTrackingSerializer(source='*', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'order_number', 'status', 'payment_status', 'subtotal',
            'tax_amount', 'shipping_amount', 'total_amount',
            'billing_name', 'billing_email', 'shipping_name',
            'billing_address_display', 'shipping_address_display',
            'created_at', 'updated_at', 'items', 'tracking_data'
        ]