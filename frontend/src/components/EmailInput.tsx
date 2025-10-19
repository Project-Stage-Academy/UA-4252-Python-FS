import React, { useState, useCallback } from 'react';
import debounce from 'lodash.debounce';

interface EmailInputProps {
  value: string;
  onChange: (value: string) => void;
}

interface CheckEmailResponse {
  exists: boolean;
}

const EmailInput: React.FC<EmailInputProps> = ({ value, onChange }) => {
  const [status, setStatus] = useState<'checking' | 'available' | 'exists' | null>(null);

  const checkEmail = useCallback(
    debounce(async (email: string) => {
      if (!email) return setStatus(null);
      setStatus('checking');
      try {
      await new Promise((r) => setTimeout(r, 800)); 
      const exists = email.includes("test") || email.endsWith("@gmail.com"); 
      setStatus(exists ? "exists" : "available");
      } catch (err) {
        console.error(err);
        setStatus(null);
      }
    }, 500),
    []
  );

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    onChange(newValue);
    checkEmail(newValue);
  };

  return (
    <div>
      <input
        type="email"
        value={value}
        onChange={handleChange}
        placeholder="Enter your email"
      />
      <div>
        {status === 'checking' && <span>Checking email...</span>}
        {status === 'available' && <span style={{ color: 'green' }}>Email is available</span>}
        {status === 'exists' && (
          <div style={{ color: 'red' }}>
            If this is your account — try <a href="/login">Login</a> or <a href="/forgot-password">Reset password</a>
          </div>
        )}
      </div>
    </div>
  );
};

export default EmailInput;
