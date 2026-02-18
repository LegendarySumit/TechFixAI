/**
 * Voice Recording Service using Web Audio API
 * Adapted from VoicetoTicket for TechFixAI integration
 */

class VoiceRecorderService {
  constructor() {
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.stream = null;
    this.isRecording = false;
    this.audioContext = null;
    this.analyser = null;
    this.dataArray = null;
    this.animationId = null;
  }

  async startRecording() {
    try {
      this.audioChunks = [];
      this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(this.stream);

      // Setup audio context for visualization
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      this.analyser = this.audioContext.createAnalyser();
      const source = this.audioContext.createMediaStreamSource(this.stream);
      source.connect(this.analyser);
      this.analyser.fftSize = 256;
      const bufferLength = this.analyser.frequencyBinCount;
      this.dataArray = new Uint8Array(bufferLength);

      this.mediaRecorder.ondataavailable = (event) => {
        this.audioChunks.push(event.data);
      };

      this.mediaRecorder.onstart = () => {
        this.isRecording = true;
      };

      this.mediaRecorder.start();
      return true;
    } catch (error) {
      console.error("Error accessing microphone:", error);
      return false;
    }
  }

  stopRecording() {
    return new Promise((resolve) => {
      if (this.mediaRecorder && this.isRecording) {
        this.mediaRecorder.onstop = () => {
          const audioBlob = new Blob(this.audioChunks, { type: "audio/wav" });
          const audioUrl = URL.createObjectURL(audioBlob);
          
          // Clean up
          if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
          }
          
          if (this.audioContext) {
            this.audioContext.close();
          }

          if (this.animationId) {
            cancelAnimationFrame(this.animationId);
          }
          
          this.isRecording = false;
          resolve({
            blob: audioBlob,
            url: audioUrl,
            size: audioBlob.size
          });
        };

        this.mediaRecorder.stop();
      } else {
        resolve(null);
      }
    });
  }

  isCurrentlyRecording() {
    return this.isRecording;
  }

  getAudioLevel() {
    if (!this.analyser || !this.dataArray) return 0;
    
    this.analyser.getByteFrequencyData(this.dataArray);
    const average = this.dataArray.reduce((a, b) => a + b) / this.dataArray.length;
    return (average / 255) * 100; // Return percentage
  }
}

// Export for global use
window.VoiceRecorderService = VoiceRecorderService;
