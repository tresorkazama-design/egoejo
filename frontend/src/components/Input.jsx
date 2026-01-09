import React from 'react';

export const Input = ({
  label,
  type = 'text',
  value,
  onChange,
  placeholder = '',
  error = null,
  required = false,
  disabled = false,
  className = '',
  name,
  ...props
}) => {
  // Générer un ID unique basé sur name ou label
  const inputId = props.id || (name ? `input-${name}` : (label ? `input-${label.replace(/\s+/g, '-').toLowerCase()}` : `input-${Math.random().toString(36).substr(2, 9)}`));
  const errorId = `${inputId}-error`;
  
  return (
    <div className={`mb-4 ${className}`}>
      {label && (
        <label htmlFor={inputId} className="block text-sm font-medium mb-1">
          {label}
          {required && <span className="text-red-500 ml-1" aria-label="Champ requis" aria-hidden="true">*</span>}
        </label>
      )}
      <input
        id={inputId}
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={error ? errorId : undefined}
        aria-required={required}
        className={`w-full px-3 py-2 border rounded-md ${
          error ? 'border-red-500' : 'border-gray-300'
        } ${disabled ? 'bg-gray-100 cursor-not-allowed' : ''}`}
        data-testid={props['data-testid']}
        {...props}
      />
      {error && <p className="text-red-500 text-sm mt-1" role="alert" id={errorId} aria-live="polite">{error}</p>}
    </div>
  );
};

