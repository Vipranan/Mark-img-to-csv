import { useState } from 'react';

function App() {
  const [file, setFile] = useState(null);
  const [ocrResult, setOcrResult] = useState(null);

  const handleUpload = async () => {
    if (!file) return alert("Please select a file!");

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('http://localhost:8000/upload', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    setOcrResult(data);
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100">
      <h1 className="text-3xl font-bold mb-4">Marksheet OCR Upload</h1>

      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button
        onClick={handleUpload}
        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded"
      >
        Upload & Extract Marks
      </button>

      {ocrResult && (
        <div className="mt-6 p-4 bg-white rounded shadow-md">
          <h2 className="text-xl font-semibold mb-2">Extracted Data</h2>
          <p><strong>RRN:</strong> {ocrResult.RRN}</p>
          <p><strong>Name:</strong> {ocrResult.Name}</p>
          <p><strong>Part-A:</strong> {ocrResult["Part-A"]}</p>
          <p><strong>Part-B:</strong> {ocrResult["Part-B"]}</p>
          <p><strong>Total:</strong> {ocrResult.Total}</p>
        </div>
      )}
    </div>
  );
}

export default App;

