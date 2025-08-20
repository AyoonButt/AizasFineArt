import React from 'react';
import { motion } from 'framer-motion';

const Input = ({
  label,
  error,
  required = false,
  className = '',
  type = 'text',
  ...props
}) => {
  const hasError = !!error;

  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-neutral-700">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <motion.input
        type={type}
        className={`
          w-full px-3 py-2 border rounded-lg shadow-sm
          focus:outline-none focus:ring-2 focus:ring-offset-0
          ${hasError 
            ? 'border-red-300 focus:ring-red-500 focus:border-red-500' 
            : 'border-neutral-300 focus:ring-primary-500 focus:border-primary-500'
          }
          ${className}
        `}
        whileFocus={{ scale: 1.01 }}
        animate={hasError ? { x: [-2, 2, -2, 2, 0] } : {}}
        transition={{ duration: 0.4 }}
        {...props}
      />
      
      {error && (
        <motion.p
          className="text-sm text-red-600"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
        >
          {error}
        </motion.p>
      )}
    </div>
  );
};

export default Input;