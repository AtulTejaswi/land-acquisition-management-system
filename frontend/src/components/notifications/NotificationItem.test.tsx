import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { NotificationItem } from './NotificationItem';

const baseNotification = {
  id: '1',
  type: 'info',
  title: 'Test Notification',
  body: 'This is a test message',
  is_read: false,
  created_at: '2024-03-15T10:30:00Z',
};

describe('NotificationItem', () => {
  it('renders notification title', () => {
    render(<NotificationItem notification={baseNotification} index={0} />);
    expect(screen.getByText('Test Notification')).toBeInTheDocument();
  });

  it('renders notification body', () => {
    render(<NotificationItem notification={baseNotification} index={0} />);
    expect(screen.getByText('This is a test message')).toBeInTheDocument();
  });

  it('shows unread indicator dot for unread notifications', () => {
    const { container } = render(
      <NotificationItem notification={{ ...baseNotification, is_read: false }} index={0} />,
    );
    const dot = container.querySelector('.bg-primary-500');
    expect(dot).toBeInTheDocument();
  });

  it('does not show unread dot for read notifications', () => {
    const { container } = render(
      <NotificationItem notification={{ ...baseNotification, is_read: true }} index={0} />,
    );
    const dot = container.querySelector('.bg-primary-500');
    expect(dot).not.toBeInTheDocument();
  });

  it('applies blue left border for unread notifications', () => {
    const { container } = render(
      <NotificationItem notification={{ ...baseNotification, is_read: false }} index={0} />,
    );
    const card = container.querySelector('.border-l-4');
    expect(card).toBeInTheDocument();
  });

  it('does not apply blue left border for read notifications', () => {
    const { container } = render(
      <NotificationItem notification={{ ...baseNotification, is_read: true }} index={0} />,
    );
    const card = container.querySelector('.border-l-4');
    expect(card).not.toBeInTheDocument();
  });

  it('renders info icon for info type', () => {
    render(<NotificationItem notification={{ ...baseNotification, type: 'info' }} index={0} />);
    expect(screen.getByText('ℹ️')).toBeInTheDocument();
  });

  it('renders success icon for success type', () => {
    render(<NotificationItem notification={{ ...baseNotification, type: 'success' }} index={0} />);
    expect(screen.getByText('✅')).toBeInTheDocument();
  });

  it('renders warning icon for warning type', () => {
    render(<NotificationItem notification={{ ...baseNotification, type: 'warning' }} index={0} />);
    expect(screen.getByText('⚠️')).toBeInTheDocument();
  });

  it('renders alert icon for alert type', () => {
    render(<NotificationItem notification={{ ...baseNotification, type: 'alert' }} index={0} />);
    expect(screen.getByText('🚨')).toBeInTheDocument();
  });

  it('renders default icon for unknown type', () => {
    render(<NotificationItem notification={{ ...baseNotification, type: 'unknown' }} index={0} />);
    expect(screen.getByText('📢')).toBeInTheDocument();
  });
});
