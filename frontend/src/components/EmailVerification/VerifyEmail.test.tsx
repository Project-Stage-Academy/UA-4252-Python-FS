import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';

const VerifyEmailNotice = () => (
  <div>
    <h1>Check your email</h1>
    <button>Resend</button>
    <input placeholder="Paste token" />
  </div>
);

describe('VerifyEmailNotice', () => {
  test('renders message to check email', () => {
    render(<VerifyEmailNotice />);
    expect(screen.getByText(/Check your email/i)).toBeInTheDocument();
  });

  test('renders Resend button and it can be clicked', () => {
    render(<VerifyEmailNotice />);
    const button = screen.getByText(/Resend/i);
    expect(button).toBeInTheDocument();
    fireEvent.click(button); 
  });

  test('renders token input', () => {
    render(<VerifyEmailNotice />);
    const input = screen.getByPlaceholderText(/Paste token/i);
    expect(input).toBeInTheDocument();
  });
});
