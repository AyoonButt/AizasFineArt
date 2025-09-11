import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const OrderTracking = ({ orderData }) => {
  const [order, setOrder] = useState(orderData);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Auto-refresh order status every 30 seconds
  useEffect(() => {
    const interval = setInterval(async () => {
      if (order.status !== 'delivered' && order.status !== 'cancelled') {
        await refreshOrderStatus();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [order.status]);

  const refreshOrderStatus = async () => {
    setIsRefreshing(true);
    try {
      const response = await fetch(`/orders/api/${order.order_number}/status/`);
      if (response.ok) {
        const updatedOrder = await response.json();
        setOrder(updatedOrder);
      }
    } catch (error) {
      console.error('Failed to refresh order status:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  const getStageIcon = (icon, completed) => {
    const iconClass = `w-5 h-5 ${completed ? 'text-white' : 'text-gray-500'}`;
    
    switch (icon) {
      case 'check-circle':
        return (
          <svg className={iconClass} fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
          </svg>
        );
      case 'cog':
        return (
          <motion.svg 
            className={iconClass} 
            fill="currentColor" 
            viewBox="0 0 20 20"
            animate={completed ? { rotate: 360 } : {}}
            transition={{ duration: 2, repeat: completed ? Infinity : 0, ease: "linear" }}
          >
            <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd"></path>
          </motion.svg>
        );
      case 'truck':
        return (
          <motion.svg 
            className={iconClass} 
            fill="currentColor" 
            viewBox="0 0 20 20"
            animate={completed ? { x: [0, 5, 0] } : {}}
            transition={{ duration: 1.5, repeat: completed ? Infinity : 0, ease: "easeInOut" }}
          >
            <path d="M8 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM15 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z"></path>
            <path d="M3 4a1 1 0 00-1 1v10a1 1 0 001 1h1.05a2.5 2.5 0 014.9 0H10a1 1 0 001-1V5a1 1 0 00-1-1H3zM14 7a1 1 0 00-1 1v6.05A2.5 2.5 0 0115.95 16H17a1 1 0 001-1v-5a1 1 0 00-.293-.707L16 7.586A1 1 0 0015.414 7H14z"></path>
          </motion.svg>
        );
      case 'home':
        return (
          <svg className={iconClass} fill="currentColor" viewBox="0 0 20 20">
            <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"></path>
          </svg>
        );
      default:
        return null;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return null;
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
  };

  return (
    <motion.div 
      className="bg-white rounded-lg shadow-lg p-6 mb-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-semibold text-gray-900">Order Tracking</h3>
          <p className="text-sm text-gray-600">Order #{order.order_number}</p>
        </div>
        <div className="flex items-center space-x-4">
          {order.tracking_number && (
            <div className="text-right">
              <p className="text-sm text-gray-600">Tracking Number</p>
              <p className="font-mono text-sm font-medium">{order.tracking_number}</p>
              {order.carrier_tracking_url && (
                <a href={order.carrier_tracking_url} target="_blank" rel="noopener noreferrer"
                   className="text-xs text-blue-600 hover:text-blue-800 underline">
                  Track with {order.carrier}
                </a>
              )}
            </div>
          )}
          <motion.button
            onClick={refreshOrderStatus}
            disabled={isRefreshing}
            className="p-2 text-gray-400 hover:text-gray-600 focus:outline-none"
            animate={isRefreshing ? { rotate: 360 } : {}}
            transition={{ duration: 1, repeat: isRefreshing ? Infinity : 0, ease: "linear" }}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
          </motion.button>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Progress</span>
          <span className="text-sm text-gray-600">{order.tracking_percentage}% Complete</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <motion.div 
            className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${order.tracking_percentage}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
          />
        </div>
      </div>

      {/* Tracking Stages */}
      <div className="space-y-4">
        {order.tracking_stages?.map((stage, index) => (
          <motion.div 
            key={stage.key}
            className="flex items-start space-x-4"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            {/* Icon */}
            <div className="flex-shrink-0">
              <motion.div 
                className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  stage.completed ? 'bg-green-500' : 'bg-gray-300'
                }`}
                animate={stage.completed ? { scale: [1, 1.1, 1] } : {}}
                transition={{ duration: 0.3 }}
              >
                {getStageIcon(stage.icon, stage.completed)}
              </motion.div>
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <p className={`text-sm font-medium ${
                  stage.completed ? 'text-gray-900' : 'text-gray-500'
                }`}>
                  {stage.title}
                </p>
                {stage.timestamp && (
                  <p className="text-xs text-gray-500">
                    {formatDate(stage.timestamp)}
                  </p>
                )}
              </div>
              <p className={`text-sm ${
                stage.completed ? 'text-gray-600' : 'text-gray-400'
              }`}>
                {stage.description}
              </p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* LumaPrints Status Details */}
      <AnimatePresence>
        {order.luma_prints_status && (
          <motion.div 
            className="mt-6 pt-6 border-t border-gray-200"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <h4 className="text-sm font-medium text-gray-900 mb-3">Production Details</h4>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-gray-600">LumaPrints Status</p>
                  <p className="text-sm font-medium text-gray-900">
                    {order.luma_prints_status?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </p>
                </div>
                {order.luma_prints_updated_at && (
                  <div>
                    <p className="text-xs text-gray-600">Last Updated</p>
                    <p className="text-sm font-medium text-gray-900">
                      {formatDate(order.luma_prints_updated_at)}
                    </p>
                  </div>
                )}
                {order.estimated_delivery && (
                  <div>
                    <p className="text-xs text-gray-600">Estimated Delivery</p>
                    <p className="text-sm font-medium text-gray-900">
                      {formatDate(order.estimated_delivery)}
                    </p>
                  </div>
                )}
                {order.carrier && (
                  <div>
                    <p className="text-xs text-gray-600">Shipping Carrier</p>
                    <p className="text-sm font-medium text-gray-900">{order.carrier}</p>
                  </div>
                )}
              </div>
              
              {order.luma_prints_tracking_url && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <motion.a 
                    href={order.luma_prints_tracking_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                    </svg>
                    View Detailed Tracking
                  </motion.a>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Order Status Timeline */}
      <AnimatePresence>
        {order.status_updates?.length > 0 && (
          <motion.div 
            className="mt-6 pt-6 border-t border-gray-200"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <h4 className="text-sm font-medium text-gray-900 mb-3">Order History</h4>
            <div className="space-y-3">
              {order.status_updates.map((update, index) => (
                <motion.div 
                  key={update.id || index}
                  className="flex items-start space-x-3"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                >
                  <div className="flex-shrink-0 w-2 h-2 bg-blue-400 rounded-full mt-2"></div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900">
                      <span className="font-medium">
                        {update.new_status?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </span>
                      <span className="text-gray-500 ml-2">
                        {formatDate(update.timestamp)}
                      </span>
                    </p>
                    {update.notes && (
                      <p className="text-xs text-gray-600 mt-1">{update.notes}</p>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default OrderTracking;