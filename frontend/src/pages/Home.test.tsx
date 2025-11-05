import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Home from './Home';
import { MemoryRouter } from 'react-router-dom';

test('Home renders key sections', () => {
  render(
    <MemoryRouter>
      <Home />
    </MemoryRouter>
  );

  expect(screen.getByText(/Майданчик для тих/i)).toBeInTheDocument();
  expect(screen.getByRole('region', { name: /Для кого/i })).toBeInTheDocument();
});
