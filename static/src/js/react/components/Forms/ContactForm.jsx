import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const ContactForm = ({ endpoint = '/htmx/contact/' }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null); // 'success' | 'error'
  const [submitMessage, setSubmitMessage] = useState('');

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 24,
        staggerChildren: 0.1
      }
    }
  };

  const fieldVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: { 
      opacity: 1, 
      x: 0,
      transition: { type: "spring", stiffness: 300, damping: 24 }
    }
  };

  const messageVariants = {
    hidden: { opacity: 0, scale: 0.9, y: -10 },
    visible: { 
      opacity: 1, 
      scale: 1, 
      y: 0,
      transition: { type: "spring", stiffness: 300, damping: 24 }
    },
    exit: { 
      opacity: 0, 
      scale: 0.9, 
      y: -10,
      transition: { duration: 0.2 }
    }
  };

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear errors when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  // Validate form
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    
    if (!formData.subject.trim()) {
      newErrors.subject = 'Subject is required';
    }
    
    if (!formData.message.trim()) {
      newErrors.message = 'Message is required';
    } else if (formData.message.trim().length < 10) {
      newErrors.message = 'Message must be at least 10 characters long';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setIsSubmitting(true);
    setSubmitStatus(null);
    
    try {
      const response = await axios.post(endpoint, formData, {
        headers: {
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value,
          'Content-Type': 'application/json'
        }
      });
      
      setSubmitStatus('success');
      setSubmitMessage('Thank you for your message! I\'ll get back to you soon.');
      
      // Reset form after successful submission
      setTimeout(() => {
        setFormData({ name: '', email: '', subject: '', message: '' });
        setSubmitStatus(null);
      }, 3000);
      
    } catch (error) {
      setSubmitStatus('error');
      setSubmitMessage(
        error.response?.data?.message || 
        'There was an error sending your message. Please try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  // Field component with animations
  const AnimatedField = ({ 
    label, 
    name, 
    type = 'text', 
    as = 'input', 
    required = false, 
    rows = 5,
    placeholder = '',
    ...props 
  }) => {
    const Component = as;
    const hasError = !!errors[name];
    
    return (
      <motion.div variants={fieldVariants}>
        <label htmlFor={name} className="block text-sm font-medium text-neutral-700 mb-2">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
        <motion.div
          animate={hasError ? { x: [-5, 5, -5, 5, 0] } : {}}
          transition={{ duration: 0.4 }}
        >
          <Component
            id={name}
            name={name}
            type={type}
            rows={as === 'textarea' ? rows : undefined}
            value={formData[name]}
            onChange={handleChange}
            placeholder={placeholder}
            className={`form-${as} ${hasError ? 'border-red-500 focus:ring-red-500' : ''}`}
            {...props}
          />
        </motion.div>
        <AnimatePresence>
          {hasError && (
            <motion.p
              className="mt-1 text-sm text-red-600"
              variants={messageVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
            >
              {errors[name]}
            </motion.p>
          )}
        </AnimatePresence>
      </motion.div>
    );
  };

  return (
    <div className="contact-form-container form-container relative">
      {/* Success/Error Messages */}
      <AnimatePresence>
        {submitStatus && (
          <motion.div
            className={`mb-6 p-4 rounded-lg border ${
              submitStatus === 'success'
                ? 'bg-green-50 border-green-200'
                : 'bg-red-50 border-red-200'
            }`}
            variants={messageVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
          >
            <div className="flex items-start">
              <motion.div
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ delay: 0.2, type: "spring", stiffness: 300, damping: 24 }}
              >
                {submitStatus === 'success' ? (
                  <svg className="w-6 h-6 text-green-500 mr-3 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="w-6 h-6 text-red-500 mr-3 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                )}
              </motion.div>
              <div className="flex-1">
                <h4 className={`font-semibold mb-1 ${
                  submitStatus === 'success' ? 'text-green-800' : 'text-red-800'
                }`}>
                  {submitStatus === 'success' ? 'Message Sent!' : 'Error'}
                </h4>
                <p className={submitStatus === 'success' ? 'text-green-700' : 'text-red-700'}>
                  {submitMessage}
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Contact Form */}
      <motion.form
        onSubmit={handleSubmit}
        className="space-y-6 relative"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Loading overlay */}
        <AnimatePresence>
          {isSubmitting && (
            <motion.div
              className="absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-10 rounded-lg"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <motion.div
                className="flex flex-col items-center space-y-3"
                initial={{ scale: 0.8 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 300, damping: 24 }}
              >
                <motion.div
                  className="w-8 h-8 border-3 border-primary-300 border-t-primary-600 rounded-full"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                />
                <p className="text-sm text-neutral-600">Sending message...</p>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Form Fields */}
        <AnimatedField
          label="Full Name"
          name="name"
          required
          placeholder="Your full name"
        />

        <AnimatedField
          label="Email Address"
          name="email"
          type="email"
          required
          placeholder="your.email@example.com"
        />

        <AnimatedField
          label="Subject"
          name="subject"
          required
          placeholder="Subject of your message"
        />

        <AnimatedField
          label="Message"
          name="message"
          as="textarea"
          rows={5}
          required
          placeholder="Your message here..."
        />

        {/* Submit Button */}
        <motion.div variants={fieldVariants}>
          <motion.button
            type="submit"
            className="btn-primary w-full sm:w-auto relative overflow-hidden"
            disabled={isSubmitting}
            whileHover={{ scale: isSubmitting ? 1 : 1.02 }}
            whileTap={{ scale: isSubmitting ? 1 : 0.98 }}
            transition={{ type: "spring", stiffness: 300, damping: 24 }}
          >
            <motion.span
              className="flex items-center justify-center"
              animate={isSubmitting ? { opacity: 0.7 } : { opacity: 1 }}
            >
              {isSubmitting ? 'Sending...' : 'Send Message'}
            </motion.span>
          </motion.button>
        </motion.div>

        {/* Privacy Notice */}
        <motion.div 
          className="pt-4 border-t border-neutral-200"
          variants={fieldVariants}
        >
          <p className="text-xs text-neutral-500">
            Your information is secure and will only be used to respond to your inquiry. 
            See our{' '}
            <a href="/privacy/" className="text-primary-600 hover:underline">
              Privacy Policy
            </a>{' '}
            for details.
          </p>
        </motion.div>
      </motion.form>
    </div>
  );
};

export default ContactForm;