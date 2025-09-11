"""
Luma Prints API Integration
Handles communication with Luma Prints for print order fulfillment
"""
import requests
import json
from typing import Dict, List, Optional, Union
from decimal import Decimal
from django.conf import settings


class LumaPrintsAPI:
    """
    Luma Prints API client for handling print orders
    """
    
    def __init__(self):
        """Initialize API client with credentials"""
        self.api_key = getattr(settings, 'LUMA_PRINTS_API_KEY', '')
        self.base_url = getattr(settings, 'LUMA_PRINTS_BASE_URL', 'https://api.lumaprints.com/v1')
        self.test_mode = getattr(settings, 'LUMA_PRINTS_TEST_MODE', True)
        
        # Common headers for all requests
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if not self.api_key:
            raise ValueError('LUMA_PRINTS_API_KEY setting is required')
    
    def create_print_order(self, order_data: Dict) -> Dict:
        """
        Create a new print order with Luma Prints
        
        Args:
            order_data: Dict containing order information
            
        Returns:
            Dict with Luma Prints order response
        """
        try:
            # Prepare order payload
            payload = self._prepare_order_payload(order_data)
            
            # Make API request
            endpoint = f"{self.base_url}/orders"
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise LumaPrintsAPIError(f"Failed to create print order: {str(e)}")
        except Exception as e:
            raise LumaPrintsAPIError(f"Unexpected error creating print order: {str(e)}")
    
    def get_order_status(self, luma_order_id: str) -> Dict:
        """
        Get the status of a print order
        
        Args:
            luma_order_id: Luma Prints order ID
            
        Returns:
            Dict with order status information
        """
        try:
            endpoint = f"{self.base_url}/orders/{luma_order_id}"
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise LumaPrintsAPIError(f"Failed to get order status: {str(e)}")
    
    def get_shipping_rates(self, shipping_info: Dict) -> List[Dict]:
        """
        Get available shipping rates for an order
        
        Args:
            shipping_info: Dict with shipping address and items
            
        Returns:
            List of available shipping options with rates
        """
        try:
            endpoint = f"{self.base_url}/shipping/rates"
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=shipping_info,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json().get('rates', [])
            
        except requests.exceptions.RequestException as e:
            raise LumaPrintsAPIError(f"Failed to get shipping rates: {str(e)}")
    
    def cancel_order(self, luma_order_id: str) -> Dict:
        """
        Cancel a print order
        
        Args:
            luma_order_id: Luma Prints order ID
            
        Returns:
            Dict with cancellation response
        """
        try:
            endpoint = f"{self.base_url}/orders/{luma_order_id}/cancel"
            response = requests.post(
                endpoint,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise LumaPrintsAPIError(f"Failed to cancel order: {str(e)}")
    
    def get_product_catalog(self) -> List[Dict]:
        """
        Get available print products and specifications
        
        Returns:
            List of available products with specifications
        """
        try:
            endpoint = f"{self.base_url}/products"
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json().get('products', [])
            
        except requests.exceptions.RequestException as e:
            raise LumaPrintsAPIError(f"Failed to get product catalog: {str(e)}")
    
    def create_product(self, artwork_data: Dict) -> Dict:
        """
        Create a new print product in LumaPrints catalog
        
        Args:
            artwork_data: Dict containing artwork information
            
        Returns:
            Dict with LumaPrints product response including product_id
        """
        try:
            # Prepare product payload
            payload = self._prepare_product_payload(artwork_data)
            
            # Make API request
            endpoint = f"{self.base_url}/products"
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise LumaPrintsAPIError(f"Failed to create product: {str(e)}")
        except Exception as e:
            raise LumaPrintsAPIError(f"Unexpected error creating product: {str(e)}")
    
    def update_product(self, product_id: str, artwork_data: Dict) -> Dict:
        """
        Update an existing print product in LumaPrints catalog
        
        Args:
            product_id: LumaPrints product ID
            artwork_data: Dict containing updated artwork information
            
        Returns:
            Dict with LumaPrints product response
        """
        try:
            # Prepare product payload
            payload = self._prepare_product_payload(artwork_data)
            
            # Make API request
            endpoint = f"{self.base_url}/products/{product_id}"
            response = requests.put(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise LumaPrintsAPIError(f"Failed to update product: {str(e)}")
        except Exception as e:
            raise LumaPrintsAPIError(f"Unexpected error updating product: {str(e)}")
    
    def delete_product(self, product_id: str) -> Dict:
        """
        Delete a print product from LumaPrints catalog
        
        Args:
            product_id: LumaPrints product ID
            
        Returns:
            Dict with deletion response
        """
        try:
            endpoint = f"{self.base_url}/products/{product_id}"
            response = requests.delete(
                endpoint,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise LumaPrintsAPIError(f"Failed to delete product: {str(e)}")
    
    def _prepare_order_payload(self, order_data: Dict) -> Dict:
        """
        Prepare order data for Luma Prints API
        
        Args:
            order_data: Django order data
            
        Returns:
            Dict formatted for Luma Prints API
        """
        # Extract Django order object
        order = order_data['order']
        print_items = order_data['print_items']
        
        # Prepare items for Luma Prints
        items = []
        for item in print_items:
            luma_item = {
                'sku': self._get_luma_sku(item.item_type),
                'quantity': item.quantity,
                'artwork_url': item.artwork.gallery_image,
                'artwork_name': item.artwork.title,
                'print_specifications': {
                    'size': self._parse_print_size(item.item_type),
                    'material': 'fine_art_paper',  # Default material
                    'finish': 'matte',  # Default finish
                },
                'metadata': {
                    'artwork_id': str(item.artwork.id),
                    'order_item_id': str(item.id),
                    'artist': 'Aiza\'s Fine Art'
                }
            }
            items.append(luma_item)
        
        # Prepare shipping address
        shipping_address = {
            'name': order.shipping_name or order.billing_name,
            'address_line_1': order.shipping_address_1 or order.billing_address_1,
            'address_line_2': order.shipping_address_2 or order.billing_address_2,
            'city': order.shipping_city or order.billing_city,
            'state': order.shipping_state or order.billing_state,
            'postal_code': order.shipping_postal_code or order.billing_postal_code,
            'country': order.shipping_country or order.billing_country or 'US',
        }
        
        # Remove empty values
        shipping_address = {k: v for k, v in shipping_address.items() if v}
        
        # Prepare full payload
        payload = {
            'external_order_id': order.order_number,
            'items': items,
            'shipping_address': shipping_address,
            'shipping_method': 'standard',  # Default shipping
            'test_mode': self.test_mode,
            'metadata': {
                'source': 'aizasfineart_website',
                'order_id': str(order.id),
                'customer_email': order.billing_email,
            }
        }
        
        return payload
    
    def _get_luma_sku(self, item_type: str) -> str:
        """
        Map internal item types to Luma Prints SKUs
        
        Args:
            item_type: Internal item type (e.g., 'print-8x10')
            
        Returns:
            Luma Prints SKU
        """
        # Map our print types to Luma Prints SKUs
        sku_map = {
            'print-8x10': 'PRINT_8X10_FINE_ART',
            'print-11x14': 'PRINT_11X14_FINE_ART',
            'print-16x20': 'PRINT_16X20_FINE_ART',
            'print-24x30': 'PRINT_24X30_FINE_ART',
        }
        
        return sku_map.get(item_type, 'PRINT_8X10_FINE_ART')
    
    def _parse_print_size(self, item_type: str) -> Dict[str, int]:
        """
        Parse print size from item type
        
        Args:
            item_type: Item type like 'print-8x10'
            
        Returns:
            Dict with width and height in inches
        """
        size_map = {
            'print-8x10': {'width': 8, 'height': 10},
            'print-11x14': {'width': 11, 'height': 14},
            'print-16x20': {'width': 16, 'height': 20},
            'print-24x30': {'width': 24, 'height': 30},
        }
        
        return size_map.get(item_type, {'width': 8, 'height': 10})
    
    def _prepare_product_payload(self, artwork_data: Dict) -> Dict:
        """
        Prepare artwork data for LumaPrints product creation
        
        Args:
            artwork_data: Dict containing artwork information
            
        Returns:
            Dict formatted for LumaPrints product API
        """
        artwork = artwork_data['artwork']
        image_url = artwork_data.get('image_url', artwork.get_simple_signed_url())
        
        # Prepare product payload
        payload = {
            'name': artwork.title,
            'description': artwork.description or f"Fine art print of {artwork.title}",
            'external_id': str(artwork.id),  # Our artwork ID for reference
            'artwork_url': image_url,
            'artist_name': 'Aiza',
            'artwork_metadata': {
                'title': artwork.title,
                'medium': artwork.get_medium_display(),
                'year_created': artwork.year_created,
                'dimensions': f"{artwork.dimensions_width}\" × {artwork.dimensions_height}\"",
                'category': artwork.category.name if artwork.category else '',
            },
            'print_options': [
                {
                    'size': '8x10',
                    'material': 'fine_art_paper',
                    'finish': 'matte',
                    'price': 45.00,
                    'sku': f'PRINT_8X10_{artwork.id}'
                },
                {
                    'size': '11x14',
                    'material': 'fine_art_paper',
                    'finish': 'matte',
                    'price': 65.00,
                    'sku': f'PRINT_11X14_{artwork.id}'
                },
                {
                    'size': '16x20',
                    'material': 'fine_art_paper',
                    'finish': 'matte',
                    'price': 95.00,
                    'sku': f'PRINT_16X20_{artwork.id}'
                },
                {
                    'size': '24x30',
                    'material': 'fine_art_paper',
                    'finish': 'matte',
                    'price': 150.00,
                    'sku': f'PRINT_24X30_{artwork.id}'
                }
            ],
            'status': 'active',
            'test_mode': self.test_mode
        }
        
        return payload


class LumaPrintsWebhookHandler:
    """
    Handle webhooks from Luma Prints for order status updates
    """
    
    def __init__(self):
        self.webhook_secret = getattr(settings, 'LUMA_PRINTS_WEBHOOK_SECRET', '')
    
    def handle_webhook(self, payload: Dict, signature: str) -> Dict:
        """
        Process incoming webhook from Luma Prints
        
        Args:
            payload: Webhook payload
            signature: Webhook signature for verification
            
        Returns:
            Dict with processing result
        """
        try:
            # Verify webhook signature
            if not self._verify_signature(payload, signature):
                raise LumaPrintsAPIError('Invalid webhook signature')
            
            # Process based on event type
            event_type = payload.get('event_type')
            
            if event_type == 'order.status_changed':
                return self._handle_order_status_change(payload)
            elif event_type == 'order.shipped':
                return self._handle_order_shipped(payload)
            elif event_type == 'order.delivered':
                return self._handle_order_delivered(payload)
            else:
                return {'status': 'ignored', 'message': f'Unknown event type: {event_type}'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _verify_signature(self, payload: Dict, signature: str) -> bool:
        """
        Verify webhook signature for security
        
        Args:
            payload: Webhook payload
            signature: Signature to verify
            
        Returns:
            True if signature is valid
        """
        if not self.webhook_secret:
            # If no secret configured, skip verification (not recommended for production)
            return True
        
        import hmac
        import hashlib
        
        # Calculate expected signature
        payload_string = json.dumps(payload, sort_keys=True)
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f'sha256={expected_signature}', signature)
    
    def _handle_order_status_change(self, payload: Dict) -> Dict:
        """Handle order status change webhook"""
        from .models import Order, OrderStatusUpdate
        from django.utils import timezone
        
        try:
            # Find order by external ID
            external_order_id = payload.get('external_order_id')
            order = Order.objects.get(order_number=external_order_id)
            
            # Store previous status for tracking
            previous_status = order.status
            
            # Update order with Luma Prints information
            luma_status = payload.get('status')
            order.luma_prints_order_id = payload.get('luma_order_id', order.luma_prints_order_id)
            order.luma_prints_status = luma_status
            order.luma_prints_updated_at = timezone.now()
            
            # Update tracking URL if provided
            if payload.get('tracking_url'):
                order.luma_prints_tracking_url = payload.get('tracking_url')
            
            # Update estimated delivery if provided
            if payload.get('estimated_delivery'):
                try:
                    from datetime import datetime
                    estimated_date = datetime.fromisoformat(payload['estimated_delivery'])
                    order.estimated_delivery = estimated_date
                except (ValueError, TypeError):
                    pass
            
            # Map Luma status to our status
            status_mapping = {
                'pending': 'confirmed',
                'processing': 'processing',
                'printed': 'processing',
                'quality_check': 'processing',
                'packaged': 'processing',
                'shipped': 'shipped',
                'in_transit': 'shipped',
                'out_for_delivery': 'shipped',
                'delivered': 'delivered',
                'cancelled': 'cancelled',
                'returned': 'cancelled'
            }
            
            if luma_status in status_mapping:
                new_status = status_mapping[luma_status]
                order.status = new_status
                
                # Update specific timestamps
                if new_status == 'confirmed' and not order.confirmed_at:
                    order.confirmed_at = timezone.now()
                elif new_status == 'shipped' and not order.shipped_at:
                    order.shipped_at = timezone.now()
                elif new_status == 'delivered' and not order.delivered_at:
                    order.delivered_at = timezone.now()
                
                order.save()
                
                # Create status update record
                OrderStatusUpdate.objects.create(
                    order=order,
                    previous_status=previous_status,
                    new_status=new_status,
                    notes=f'Updated via LumaPrints webhook. Luma status: {luma_status}'
                )
            
            return {'status': 'success', 'message': 'Order status updated'}
            
        except Order.DoesNotExist:
            return {'status': 'error', 'message': 'Order not found'}
    
    def _handle_order_shipped(self, payload: Dict) -> Dict:
        """Handle order shipped webhook"""
        from .models import Order, OrderStatusUpdate
        from django.utils import timezone
        
        try:
            external_order_id = payload.get('external_order_id')
            order = Order.objects.get(order_number=external_order_id)
            
            # Store previous status
            previous_status = order.status
            
            # Update order with comprehensive shipping information
            order.status = 'shipped'
            order.shipped_at = timezone.now()
            order.tracking_number = payload.get('tracking_number', '')
            order.carrier = payload.get('carrier', '').upper()
            order.luma_prints_status = 'shipped'
            order.luma_prints_updated_at = timezone.now()
            
            # Update tracking URLs
            if payload.get('tracking_url'):
                order.luma_prints_tracking_url = payload.get('tracking_url')
            
            # Update estimated delivery
            if payload.get('estimated_delivery'):
                try:
                    from datetime import datetime
                    estimated_date = datetime.fromisoformat(payload['estimated_delivery'])
                    order.estimated_delivery = estimated_date
                except (ValueError, TypeError):
                    pass
            
            order.save()
            
            # Create detailed status update
            tracking_info = f"Tracking: {order.tracking_number}" if order.tracking_number else "No tracking number provided"
            carrier_info = f"Carrier: {order.carrier}" if order.carrier else ""
            notes_parts = [f'Shipped by Luma Prints', tracking_info, carrier_info]
            notes = '. '.join([part for part in notes_parts if part])
            
            OrderStatusUpdate.objects.create(
                order=order,
                previous_status=previous_status,
                new_status='shipped',
                notes=notes
            )
            
            return {'status': 'success', 'message': 'Order marked as shipped'}
            
        except Order.DoesNotExist:
            return {'status': 'error', 'message': 'Order not found'}
    
    def _handle_order_delivered(self, payload: Dict) -> Dict:
        """Handle order delivered webhook"""
        from .models import Order
        from django.utils import timezone
        
        try:
            external_order_id = payload.get('external_order_id')
            order = Order.objects.get(order_number=external_order_id)
            
            # Update order status
            order.status = 'delivered'
            order.delivered_at = timezone.now()
            order.save()
            
            return {'status': 'success', 'message': 'Order marked as delivered'}
            
        except Order.DoesNotExist:
            return {'status': 'error', 'message': 'Order not found'}


class LumaPrintsAPIError(Exception):
    """Custom exception for Luma Prints API errors"""
    pass


def send_print_order_to_luma(order):
    """
    Helper function to send print orders to Luma Prints
    
    Args:
        order: Django Order instance
        
    Returns:
        Dict with Luma Prints response
    """
    # Get print items from order
    print_items = [item for item in order.items.all() if 'print' in item.item_type]
    
    if not print_items:
        return {'status': 'no_prints', 'message': 'No print items found in order'}
    
    try:
        # Initialize API client
        api = LumaPrintsAPI()
        
        # Prepare order data
        order_data = {
            'order': order,
            'print_items': print_items
        }
        
        # Send to Luma Prints
        response = api.create_print_order(order_data)
        
        # Update order with Luma Prints ID
        if response.get('order_id'):
            order.luma_prints_order_id = response['order_id']
            order.save()
        
        return {
            'status': 'success',
            'luma_order_id': response.get('order_id'),
            'message': 'Print order sent to Luma Prints successfully'
        }
        
    except LumaPrintsAPIError as e:
        return {'status': 'error', 'message': str(e)}


def create_luma_prints_product(artwork, image_url=None):
    """
    Helper function to create a new print product in LumaPrints for an artwork
    
    Args:
        artwork: Django Artwork instance
        image_url: Optional image URL, if not provided will use artwork.get_simple_signed_url()
        
    Returns:
        Dict with LumaPrints response including product_id
    """
    try:
        # Initialize API client
        api = LumaPrintsAPI()
        
        # Prepare artwork data
        artwork_data = {
            'artwork': artwork,
            'image_url': image_url or artwork.get_simple_signed_url()
        }
        
        # Create product in LumaPrints
        response = api.create_product(artwork_data)
        
        # Update artwork with LumaPrints product ID
        if response.get('product_id'):
            artwork.lumaprints_product_id = response['product_id']
            artwork.save(update_fields=['lumaprints_product_id'])
        
        return {
            'status': 'success',
            'product_id': response.get('product_id'),
            'message': 'Product created in LumaPrints successfully'
        }
        
    except LumaPrintsAPIError as e:
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        return {'status': 'error', 'message': f'Unexpected error: {str(e)}'}


def update_luma_prints_product(artwork, image_url=None):
    """
    Helper function to update an existing print product in LumaPrints
    
    Args:
        artwork: Django Artwork instance with lumaprints_product_id
        image_url: Optional image URL, if not provided will use artwork.get_simple_signed_url()
        
    Returns:
        Dict with LumaPrints response
    """
    if not artwork.lumaprints_product_id:
        return {'status': 'error', 'message': 'No LumaPrints product ID found for this artwork'}
    
    try:
        # Initialize API client
        api = LumaPrintsAPI()
        
        # Prepare artwork data
        artwork_data = {
            'artwork': artwork,
            'image_url': image_url or artwork.get_simple_signed_url()
        }
        
        # Update product in LumaPrints
        response = api.update_product(artwork.lumaprints_product_id, artwork_data)
        
        return {
            'status': 'success',
            'product_id': artwork.lumaprints_product_id,
            'message': 'Product updated in LumaPrints successfully'
        }
        
    except LumaPrintsAPIError as e:
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        return {'status': 'error', 'message': f'Unexpected error: {str(e)}'}


def delete_luma_prints_product(artwork):
    """
    Helper function to delete a print product from LumaPrints
    
    Args:
        artwork: Django Artwork instance with lumaprints_product_id
        
    Returns:
        Dict with deletion response
    """
    if not artwork.lumaprints_product_id:
        return {'status': 'error', 'message': 'No LumaPrints product ID found for this artwork'}
    
    try:
        # Initialize API client
        api = LumaPrintsAPI()
        
        # Delete product from LumaPrints
        response = api.delete_product(artwork.lumaprints_product_id)
        
        # Clear LumaPrints product ID from artwork
        artwork.lumaprints_product_id = ''
        artwork.save(update_fields=['lumaprints_product_id'])
        
        return {
            'status': 'success',
            'message': 'Product deleted from LumaPrints successfully'
        }
        
    except LumaPrintsAPIError as e:
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        return {'status': 'error', 'message': f'Unexpected error: {str(e)}'}
    except Exception as e:
        return {'status': 'error', 'message': f'Unexpected error: {str(e)}'}


def check_luma_order_status(order):
    """
    Check the status of a print order with Luma Prints
    
    Args:
        order: Django Order instance
        
    Returns:
        Dict with order status information
    """
    if not order.luma_prints_order_id:
        return {'status': 'error', 'message': 'No Luma Prints order ID found'}
    
    try:
        api = LumaPrintsAPI()
        status_info = api.get_order_status(order.luma_prints_order_id)
        
        return {
            'status': 'success',
            'luma_status': status_info.get('status'),
            'tracking_info': status_info.get('tracking'),
            'estimated_delivery': status_info.get('estimated_delivery')
        }
        
    except LumaPrintsAPIError as e:
        return {'status': 'error', 'message': str(e)}


def create_luma_prints_product(artwork, image_url=None):
    """
    Helper function to create a new print product in LumaPrints for an artwork
    
    Args:
        artwork: Django Artwork instance
        image_url: Optional image URL, if not provided will use artwork.get_simple_signed_url()
        
    Returns:
        Dict with LumaPrints response including product_id
    """
    try:
        # Initialize API client
        api = LumaPrintsAPI()
        
        # Prepare artwork data
        artwork_data = {
            'artwork': artwork,
            'image_url': image_url or artwork.get_simple_signed_url()
        }
        
        # Create product in LumaPrints
        response = api.create_product(artwork_data)
        
        # Update artwork with LumaPrints product ID
        if response.get('product_id'):
            artwork.lumaprints_product_id = response['product_id']
            artwork.save(update_fields=['lumaprints_product_id'])
        
        return {
            'status': 'success',
            'product_id': response.get('product_id'),
            'message': 'Product created in LumaPrints successfully'
        }
        
    except LumaPrintsAPIError as e:
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        return {'status': 'error', 'message': f'Unexpected error: {str(e)}'}


def update_luma_prints_product(artwork, image_url=None):
    """
    Helper function to update an existing print product in LumaPrints
    
    Args:
        artwork: Django Artwork instance with lumaprints_product_id
        image_url: Optional image URL, if not provided will use artwork.get_simple_signed_url()
        
    Returns:
        Dict with LumaPrints response
    """
    if not artwork.lumaprints_product_id:
        return {'status': 'error', 'message': 'No LumaPrints product ID found for this artwork'}
    
    try:
        # Initialize API client
        api = LumaPrintsAPI()
        
        # Prepare artwork data
        artwork_data = {
            'artwork': artwork,
            'image_url': image_url or artwork.get_simple_signed_url()
        }
        
        # Update product in LumaPrints
        response = api.update_product(artwork.lumaprints_product_id, artwork_data)
        
        return {
            'status': 'success',
            'product_id': artwork.lumaprints_product_id,
            'message': 'Product updated in LumaPrints successfully'
        }
        
    except LumaPrintsAPIError as e:
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        return {'status': 'error', 'message': f'Unexpected error: {str(e)}'}


def delete_luma_prints_product(artwork):
    """
    Helper function to delete a print product from LumaPrints
    
    Args:
        artwork: Django Artwork instance with lumaprints_product_id
        
    Returns:
        Dict with deletion response
    """
    if not artwork.lumaprints_product_id:
        return {'status': 'error', 'message': 'No LumaPrints product ID found for this artwork'}
    
    try:
        # Initialize API client
        api = LumaPrintsAPI()
        
        # Delete product from LumaPrints
        response = api.delete_product(artwork.lumaprints_product_id)
        
        # Clear LumaPrints product ID from artwork
        artwork.lumaprints_product_id = ''
        artwork.save(update_fields=['lumaprints_product_id'])
        
        return {
            'status': 'success',
            'message': 'Product deleted from LumaPrints successfully'
        }
        
    except LumaPrintsAPIError as e:
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        return {'status': 'error', 'message': f'Unexpected error: {str(e)}'}