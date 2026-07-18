export default function LoadingSpinner({ size = 'md', message }) {
  return (
    <div className="loading-spinner-container">
      <div className={`loading-spinner-ring ${size}`} />
      {message && <p className="loading-spinner-text">{message}</p>}
    </div>
  );
}
