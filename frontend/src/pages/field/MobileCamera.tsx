import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import api from '../../services/api';
import { useToast } from '../../components/toast/ToastProvider';

export default function MobileCamera() {
  const { toast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [gpsCoords, setGpsCoords] = useState<{ lat: number; lng: number } | null>(null);
  const [notes, setNotes] = useState('');
  const [capturing, setCapturing] = useState(false);
  const [uploading, setUploading] = useState(false);

  const captureGPS = () => {
    setCapturing(true);
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setGpsCoords({ lat: pos.coords.latitude, lng: pos.coords.longitude });
          setCapturing(false);
        },
        () => {
          // Mock GPS for demo
          setGpsCoords({ lat: 21.1458 + Math.random() * 0.01, lng: 79.0882 + Math.random() * 0.01 });
          setCapturing(false);
          toast('Using mock GPS coordinates for demo', 'info');
        }
      );
    } else {
      setGpsCoords({ lat: 21.1458, lng: 79.0882 });
      setCapturing(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setPreview(url);
      if (!gpsCoords) captureGPS();
    }
  };

  const handleUpload = async () => {
    if (!preview) {
      toast('Please capture a photo first', 'warning');
      return;
    }
    setUploading(true);
    try {
      // Mock upload for demo
      await new Promise((resolve) => setTimeout(resolve, 1500));
      toast('Photo uploaded successfully with geo-tag', 'success');
      setPreview(null);
      setNotes('');
      setGpsCoords(null);
    } catch {
      toast('Upload failed', 'error');
    }
    setUploading(false);
  };

  return (
    <div className="max-w-md mx-auto space-y-4 pb-20">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-xl font-bold text-slate-900">📸 Camera</h1>
        <p className="text-sm text-slate-500">Capture geo-tagged inspection photos</p>
      </motion.div>

      {/* Camera / Upload Area */}
      <Card>
        <CardContent className="p-4">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={handleFileChange}
          />

          {preview ? (
            <div className="space-y-3">
              <div className="relative rounded-xl overflow-hidden border border-slate-200">
                <img src={preview} alt="Captured" className="w-full h-64 object-cover" />
                <button
                  onClick={() => { setPreview(null); }}
                  className="absolute top-2 right-2 bg-black/50 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm"
                  aria-label="Remove photo"
                >
                  ✕
                </button>
              </div>
              <Button variant="outline" className="w-full" onClick={() => fileInputRef.current?.click()}>
                📷 Retake Photo
              </Button>
            </div>
          ) : (
            <button
              onClick={() => fileInputRef.current?.click()}
              className="w-full h-48 border-2 border-dashed border-slate-300 rounded-xl flex flex-col items-center justify-center gap-2 hover:border-primary-400 hover:bg-primary-50/30 transition-colors"
            >
              <span className="text-4xl">📷</span>
              <span className="text-sm text-slate-500">Tap to capture photo</span>
            </button>
          )}
        </CardContent>
      </Card>

      {/* GPS Capture */}
      <Button variant="outline" className="w-full min-h-[44px]" onClick={captureGPS} disabled={capturing}>
        {capturing ? '📍 Capturing GPS...' : gpsCoords ? `✅ GPS: ${gpsCoords.lat.toFixed(4)}, ${gpsCoords.lng.toFixed(4)}` : '📍 Capture GPS Location'}
      </Button>

      {/* Notes */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Condition Notes</CardTitle>
        </CardHeader>
        <CardContent>
          <label htmlFor="camera-notes" className="text-sm font-medium text-slate-700 sr-only">Condition Notes</label>
          <textarea
            id="camera-notes"
            className="w-full rounded-lg border border-slate-300 p-3 text-sm"
            rows={3}
            placeholder="Describe the current condition of the parcel..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </CardContent>
      </Card>

      {/* Submit */}
      <Button className="w-full shadow-lg min-h-[44px]" size="lg" onClick={handleUpload} disabled={uploading}>
        {uploading ? '📤 Uploading...' : '📤 Upload Photo'}
      </Button>
    </div>
  );
}
