import { render, screen } from '@testing-library/react';
import App from './App';

test('renders learn react link', () => {
  render(<App />);
  const linkElement = screen.getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});

test('shows loading when sending message', async () => {
  render(<App />);
  const inputElement = screen.getByPlaceholderText(/Escribe un mensaje.../i);
  fireEvent.change(inputElement, { target: { value: 'Hola' } });
  fireEvent.keyDown(inputElement, { key: 'Enter' });
  
  expect(screen.getByText(/Enviando.../i)).toBeInTheDocument();
});