import { render } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ParcelLayer } from './ParcelLayer';

// Mock maplibre-gl
vi.mock('maplibre-gl', () => {
  const mockMap = {
    getLayer: vi.fn(),
    removeLayer: vi.fn(),
    getSource: vi.fn(),
    removeSource: vi.fn(),
    addSource: vi.fn(),
    addLayer: vi.fn(),
    on: vi.fn(),
    off: vi.fn(),
    fitBounds: vi.fn(),
  };
  class MockLngLatBounds {
    extend = vi.fn().mockReturnThis();
    constructor(_sw?: any, _ne?: any) {}
  }
  return {
    default: {
      Map: vi.fn(() => mockMap),
      LngLatBounds: MockLngLatBounds,
    },
  };
});

const geojsonData = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      properties: { id: '1', verification_status: 'verified', survey_no: '100' },
      geometry: {
        type: 'Polygon',
        coordinates: [[[73.8, 20.0], [73.9, 20.0], [73.9, 20.1], [73.8, 20.1], [73.8, 20.0]]],
      },
    },
  ],
};

describe('ParcelLayer', () => {
  const mockMap = {
    getLayer: vi.fn(),
    removeLayer: vi.fn(),
    getSource: vi.fn(),
    removeSource: vi.fn(),
    addSource: vi.fn(),
    addLayer: vi.fn(),
    on: vi.fn(),
    off: vi.fn(),
    fitBounds: vi.fn(),
  };

  const mockOnSelectParcel = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    // Make map.getLayer return truthy so cleanup runs
    mockMap.getLayer.mockReturnValue(true);
    mockMap.getSource.mockReturnValue(true);
  });

  it('renders nothing (headless component)', () => {
    const { container } = render(
      <ParcelLayer map={null} geojsonData={geojsonData} mapLoaded={false} onSelectParcel={mockOnSelectParcel} />,
    );
    expect(container.innerHTML).toBe('');
  });

  it('does not add layers when map is null', () => {
    render(
      <ParcelLayer map={null} geojsonData={geojsonData} mapLoaded={true} onSelectParcel={mockOnSelectParcel} />,
    );
    expect(mockMap.addSource).not.toHaveBeenCalled();
  });

  it('does not add layers when mapLoaded is false', () => {
    render(
      <ParcelLayer map={mockMap as any} geojsonData={geojsonData} mapLoaded={false} onSelectParcel={mockOnSelectParcel} />,
    );
    expect(mockMap.addSource).not.toHaveBeenCalled();
  });

  it('does not add layers when geojsonData is null', () => {
    render(
      <ParcelLayer map={mockMap as any} geojsonData={null} mapLoaded={true} onSelectParcel={mockOnSelectParcel} />,
    );
    expect(mockMap.addSource).not.toHaveBeenCalled();
  });

  it('does not add layers when features array is empty', () => {
    render(
      <ParcelLayer map={mockMap as any} geojsonData={{ features: [] }} mapLoaded={true} onSelectParcel={mockOnSelectParcel} />,
    );
    expect(mockMap.addSource).not.toHaveBeenCalled();
  });

  it('cleans up old layers before adding new ones', () => {
    render(
      <ParcelLayer map={mockMap as any} geojsonData={geojsonData} mapLoaded={true} onSelectParcel={mockOnSelectParcel} />,
    );
    expect(mockMap.removeLayer).toHaveBeenCalledWith('parcels-fill');
    expect(mockMap.removeLayer).toHaveBeenCalledWith('parcels-outline');
    expect(mockMap.removeSource).toHaveBeenCalledWith('parcels');
  });
});
