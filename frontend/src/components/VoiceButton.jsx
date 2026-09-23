import { useState, useRef, useEffect } from 'react';

export default function VoiceButton({ onRecordingComplete, disabled }) {
  const [isRecording, setIsRecording] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Cleanup stream on unmount
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const startRecording = async () => {
    setErrorMessage(null);
    audioChunksRef.current = [];

    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Microphone access is not supported in this browser.');
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        if (onRecordingComplete) {
          onRecordingComplete(audioBlob);
        }
        // Stop all tracks to release mic hardware
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((track) => track.stop());
          streamRef.current = null;
        }
        setIsRecording(false);
      };

      recorder.start();
      setIsRecording(true);
    } catch (err) {
      console.warn('Voice recording error:', err);
      setErrorMessage('Microphone access denied. Please allow mic permissions and try again.');
      setIsRecording(false);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      }
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
  };

  const handleClick = (e) => {
    e.preventDefault();
    if (disabled) return;

    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <div className="relative inline-flex items-center">
      {/* Inline Error Popover */}
      {errorMessage && (
        <div className="absolute bottom-full mb-2 right-0 sm:left-1/2 sm:-translate-x-1/2 w-64 p-2.5 bg-rose-600 text-white text-xs rounded-xl shadow-lg border border-rose-500 z-30 flex items-start justify-between gap-2 animate-fadeIn">
          <div className="flex items-start gap-1.5">
            <svg className="w-4 h-4 shrink-0 mt-0.5 text-rose-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span>{errorMessage}</span>
          </div>
          <button
            type="button"
            onClick={() => setErrorMessage(null)}
            className="text-rose-200 hover:text-white font-bold leading-none"
          >
            &times;
          </button>
        </div>
      )}

      {/* Mic Trigger Button */}
      <button
        type="button"
        onClick={handleClick}
        disabled={disabled}
        title={isRecording ? 'Click to stop recording' : 'Click to speak question'}
        className={`relative p-2.5 sm:p-3 rounded-2xl border transition-all duration-200 shrink-0 flex items-center justify-center ${
          isRecording
            ? 'bg-rose-500 hover:bg-rose-600 text-white border-rose-400 ring-4 ring-rose-200 animate-pulse'
            : errorMessage
            ? 'bg-rose-50 border-rose-300 text-rose-600'
            : 'bg-white hover:bg-teal-50/80 text-slate-600 hover:text-teal-700 border-slate-200/80 hover:border-teal-300 shadow-2xs'
        } disabled:opacity-40 disabled:cursor-not-allowed`}
      >
        {isRecording ? (
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-white animate-ping"></span>
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <rect x="6" y="6" width="12" height="12" rx="2" fill="currentColor" />
            </svg>
          </div>
        ) : (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        )}
      </button>
    </div>
  );
}
