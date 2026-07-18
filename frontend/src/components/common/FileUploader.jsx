import { useState, useRef } from 'react';
import { Upload } from 'lucide-react';
import { ALLOWED_FILE_EXTENSIONS, MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB } from '../../utils/constants';
import toast from 'react-hot-toast';

export default function FileUploader({ onFileSelect, maxSize = MAX_FILE_SIZE_BYTES }) {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef(null);

  const validateFile = (file) => {
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!ALLOWED_FILE_EXTENSIONS.includes(ext)) {
      toast.error(`Unsupported file type: ${ext}`);
      return false;
    }
    if (file.size > maxSize) {
      toast.error(`File too large. Maximum size is ${MAX_FILE_SIZE_MB}MB`);
      return false;
    }
    return true;
  };

  const handleFile = (file) => {
    if (file && validateFile(file)) {
      onFileSelect(file);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    handleFile(file);
  };

  return (
    <div
      className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
    >
      <Upload size={40} />
      <p className="font-medium">Drop files here or click to upload</p>
      <p className="text-sm text-muted">PDF, Images, Spreadsheets, Documents — up to {MAX_FILE_SIZE_MB}MB</p>
      <input
        ref={inputRef}
        type="file"
        style={{ display: 'none' }}
        accept={ALLOWED_FILE_EXTENSIONS.join(',')}
        onChange={(e) => handleFile(e.target.files[0])}
      />
    </div>
  );
}
