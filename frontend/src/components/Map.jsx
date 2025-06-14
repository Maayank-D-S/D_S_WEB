import React from 'react';
import { GoogleMap, LoadScript, Marker } from '@react-google-maps/api';

const defaultCenter = {
  lat: 28.6139,
  lng: 77.2090,
};

const Map = ({ projectTitle, latitude, longitude }) => {
  const center = latitude && longitude ? { lat: latitude, lng: longitude } : defaultCenter;

  // Responsive height: adjust based on screen width
  const mapHeight = typeof window !== 'undefined' && window.innerWidth < 768 ? '300px' : '400px';

  const containerStyle = {
    width: '100%',
    height: mapHeight,
    borderRadius: '0.5rem',
  };

  return (
    <div className="relative w-full overflow-hidden shadow-md rounded-lg">
      <LoadScript googleMapsApiKey="AIzaSyAFrqjqk0SjeH4kKzLiYoI08div5TuO1TI">
        <GoogleMap mapContainerStyle={containerStyle} center={center} zoom={15}>
          <Marker position={center} />
        </GoogleMap>
      </LoadScript>

      {/* Title Overlay */}
      <div className="absolute bottom-4 left-4 bg-white px-3 py-2 rounded shadow text-sm font-medium text-gray-900">
        {projectTitle}
      </div>
    </div>
  );
};

export default Map;
