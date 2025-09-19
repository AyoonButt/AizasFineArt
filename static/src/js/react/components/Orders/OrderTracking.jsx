import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const OrderTracking = ({ orderData }) => {
  const [order, setOrder] = useState(orderData);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [animationTrigger, setAnimationTrigger] = useState(0);

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
        // Trigger animation when status changes
        if (updatedOrder.tracking_percentage !== order.tracking_percentage) {
          setAnimationTrigger(prev => prev + 1);
        }
        setOrder(updatedOrder);
      }
    } catch (error) {
      console.error('Failed to refresh order status:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  // Define the 4 tracking steps with enhanced icons
  const TRACKING_STEPS = [
    {
      id: 'confirmed',
      title: 'Order Confirmed',
      description: 'Payment processed successfully',
      percentage: 25,
      status: ['confirmed', 'processing', 'shipped', 'delivered']
    },
    {
      id: 'processing',
      title: 'In Production', 
      description: 'Creating your prints',
      percentage: 50,
      status: ['processing', 'shipped', 'delivered']
    },
    {
      id: 'shipped',
      title: 'Shipped',
      description: 'Package in transit',
      percentage: 75,
      status: ['shipped', 'delivered']
    },
    {
      id: 'delivered', 
      title: 'Delivered',
      description: 'Enjoy your artwork!',
      percentage: 100,
      status: ['delivered']
    }
  ];

  // Enhanced icon components with website theme colors
  const StepIcon = ({ stepId, isCompleted, isCurrent }) => {
    const baseIconClass = "w-8 h-8";
    const iconClass = isCompleted ? "text-white" : isCurrent ? "text-white" : "text-gray-400";
    
    const iconVariants = {
      completed: { scale: [1, 1.2, 1], transition: { duration: 0.5 } },
      current: { 
        scale: [1, 1.1, 1], 
        transition: { duration: 2, repeat: Infinity, ease: "easeInOut" }
      },
      pending: { scale: 1 }
    };

    const getAnimationState = () => {
      if (isCompleted) return "completed";
      if (isCurrent) return "current"; 
      return "pending";
    };

    switch (stepId) {
      case 'confirmed':
        return (
          <motion.svg 
            className={`${baseIconClass} ${iconClass}`}
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
            variants={iconVariants}
            animate={getAnimationState()}
          >
            {/* Credit card with checkmark for payment confirmation */}
            <rect x="2" y="6" width="20" height="12" rx="2" strokeWidth="2"/>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2 10h20"/>
            {isCompleted ? (
              <motion.g>
                <motion.path
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth="2.5"
                  d="m7 13 2 2 4-4"
                  stroke="#A38194"
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{ duration: 0.6, delay: 0.2 }}
                />
              </motion.g>
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M6 14h6" opacity="0.4"/>
            )}
          </motion.svg>
        );
      
      case 'processing':
        return (
          <motion.svg 
            className={`${baseIconClass} ${iconClass}`}
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
            variants={iconVariants}
            animate={getAnimationState()}
          >
            {/* Printer/production icon for processing */}
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/>
            {(isCurrent || isCompleted) && (
              <motion.g>
                <motion.circle 
                  cx="18" cy="12" r="1.5" 
                  fill="currentColor"
                  animate={{ opacity: [1, 0.3, 1] }}
                  transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                />
                <motion.path
                  strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" 
                  d="M9 15h6" 
                  opacity="0.6"
                  animate={{ scaleX: [1, 0.8, 1] }}
                  transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                />
              </motion.g>
            )}
          </motion.svg>
        );
      
      case 'shipped':
        return (
          <motion.svg 
            className={`${baseIconClass} ${iconClass}`}
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
            variants={iconVariants}
            animate={getAnimationState()}
          >
            {/* Clean delivery truck icon */}
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM21 17a2 2 0 11-4 0 2 2 0 014 0z"/>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6"/>
            <rect x="14" y="6" width="8" height="6" rx="1" strokeWidth="2"/>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 9h6"/>
            {isCurrent && (
              <motion.g
                animate={{ x: [0, 1, 0], y: [0, -0.5, 0] }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M2 8l2-2m0 0l2 2" opacity="0.7"/>
              </motion.g>
            )}
          </motion.svg>
        );
      
      case 'delivered':
        return (
          <motion.svg 
            className={`${baseIconClass} ${iconClass}`}
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
            variants={iconVariants}
            animate={getAnimationState()}
          >
            {/* Package with checkmark for delivery */}
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10"/>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 7v10l8 4"/>
            {isCompleted && (
              <motion.g
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.3 }}
              >
                <circle cx="18" cy="6" r="3.5" fill="#A38194" stroke="white" strokeWidth="2"/>
                <motion.path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2.5"
                  d="m16.5 6 1 1 2-2"
                  stroke="white"
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{ duration: 0.4, delay: 0.6 }}
                />
              </motion.g>
            )}
            {isCurrent && !isCompleted && (
              <motion.g
                animate={{ scale: [1, 1.05, 1] }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
              >
                <circle cx="18" cy="6" r="2" stroke="currentColor" strokeWidth="1.5" opacity="0.6"/>
              </motion.g>
            )}
          </motion.svg>
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
      <div className="flex items-center justify-between mb-8">
        <div>
          <h3 className="text-2xl font-bold text-gray-900">Order Tracking</h3>
          <p className="text-sm text-gray-600 mt-1">Order #{order.order_number}</p>
        </div>
        <div className="flex items-center space-x-6">
          {order.tracking_number && (
            <div className="text-right">
              <p className="text-xs text-gray-500 uppercase tracking-wide">Tracking Number</p>
              <p className="font-mono text-sm font-semibold text-gray-900">{order.tracking_number}</p>
              {order.carrier_tracking_url && (
                <motion.a 
                  href={order.carrier_tracking_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-xs text-blue-600 hover:text-blue-800 underline font-medium"
                  whileHover={{ scale: 1.05 }}
                >
                  Track with {order.carrier}
                </motion.a>
              )}
            </div>
          )}
          <motion.button
            onClick={refreshOrderStatus}
            disabled={isRefreshing}
            className="p-3 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            animate={isRefreshing ? { rotate: 360 } : {}}
            transition={{ duration: 1, repeat: isRefreshing ? Infinity : 0, ease: "linear" }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
          </motion.button>
        </div>
      </div>

      {/* Horizontal 4-Step Progress Tracker */}
      <div className="relative mb-8">
        {/* Progress Background Line */}
        <div className="absolute top-6 left-8 right-8 h-1 bg-gray-200 rounded-full"></div>
        
        {/* Dynamic Progress Line */}
        <motion.div 
          className="absolute top-6 left-8 h-1 bg-gradient-to-r from-primary via-secondary to-mauve-plum rounded-full"
          initial={{ width: "0%" }}
          animate={{ 
            width: `${Math.max(0, ((order.tracking_percentage / 100) * 100) - 6)}%` 
          }}
          transition={{ 
            duration: 1.2, 
            ease: "easeOut",
            delay: 0.3 
          }}
          key={animationTrigger} // Retrigger animation on status change
        />

        {/* Step Indicators */}
        <div className="relative flex justify-between">
          {TRACKING_STEPS.map((step, index) => {
            const isCompleted = order.status && step.status.includes(order.status);
            const isCurrent = !isCompleted && 
              (index === 0 || TRACKING_STEPS[index - 1].status.includes(order.status));
            
            const stepTimestamp = order.tracking_stages?.find(s => s.key === step.id)?.timestamp;

            return (
              <motion.div 
                key={step.id}
                className="flex flex-col items-center"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 + 0.2 }}
              >
                {/* Step Circle with Icon */}
                <motion.div 
                  className={`
                    relative z-10 w-12 h-12 rounded-full flex items-center justify-center border-4 transition-colors
                    ${isCompleted 
                      ? 'bg-mauve-plum border-mauve-plum shadow-lg shadow-mauve-plum/25' 
                      : isCurrent 
                      ? 'bg-primary border-primary shadow-lg shadow-primary/25'
                      : 'bg-white border-gray-300'
                    }
                  `}
                  animate={isCurrent ? { 
                    boxShadow: ["0 0 0 0 rgba(156, 107, 104, 0.4)", "0 0 0 10px rgba(156, 107, 104, 0)", "0 0 0 0 rgba(156, 107, 104, 0.4)"]
                  } : {}}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <StepIcon 
                    stepId={step.id} 
                    isCompleted={isCompleted} 
                    isCurrent={isCurrent}
                  />
                  
                  {/* Completion Checkmark Overlay */}
                  {isCompleted && (
                    <motion.div 
                      className="absolute inset-0 flex items-center justify-center"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ duration: 0.3, delay: 0.4 }}
                    >
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <motion.path
                          strokeLinecap="round" 
                          strokeLinejoin="round" 
                          strokeWidth="3"
                          d="M5 13l4 4L19 7"
                          initial={{ pathLength: 0 }}
                          animate={{ pathLength: 1 }}
                          transition={{ duration: 0.5, delay: 0.5 }}
                        />
                      </svg>
                    </motion.div>
                  )}
                </motion.div>

                {/* Step Labels */}
                <div className="mt-4 text-center max-w-[120px]">
                  <motion.h4 
                    className={`text-sm font-semibold ${
                      isCompleted ? 'text-green-600' : isCurrent ? 'text-blue-600' : 'text-gray-500'
                    }`}
                    animate={isCurrent ? { scale: [1, 1.05, 1] } : {}}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    {step.title}
                  </motion.h4>
                  <p className={`text-xs mt-1 ${
                    isCompleted ? 'text-gray-700' : isCurrent ? 'text-gray-600' : 'text-gray-400'
                  }`}>
                    {step.description}
                  </p>
                  
                  {/* Timestamp */}
                  {stepTimestamp && (
                    <motion.p 
                      className="text-xs text-gray-500 mt-1 font-mono"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.8 }}
                    >
                      {formatDate(stepTimestamp)}
                    </motion.p>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Progress Percentage Display */}
        <motion.div 
          className="flex justify-center mt-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
        >
          <div className="bg-gray-50 px-4 py-2 rounded-full border">
            <span className="text-sm font-medium text-gray-700">
              {order.tracking_percentage}% Complete
            </span>
          </div>
        </motion.div>
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