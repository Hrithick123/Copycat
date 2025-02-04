import librosa
import numpy as np
import os
import matplotlib.pyplot as plt
from collections import defaultdict
from sklearn.preprocessing import MinMaxScaler
from scipy.spatial.distance import cosine
import matplotlib

# Use non-interactive backend to avoid RuntimeError
matplotlib.use('Agg')

class EnhancedCarnaticAnalyzer:
    def __init__(self, sr=22050):
        self.sr = sr
        self.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.scaler = MinMaxScaler()

    def hz_to_note(self, frequency):
        """Convert frequency in Hz to a musical note."""
        if frequency <= 0:
            return None
        midi_number = librosa.hz_to_midi(frequency)
        note_idx = int(midi_number % 12)
        octave = int(midi_number // 12) - 1
        return f"{self.note_names[note_idx]}{octave}"

    def extract_pitch_features(self, audio_file):
        """Extract detailed pitch features."""
        y, sr = librosa.load(audio_file, sr=self.sr)

        # Extract pitch using piptrack
        hop_length = 512
        fmin = librosa.note_to_hz('C2')
        fmax = librosa.note_to_hz('C7')
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr, fmin=fmin, fmax=fmax, hop_length=hop_length)

        pitch_sequence = []
        confidence_sequence = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            confidence = magnitudes[index, t]

            if confidence > 0.1:
                pitch_sequence.append(pitch)
                confidence_sequence.append(confidence)

        # Convert pitch sequence to notes
        note_sequence = [self.hz_to_note(hz) for hz in pitch_sequence if hz > 0]

        return {
            'pitch_sequence': pitch_sequence,
            'confidence_sequence': confidence_sequence,
            'note_sequence': note_sequence,
        }

    def analyze_note_distribution(self, note_sequence):
        """Analyze note occurrences for plotting."""
        if not note_sequence:
            return {}

        note_counts = defaultdict(int)
        for note in note_sequence:
            if note:
                base_note = note[:-1]  # Strip octave
                note_counts[base_note] += 1

        total_notes = sum(note_counts.values())
        normalized_counts = {note: count / total_notes for note, count in note_counts.items()}

        return normalized_counts

    def pattern_similarity(self, pattern1, pattern2):
        """Calculate pattern similarity using cosine similarity."""
        # Convert patterns into numerical vectors (note counts or binary representation)
        all_notes = sorted(set(pattern1) | set(pattern2))
        vector1 = [pattern1.count(note) for note in all_notes]
        vector2 = [pattern2.count(note) for note in all_notes]

        # Calculate cosine similarity between the two patterns
        return 1 - cosine(vector1, vector2)

    def swara_similarity(self, features1, features2):
        """Calculate a stricter swara similarity score by considering both frequency proximity and note distribution."""
        pitch_sequence1 = np.array(features1['pitch_sequence'])
        pitch_sequence2 = np.array(features2['pitch_sequence'])

        # Step 1: Match pitches within a small tolerance (e.g., ±20 cents)
        tolerance_semitones = 0.2  # Adjust based on Carnatic nuances
        tolerance_hz = librosa.midi_to_hz(tolerance_semitones)

        matched_pitches = 0
        for pitch1 in pitch_sequence1:
            for pitch2 in pitch_sequence2:
                if abs(pitch1 - pitch2) <= tolerance_hz:
                    matched_pitches += 1
                    break  # Move to the next pitch in sequence 1 after finding a match

        pitch_similarity = matched_pitches / max(len(pitch_sequence1), len(pitch_sequence2))

        # Step 2: Combine with note distribution similarity
        note_distribution1 = self.analyze_note_distribution(features1['note_sequence'])
        note_distribution2 = self.analyze_note_distribution(features2['note_sequence'])

        # Ensure all unique notes are represented
        all_notes = sorted(set(note_distribution1.keys()) | set(note_distribution2.keys()))
        note_similarity = 0
        for note in all_notes:
            freq1 = note_distribution1.get(note, 0)
            freq2 = note_distribution2.get(note, 0)
            note_similarity += 1 - abs(freq1 - freq2)

        note_similarity /= len(all_notes)

        # Step 3: Weighted combination
        weight_pitch = 0.7  # Give more weight to pitch-level similarity
        weight_note = 0.3

        overall_similarity = (weight_pitch * pitch_similarity) + (weight_note * note_similarity)
        return overall_similarity

    def visualize_comparison(self, file1, file2, save_path="./uploads/comparison_plot.png"):
        """Create improved visualizations for note and pitch comparison."""
        features1 = self.extract_pitch_features(file1)
        features2 = self.extract_pitch_features(file2)

        note_distribution1 = self.analyze_note_distribution(features1['note_sequence'])
        note_distribution2 = self.analyze_note_distribution(features2['note_sequence'])

        # Compute note similarity
        all_notes = sorted(set(note_distribution1.keys()) | set(note_distribution2.keys()))
        note_similarity_scores = [1 - abs(note_distribution1.get(note, 0) - note_distribution2.get(note, 0)) for note in all_notes]
        overall_similarity = sum(note_similarity_scores) / len(all_notes)

        # Compute pattern similarity
        pattern_sim = self.pattern_similarity(features1['note_sequence'], features2['note_sequence'])

        # Compute swara/note similarity
        swara_sim = self.swara_similarity(features1, features2)

        # Plot comparison
        fig, axes = plt.subplots(3, 1, figsize=(15, 12))

        # 1. Note Distribution Comparison
        x = np.arange(len(all_notes))
        width = 0.35

        axes[0].bar(x - width / 2, [note_distribution1.get(note, 0) for note in all_notes], width, label=os.path.basename(file1))
        axes[0].bar(x + width / 2, [note_distribution2.get(note, 0) for note in all_notes], width, label=os.path.basename(file2))

        axes[0].set_xticks(x)
        axes[0].set_xticklabels(all_notes)
        axes[0].set_title('Note Distribution Comparison')
        axes[0].legend()

        # 2. Pitch Contour Comparison
        time1 = np.arange(len(features1['pitch_sequence'])) * 512 / self.sr
        time2 = np.arange(len(features2['pitch_sequence'])) * 512 / self.sr

        axes[1].scatter(time1, features1['pitch_sequence'], alpha=0.6, label=os.path.basename(file1), color='blue')
        axes[1].scatter(time2, features2['pitch_sequence'], alpha=0.6, label=os.path.basename(file2), color='red')

        axes[1].set_title('Pitch Contour Comparison')
        axes[1].set_xlabel('Time (s)')
        axes[1].set_ylabel('Frequency (Hz)')
        axes[1].legend()

        # 3. Note Similarity Plot
        axes[2].bar(all_notes, note_similarity_scores, color='green')
        axes[2].set_title('Note Similarity (1 - Absolute Difference)')
        axes[2].set_ylabel('Similarity Score')
        axes[2].set_ylim(0, 1)

        # Display similarity scores on the plot
        axes[2].text(len(all_notes) - 1, 0.9, f'Overall Note Similarity: {overall_similarity:.3f}', ha='right', va='center', fontsize=12, color='black')
        axes[2].text(len(all_notes) - 1, 0.85, f'Pattern Similarity: {pattern_sim:.3f}', ha='right', va='center', fontsize=12, color='black')
        axes[2].text(len(all_notes) - 1, 0.8, f'Swara/Note Similarity: {swara_sim:.3f}', ha='right', va='center', fontsize=12, color='black')

        plt.tight_layout()

        # Save plot to a file
        fig.savefig(save_path)
        print(f"Plot saved to {save_path}")
        plt.close(fig)

    def analyze_similarity(self, file1, file2):
        """Analyze similarity between two audio files and return the results and visualization."""
        features1 = self.extract_pitch_features(file1)
        features2 = self.extract_pitch_features(file2)

        overall_similarity = self.swara_similarity(features1, features2)
        pattern_sim = self.pattern_similarity(features1['note_sequence'], features2['note_sequence'])
        swara_sim = self.swara_similarity(features1, features2)

        # Visualize and save comparison
        self.visualize_comparison(file1, file2, save_path="static/uploads/comparison_plot.png")

        return {
            'overall_similarity': overall_similarity,
            'pattern_similarity': pattern_sim,
            'swara_similarity': swara_sim,
            'visualization_file': "comparison_plot.png"
        }
