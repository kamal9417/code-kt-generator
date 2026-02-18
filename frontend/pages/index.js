import { useState } from 'react';
import { useRouter } from 'next/router';

export default function Home() {
  const [uploadMethod, setUploadMethod] = useState('zip'); // 'zip' or 'github'
  const [file, setFile] = useState(null);
  const [githubUrl, setGithubUrl] = useState('');
  const [branch, setBranch] = useState('main');
  const [role, setRole] = useState('fullstack');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && !selectedFile.name.endsWith('.zip')) {
      setError('Please upload a ZIP file');
      return;
    }
    setFile(selectedFile);
    setError('');
  };

  const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

  const handleAnalyze = async () => {
    setError('');
    setLoading(true);

    try {
      let response;

      if (uploadMethod === 'zip') {
        // Upload ZIP file
        if (!file) {
          setError('Please select a ZIP file');
          setLoading(false);
          return;
        }

        const formData = new FormData();
        formData.append('file', file);

        response = await fetch(`${API_URL}/api/analyze/upload?role=${role}`, {
          method: 'POST',
          body: formData
        });
      } else {
        // GitHub URL
        if (!githubUrl) {
          setError('Please enter a GitHub URL');
          setLoading(false);
          return;
        }

        response = await fetch(`${API_URL}/api/analyze/github`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            repo_url: githubUrl,
            role: role,
            branch: branch
          })
        });
      }

      const data = await response.json();

      if (response.ok) {
        router.push(`/docs?project_id=${data.project_id}`);
      } else {
        setError(data.detail || 'Error analyzing project');
      }
    } catch (err) {
      setError('Failed to connect to server. Make sure backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-800 mb-4">
            📚 Code Documentation & KT Generator
          </h1>
          <p className="text-xl text-gray-600">
            Generate comprehensive documentation and personalized onboarding plans from any codebase
          </p>
        </div>

        {/* Main Card */}
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          
          {/* Method Selection */}
          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Choose Upload Method
            </label>
            <div className="flex gap-4">
              <button
                onClick={() => setUploadMethod('zip')}
                className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-all ${
                  uploadMethod === 'zip'
                    ? 'bg-indigo-600 text-white shadow-lg'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                📦 Upload ZIP File
              </button>
              <button
                onClick={() => setUploadMethod('github')}
                className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-all ${
                  uploadMethod === 'github'
                    ? 'bg-indigo-600 text-white shadow-lg'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                🐙 GitHub Repository
              </button>
            </div>
          </div>

          {/* ZIP Upload */}
          {uploadMethod === 'zip' && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload Project ZIP File
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-indigo-500 transition-colors">
                <input
                  type="file"
                  accept=".zip"
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-upload"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <div className="text-6xl mb-4">📦</div>
                  {file ? (
                    <p className="text-indigo-600 font-semibold">{file.name}</p>
                  ) : (
                    <>
                      <p className="text-gray-600 mb-2">Click to upload or drag and drop</p>
                      <p className="text-sm text-gray-500">ZIP files only</p>
                    </>
                  )}
                </label>
              </div>
              
              {/* Instructions */}
              <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-gray-700 mb-2">
                  <strong>How to create a ZIP:</strong>
                </p>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Right-click your project folder</li>
                  <li>• Select "Compress" or "Send to → Compressed folder"</li>
                  <li>• Upload the resulting .zip file here</li>
                </ul>
              </div>
            </div>
          )}

          {/* GitHub URL */}
          {uploadMethod === 'github' && (
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  GitHub Repository URL
                </label>
                <input
                  type="text"
                  value={githubUrl}
                  onChange={(e) => setGithubUrl(e.target.value)}
                  placeholder="https://github.com/username/repository"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Branch (optional)
                </label>
                <input
                  type="text"
                  value={branch}
                  onChange={(e) => setBranch(e.target.value)}
                  placeholder="main"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>

              {/* Instructions */}
              <div className="p-4 bg-green-50 rounded-lg">
                <p className="text-sm text-gray-700 mb-2">
                  <strong>Supports:</strong>
                </p>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>✅ Public repositories (no authentication needed)</li>
                  <li>✅ Any branch (main, develop, etc.)</li>
                  <li>✅ Python, JavaScript, TypeScript projects</li>
                </ul>
              </div>
            </div>
          )}

          {/* Role Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Your Role
            </label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            >
              <option value="fullstack">Full Stack Developer</option>
              <option value="frontend">Frontend Developer</option>
              <option value="backend">Backend Developer</option>
              <option value="devops">DevOps Engineer</option>
            </select>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600 text-sm">❌ {error}</p>
            </div>
          )}

          {/* Analyze Button */}
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-4 px-6 rounded-lg font-semibold text-lg hover:bg-indigo-700 disabled:bg-gray-400 transition-colors shadow-lg hover:shadow-xl"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Analyzing...
              </span>
            ) : (
              '🚀 Generate Documentation & KT Plan'
            )}
          </button>

          {/* Features List */}
          <div className="mt-8 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg">
            <h3 className="font-semibold text-gray-800 mb-3">✨ What you'll get:</h3>
            <div className="grid grid-cols-2 gap-3 text-sm text-gray-600">
              <div className="flex items-start">
                <span className="mr-2">📄</span>
                <span>Comprehensive documentation</span>
              </div>
              <div className="flex items-start">
                <span className="mr-2">📚</span>
                <span>10-day learning roadmap</span>
              </div>
              <div className="flex items-start">
                <span className="mr-2">🎯</span>
                <span>Role-based focus areas</span>
              </div>
              <div className="flex items-start">
                <span className="mr-2">✅</span>
                <span>Knowledge checkpoints</span>
              </div>
            </div>
          </div>
        </div>

        {/* Tech Stack Badge */}
        <div className="text-center mt-8 text-sm text-gray-500">
          Powered by FastAPI, Next.js, and AI
        </div>
      </div>
    </div>
  );
}
// import { useState } from 'react';
// import { useRouter } from 'next/router';

// export default function Home() {
//   const [path, setPath] = useState('');
//   const [role, setRole] = useState('fullstack');
//   const [loading, setLoading] = useState(false);
//   const router = useRouter();

//   const handleAnalyze = async () => {
//     if (!path) {
//       alert('Please enter a project path');
//       return;
//     }

//     setLoading(true);
    
//     try {
//       const response = await fetch('http://localhost:8000/api/analyze', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ path, role })
//       });

//       const data = await response.json();
      
//       if (response.ok) {
//         // Redirect to documentation page
//         router.push(`/docs?project_id=${data.project_id}`);
//       } else {
//         alert(data.detail || 'Error analyzing project');
//       }
//     } catch (error) {
//       alert('Failed to connect to server');
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="min-h-screen bg-linear-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
//       <div className="bg-white rounded-2xl shadow-xl p-8 max-w-2xl w-full">
//         <h1 className="text-4xl font-bold text-gray-800 mb-2">
//           📚 Code Documentation & KT Generator
//         </h1>
//         <p className="text-gray-600 mb-8">
//           Automatically generate documentation and personalized onboarding plans from your codebase
//         </p>

//         <div className="space-y-6">
//           <div>
//             <label className="block text-sm font-medium text-gray-700 mb-2">
//               Project Folder Path
//             </label>
//             <input
//               type="text"
//               value={path}
//               onChange={(e) => setPath(e.target.value)}
//               placeholder="/home/user/my-project"
//               className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
//             />
//           </div>

//           <div>
//             <label className="block text-sm font-medium text-gray-700 mb-2">
//               Your Role
//             </label>
//             <select
//               value={role}
//               onChange={(e) => setRole(e.target.value)}
//               className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
//             >
//               <option value="fullstack">Full Stack Developer</option>
//               <option value="frontend">Frontend Developer</option>
//               <option value="backend">Backend Developer</option>
//               <option value="devops">DevOps Engineer</option>
//             </select>
//           </div>

//           <button
//             onClick={handleAnalyze}
//             disabled={loading}
//             className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-indigo-700 disabled:bg-gray-400 transition-colors"
//           >
//             {loading ? '🔄 Analyzing...' : '🚀 Generate Documentation & KT'}
//           </button>
//         </div>

//         <div className="mt-8 p-4 bg-blue-50 rounded-lg">
//           <h3 className="font-semibold text-gray-800 mb-2">✨ What you'll get:</h3>
//           <ul className="text-sm text-gray-600 space-y-1">
//             <li>✅ Comprehensive project documentation</li>
//             <li>✅ Personalized 10-day learning plan</li>
//             <li>✅ Interactive codebase Q&A</li>
//             <li>✅ Knowledge checkpoints</li>
//           </ul>
//         </div>
//       </div>
//     </div>
//   );
// }