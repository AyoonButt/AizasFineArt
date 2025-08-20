import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const CommissionForm = ({ endpoint = '/htmx/commission/' }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    artworkType: '',
    size: '',
    subject: '',
    description: '',
    budget: '',
    timeline: '',
    referenceImages: null
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);
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
    const { name, value, files } = e.target;
    if (name === 'referenceImages') {
      setFormData(prev => ({ ...prev, [name]: files }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
    
    // Clear errors when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  // Validate form
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) newErrors.name = 'Name is required';
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    if (!formData.artworkType) newErrors.artworkType = 'Please select an artwork type';
    if (!formData.subject.trim()) newErrors.subject = 'Subject is required';
    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    } else if (formData.description.trim().length < 20) {
      newErrors.description = 'Please provide more details (at least 20 characters)';
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
      const formDataToSend = new FormData();
      Object.keys(formData).forEach(key => {
        if (key === 'referenceImages' && formData[key]) {
          Array.from(formData[key]).forEach((file, index) => {
            formDataToSend.append(`referenceImages`, file);
          });
        } else {
          formDataToSend.append(key, formData[key]);
        }
      });

      const response = await axios.post(endpoint, formDataToSend, {
        headers: {
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value,
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setSubmitStatus('success');
      setSubmitMessage('Thank you for your commission request! I\'ll review it and get back to you within 2-3 business days.');
      
      // Reset form after successful submission
      setTimeout(() => {
        setFormData({
          name: '', email: '', phone: '', artworkType: '', size: '',
          subject: '', description: '', budget: '', timeline: '', referenceImages: null
        });
        setSubmitStatus(null);
      }, 5000);
      
    } catch (error) {
      setSubmitStatus('error');
      setSubmitMessage(
        error.response?.data?.message || 
        'There was an error submitting your request. Please try again.'
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
    rows = 3,
    placeholder = '',
    children,
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
          animate={hasError ? { x: [-3, 3, -3, 3, 0] } : {}}
          transition={{ duration: 0.4 }}
        >
          {children ? (
            <Component
              id={name}
              name={name}
              value={formData[name]}
              onChange={handleChange}
              className={`form-${as} ${hasError ? 'border-red-500 focus:ring-red-500' : ''}`}
              {...props}
            >
              {children}
            </Component>
          ) : (
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
          )}
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
    <div className="commission-form-container form-container relative">
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
                  {submitStatus === 'success' ? 'Request Submitted!' : 'Error'}
                </h4>
                <p className={submitStatus === 'success' ? 'text-green-700' : 'text-red-700'}>
                  {submitMessage}
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Commission Form */}
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
                <p className="text-sm text-neutral-600">Submitting request...</p>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Contact Information */}
        <div className="grid md:grid-cols-2 gap-6">
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
        </div>

        <AnimatedField
          label="Phone Number"
          name="phone"
          type="tel"
          placeholder="(optional) for quick questions"
        />

        {/* Artwork Details */}
        <div className="grid md:grid-cols-2 gap-6">
          <AnimatedField
            label="Artwork Type"
            name="artworkType"
            as="select"
            required
          >
            <option value="">Select type...</option>
            <option value="watercolor">Watercolor Painting</option>
            <option value="oil">Oil Painting</option>
            <option value="mixed">Mixed Media</option>
            <option value="digital">Digital Art</option>
          </AnimatedField>

          <AnimatedField
            label="Preferred Size"
            name="size"
            as="select"
          >
            <option value="">Select size...</option>
            <option value="small">Small (8x10 to 11x14 inches)</option>
            <option value="medium">Medium (16x20 to 18x24 inches)</option>
            <option value="large">Large (24x30+ inches)</option>
            <option value="custom">Custom size</option>
          </AnimatedField>
        </div>

        <AnimatedField
          label="Subject/Theme"
          name="subject"
          required
          placeholder="Portrait, landscape, pet, abstract, etc."
        />

        <AnimatedField
          label="Detailed Description"
          name="description"
          as="textarea"
          rows={5}
          required
          placeholder="Describe your vision, inspiration, colors, mood, specific details you'd like included..."
        />

        {/* Budget and Timeline */}
        <div className="grid md:grid-cols-2 gap-6">
          <AnimatedField
            label="Budget Range"
            name="budget"
            as="select"
          >
            <option value="">Select budget...</option>
            <option value="under-500">Under $500</option>
            <option value="500-1000">$500 - $1,000</option>
            <option value="1000-2000">$1,000 - $2,000</option>
            <option value="2000-plus">$2,000+</option>
            <option value="discuss">Prefer to discuss</option>
          </AnimatedField>

          <AnimatedField
            label="Timeline"
            name="timeline"
            as="select"
          >
            <option value="">When do you need it?</option>
            <option value="flexible">Flexible timing</option>
            <option value="1-month">Within 1 month</option>
            <option value="2-3-months">2-3 months</option>
            <option value="holiday">For a specific date/holiday</option>
          </AnimatedField>
        </div>

        {/* Reference Images */}
        <AnimatedField
          label="Reference Images"
          name="referenceImages"
          type="file"
          multiple
          accept="image/*"
        />
        <p className="text-xs text-neutral-500 -mt-4">
          Upload any reference photos, inspiration images, or sketches (optional)
        </p>

        {/* Submit Button */}
        <motion.div variants={fieldVariants}>
          <motion.button
            type="submit"
            className="btn-primary w-full sm:w-auto relative overflow-hidden px-8"
            disabled={isSubmitting}
            whileHover={{ scale: isSubmitting ? 1 : 1.02 }}
            whileTap={{ scale: isSubmitting ? 1 : 0.98 }}
            transition={{ type: "spring", stiffness: 300, damping: 24 }}
          >
            <motion.span
              className="flex items-center justify-center"
              animate={isSubmitting ? { opacity: 0.7 } : { opacity: 1 }}
            >
              {isSubmitting ? 'Submitting Request...' : 'Submit Commission Request'}
            </motion.span>
          </motion.button>
        </motion.div>

        {/* Process Information */}
        <motion.div 
          className="pt-6 border-t border-neutral-200 bg-neutral-50 p-4 rounded-lg"
          variants={fieldVariants}
        >
          <h4 className="font-semibold text-neutral-800 mb-2">Commission Process:</h4>
          <ul className="text-sm text-neutral-600 space-y-1">
            <li>• I'll review your request and respond within 2-3 business days</li>
            <li>• We'll discuss details, timeline, and pricing</li>
            <li>• 50% deposit required to begin work</li>
            <li>• I'll send progress photos during creation</li>
            <li>• Final payment due upon completion</li>
          </ul>
        </motion.div>
      </motion.form>
    </div>
  );
};

export default CommissionForm;