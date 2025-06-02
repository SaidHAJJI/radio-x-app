import React from 'react';
import { render, screen } from '@testing-library/react';
import App from '../App'; // Adjust path as necessary

test('renders App component without crashing', () => {
  render(<App />);
  // Example assertion: Check if some text or element rendered by App is present
  // This will depend on what your App component actually renders.
  // For now, let's assume App renders a div or some identifiable element.
  // If App renders "Learn React" for example:
  // expect(screen.getByText(/learn react/i)).toBeInTheDocument();
  // For a generic check, we can see if the container is not empty:
  const { container } = render(<App />);
  expect(container.firstChild).not.toBeNull();
});
