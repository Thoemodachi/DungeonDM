// /components/AudioController.js

export const audioController = (() => {
  let currentAudio = null;

  const fadeIn = (audio, duration) => {
    audio.volume = 0;
    audio.play();
    const fadeInterval = setInterval(() => {
      if (audio.volume < 1) {
        audio.volume = Math.min(audio.volume + 0.05, 1);
      } else {
        clearInterval(fadeInterval);
      }
    }, duration / 20);
  };

  const fadeOut = (audio, duration) => {
    const fadeInterval = setInterval(() => {
      if (audio.volume > 0) {
        audio.volume = Math.max(audio.volume - 0.05, 0);
      } else {
        clearInterval(fadeInterval);
        audio.pause();
        audio.currentTime = 0;
      }
    }, duration / 20);
  };

  const play = (src, fadeDuration = 1000) => {
    if (currentAudio) {
      fadeOut(currentAudio, fadeDuration);
    }
    currentAudio = new Audio(`/audio/${src}.ogg`);
    fadeIn(currentAudio, fadeDuration);
  };

  return { play };
})();
