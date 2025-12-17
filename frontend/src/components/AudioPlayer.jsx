/**
 * Composant pour lecture audio (TTS)
 * Permet d'écouter les contenus éducatifs en mode "Podcast"
 */
import { useState, useRef, useEffect } from 'react';
import { fetchAPI } from '../utils/api';

export default function AudioPlayer({ contentId, autoPlay = false }) {
  const [audioUrl, setAudioUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const audioRef = useRef(null);

  useEffect(() => {
    const loadAudio = async () => {
      if (!contentId) return;

      setLoading(true);
      try {
        const content = await fetchAPI(`/contents/${contentId}/`);
        if (content.audio_file) {
          // Construire l'URL complète
          const apiBase = import.meta.env.VITE_API_URL 
            ? `${import.meta.env.VITE_API_URL}/api` 
            : 'http://localhost:8000/api';
          setAudioUrl(`${apiBase.replace('/api', '')}${content.audio_file}`);
        }
      } catch (error) {
        console.error('Erreur chargement audio:', error);
      } finally {
        setLoading(false);
      }
    };

    loadAudio();
  }, [contentId]);

  useEffect(() => {
    if (audioRef.current && autoPlay && audioUrl) {
      audioRef.current.play();
      setPlaying(true);
    }
  }, [audioUrl, autoPlay]);

  const handlePlayPause = () => {
    if (audioRef.current) {
      if (playing) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setPlaying(!playing);
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
      setDuration(audioRef.current.duration || 0);
    }
  };

  const handleSeek = (e) => {
    const newTime = parseFloat(e.target.value);
    if (audioRef.current) {
      audioRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };

  if (loading) {
    return <div className="audio-player loading">Chargement audio...</div>;
  }

  if (!audioUrl) {
    return (
      <div className="audio-player no-audio">
        <p>Version audio non disponible pour ce contenu.</p>
      </div>
    );
  }

  const formatTime = (seconds) => {
    if (isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="audio-player">
      <audio
        ref={audioRef}
        src={audioUrl}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleTimeUpdate}
        onEnded={() => setPlaying(false)}
      />

      <div className="audio-player__controls">
        <button
          onClick={handlePlayPause}
          className="audio-player__play-pause"
          aria-label={playing ? 'Pause' : 'Play'}
        >
          {playing ? '⏸️' : '▶️'}
        </button>

        <div className="audio-player__progress">
          <input
            type="range"
            min="0"
            max={duration || 0}
            value={currentTime}
            onChange={handleSeek}
            className="audio-player__slider"
          />
          <div className="audio-player__time">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

